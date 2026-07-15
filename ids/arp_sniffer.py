import threading
import time
import json
from scapy.all import sniff, ARP

class ARPSniffer:
    def __init__(self, callback):
        self.callback = callback
        self.thread = None
        self.running = False
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

    def _handle_packet(self, packet):
        if packet.haslayer(ARP) and packet[ARP].op in (1, 2):
            ip = packet[ARP].psrc
            mac = packet[ARP].hwsrc
            
            if ip == "0.0.0.0":
                return
                
            old_mac = self.arp_table.get(ip)
            spoofed = False
            if old_mac and old_mac != mac:
                spoofed = True
            else:
                self.arp_table[ip] = mac

            if spoofed:
                self.callback({
                    "type": "ARP",
                    "subtype": "ARP Spoof",
                    "source_ip": ip,
                    "mac_src": mac,
                    "mac_dst": packet[ARP].hwdst,
                    "old_mac": old_mac or "",
                    "spoofed": True,
                    "timestamp": time.time()
                })
