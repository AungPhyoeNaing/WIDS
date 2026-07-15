import unittest
from gui.app import App


class DummyApp:
    def __init__(self):
        self.alert_count = 0
        self.alerts_list = []
        self.deauth_count = 0
        self.last_deauth_alert_time = 0.0
        self.deauth_history = {}
        self.deauth_alert_cooldown = {}

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

    def test_first_deauth_creates_suspicious_alert(self):
        app = self._make_app()
        packet = {"subtype": "Deauthentication", "mac_dst": "AA:BB:CC:DD:EE:FF"}
        App._handle_deauth_packet(app, packet)

        self.assertEqual(app.alert_count, 1)
        self.assertEqual(len(app.alerts_list), 1)
        self.assertEqual(app.alerts_list[0]["type"], "Deauth Activity")
        self.assertEqual(app.alerts_list[0]["severity"], "Medium")

    def test_tenth_deauth_escalates_to_flood_alert(self):
        app = self._make_app(deauth_count=9)
        import time
        from collections import deque
        mac = "AA:BB:CC:DD:EE:FF"
        now = time.time()
        # Pre-populate 9 deauths within the last 5 seconds
        app.deauth_history[mac] = deque([now - 1] * 9, maxlen=50)
        packet = {"subtype": "Deauthentication", "mac_dst": mac}
        App._handle_deauth_packet(app, packet)

        self.assertEqual(app.alert_count, 1)
        self.assertEqual(len(app.alerts_list), 1)
        self.assertEqual(app.alerts_list[0]["type"], "Deauth Flood")
        self.assertEqual(app.alerts_list[0]["severity"], "High")


if __name__ == "__main__":
    unittest.main()
