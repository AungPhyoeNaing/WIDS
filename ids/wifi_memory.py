import subprocess
import json
import os
import logging
import re

logger = logging.getLogger(__name__)

LEGIT_WIFI_FILE = os.path.join(os.path.dirname(__file__), "legit_wifi.json")

def get_current_wifi_windows():
    """
    Run 'netsh wlan show interfaces' and parse out the current SSID and BSSID.
    Returns a dict {"ssid": <str>, "bssid": <str>} or None if not connected.
    """
    try:
        output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], stderr=subprocess.STDOUT, text=True)
        
        ssid = None
        bssid = None
        
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith("SSID") and not line.startswith("BSSID"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    ssid = parts[1].strip()
            elif line.startswith("BSSID"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    bssid = parts[1].strip().upper()
        
        if ssid and bssid:
            return {"ssid": ssid, "bssid": bssid}
        return None
    except Exception as e:
        logger.error(f"Failed to run netsh: {e}")
        return None

def load_legit_wifi():
    """
    Load the legit Wi-Fi from the config file.
    Returns dict {"ssid": <str>, "bssid": <str>} or None if file doesn't exist/invalid.
    """
    if os.path.exists(LEGIT_WIFI_FILE):
        try:
            with open(LEGIT_WIFI_FILE, "r") as f:
                data = json.load(f)
                if "ssid" in data and "bssid" in data:
                    return data
        except Exception as e:
            logger.error(f"Failed to read {LEGIT_WIFI_FILE}: {e}")
    return None

def save_legit_wifi(ssid, bssid):
    """
    Save the legit Wi-Fi to the config file.
    """
    data = {"ssid": ssid, "bssid": bssid}
    try:
        with open(LEGIT_WIFI_FILE, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved legit Wi-Fi: {ssid} ({bssid})")
    except Exception as e:
        logger.error(f"Failed to save {LEGIT_WIFI_FILE}: {e}")

def get_or_set_legit_wifi():
    """
    Main entry point. Loads the legit Wi-Fi. If it doesn't exist, or if the user
    has connected to a completely different SSID (legitimate network change),
    it updates the legit Wi-Fi.
    Returns dict or None.
    """
    legit = load_legit_wifi()
    current = get_current_wifi_windows()
    
    if legit:
        # If we are connected to a completely different network name, assume it's a legitimate network change
        if current and current["ssid"] != legit["ssid"]:
            logger.info(f"Network change detected. Updating legit Wi-Fi from {legit['ssid']} to {current['ssid']}")
            save_legit_wifi(current["ssid"], current["bssid"])
            return current
            
        # Otherwise (either same SSID or not connected), trust the saved legit wifi
        return legit
    
    if current:
        logger.info(f"No legit Wi-Fi found. Setting current connection as legit: {current['ssid']} ({current['bssid']})")
        save_legit_wifi(current["ssid"], current["bssid"])
        return current
    
    logger.warning("No legit Wi-Fi found and currently not connected to Wi-Fi.")
    return None
