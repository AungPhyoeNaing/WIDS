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

ALERT_COOLDOWN = 10  # Seconds before same (src, dst) can trigger another alert
GLOBAL_ALERT_COOLDOWN = 30  # Seconds before ANY new deauth alert can fire (prevents flood during mass attacks)


class DeauthDetector:
    def __init__(self):
        self.logger = IDSLogger()

        self.packet_times = deque()
        self.ap_victims = defaultdict(set)
        # Store (victim, timestamp) for cleanup
        self.victim_counter = defaultdict(list)
        self.attack_times = defaultdict(list)
        self.timing_history = defaultdict(list)
        self.reason_counter = defaultdict(list)
        self.alert_cache = {}
        self.last_global_alert = 0  # Timestamp of last alert fired globally
        
        self.last_cleanup = time.time()

    def _cleanup_old_state(self, now):
        """Periodically clean up state older than TIME_WINDOW to prevent memory leaks and permanent false positives."""
        if now - self.last_cleanup < 5:  # Run cleanup every 5 seconds at most
            return
        self.last_cleanup = now
        cutoff = now - (TIME_WINDOW * 2)

        # Cleanup attack times
        for src in list(self.attack_times.keys()):
            self.attack_times[src] = [t for t in self.attack_times[src] if t > cutoff]
            if not self.attack_times[src]:
                del self.attack_times[src]
                if src in self.ap_victims:
                    del self.ap_victims[src]

        # Cleanup victim counter
        for dst in list(self.victim_counter.keys()):
            self.victim_counter[dst] = [t for t in self.victim_counter[dst] if t > cutoff]
            if not self.victim_counter[dst]:
                del self.victim_counter[dst]

        # Cleanup timing history
        for src in list(self.timing_history.keys()):
            self.timing_history[src] = [t for t in self.timing_history[src] if t > cutoff]
            if not self.timing_history[src]:
                del self.timing_history[src]

        # Cleanup reason counter
        for src in list(self.reason_counter.keys()):
            self.reason_counter[src] = [(r, t) for r, t in self.reason_counter[src] if t > cutoff]
            if not self.reason_counter[src]:
                del self.reason_counter[src]

        # Cleanup alert cache
        for key in list(self.alert_cache.keys()):
            if now - self.alert_cache[key] > ALERT_COOLDOWN:
                del self.alert_cache[key]

    def process(self, packet):
        if not packet:
            return None

        # 1. MAC Normalization
        src = packet.get("src", "").upper() if packet.get("src") else None
        dst = packet.get("dst", "").upper() if packet.get("dst") else None
        bssid = packet.get("bssid", "").upper() if packet.get("bssid") else None
        reason = packet.get("reason", 0)
        
        # 2. Timestamping
        now = packet.get("timestamp", time.time())

        if not packet.get("subtype") == "Deauthentication":
            return None

        # 3. State Cleanup
        self._cleanup_old_state(now)

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
            if bssid not in ids_config.WHITELIST_BSSID:
                score += 3
                reasons.append("Deauth source is not in trusted AP list")

        # CONDITION 3: Broadcast destination
        if dst:
            if dst == "FF:FF:FF:FF:FF:FF":
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
            self.victim_counter[dst].append(now)
            if len(self.victim_counter[dst]) >= MAX_REPEAT_TO_VICTIM:
                score += 2
                reasons.append(
                    f"Victim repeatedly attacked ({len(self.victim_counter[dst])} times)"
                )

        # CONDITION 6: Reason code analysis
        if src:
            self.reason_counter[src].append((reason, now))
            recent_reasons = [r[0] for r in self.reason_counter[src][-10:]]
            if len(set(recent_reasons)) == 1 and len(recent_reasons) >= 5:
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
                
                # 5. Fast-Rate Timing Check (Ignore slow, routine disassociations)
                if avg < 2.0:
                    stable = True
                    for interval in intervals:
                        if abs(interval - avg) > TIMING_TOLERANCE:
                            stable = False
                    if stable:
                        score += 1
                        reasons.append(
                            "Suspicious fixed packet timing pattern"
                        )
            if len(history) > 20:
                history.pop(0)

        # Final decision & Alert Cooldown
        if score >= ALERT_SCORE:
            alert_key = (src, dst)
            last_alert = self.alert_cache.get(alert_key, 0)
            
            # 4. Alert Rate-Limiting (Anti-Spam)
            # Two-tier cooldown:
            #   - Per (src, dst) pair: ALERT_COOLDOWN seconds
            #   - Global: GLOBAL_ALERT_COOLDOWN seconds (prevents flood from mass deauth to many clients)
            if now - last_alert >= ALERT_COOLDOWN and now - self.last_global_alert >= GLOBAL_ALERT_COOLDOWN:
                self.alert_cache[alert_key] = now
                self.last_global_alert = now
                alert = {
                    "type": "DEAUTHENTICATION_ATTACK",
                    "time": datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S"),
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
        message = "\n"
        message += "=" * 55 + "\n"
        message += "DEAUTHENTICATION ATTACK DETECTED\n"
        message += "=" * 55 + "\n"
        message += f"Time: {alert['time']}\n"
        
        if alert['source'] == alert['bssid']:
            message += f"Spoofed Source: {alert['source']} (Attacker impersonating AP!)\n"
        else:
            message += f"Spoofed Source: {alert['source']} (Attacker impersonating Client!)\n"
            
        message += f"Target/Victim: {alert['victim']}\n"
        message += f"BSSID: {alert['bssid']}\n"
        message += f"Suspicion Score: {alert['score']}\n\n"
        message += "Triggered Conditions:\n"
        for r in alert["reasons"]:
            message += "  * " + r + "\n"
        message += "=" * 55 + "\n"

        self.logger.warning(message)
