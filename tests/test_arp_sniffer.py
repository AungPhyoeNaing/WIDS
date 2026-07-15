import unittest
from unittest.mock import MagicMock
from ids.arp_sniffer import ARPSniffer

# Create a mock ARP packet class since scapy might not be available or 
# we don't want to rely on the actual packet in tests
class MockARP:
    def __init__(self, op, psrc, hwsrc, hwdst):
        self.op = op
        self.psrc = psrc
        self.hwsrc = hwsrc
        self.hwdst = hwdst

class MockPacket:
    def __init__(self, arp_layer=None):
        self._arp_layer = arp_layer

    def haslayer(self, layer):
        return self._arp_layer is not None
        
    def __getitem__(self, layer):
        return self._arp_layer


class MockGatewayResolver:
    """Mock GatewayResolver for testing."""
    def __init__(self, gateway_ip=None, gateway_mac=None, confidence="FIRST_SEEN"):
        self.gateway_ip = gateway_ip
        self.gateway_mac = gateway_mac
        self._confidence = confidence
    
    def get_confidence(self):
        return self._confidence


class TestARPSniffer(unittest.TestCase):
    def setUp(self):
        self.mock_callback = MagicMock()
        self.sniffer = ARPSniffer(self.mock_callback)

    def test_normal_arp_reply_no_alert(self):
        packet = MockPacket(MockARP(op=2, psrc="192.168.1.1", hwsrc="AA:AA:AA:AA:AA:AA", hwdst="BB:BB:BB:BB:BB:BB"))
        self.sniffer._handle_packet(packet)
        self.mock_callback.assert_not_called()
        # arp_table now stores (mac, timestamp) tuples
        self.assertEqual(self.sniffer.arp_table["192.168.1.1"][0], "AA:AA:AA:AA:AA:AA")

    def test_arp_spoof_detection(self):
        # First ARP reply (normal)
        packet1 = MockPacket(MockARP(op=2, psrc="192.168.1.1", hwsrc="AA:AA:AA:AA:AA:AA", hwdst="BB:BB:BB:BB:BB:BB"))
        self.sniffer._handle_packet(packet1)
        
        # Second ARP reply from SAME IP but DIFFERENT MAC (Spoofing)
        packet2 = MockPacket(MockARP(op=2, psrc="192.168.1.1", hwsrc="CC:CC:CC:CC:CC:CC", hwdst="BB:BB:BB:BB:BB:BB"))
        self.sniffer._handle_packet(packet2)
        
        # Check if callback was called with spoofed alert
        self.assertTrue(self.mock_callback.called)
        alert = self.mock_callback.call_args[0][0]
        self.assertEqual(alert["type"], "ARP")
        self.assertEqual(alert["subtype"], "ARP Spoof")
        self.assertTrue(alert["spoofed"])
        self.assertEqual(alert["source_ip"], "192.168.1.1")
        self.assertEqual(alert["old_mac"], "AA:AA:AA:AA:AA:AA")
        self.assertEqual(alert["mac_src"], "CC:CC:CC:CC:CC:CC")
        self.assertEqual(alert["alert_type"], "ip_mac_change")
        self.assertEqual(alert["confidence"], "FIRST_SEEN")

    def test_ignore_zero_ip(self):
        """ARP packets with 0.0.0.0 source should be silently ignored."""
        packet = MockPacket(MockARP(op=1, psrc="0.0.0.0", hwsrc="AA:AA:AA:AA:AA:AA", hwdst="FF:FF:FF:FF:FF:FF"))
        self.sniffer._handle_packet(packet)
        self.mock_callback.assert_not_called()
        self.assertEqual(len(self.sniffer.arp_table), 0)

    def test_same_mac_no_alert(self):
        """Same IP+MAC seen twice should not trigger an alert."""
        packet = MockPacket(MockARP(op=2, psrc="192.168.1.1", hwsrc="AA:AA:AA:AA:AA:AA", hwdst="BB:BB:BB:BB:BB:BB"))
        self.sniffer._handle_packet(packet)
        self.sniffer._handle_packet(packet)
        self.mock_callback.assert_not_called()


