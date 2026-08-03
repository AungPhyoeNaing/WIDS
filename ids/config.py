import json
import os
import logging

_logger = logging.getLogger(__name__)

TIME_WINDOW = 30
MAX_DEAUTH_PER_WINDOW = 10
MAX_VICTIMS_PER_AP = 3
MAX_REPEAT_TO_VICTIM = 5
ATTACK_DURATION = 30
TIMING_TOLERANCE = 0.5
ALERT_SCORE = 5
WHITELIST_BSSID = set()
REASON_CODES = {
    1: "Unspecified",
    2: "Previous authentication no longer valid",
    3: "Deauthenticated because sending STA is leaving IBSS or ESS",
    4: "Disassociated due to inactivity",
    5: "Disassociated because sending STA is not authenticated",
    6: "Class 2 frame received from nonauthenticated STA",
    7: "Class 3 frame received from nonassociated STA",
    8: "Disassociated because sending STA is leaving BSS",
    9: "STA requesting authentication is not authenticated",
    10: "Information element mismatch",
    13: "Michael MIC failure",
    14: "4-Way Handshake timeout",
    15: "Group Key Handshake timeout",
    16: "Information element in 4-Way Handshake different from (Re)Association Request",
    17: "Invalid group cipher",
    18: "Invalid pairwise cipher",
    19: "Invalid AKMP",
    20: "Unsupported RSNE version",
    21: "Invalid RSNE capabilities",
    22: "Cipher suite rejected because of security policies",
    34: "TDLS direct teardown",
    36: "Requested from peer STA as STA does not want to use the mechanism",
    37: "Requested from peer STA as mechanism is not supported",
    38: "Requested from peer STA as receiving STA has not authenticated",
    39: "Requested from peer STA due to timeout",
    45: "Peer STA does not support the requested QoS",
}

def _load_whitelist():
    """Load trusted BSSIDs from whitelist.json into WHITELIST_BSSID."""
    whitelist_path = os.path.join(os.path.dirname(__file__), "whitelist.json")
    try:
        if os.path.exists(whitelist_path):
            with open(whitelist_path, "r") as f:
                data = json.load(f)
            for group_name, mac_list in data.items():
                for mac in mac_list:
                    WHITELIST_BSSID.add(mac.upper())
            if WHITELIST_BSSID:
                _logger.info(f"Loaded {len(WHITELIST_BSSID)} trusted BSSIDs from whitelist.json")
    except Exception as e:
        _logger.warning(f"Could not load whitelist.json: {e}")

_load_whitelist()
