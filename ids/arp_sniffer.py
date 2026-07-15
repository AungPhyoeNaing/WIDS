import threading
import time
import json
from scapy.all import sniff, ARP

# ARP table entry aging: entries older than this are expired
# to prevent false positives from DHCP reassignment
ARP_TABLE_TIMEOUT = 300  # 5 minutes


class ARPSniffer:
    def __init__(self, callback, gateway_resolver=None):
        self.callback = callback
        self.gateway_resolver = gateway_resolver
        self.thread = None
        self.running = False
        # arp_table now stores (mac, timestamp) tuples for aging
        self.arp_table = {}

    def start(self, interface=None):
        self.running = True
        self.thread = threading.Thread(target=self._sniff_loop, args=(interface,), daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.running = False

    def _sniff_loop(self, interface):
        sniff(filter="arp", prn=self._handle_packet, store=False,
              stop_filter=lambda _: not self.running)

    def _expire_stale_entries(self):
        """Remove ARP table entries older than ARP_TABLE_TIMEOUT."""
        now = time.time()
        stale_ips = [
            ip for ip, (mac, ts) in self.arp_table.items()
            if now - ts > ARP_TABLE_TIMEOUT
        ]
        for ip in stale_ips:
            del self.arp_table[ip]

    def _handle_packet(self, packet):
        if packet.haslayer(ARP) and packet[ARP].op in (1, 2):
            ip = packet[ARP].psrc
            mac = packet[ARP].hwsrc

            if ip == "0.0.0.0":
                return

            # Periodically expire stale entries
            self._expire_stale_entries()

            # ── Gateway-specific detection (ESP32-powered) ──────────────
            if self.gateway_resolver and ip == self.gateway_resolver.gateway_ip:
                gateway_mac = self.gateway_resolver.gateway_mac
                if gateway_mac and mac.upper() != gateway_mac.upper():
                    # Gateway MAC mismatch! This is a spoof attempt.
                    self.callback({
                        "type": "ARP",
                        "subtype": "ARP Spoof",
                        "alert_type": "gateway_spoof",
                        "source_ip": ip,
                        "mac_src": mac,
                        "mac_dst": packet[ARP].hwdst,
                        "old_mac": gateway_mac,
                        "gateway_mac": gateway_mac,
                        "confidence": self.gateway_resolver.get_confidence(),
                        "spoofed": True,
                        "timestamp": time.time()
                    })
                    return

                # Gateway MAC matches — update table, no alert
                self.arp_table[ip] = (mac, time.time())
                return

            # ── Standard first-seen detection for non-gateway IPs ───────
            entry = self.arp_table.get(ip)
            old_mac = entry[0] if entry else None

            spoofed = False
            if old_mac and old_mac != mac:
                spoofed = True
            else:
                self.arp_table[ip] = (mac, time.time())

            if spoofed:
                # Determine confidence based on gateway resolver state
                confidence = "FIRST_SEEN"
                if self.gateway_resolver:
                    confidence = self.gateway_resolver.get_confidence()

                self.callback({
                    "type": "ARP",
                    "subtype": "ARP Spoof",
                    "alert_type": "ip_mac_change",
                    "source_ip": ip,
                    "mac_src": mac,
                    "mac_dst": packet[ARP].hwdst,
                    "old_mac": old_mac or "",
                    "confidence": confidence,
                    "spoofed": True,
                    "timestamp": time.time()
                })
