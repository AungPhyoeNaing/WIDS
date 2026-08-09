import unittest
import time
from collections import deque
from gui.app import App
from ids.deauth_detector import DeauthDetector


class DummyApp:
    def __init__(self):
        self.alert_count = 0
        self.alerts_list = []
        self.deauth_count = 0
        self.deauth_detector = DeauthDetector()

    def _add_alert(self, alert):
        self.alert_count += 1
        alert.setdefault("time", "now")
        alert.setdefault("last_seen", "now")
        self.alerts_list.append(alert)
        return alert


class DeauthAlertTests(unittest.TestCase):
    def _make_app(self, deauth_count=0):
        app = DummyApp()
        app.deauth_count = deauth_count
        return app

    def test_single_deauth_from_unknown_bssid_with_broadcast(self):
        app = self._make_app()
        packet = {
            "mac_src": "AA:BB:CC:DD:EE:FF",
            "mac_dst": "FF:FF:FF:FF:FF:FF",
            "bssid": "11:22:33:44:55:66",
            "subtype": "Deauthentication",
        }
        App._handle_deauth_packet(app, packet)

        self.assertEqual(app.alert_count, 1)
        self.assertEqual(len(app.alerts_list), 1)
        alert = app.alerts_list[0]
        self.assertIn("Deauth Attack", alert["type"])
        self.assertIn(alert["severity"], ("Critical", "High", "Medium"))
        self.assertEqual(alert["target_mac"], "FF:FF:FF:FF:FF:FF")
        self.assertEqual(alert["source_mac"], "AA:BB:CC:DD:EE:FF")
        self.assertGreaterEqual(alert["score"], 5)

    def test_single_deauth_below_threshold_no_alert(self):
        app = self._make_app()
        # Use a whitelisted BSSID and unicast destination to keep score low
        from ids import config as ids_config
        ids_config.WHITELIST_BSSID = {"AA:BB:CC:DD:EE:FF"}
        try:
            packet = {
                "mac_src": "AA:BB:CC:DD:EE:FF",
                "mac_dst": "11:22:33:44:55:66",
                "bssid": "AA:BB:CC:DD:EE:FF",
                "subtype": "Deauthentication",
            }
            App._handle_deauth_packet(app, packet)
            self.assertEqual(app.alert_count, 0)
        finally:
            ids_config.WHITELIST_BSSID = set()

    def test_deauth_attack_alert_includes_reasons(self):
        app = self._make_app()
        packet = {
            "mac_src": "AA:BB:CC:DD:EE:FF",
            "mac_dst": "FF:FF:FF:FF:FF:FF",
            "bssid": "11:22:33:44:55:66",
            "subtype": "Deauthentication",
        }
        App._handle_deauth_packet(app, packet)

        alert = app.alerts_list[0]
        self.assertIn("reasons", alert)
        self.assertIsInstance(alert["reasons"], list)
        self.assertGreater(len(alert["reasons"]), 0)
        self.assertIn("details", alert)
        self.assertIn("score", alert)

    def test_deauth_alert_rate_limiting_cooldown(self):
        app = self._make_app()
        packet1 = {
            "mac_src": "AA:BB:CC:DD:EE:FF",
            "mac_dst": "FF:FF:FF:FF:FF:FF",
            "bssid": "11:22:33:44:55:66",
            "subtype": "Deauthentication",
        }
        # First packet should trigger an alert
        App._handle_deauth_packet(app, packet1)
        self.assertEqual(app.alert_count, 1)

        # Second packet immediately after should NOT trigger an alert due to cooldown
        App._handle_deauth_packet(app, packet1)
        self.assertEqual(app.alert_count, 1)
        
        # Override the alert_cache time to simulate 11 seconds passing
        alert_key = ("AA:BB:CC:DD:EE:FF", "FF:FF:FF:FF:FF:FF")
        if alert_key in app.deauth_detector.alert_cache:
            app.deauth_detector.alert_cache[alert_key] -= 15
            
        # Third packet after cooldown should trigger an alert
        App._handle_deauth_packet(app, packet1)
        self.assertEqual(app.alert_count, 2)

    def test_deauth_mac_case_insensitivity(self):
        app = self._make_app()
        packet = {
            "mac_src": "aa:bb:cc:dd:ee:ff",
            "mac_dst": "ff:ff:ff:ff:ff:ff",
            "bssid": "11:22:33:44:55:66",
            "subtype": "Deauthentication",
        }
        App._handle_deauth_packet(app, packet)
        
        self.assertEqual(app.alert_count, 1)
        alert = app.alerts_list[0]
        self.assertEqual(alert["target_mac"], "FF:FF:FF:FF:FF:FF")
        self.assertEqual(alert["source_mac"], "AA:BB:CC:DD:EE:FF")

if __name__ == "__main__":
    unittest.main()
