"""Deauthentication Attack Detection Engine"""

from collections import deque, defaultdict
from datetime import datetime
import time

from ids.config import (
    TIME_WINDOW,
    MAX_DEAUTH_PER_WINDOW,
    MAX_VICTIMS_PER_AP,
    MAX_REPEAT_TO_VICTIM,
    ATTACK_DURATION,
    TIMING_TOLERANCE,
    ALERT_SCORE,
    REASON_CODES,
)
from ids import config as ids_config

from ids.logger import IDSLogger


class DeauthDetector:
    def __init__(self):
        self.logger = IDSLogger()

        self.packet_times = deque()
        self.ap_victims = defaultdict(set)
        self.victim_counter = defaultdict(int)
        self.attack_times = defaultdict(list)
        self.timing_history = defaultdict(lambda: deque(maxlen=20))
        self.reason_counter = defaultdict(lambda: deque(maxlen=20))
        self.alert_cache = {}
        self._last_log_time = {}
        self._last_cleanup_time = 0

    def _cleanup_stale_data(self, now):
        """Prune historical state to prevent memory leaks during flood attacks."""
        if now - self._last_cleanup_time < 10:
            return
        self._last_cleanup_time = now

        # Prune attack_times older than 60s
        for src in list(self.attack_times.keys()):
            times = self.attack_times[src]
            self.attack_times[src] = [t for t in times if now - t <= 60]
            if not self.attack_times[src]:
                del self.attack_times[src]

        # Prune timing_history older than 60s
        for src in list(self.timing_history.keys()):
            while self.timing_history[src] and now - self.timing_history[src][0] > 60:
                self.timing_history[src].popleft()
            if not self.timing_history[src]:
                del self.timing_history[src]

    def process(self, packet):
        """
        Input:
        {
            "src": attacker MAC,
            "dst": victim MAC,
            "bssid": AP MAC,
            "reason": reason code,
            "timestamp": time
        }
        Output: Alert dictionary or None
        """
        if not packet:
            return None

        src = packet.get("src")
        dst = packet.get("dst")
        bssid = packet.get("bssid")
        reason = packet.get("reason", 0)
        now = time.time()

        if not packet.get("subtype") == "Deauthentication":
            return None

        self._cleanup_stale_data(now)

        score = 0
        reasons = []

        # CONDITION 1: High packet rate
        self.packet_times.append(now)
        while self.packet_times:
            if now - self.packet_times[0] > TIME_WINDOW:
                self.packet_times.popleft()
            else:
                break
        packet_count = len(self.packet_times)
        if packet_count >= MAX_DEAUTH_PER_WINDOW:
            score += 3
            reasons.append(
                f"High deauth rate ({packet_count} packets/{TIME_WINDOW}s)"
            )

        # CONDITION 2: Unknown BSSID
        if bssid:
            if bssid.upper() not in ids_config.WHITELIST_BSSID:
                score += 3
                reasons.append("Deauth source is not in trusted AP list")

        # CONDITION 3: Broadcast destination
        if dst:
            if dst.upper() == "FF:FF:FF:FF:FF:FF":
                score += 2
                reasons.append("Broadcast deauthentication detected")

        # CONDITION 4: One AP attacks many clients
        if src and dst:
            self.ap_victims[src].add(dst)
            victim_count = len(self.ap_victims[src])
            if victim_count >= MAX_VICTIMS_PER_AP:
                score += 2
                reasons.append(
                    f"One AP attacking many clients ({victim_count})"
                )

        # CONDITION 5: Repeated victim targeting
        if dst:
            self.victim_counter[dst] += 1
            if self.victim_counter[dst] >= MAX_REPEAT_TO_VICTIM:
                score += 2
                reasons.append(
                    f"Victim repeatedly attacked ({self.victim_counter[dst]} times)"
                )

        # CONDITION 6: Reason code analysis
        if src:
            self.reason_counter[src].append(reason)
            recent = list(self.reason_counter[src])[-10:]
            if len(set(recent)) == 1 and len(recent) >= 5:
                score += 1
                reason_name = REASON_CODES.get(reason, "Unknown")
                reasons.append(f"Repeated reason code: {reason_name}")

        # CONDITION 7: Attack duration
        if src:
            self.attack_times[src].append(now)
            start = self.attack_times[src][0]
            duration = now - start
            if duration >= ATTACK_DURATION:
                score += 2
                reasons.append(
                    f"Long attack duration ({int(duration)} seconds)"
                )

        # CONDITION 8: Fixed interval detection
        if src:
            history = self.timing_history[src]
            history.append(now)
            if len(history) >= 5:
                intervals = []
                for i in range(1, len(history)):
                    intervals.append(history[i] - history[i - 1])
                avg = sum(intervals) / len(intervals)
                stable = True
                for interval in intervals:
                    if abs(interval - avg) > TIMING_TOLERANCE:
                        stable = False
                if stable:
                    score += 1
                    reasons.append(
                        "Suspicious fixed packet timing pattern"
                    )

        # Final decision
        if score >= ALERT_SCORE:
            alert = {
                "type": "DEAUTHENTICATION_ATTACK",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": src,
                "victim": dst,
                "bssid": bssid,
                "score": score,
                "reasons": reasons,
            }
            self.generate_alert(alert)
            return alert

        return None

    def generate_alert(self, alert):
        now = time.time()
        key = (alert.get("source"), alert.get("bssid"))
        # Rate limit file logging to once every 5 seconds per (source, bssid)
        if now - self._last_log_time.get(key, 0) < 5:
            return
        self._last_log_time[key] = now

        message = "\n"
        message += "=" * 55 + "\n"
        message += "DEAUTHENTICATION ATTACK DETECTED\n"
        message += "=" * 55 + "\n"
        message += f"Time: {alert['time']}\n"
        message += f"Source: {alert['source']}\n"
        message += f"Victim: {alert['victim']}\n"
        message += f"BSSID: {alert['bssid']}\n"
        message += f"Suspicion Score: {alert['score']}\n\n"
        message += "Triggered Conditions:\n"
        for r in alert["reasons"]:
            message += "  * " + r + "\n"
        message += "=" * 55 + "\n"

        self.logger.warning(message)
