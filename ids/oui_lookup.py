"""
OUI (Organizationally Unique Identifier) Lookup Module.

Provides an offline, hardcoded database of common MAC address vendor prefixes
to classify network devices as router/network equipment vs consumer devices.
Used by GatewayResolver for vendor heuristic checks.
"""

# OUI prefix (first 3 bytes, uppercase, colon-separated) -> (vendor_name, category)
# Categories: "network_equipment", "consumer_device", "iot_device", "unknown"
OUI_DATABASE = {
    # ── Network Equipment (Routers, APs, Switches) ──────────────────────
    # Cisco
    "00:1A:2B": ("Cisco Systems", "network_equipment"),
    "00:1B:0D": ("Cisco Systems", "network_equipment"),
    "00:1C:0E": ("Cisco Systems", "network_equipment"),
    "00:22:55": ("Cisco Systems", "network_equipment"),
    "00:23:04": ("Cisco Systems", "network_equipment"),
    "00:25:45": ("Cisco Systems", "network_equipment"),
    "00:26:0B": ("Cisco Systems", "network_equipment"),
    "00:50:56": ("Cisco Systems (VMware)", "network_equipment"),
    "58:97:1E": ("Cisco Systems", "network_equipment"),
    "AC:F2:C5": ("Cisco Systems", "network_equipment"),
    "F4:CF:E2": ("Cisco Systems", "network_equipment"),
    # TP-Link
    "14:CC:20": ("TP-Link", "network_equipment"),
    "14:CF:92": ("TP-Link", "network_equipment"),
    "18:A6:F7": ("TP-Link", "network_equipment"),
    "30:B5:C2": ("TP-Link", "network_equipment"),
    "50:C7:BF": ("TP-Link", "network_equipment"),
    "54:C8:0F": ("TP-Link", "network_equipment"),
    "60:32:B1": ("TP-Link", "network_equipment"),
    "78:8A:20": ("TP-Link", "network_equipment"),
    "98:DA:C4": ("TP-Link", "network_equipment"),
    "B0:BE:76": ("TP-Link", "network_equipment"),
    "C0:06:C3": ("TP-Link", "network_equipment"),
    "C0:25:E9": ("TP-Link", "network_equipment"),
    "D8:07:B6": ("TP-Link", "network_equipment"),
    "EC:08:6B": ("TP-Link", "network_equipment"),
    "F4:F2:6D": ("TP-Link", "network_equipment"),
    # Netgear
    "00:14:6C": ("Netgear", "network_equipment"),
    "00:1B:2F": ("Netgear", "network_equipment"),
    "00:1E:2A": ("Netgear", "network_equipment"),
    "20:0C:C8": ("Netgear", "network_equipment"),
    "28:C6:8E": ("Netgear", "network_equipment"),
    "2C:B0:5D": ("Netgear", "network_equipment"),
    "4C:60:DE": ("Netgear", "network_equipment"),
    "6C:B0:CE": ("Netgear", "network_equipment"),
    "84:1B:5E": ("Netgear", "network_equipment"),
    "A4:2B:8C": ("Netgear", "network_equipment"),
    "C4:04:15": ("Netgear", "network_equipment"),
    "E4:F4:C6": ("Netgear", "network_equipment"),
    # Ubiquiti
    "04:18:D6": ("Ubiquiti", "network_equipment"),
    "18:E8:29": ("Ubiquiti", "network_equipment"),
    "24:5A:4C": ("Ubiquiti", "network_equipment"),
    "44:D9:E7": ("Ubiquiti", "network_equipment"),
    "68:72:51": ("Ubiquiti", "network_equipment"),
    "74:83:C2": ("Ubiquiti", "network_equipment"),
    "78:8A:20": ("Ubiquiti", "network_equipment"),
    "80:2A:A8": ("Ubiquiti", "network_equipment"),
    "B4:FB:E4": ("Ubiquiti", "network_equipment"),
    "DC:9F:DB": ("Ubiquiti", "network_equipment"),
    "F0:9F:C2": ("Ubiquiti", "network_equipment"),
    "FC:EC:DA": ("Ubiquiti", "network_equipment"),
    # D-Link
    "00:05:5D": ("D-Link", "network_equipment"),
    "00:0D:88": ("D-Link", "network_equipment"),
    "00:17:9A": ("D-Link", "network_equipment"),
    "00:1C:F0": ("D-Link", "network_equipment"),
    "1C:7E:E5": ("D-Link", "network_equipment"),
    "28:10:7B": ("D-Link", "network_equipment"),
    "84:C9:B2": ("D-Link", "network_equipment"),
    "B8:A3:86": ("D-Link", "network_equipment"),
    "C8:BE:19": ("D-Link", "network_equipment"),
    "F0:7D:68": ("D-Link", "network_equipment"),
    # Aruba / HPE
    "00:0B:86": ("Aruba Networks", "network_equipment"),
    "00:1A:1E": ("Aruba Networks", "network_equipment"),
    "20:4C:03": ("Aruba Networks", "network_equipment"),
    "24:DE:C6": ("Aruba Networks", "network_equipment"),
    "6C:F3:7F": ("Aruba Networks", "network_equipment"),
    "9C:1C:12": ("Aruba Networks", "network_equipment"),
    "D8:C7:C8": ("Aruba Networks", "network_equipment"),
    # MikroTik
    "00:0C:42": ("MikroTik", "network_equipment"),
    "2C:C8:1B": ("MikroTik", "network_equipment"),
    "48:8F:5A": ("MikroTik", "network_equipment"),
    "4C:5E:0C": ("MikroTik", "network_equipment"),
    "6C:3B:6B": ("MikroTik", "network_equipment"),
    "B8:69:F4": ("MikroTik", "network_equipment"),
    "CC:2D:E0": ("MikroTik", "network_equipment"),
    "D4:CA:6D": ("MikroTik", "network_equipment"),
    "E4:8D:8C": ("MikroTik", "network_equipment"),
    # Linksys
    "00:06:25": ("Linksys", "network_equipment"),
    "00:12:17": ("Linksys", "network_equipment"),
    "00:14:BF": ("Linksys", "network_equipment"),
    "00:18:F8": ("Linksys", "network_equipment"),
    "00:1A:70": ("Linksys", "network_equipment"),
    "00:1E:E5": ("Linksys", "network_equipment"),
    "20:AA:4B": ("Linksys", "network_equipment"),
    "C0:56:27": ("Linksys", "network_equipment"),
    # ASUS
    "00:11:D8": ("ASUS", "network_equipment"),
    "08:60:6E": ("ASUS", "network_equipment"),
    "10:C3:7B": ("ASUS", "network_equipment"),
    "1C:87:2C": ("ASUS", "network_equipment"),
    "2C:FD:A1": ("ASUS", "network_equipment"),
    "30:85:A9": ("ASUS", "network_equipment"),
    "38:D5:47": ("ASUS", "network_equipment"),
    "40:B0:76": ("ASUS", "network_equipment"),
    "50:46:5D": ("ASUS", "network_equipment"),
    "74:D0:2B": ("ASUS", "network_equipment"),
    "AC:9E:17": ("ASUS", "network_equipment"),
    "F8:32:E4": ("ASUS", "network_equipment"),
    # Huawei (networking)
    "00:E0:FC": ("Huawei", "network_equipment"),
    "04:02:1F": ("Huawei", "network_equipment"),
    "20:F3:A3": ("Huawei", "network_equipment"),
    "48:46:FB": ("Huawei", "network_equipment"),
    "70:72:3C": ("Huawei", "network_equipment"),
    "88:66:A5": ("Huawei", "network_equipment"),
    "AC:85:3D": ("Huawei", "network_equipment"),
    "CC:A2:23": ("Huawei", "network_equipment"),
    # ZTE
    "00:19:CB": ("ZTE", "network_equipment"),
    "00:1E:73": ("ZTE", "network_equipment"),
    "34:4B:50": ("ZTE", "network_equipment"),
    "54:22:F8": ("ZTE", "network_equipment"),
    "68:77:24": ("ZTE", "network_equipment"),
    # Juniper
    "00:05:85": ("Juniper Networks", "network_equipment"),
    "00:12:1E": ("Juniper Networks", "network_equipment"),
    "00:19:E2": ("Juniper Networks", "network_equipment"),
    "00:23:9C": ("Juniper Networks", "network_equipment"),
    "28:8A:1C": ("Juniper Networks", "network_equipment"),
    "54:E0:32": ("Juniper Networks", "network_equipment"),
    "84:18:88": ("Juniper Networks", "network_equipment"),
    "AC:4B:C8": ("Juniper Networks", "network_equipment"),
    # Ruckus
    "00:1F:41": ("Ruckus Wireless", "network_equipment"),
    "24:C9:A1": ("Ruckus Wireless", "network_equipment"),
    "58:B6:33": ("Ruckus Wireless", "network_equipment"),
    "74:91:1A": ("Ruckus Wireless", "network_equipment"),
    "C4:10:8A": ("Ruckus Wireless", "network_equipment"),
    # Fortinet
    "00:09:0F": ("Fortinet", "network_equipment"),
    "08:5B:0E": ("Fortinet", "network_equipment"),
    "70:4C:A5": ("Fortinet", "network_equipment"),
    "90:6C:AC": ("Fortinet", "network_equipment"),
    "E8:1C:BA": ("Fortinet", "network_equipment"),

    # ── Consumer Devices (Laptops, Phones, etc.) ────────────────────────
    # Apple
    "00:03:93": ("Apple", "consumer_device"),
    "00:0A:95": ("Apple", "consumer_device"),
    "00:0D:93": ("Apple", "consumer_device"),
    "00:17:F2": ("Apple", "consumer_device"),
    "00:1C:B3": ("Apple", "consumer_device"),
    "00:21:E9": ("Apple", "consumer_device"),
    "00:25:BC": ("Apple", "consumer_device"),
    "14:99:E2": ("Apple", "consumer_device"),
    "28:6A:BA": ("Apple", "consumer_device"),
    "3C:15:C2": ("Apple", "consumer_device"),
    "48:74:6E": ("Apple", "consumer_device"),
    "58:55:CA": ("Apple", "consumer_device"),
    "60:FA:CD": ("Apple", "consumer_device"),
    "70:56:81": ("Apple", "consumer_device"),
    "7C:D1:C3": ("Apple", "consumer_device"),
    "84:FC:FE": ("Apple", "consumer_device"),
    "A8:60:B6": ("Apple", "consumer_device"),
    "AC:BC:32": ("Apple", "consumer_device"),
    "BC:52:B7": ("Apple", "consumer_device"),
    "C8:69:CD": ("Apple", "consumer_device"),
    "D0:03:4B": ("Apple", "consumer_device"),
    "DC:A9:04": ("Apple", "consumer_device"),
    "F0:B4:79": ("Apple", "consumer_device"),
    # Intel
    "00:02:B3": ("Intel", "consumer_device"),
    "00:13:02": ("Intel", "consumer_device"),
    "00:13:CE": ("Intel", "consumer_device"),
    "00:15:00": ("Intel", "consumer_device"),
    "00:1B:21": ("Intel", "consumer_device"),
    "00:1E:64": ("Intel", "consumer_device"),
    "00:1E:65": ("Intel", "consumer_device"),
    "3C:F0:11": ("Intel", "consumer_device"),
    "48:51:B7": ("Intel", "consumer_device"),
    "5C:80:B6": ("Intel", "consumer_device"),
    "68:17:29": ("Intel", "consumer_device"),
    "7C:5C:F8": ("Intel", "consumer_device"),
    "8C:8D:28": ("Intel", "consumer_device"),
    "A4:C4:94": ("Intel", "consumer_device"),
    "B4:96:91": ("Intel", "consumer_device"),
    "D0:21:F9": ("Intel", "consumer_device"),
    "DC:71:96": ("Intel", "consumer_device"),
    # Realtek
    "00:E0:4C": ("Realtek", "consumer_device"),
    "48:5D:60": ("Realtek", "consumer_device"),
    "52:54:00": ("Realtek (QEMU/KVM)", "consumer_device"),
    "7C:8B:CA": ("Realtek", "consumer_device"),
    "D8:EC:5E": ("Realtek", "consumer_device"),
    # Samsung
    "00:12:FB": ("Samsung", "consumer_device"),
    "00:15:99": ("Samsung", "consumer_device"),
    "00:1A:8A": ("Samsung", "consumer_device"),
    "08:37:3D": ("Samsung", "consumer_device"),
    "14:49:E0": ("Samsung", "consumer_device"),
    "28:98:7B": ("Samsung", "consumer_device"),
    "34:23:BA": ("Samsung", "consumer_device"),
    "44:78:3E": ("Samsung", "consumer_device"),
    "50:01:BB": ("Samsung", "consumer_device"),
    "5C:3A:45": ("Samsung", "consumer_device"),
    "78:D6:F0": ("Samsung", "consumer_device"),
    "84:25:19": ("Samsung", "consumer_device"),
    "94:63:D1": ("Samsung", "consumer_device"),
    "A8:F2:74": ("Samsung", "consumer_device"),
    "BC:44:86": ("Samsung", "consumer_device"),
    "C4:73:1E": ("Samsung", "consumer_device"),
    "D0:22:BE": ("Samsung", "consumer_device"),
    "EC:1F:72": ("Samsung", "consumer_device"),
    "F8:04:2E": ("Samsung", "consumer_device"),
    # Xiaomi
    "00:9E:C8": ("Xiaomi", "consumer_device"),
    "0C:1D:AF": ("Xiaomi", "consumer_device"),
    "18:59:36": ("Xiaomi", "consumer_device"),
    "28:6C:07": ("Xiaomi", "consumer_device"),
    "34:CE:00": ("Xiaomi", "consumer_device"),
    "50:64:2B": ("Xiaomi", "consumer_device"),
    "64:CC:2E": ("Xiaomi", "consumer_device"),
    "74:23:44": ("Xiaomi", "consumer_device"),
    "7C:1D:D9": ("Xiaomi", "consumer_device"),
    "8C:DE:F9": ("Xiaomi", "consumer_device"),
    "9C:99:A0": ("Xiaomi", "consumer_device"),
    "AC:C1:EE": ("Xiaomi", "consumer_device"),
    "B0:E2:35": ("Xiaomi", "consumer_device"),
    "F8:A4:5F": ("Xiaomi", "consumer_device"),
    # OPPO / OnePlus / Vivo
    "18:F0:E4": ("OPPO", "consumer_device"),
    "2C:5B:E1": ("OPPO", "consumer_device"),
    "88:D5:0C": ("OPPO", "consumer_device"),
    "94:65:2D": ("OnePlus", "consumer_device"),
    "C0:EE:FB": ("OnePlus", "consumer_device"),
    "98:6E:E8": ("Vivo", "consumer_device"),
    "C4:77:AB": ("Vivo", "consumer_device"),
    # Dell
    "00:06:5B": ("Dell", "consumer_device"),
    "00:08:74": ("Dell", "consumer_device"),
    "00:14:22": ("Dell", "consumer_device"),
    "14:B3:1F": ("Dell", "consumer_device"),
    "18:DB:F2": ("Dell", "consumer_device"),
    "34:17:EB": ("Dell", "consumer_device"),
    "5C:26:0A": ("Dell", "consumer_device"),
    "74:E6:E2": ("Dell", "consumer_device"),
    "B0:83:FE": ("Dell", "consumer_device"),
    "D4:BE:D9": ("Dell", "consumer_device"),
    "F8:BC:12": ("Dell", "consumer_device"),
    # HP
    "00:01:E6": ("HP", "consumer_device"),
    "00:0B:CD": ("HP", "consumer_device"),
    "00:14:38": ("HP", "consumer_device"),
    "00:17:A4": ("HP", "consumer_device"),
    "00:1C:C4": ("HP", "consumer_device"),
    "00:21:5A": ("HP", "consumer_device"),
    "10:60:4B": ("HP", "consumer_device"),
    "2C:41:38": ("HP", "consumer_device"),
    "3C:D9:2B": ("HP", "consumer_device"),
    "68:B5:99": ("HP", "consumer_device"),
    "80:CE:62": ("HP", "consumer_device"),
    "94:57:A5": ("HP", "consumer_device"),
    # Lenovo
    "00:06:1B": ("Lenovo", "consumer_device"),
    "28:D2:44": ("Lenovo", "consumer_device"),
    "50:7B:9D": ("Lenovo", "consumer_device"),
    "70:5A:0F": ("Lenovo", "consumer_device"),
    "98:FA:9B": ("Lenovo", "consumer_device"),
    "C8:5B:76": ("Lenovo", "consumer_device"),
    "E8:2A:44": ("Lenovo", "consumer_device"),
    # Broadcom
    "00:10:18": ("Broadcom", "consumer_device"),
    "00:1B:E9": ("Broadcom", "consumer_device"),
    "20:10:7A": ("Broadcom", "consumer_device"),
    # Qualcomm / Atheros
    "00:03:7F": ("Atheros", "consumer_device"),
    "00:0E:6D": ("Atheros", "consumer_device"),
    "04:F0:21": ("Qualcomm", "consumer_device"),

    # ── IoT / Embedded Devices ──────────────────────────────────────────
    # Raspberry Pi Foundation
    "28:CD:C1": ("Raspberry Pi", "iot_device"),
    "B8:27:EB": ("Raspberry Pi", "iot_device"),
    "D8:3A:DD": ("Raspberry Pi", "iot_device"),
    "DC:A6:32": ("Raspberry Pi", "iot_device"),
    "E4:5F:01": ("Raspberry Pi", "iot_device"),
    # Espressif (ESP32/ESP8266)
    "24:0A:C4": ("Espressif", "iot_device"),
    "24:6F:28": ("Espressif", "iot_device"),
    "30:AE:A4": ("Espressif", "iot_device"),
    "3C:61:05": ("Espressif", "iot_device"),
    "3C:71:BF": ("Espressif", "iot_device"),
    "84:CC:A8": ("Espressif", "iot_device"),
    "A4:CF:12": ("Espressif", "iot_device"),
    "AC:67:B2": ("Espressif", "iot_device"),
    "BC:DD:C2": ("Espressif", "iot_device"),
    "C4:4F:33": ("Espressif", "iot_device"),
    "CC:50:E3": ("Espressif", "iot_device"),
    "EC:FA:BC": ("Espressif", "iot_device"),
    # Amazon (Echo, Fire, etc.)
    "00:FC:8B": ("Amazon", "iot_device"),
    "10:CE:A9": ("Amazon", "iot_device"),
    "34:D2:70": ("Amazon", "iot_device"),
    "44:65:0D": ("Amazon", "iot_device"),
    "68:54:FD": ("Amazon", "iot_device"),
    "74:C2:46": ("Amazon", "iot_device"),
    "A0:02:DC": ("Amazon", "iot_device"),
    "FC:65:DE": ("Amazon", "iot_device"),
    # Google (Nest, Chromecast, etc.)
    "08:9E:08": ("Google", "iot_device"),
    "1C:F2:9A": ("Google", "iot_device"),
    "30:FD:38": ("Google", "iot_device"),
    "54:60:09": ("Google", "iot_device"),
    "6C:AD:F8": ("Google", "iot_device"),
    "A4:77:33": ("Google", "iot_device"),
    "F4:F5:D8": ("Google", "iot_device"),
    "F4:F5:E8": ("Google", "iot_device"),
}


