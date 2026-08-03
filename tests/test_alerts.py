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

    def test_high_volume_deauth_flood_rate_limiting(self):
        app = self._make_app()
        packet = {
            "mac_src": "AA:BB:CC:DD:EE:FF",
            "mac_dst": "FF:FF:FF:FF:FF:FF",
            "bssid": "11:22:33:44:55:66",
            "subtype": "Deauthentication",
        }
        # Simulate a burst of 500 deauth packets
        for _ in range(500):
            App._handle_deauth_packet(app, packet)

        # Should deduplicate into a single alert card with updated seen_count
        self.assertEqual(len(app.alerts_list), 1)
        self.assertEqual(app.alert_count, 1)
        alert = app.alerts_list[0]
        self.assertEqual(alert["seen_count"], 500)

    def test_evil_twin_detection_rogue_bssid(self):
        app = App.__new__(App)
        app.ssid_to_bssid = {"TargetWiFi": {"11:22:33:44:55:66"}}
        app.bssid_last_seen = {"11:22:33:44:55:66": time.time() - 30} # Seen 30s ago (exceeded 15s)
        app.bssid_channel = {"11:22:33:44:55:66": 6}
        app.bssid_rssi = {"11:22:33:44:55:66": deque([-50])}
        app.target_ssid = "TargetWiFi"
        app.whitelist = {}
        app.ROUTER_OUIS = set()
        app.LAPTOP_NIC_OUIS = set()
        app.OUI_DATABASE = {}

        # Rogue AP appears (airbase-ng / hostapd with local admin MAC)
        rogue_bssid = "02:00:00:11:22:33"
        score, reasons = app._score_evil_twin("TargetWiFi", rogue_bssid, 11, -75)

        # Baseline score: BSSID conflict (+50), Channel mismatch (+20), RSSI anomaly (+20), Locally Admin MAC (+30) = 100
        self.assertGreaterEqual(score, 70)
        self.assertGreater(len(reasons), 0)


if __name__ == "__main__":
    unittest.main()
