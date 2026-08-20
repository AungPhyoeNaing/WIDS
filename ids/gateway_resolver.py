"""
Gateway Resolver Module.

Provides dynamic gateway detection, ESP32 BSSID cross-referencing,
duplicate-MAC subnet scanning, and OUI vendor heuristic checks
for robust ARP spoof detection.
"""

import threading
import time
import logging

from ids.oui_lookup import lookup_oui, is_network_equipment, is_consumer_device, is_iot_device

logger = logging.getLogger(__name__)


class GatewayResolver:
    """
    Dynamically resolves the default gateway and cross-references it
    against ESP32-observed BSSIDs to detect pre-existing MITM attacks.

    Confidence levels:
        - "HARDWARE_VERIFIED": The gateway MAC matches a BSSID seen by
          the ESP32 over the air. Highest confidence.
        - "VENDOR_VERIFIED": The gateway MAC belongs to a known network
          equipment vendor (e.g., TP-Link, Cisco). Medium confidence.
        - "FIRST_SEEN": The gateway MAC was dynamically resolved but has
          not been verified by ESP32 or vendor lookup. Lowest confidence.
    """

    def __init__(self):
        self.gateway_ip = None
        self.gateway_mac = None
        self.confidence = "UNRESOLVED"

        # Set of BSSIDs observed by the ESP32 from Beacon frames
        self._esp32_bssids = set()
        self._lock = threading.Lock()

        # Results from the subnet duplicate-MAC scan
        self.duplicate_macs = {}  # mac -> list of IPs
        self.scan_complete = False

        # Vendor info for the gateway
        self.gateway_vendor = None
        self.gateway_vendor_category = None

    def resolve(self):
        """
        Dynamically discover the default gateway IP and MAC address.
        Should be called once at startup from a background thread.

        Returns:
            bool: True if gateway was successfully resolved, False otherwise.
        """
        try:
            from scapy.config import conf
            from scapy.layers.l2 import getmacbyip
            from ids.wifi_memory import get_or_set_legit_wifi, get_current_wifi_windows

            # Get the default gateway IP from the OS routing table
            route_info = conf.route.route("0.0.0.0")
            self.gateway_ip = route_info[2]

            if not self.gateway_ip or self.gateway_ip == "0.0.0.0":
                logger.warning("Could not determine default gateway IP.")
                return False

            # Try to get MAC from legit Wi-Fi memory
            legit_wifi = get_or_set_legit_wifi()
            current_wifi = get_current_wifi_windows()

            if legit_wifi:
                self.gateway_mac = legit_wifi["bssid"].upper()
                logger.info(f"Loaded legit Wi-Fi gateway MAC: {self.gateway_mac} (SSID: {legit_wifi['ssid']})")
                
                if current_wifi and current_wifi["ssid"] == legit_wifi["ssid"]:
                    if current_wifi["bssid"].upper() != self.gateway_mac:
                        logger.warning(f"⚠ IMMEDIATE EVIL TWIN DETECTED: Connected to {current_wifi['bssid']} instead of legit {self.gateway_mac}")
            else:
                # Fallback: Resolve gateway MAC via ARP
                self.gateway_mac = getmacbyip(self.gateway_ip)

            if not self.gateway_mac:
                logger.warning(f"Could not resolve MAC for gateway {self.gateway_ip}")
                return False

            # Normalize MAC to uppercase
            self.gateway_mac = self.gateway_mac.upper()

            # Perform vendor lookup
            self.gateway_vendor, self.gateway_vendor_category = lookup_oui(self.gateway_mac)

            # Set initial confidence based on vendor
            if is_network_equipment(self.gateway_mac):
                self.confidence = "VENDOR_VERIFIED"
                logger.info(
                    f"Gateway {self.gateway_ip} -> {self.gateway_mac} "
                    f"(Vendor: {self.gateway_vendor}) [VENDOR_VERIFIED]"
                )
            else:
                self.confidence = "FIRST_SEEN"
                vendor_warning = ""
                if is_consumer_device(self.gateway_mac):
                    vendor_warning = (
                        f" ⚠ WARNING: Gateway MAC vendor is '{self.gateway_vendor}' "
                        f"(consumer device) — unusual for a router!"
                    )
                elif is_iot_device(self.gateway_mac):
                    vendor_warning = (
                        f" ⚠ WARNING: Gateway MAC vendor is '{self.gateway_vendor}' "
                        f"(IoT device) — suspicious for a router!"
                    )
                logger.info(
                    f"Gateway {self.gateway_ip} -> {self.gateway_mac} "
                    f"[FIRST_SEEN]{vendor_warning}"
                )

            return True

        except Exception as e:
            logger.error(f"Gateway resolution failed: {e}")
            return False

    def resolve_async(self):
        """Resolve gateway in a background thread."""
        thread = threading.Thread(target=self.resolve, daemon=True)
        thread.start()
        return thread

    def verify_with_bssid(self, bssid):
        """
        Feed an ESP32-observed BSSID (from a Beacon frame) to the resolver.
        If the BSSID matches the gateway MAC, upgrade confidence to
        HARDWARE_VERIFIED.

        Args:
            bssid: The BSSID MAC address string from an ESP32 Beacon frame.

        Returns:
            bool: True if this BSSID upgraded the confidence level.
        """
        if not bssid:
            return False

        bssid_upper = bssid.upper()

        with self._lock:
            self._esp32_bssids.add(bssid_upper)

            # Check if this BSSID matches the gateway MAC
            if self.gateway_mac and bssid_upper == self.gateway_mac:
                if self.confidence != "HARDWARE_VERIFIED":
                    self.confidence = "HARDWARE_VERIFIED"
                    logger.info(
                        f"✅ Gateway {self.gateway_ip} ({self.gateway_mac}) "
                        f"HARDWARE_VERIFIED via ESP32 Beacon BSSID match!"
                    )
                    return True

        return False

    def get_confidence(self):
        """Get the current confidence level of the gateway MAC."""
        return self.confidence

    def is_hardware_verified(self):
        """Check if the gateway MAC has been verified by ESP32 hardware."""
        return self.confidence == "HARDWARE_VERIFIED"

    def get_esp32_bssids(self):
        """Get the set of all BSSIDs observed by the ESP32."""
        with self._lock:
            return self._esp32_bssids.copy()

    def check_bssid_mismatch(self):
        """
        Check if the gateway MAC is NOT in the set of ESP32-observed BSSIDs.
        This indicates a potential pre-existing MITM attack.

        Should only be called after the ESP32 has been running long enough
        to observe Beacons from the connected network (e.g., 10+ seconds).

        Returns:
            dict or None: Alert dict if mismatch detected, None otherwise.
        """
        with self._lock:
            if not self.gateway_mac or not self._esp32_bssids:
                return None

            if self.gateway_mac not in self._esp32_bssids:
                return {
                    "type": "ARP",
                    "subtype": "ARP Spoof",
                    "alert_type": "pre_existing_mitm",
                    "source_ip": self.gateway_ip,
                    "mac_src": self.gateway_mac,
                    "confidence": "HARDWARE_VERIFIED",
                    "spoofed": True,
                    "timestamp": time.time(),
                    "details": (
                        f"Gateway {self.gateway_ip} claims MAC {self.gateway_mac}, "
                        f"but ESP32 has NOT seen this MAC as a Wi-Fi BSSID. "
                        f"Possible pre-existing MITM attack!"
                    ),
                    "esp32_bssids": list(self._esp32_bssids)
                }

            return None

    def scan_subnet(self):
        """
        Perform an active ARP scan of the local subnet to detect
        duplicate MAC addresses (a strong indicator of ARP spoofing).

        This sends ARP requests to all IPs in the subnet and builds
        a reverse mapping of MAC -> [IPs].

        Returns:
            dict: MAC addresses mapped to multiple IPs (potential spoofers).
        """
        try:
            from scapy.all import ARP, Ether, srp, conf
            import ipaddress

            if not self.gateway_ip:
                logger.warning("Cannot scan subnet: gateway IP not resolved.")
                return {}

            # Determine the subnet (assume /24 for most home/office networks)
            network = ipaddress.IPv4Network(
                f"{self.gateway_ip}/24", strict=False
            )

            logger.info(f"Starting subnet scan on {network}...")

            # Build ARP request
            arp_request = ARP(pdst=str(network))
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast / arp_request

            # Send and receive (timeout 3 seconds, verbose off)
            answered, _ = srp(packet, timeout=3, verbose=False)

            # Build MAC -> IPs mapping
            mac_to_ips = {}
            for sent, received in answered:
                ip = received.psrc
                mac = received.hwsrc.upper()
                if mac not in mac_to_ips:
                    mac_to_ips[mac] = []
                mac_to_ips[mac].append(ip)

            # Filter to only MACs with multiple IPs (duplicates)
            self.duplicate_macs = {
                mac: ips for mac, ips in mac_to_ips.items()
                if len(ips) > 1
            }

            self.scan_complete = True

            if self.duplicate_macs:
                for mac, ips in self.duplicate_macs.items():
                    logger.warning(
                        f"⚠ Duplicate MAC detected: {mac} -> {ips} "
                        f"(possible ARP spoofing!)"
                    )
            else:
                logger.info("Subnet scan complete. No duplicate MACs found.")

            return self.duplicate_macs

        except Exception as e:
            logger.error(f"Subnet scan failed: {e}")
            self.scan_complete = True
            return {}

    def scan_subnet_async(self):
        """Perform subnet scan in a background thread."""
        thread = threading.Thread(target=self.scan_subnet, daemon=True)
        thread.start()
        return thread

    def get_gateway_info(self):
        """
        Get a summary dict of the current gateway state.
        Useful for displaying in the GUI.
        """
        return {
            "gateway_ip": self.gateway_ip,
            "gateway_mac": self.gateway_mac,
            "confidence": self.confidence,
            "vendor": self.gateway_vendor,
            "vendor_category": self.gateway_vendor_category,
            "esp32_bssid_count": len(self._esp32_bssids),
            "duplicate_macs": self.duplicate_macs,
            "scan_complete": self.scan_complete,
        }