class TestARPSnifferWithGateway(unittest.TestCase):
    """Tests for gateway-aware ARP spoof detection."""

    def setUp(self):
        self.mock_callback = MagicMock()
        self.gateway_resolver = MockGatewayResolver(
            gateway_ip="192.168.1.1",
            gateway_mac="RR:RR:RR:RR:RR:RR",
            confidence="HARDWARE_VERIFIED"
        )
        self.sniffer = ARPSniffer(self.mock_callback, self.gateway_resolver)

    def test_gateway_spoof_detected(self):
        """ARP reply for gateway IP with wrong MAC triggers gateway_spoof alert."""
        packet = MockPacket(MockARP(
            op=2, psrc="192.168.1.1",
            hwsrc="AA:AA:AA:AA:AA:AA",  # Wrong MAC - not the real router
            hwdst="BB:BB:BB:BB:BB:BB"
        ))
        self.sniffer._handle_packet(packet)

        self.assertTrue(self.mock_callback.called)
        alert = self.mock_callback.call_args[0][0]
        self.assertEqual(alert["type"], "ARP")
        self.assertEqual(alert["alert_type"], "gateway_spoof")
        self.assertTrue(alert["spoofed"])
        self.assertEqual(alert["source_ip"], "192.168.1.1")
        self.assertEqual(alert["mac_src"], "AA:AA:AA:AA:AA:AA")
        self.assertEqual(alert["old_mac"], "RR:RR:RR:RR:RR:RR")
        self.assertEqual(alert["confidence"], "HARDWARE_VERIFIED")

    def test_gateway_normal_no_alert(self):
        """ARP reply for gateway IP with correct MAC should NOT trigger an alert."""
        packet = MockPacket(MockARP(
            op=2, psrc="192.168.1.1",
            hwsrc="RR:RR:RR:RR:RR:RR",  # Correct MAC
            hwdst="BB:BB:BB:BB:BB:BB"
        ))
        self.sniffer._handle_packet(packet)

        self.mock_callback.assert_not_called()
        # Should be stored in arp_table
        self.assertIn("192.168.1.1", self.sniffer.arp_table)

    def test_non_gateway_ip_still_uses_first_seen(self):
        """Non-gateway IPs should still use the standard first-seen detection."""
        # First packet for a non-gateway IP
        packet1 = MockPacket(MockARP(
            op=2, psrc="192.168.1.50",
            hwsrc="DD:DD:DD:DD:DD:DD",
            hwdst="BB:BB:BB:BB:BB:BB"
        ))
        self.sniffer._handle_packet(packet1)
        self.mock_callback.assert_not_called()

        # Second packet: same IP, different MAC → spoof
        packet2 = MockPacket(MockARP(
            op=2, psrc="192.168.1.50",
            hwsrc="EE:EE:EE:EE:EE:EE",
            hwdst="BB:BB:BB:BB:BB:BB"
        ))
        self.sniffer._handle_packet(packet2)

        self.assertTrue(self.mock_callback.called)
        alert = self.mock_callback.call_args[0][0]
        self.assertEqual(alert["alert_type"], "ip_mac_change")
        self.assertEqual(alert["source_ip"], "192.168.1.50")
        self.assertEqual(alert["old_mac"], "DD:DD:DD:DD:DD:DD")
        self.assertEqual(alert["mac_src"], "EE:EE:EE:EE:EE:EE")

    def test_arp_table_aging(self):
        """Entries older than ARP_TABLE_TIMEOUT should be expired."""
        import time as time_mod

        # Insert an entry with an old timestamp
        self.sniffer.arp_table["192.168.1.50"] = ("DD:DD:DD:DD:DD:DD", time_mod.time() - 400)

        # Send a packet for a different IP to trigger expiry check
        packet = MockPacket(MockARP(
            op=2, psrc="192.168.1.60",
            hwsrc="FF:FF:FF:FF:FF:FF",
            hwdst="BB:BB:BB:BB:BB:BB"
        ))
        self.sniffer._handle_packet(packet)

        # The old entry should have been cleaned up
        self.assertNotIn("192.168.1.50", self.sniffer.arp_table)
        # The new entry should exist
        self.assertIn("192.168.1.60", self.sniffer.arp_table)

    def test_no_gateway_resolver_falls_back(self):
        """Without a gateway_resolver, sniffer should use standard detection."""
        sniffer = ARPSniffer(self.mock_callback)  # No gateway_resolver
        
        packet1 = MockPacket(MockARP(op=2, psrc="192.168.1.1", hwsrc="AA:AA:AA:AA:AA:AA", hwdst="BB:BB:BB:BB:BB:BB"))
        sniffer._handle_packet(packet1)
        self.mock_callback.assert_not_called()

        packet2 = MockPacket(MockARP(op=2, psrc="192.168.1.1", hwsrc="CC:CC:CC:CC:CC:CC", hwdst="BB:BB:BB:BB:BB:BB"))
        sniffer._handle_packet(packet2)
        self.assertTrue(self.mock_callback.called)


if __name__ == "__main__":
    unittest.main()