def lookup_oui(mac_address):
    """
    Look up a MAC address in the OUI database.

    Args:
        mac_address: MAC address string in any common format
                     (e.g., "AA:BB:CC:DD:EE:FF", "AA-BB-CC-DD-EE-FF",
                      "AABB.CCDD.EEFF", "aabbccddeeff")

    Returns:
        tuple: (vendor_name, category) if found, or ("Unknown", "unknown") if not.
               Categories: "network_equipment", "consumer_device", "iot_device", "unknown"
    """
    if not mac_address:
        return ("Unknown", "unknown")

    # Normalize: remove separators and convert to uppercase
    mac_clean = mac_address.upper().replace(":", "").replace("-", "").replace(".", "")

    if len(mac_clean) < 6:
        return ("Unknown", "unknown")

    # Build the OUI prefix in colon-separated format: "AA:BB:CC"
    oui_prefix = f"{mac_clean[0:2]}:{mac_clean[2:4]}:{mac_clean[4:6]}"

    return OUI_DATABASE.get(oui_prefix, ("Unknown", "unknown"))


def is_network_equipment(mac_address):
    """Check if a MAC address belongs to a known network equipment vendor."""
    _, category = lookup_oui(mac_address)
    return category == "network_equipment"


def is_consumer_device(mac_address):
    """Check if a MAC address belongs to a known consumer device vendor."""
    _, category = lookup_oui(mac_address)
    return category == "consumer_device"


def is_iot_device(mac_address):
    """Check if a MAC address belongs to a known IoT device vendor."""
    _, category = lookup_oui(mac_address)
    return category == "iot_device"


def get_vendor_name(mac_address):
    """Get the vendor name for a MAC address."""
    vendor, _ = lookup_oui(mac_address)
    return vendor
