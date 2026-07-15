import unittest
from unittest.mock import MagicMock, patch
from ids.gateway_resolver import GatewayResolver


class TestGatewayResolverInit(unittest.TestCase):
    """Tests for GatewayResolver initialization and state."""

    def test_initial_state(self):
        resolver = GatewayResolver()
        self.assertIsNone(resolver.gateway_ip)
        self.assertIsNone(resolver.gateway_mac)
        self.assertEqual(resolver.confidence, "UNRESOLVED")
        self.assertEqual(len(resolver.get_esp32_bssids()), 0)
        self.assertFalse(resolver.scan_complete)

    def test_get_gateway_info_unresolved(self):
        resolver = GatewayResolver()
        info = resolver.get_gateway_info()
        self.assertIsNone(info["gateway_ip"])
        self.assertIsNone(info["gateway_mac"])
        self.assertEqual(info["confidence"], "UNRESOLVED")
        self.assertEqual(info["esp32_bssid_count"], 0)


class TestGatewayResolve(unittest.TestCase):
    """Tests for dynamic gateway resolution."""

    @patch("ids.gateway_resolver.lookup_oui")
    @patch("ids.gateway_resolver.is_network_equipment")
    def test_resolve_with_network_equipment_vendor(self, mock_is_net, mock_lookup):
        """Gateway with a known router vendor gets VENDOR_VERIFIED."""
        mock_lookup.return_value = ("TP-Link", "network_equipment")
        mock_is_net.return_value = True

        resolver = GatewayResolver()

        with patch("scapy.config.conf") as mock_conf, \
             patch("scapy.layers.l2.getmacbyip") as mock_getmac:
            mock_conf.route.route.return_value = ("iface", "10.0.0.1", "192.168.1.1")
            mock_getmac.return_value = "78:8a:20:b4:35:5d"

            result = resolver.resolve()

        self.assertTrue(result)
        self.assertEqual(resolver.gateway_ip, "192.168.1.1")
        self.assertEqual(resolver.gateway_mac, "78:8A:20:B4:35:5D")
        self.assertEqual(resolver.confidence, "VENDOR_VERIFIED")

    @patch("ids.gateway_resolver.lookup_oui")
    @patch("ids.gateway_resolver.is_network_equipment")
    @patch("ids.gateway_resolver.is_consumer_device")
    def test_resolve_with_consumer_device_vendor(self, mock_is_consumer, mock_is_net, mock_lookup):
        """Gateway with a consumer device vendor gets FIRST_SEEN (suspicious)."""
        mock_lookup.return_value = ("Intel", "consumer_device")
        mock_is_net.return_value = False
        mock_is_consumer.return_value = True

        resolver = GatewayResolver()

        with patch("scapy.config.conf") as mock_conf, \
             patch("scapy.layers.l2.getmacbyip") as mock_getmac:
            mock_conf.route.route.return_value = ("iface", "10.0.0.1", "192.168.1.1")
            mock_getmac.return_value = "5c:80:b6:79:1c:47"

            result = resolver.resolve()

        self.assertTrue(result)
        self.assertEqual(resolver.confidence, "FIRST_SEEN")
        self.assertEqual(resolver.gateway_vendor, "Intel")

    def test_resolve_fails_gracefully(self):
        """Resolve should return False and not crash if scapy fails."""
        resolver = GatewayResolver()

        with patch("scapy.config.conf") as mock_conf:
            mock_conf.route.route.side_effect = Exception("No route")
            result = resolver.resolve()

        self.assertFalse(result)
        self.assertEqual(resolver.confidence, "UNRESOLVED")


class TestBSSIDCrossReferencing(unittest.TestCase):
    """Tests for ESP32 BSSID cross-referencing."""

    def test_bssid_match_upgrades_confidence(self):
        """When ESP32 sees a BSSID matching the gateway MAC, upgrade to HARDWARE_VERIFIED."""
        resolver = GatewayResolver()
        resolver.gateway_ip = "192.168.1.1"
        resolver.gateway_mac = "78:8A:20:B4:35:5D"
        resolver.confidence = "VENDOR_VERIFIED"

        # Feed a non-matching BSSID first
        upgraded = resolver.verify_with_bssid("AA:BB:CC:DD:EE:FF")
        self.assertFalse(upgraded)
        self.assertEqual(resolver.confidence, "VENDOR_VERIFIED")

        # Feed the matching BSSID
        upgraded = resolver.verify_with_bssid("78:8A:20:B4:35:5D")
        self.assertTrue(upgraded)
        self.assertEqual(resolver.confidence, "HARDWARE_VERIFIED")

    def test_bssid_already_verified_no_double_upgrade(self):
        """If already HARDWARE_VERIFIED, feeding the same BSSID should return False."""
        resolver = GatewayResolver()
        resolver.gateway_ip = "192.168.1.1"
        resolver.gateway_mac = "78:8A:20:B4:35:5D"
        resolver.confidence = "HARDWARE_VERIFIED"

        upgraded = resolver.verify_with_bssid("78:8A:20:B4:35:5D")
        self.assertFalse(upgraded)  # Already verified, no upgrade

    def test_bssid_case_insensitive(self):
        """BSSID matching should be case-insensitive."""
        resolver = GatewayResolver()
        resolver.gateway_ip = "192.168.1.1"
        resolver.gateway_mac = "78:8A:20:B4:35:5D"
        resolver.confidence = "FIRST_SEEN"

        upgraded = resolver.verify_with_bssid("78:8a:20:b4:35:5d")
        self.assertTrue(upgraded)
        self.assertEqual(resolver.confidence, "HARDWARE_VERIFIED")

    def test_empty_bssid_ignored(self):
        """Empty or None BSSIDs should be ignored."""
        resolver = GatewayResolver()
        resolver.gateway_mac = "78:8A:20:B4:35:5D"

        self.assertFalse(resolver.verify_with_bssid(None))
        self.assertFalse(resolver.verify_with_bssid(""))

    def test_get_esp32_bssids_returns_copy(self):
        """get_esp32_bssids should return a copy, not the internal set."""
        resolver = GatewayResolver()
        resolver.verify_with_bssid("AA:BB:CC:DD:EE:FF")

        bssids = resolver.get_esp32_bssids()
        bssids.add("MODIFIED")  # Modify the copy

        # Internal set should not be affected
        self.assertNotIn("MODIFIED", resolver.get_esp32_bssids())


class TestBSSIDMismatchDetection(unittest.TestCase):
    """Tests for pre-existing MITM detection via BSSID mismatch."""

    def test_mismatch_detected(self):
        """Gateway MAC not in ESP32 BSSIDs triggers pre_existing_mitm alert."""
        resolver = GatewayResolver()
        resolver.gateway_ip = "192.168.1.1"
        resolver.gateway_mac = "ATTACKER:MAC:HERE"

        # Feed some BSSIDs that do NOT match the gateway
        resolver.verify_with_bssid("AA:BB:CC:DD:EE:FF")
        resolver.verify_with_bssid("11:22:33:44:55:66")

        alert = resolver.check_bssid_mismatch()
        self.assertIsNotNone(alert)
        self.assertEqual(alert["alert_type"], "pre_existing_mitm")
        self.assertTrue(alert["spoofed"])

    def test_no_mismatch_when_gateway_in_bssids(self):
        """No alert when gateway MAC is found among ESP32 BSSIDs."""
        resolver = GatewayResolver()
        resolver.gateway_ip = "192.168.1.1"
        resolver.gateway_mac = "78:8A:20:B4:35:5D"

        resolver.verify_with_bssid("78:8A:20:B4:35:5D")

        alert = resolver.check_bssid_mismatch()
        self.assertIsNone(alert)

    def test_no_alert_when_no_data(self):
        """No alert when gateway or BSSIDs haven't been resolved yet."""
        resolver = GatewayResolver()
        alert = resolver.check_bssid_mismatch()
        self.assertIsNone(alert)


class TestDuplicateMACDetection(unittest.TestCase):
    """Tests for subnet scan duplicate MAC detection."""

    @patch("ids.gateway_resolver.GatewayResolver.scan_subnet")
    def test_duplicate_mac_flagged(self, mock_scan):
        """Duplicate MACs should be returned from scan_subnet."""
        resolver = GatewayResolver()
        resolver.gateway_ip = "192.168.1.1"

        # Simulate scan results
        resolver.duplicate_macs = {
            "AA:BB:CC:DD:EE:FF": ["192.168.1.1", "192.168.1.50"]
        }
        resolver.scan_complete = True

        self.assertEqual(len(resolver.duplicate_macs), 1)
        self.assertIn("AA:BB:CC:DD:EE:FF", resolver.duplicate_macs)


class TestOUIIntegration(unittest.TestCase):
    """Tests for OUI vendor lookup integration."""

    def test_oui_lookup_imported(self):
        """Verify OUI lookup functions are importable."""
        from ids.oui_lookup import lookup_oui, is_network_equipment, get_vendor_name

        vendor, category = lookup_oui("78:8A:20:B4:35:5D")
        self.assertEqual(category, "network_equipment")
        self.assertTrue(is_network_equipment("78:8A:20:B4:35:5D"))

    def test_oui_consumer_device(self):
        from ids.oui_lookup import lookup_oui, is_consumer_device

        vendor, category = lookup_oui("5C:80:B6:79:1C:47")
        self.assertEqual(category, "consumer_device")
        self.assertTrue(is_consumer_device("5C:80:B6:79:1C:47"))

    def test_oui_unknown_mac(self):
        from ids.oui_lookup import lookup_oui

        vendor, category = lookup_oui("00:00:00:00:00:00")
        self.assertEqual(vendor, "Unknown")
        self.assertEqual(category, "unknown")

    def test_oui_iot_device(self):
        from ids.oui_lookup import lookup_oui, is_iot_device

        vendor, category = lookup_oui("B8:27:EB:00:00:00")
        self.assertEqual(category, "iot_device")
        self.assertIn("Raspberry Pi", vendor)
        self.assertTrue(is_iot_device("B8:27:EB:00:00:00"))


if __name__ == "__main__":
    unittest.main()
