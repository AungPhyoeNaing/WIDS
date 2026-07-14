import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from datetime import datetime
import queue
import time
import collections
import json
import os
import math
from serial.tools import list_ports
from PIL import Image, ImageDraw
from gui.user_view import UserView
from gui.theme import ThemeManager


class App(ctk.CTk):
    def __init__(self, start_serial_cb, stop_serial_cb):
        super().__init__()
        
        self.title("WIDS - Dashboard")
        self.geometry("1100x700")
        
        # Premium dark mode theme
        ThemeManager.init()
        ThemeManager.on_change(self._apply_theme)
        
        self.start_serial_cb = start_serial_cb
        self.stop_serial_cb = stop_serial_cb
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Stats
        self.total_packets = 0
        self.deauth_count = 0
        self.alert_count = 0
        
        self.network_map = {} # BSSID -> SSID
        self.ssid_to_bssid = {} # SSID -> set(BSSID)
        self.bssid_channel = {} # BSSID -> channel
        self.bssid_rssi = {} # BSSID -> deque of last N RSSI readings
        self.bssid_first_seen = {} # BSSID -> timestamp of first sighting
        self.bssid_seen_count = {} # BSSID -> total packet count
        self.ssid_suspected_rogue = {} # SSID -> suspected rogue BSSID
        self.ssid_suspected_legit = {} # SSID -> suspected legitimate BSSID
        self.alerts_list = [] # Store triggered alerts
        self.last_eviltwin_alert_time = {} # BSSID -> timestamp
        self.eviltwin_alert_index = {} # (ssid, rogue_mac) -> index in alerts_list
        self.last_deauth_alert_time = 0.0
        
        # ARP tracking
        self.arp_alerts_sent = {} # (ip, mac) -> timestamp, rate-limit ARP alerts
        
        # Persistent whitelist: ssid -> set of trusted BSSIDs
        self.whitelist_path = os.path.join(os.path.dirname(__file__), "..", "ids", "whitelist.json")
        self.whitelist = self._load_whitelist()
        
        self.packet_queue = queue.Queue()
        self.update_interval = 500 # ms
        
        self.create_sidebar()
        self.create_main_content()

        self.current_view = "technician"
        self.user_view = UserView(self, self.show_technician_view, self)
        self.user_view.grid(row=0, column=1, sticky="nsew")
        self.user_view.grid_remove()
        
        self.after(self.update_interval, self.process_packet_queue)
        self.after(1000, self._try_auto_connect_serial)
        self.after(30000, self._check_unacknowledged_alerts)
        
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=ThemeManager.get("bg_sidebar"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        logo_path = os.path.join(os.path.dirname(__file__), "wids_logo.jpg")
        try:
            pil_img = Image.open(logo_path).convert("RGBA")
            mask = Image.new("L", pil_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + pil_img.size, fill=255)
            pil_img.putalpha(mask)
            
            logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(40, 40))
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=" WIDS", image=logo_img, compound="left", font=ctk.CTkFont(family="Consolas", size=26, weight="bold"))
        except Exception:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="WIDS", font=ctk.CTkFont(family="Consolas", size=26, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        self.com_port_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="COM Port (e.g. COM5)", height=45, font=ctk.CTkFont(size=14))
        self.com_port_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.baud_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Baud Rate", height=45, font=ctk.CTkFont(size=14))
        self.baud_entry.insert(0, "115200")
        self.baud_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.connect_btn = ctk.CTkButton(
            self.sidebar_frame, text="CONNECT", height=45, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            fg_color=ThemeManager.get("primary"), hover_color=ThemeManager.get("primary_hover"),
            command=self.toggle_connection
        )
        self.connect_btn.grid(row=3, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Connection status indicator
        self.status_frame = ctk.CTkFrame(self.sidebar_frame, fg_color=ThemeManager.get("bg_elevated"), corner_radius=8, height=45)
        self.status_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.status_frame.pack_propagate(False)
        self.status_label = ctk.CTkLabel(self.status_frame, text="● Disconnected", text_color=ThemeManager.get("danger"), font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(expand=True)
        
        self.is_connected = False
        
        self.view_alerts_btn = ctk.CTkButton(
            self.sidebar_frame, text="VIEW ALERTS", height=45, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            fg_color=ThemeManager.get("danger"), hover_color=ThemeManager.get("danger_hover"),
            command=self.show_alerts_window
        )
        self.view_alerts_btn.grid(row=5, column=0, padx=20, pady=(10, 10), sticky="ew")

        # Theme toggle button
        toggle_text = "☀️ Light Mode" if ThemeManager.is_dark() else "🌙 Dark Mode"
        self.theme_toggle_btn = ctk.CTkButton(
            self.sidebar_frame, text=toggle_text, height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent", text_color=ThemeManager.get("text_muted"),
            hover_color=ThemeManager.get("bg_elevated"),
            command=self.toggle_theme
        )
        self.theme_toggle_btn.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="s")

        self.switch_view_btn = ctk.CTkButton(
            self.sidebar_frame, text="\U0001F464  Switch to User View", height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ThemeManager.get("accent"), hover_color=ThemeManager.get("accent_hover"),
            command=self.toggle_view
        )
        self.switch_view_btn.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")

    def create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, fg_color=ThemeManager.get("bg_root"), corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Dashboard Stats Bar (Top)
        self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.stats_frame.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        self.stats_frame.grid_columnconfigure((0,1,2), weight=1)
        
        self.stat_packets = self.create_stat_card(self.stats_frame, "TOTAL PACKETS", "0", 0, ThemeManager.get("success"))
        self.stat_deauth = self.create_stat_card(self.stats_frame, "DEAUTH FRAMES", "0", 1, ThemeManager.get("warning"))
        self.stat_alerts = self.create_stat_card(self.stats_frame, "ALERTS TRIGGERED", "0", 2, ThemeManager.get("danger"))
        
        # Log frame (Bottom)
        self.log_frame = ctk.CTkFrame(self.main_frame, fg_color=ThemeManager.get("bg_card"), corner_radius=12)
        self.log_frame.grid(row=1, column=0, padx=30, pady=(10, 30), sticky="nsew")
        self.log_frame.grid_rowconfigure(1, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_header = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        self.log_header.grid(row=0, column=0, padx=25, pady=(20, 10), sticky="ew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self.log_header, text="Live Traffic Stream", font=ctk.CTkFont(size=18, weight="bold"), text_color=ThemeManager.get("text_heading"))
        self.title_label.pack(side="left")
        
        # Filters and Controls
        self.filter_frame = ctk.CTkFrame(self.log_header, fg_color="transparent")
        self.filter_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Search Network/MAC...", width=160)
        self.search_entry.pack(side="left", padx=10)
        
        self.show_beacons = tk.BooleanVar(value=True)
        self.cb_beacons = ctk.CTkCheckBox(self.filter_frame, text="Beacons", variable=self.show_beacons, width=60, fg_color=ThemeManager.get("tag_beacon"))
        self.cb_beacons.pack(side="left", padx=10)
        
        self.show_probes = tk.BooleanVar(value=True)
        self.cb_probes = ctk.CTkCheckBox(self.filter_frame, text="Probes", variable=self.show_probes, width=60, fg_color=ThemeManager.get("tag_probe"))
        self.cb_probes.pack(side="left", padx=10)

        self.show_deauths = tk.BooleanVar(value=True)
        self.cb_deauths = ctk.CTkCheckBox(self.filter_frame, text="Deauths", variable=self.show_deauths, width=60, fg_color=ThemeManager.get("danger"))
        self.cb_deauths.pack(side="left", padx=10)
        
        self.is_paused = False
        self.btn_pause = ctk.CTkButton(self.filter_frame, text="⏸ Pause", width=70, fg_color=ThemeManager.get("btn_pause_fg"), hover_color=ThemeManager.get("btn_pause_hover"), command=self.toggle_pause)
        self.btn_pause.pack(side="left", padx=(10, 5))
        
        self.btn_clear = ctk.CTkButton(self.filter_frame, text="🗑 Clear", width=70, fg_color=ThemeManager.get("btn_clear_fg"), hover_color=ThemeManager.get("btn_clear_hover"), command=self.clear_tree)
        self.btn_clear.pack(side="left", padx=(5, 0))
        
        # Themed Treeview
        self.style = ttk.Style()
        self.style.theme_use("default")
        self._apply_tree_style()


        self.tree = ttk.Treeview(self.log_frame, columns=("time", "rssi", "ch", "network", "src", "dst", "subtype"), show="headings")
        self.tree.heading("time", text="TIME")
        self.tree.heading("rssi", text="RSSI")
        self.tree.heading("ch", text="CH")
        self.tree.heading("network", text="NETWORK")
        self.tree.heading("src", text="SOURCE MAC")
        self.tree.heading("dst", text="DESTINATION MAC")
        self.tree.heading("subtype", text="FRAME SUBTYPE")
        
        self.tree.column("time", width=110, anchor="center")
        self.tree.column("rssi", width=70, anchor="center")
        self.tree.column("ch", width=50, anchor="center")
        self.tree.column("network", width=150, anchor="w")
        self.tree.column("src", width=150, anchor="center")
        self.tree.column("dst", width=150, anchor="center")
        self.tree.column("subtype", width=170, anchor="w")

        self.tree.grid(row=1, column=0, padx=(25,0), pady=(0, 25), sticky="nsew")
        
        self.scrollbar = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=1, padx=(0,25), pady=(0,25), sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Setup tags for color coding rows
        self._apply_tree_tags()
        
        self.max_rows = 500

    def _apply_tree_style(self):
        bg_color = ThemeManager.get("tree_bg")
        header_bg = ThemeManager.get("tree_header_bg")
        header_fg = ThemeManager.get("tree_header_fg")
        tree_fg = ThemeManager.get("tree_fg")
        selected_bg = ThemeManager.get("tree_selected")
        tree_border = ThemeManager.get("tree_border")
        
        self.style.configure("Treeview", 
                        background=bg_color,
                        foreground=tree_fg,
                        rowheight=35,
                        fieldbackground=bg_color,
                        bordercolor=tree_border,
                        borderwidth=0,
                        font=("Helvetica", 11))
                        
        self.style.map('Treeview', background=[('selected', selected_bg)])
        
        self.style.configure("Treeview.Heading", 
                        background=header_bg,
                        foreground=header_fg,
                        relief="flat",
                        font=("Helvetica", 11, "bold"))
                        
        self.style.map("Treeview.Heading", background=[('active', ThemeManager.get("bg_elevated"))])
        
    def _apply_tree_tags(self):
        self.tree.tag_configure("deauth", foreground=ThemeManager.get("tag_deauth"))
        self.tree.tag_configure("probe", foreground=ThemeManager.get("tag_probe"))
        self.tree.tag_configure("beacon", foreground=ThemeManager.get("tag_beacon"))
        self.tree.tag_configure("eviltwin_high",   foreground=ThemeManager.get("tag_eviltwin_high_fg"), background=ThemeManager.get("tag_eviltwin_high_bg"))
        self.tree.tag_configure("eviltwin_medium", foreground=ThemeManager.get("tag_eviltwin_medium_fg"), background=ThemeManager.get("tag_eviltwin_medium_bg"))
        self.tree.tag_configure("eviltwin_low",    foreground=ThemeManager.get("tag_eviltwin_low_fg"), background=ThemeManager.get("tag_eviltwin_low_bg"))
        self.tree.tag_configure("arp_spoof", foreground=ThemeManager.get("tag_arp_spoof_fg"), background=ThemeManager.get("tag_arp_spoof_bg"))

    def create_stat_card(self, parent, title, value, col, highlight_color):
        card = ctk.CTkFrame(parent, fg_color=ThemeManager.get("bg_card"), corner_radius=12, height=110)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        card.grid_propagate(False)
        card.grid_rowconfigure((0,1), weight=1)
        card.grid_columnconfigure(0, weight=1)
        
        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color=ThemeManager.get("text_muted"))
        title_lbl.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        
        val_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=36, weight="bold"), text_color=highlight_color)
        val_lbl.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        return val_lbl

    # ── OUI / vendor helpers ────────────────────────────────────────────────
    # Prefixes of MAC addresses commonly belonging to Wi-Fi routers / APs.
    # Source: IEEE OUI public registry (representative sample).
    ROUTER_OUIS = {
        # TP-Link
        "50:3e:aa","54:a7:03","60:32:b1","8c:21:0a","ac:84:c6","c4:e9:84",
        # ASUS
        "00:0c:6e","04:d4:c4","10:7b:44","2c:4d:54","50:46:5d","74:d0:2b",
        # Netgear
        "00:14:6c","20:e5:2a","2c:b0:5d","4c:60:de","9c:d3:6d","a0:21:b7",
        # Cisco / Linksys
        "00:1a:a1","00:23:eb","68:7f:74","c4:6e:1f","d0:57:7b","f8:72:ea",
        # D-Link
        "00:17:9a","1c:7e:e5","28:10:7b","34:08:04","90:94:e4","c8:be:19",
        # Huawei
        "00:18:82","04:bd:70","28:6e:d4","48:db:50","70:72:3c","a4:99:47",
        # MikroTik
        "00:0c:42","18:fd:74","48:8f:5a","64:d1:54","b8:69:f4","dc:2c:6e",
        # Ubiquiti
        "00:27:22","04:18:d6","24:a4:3c","44:d9:e7","68:72:51","dc:9f:db",
        # Xiaomi
        "28:6c:07","34:ce:00","58:44:98","64:09:80","78:11:dc","ac:c1:ee",
        # Tenda
        "c8:3a:35","d4:6e:0e","f4:ec:38",
    }
    # Prefixes associated with laptops / USB Wi-Fi dongles — common for rogue APs.
    LAPTOP_NIC_OUIS = {
        # Intel
        "00:21:5c","00:23:14","10:02:b5","34:02:86","40:4a:03","54:8b:f3",
        "8c:8d:28","a4:c3:f0","f4:06:69","00:1b:21",
        # Realtek
        "00:e0:4c","52:54:00","00:26:55",
        # Ralink / MediaTek (widely used in USB adapters)
        "00:0c:e7","00:90:4b","00:17:c5",
        # Alfa Network (popular pentest adapters)
        "00:c0:ca",
        # Atheros (used in many pentest builds)
        "00:03:7f","00:13:74",
    }

    def _classify_oui(self, mac: str) -> str:
        """Returns 'router', 'laptop', or 'unknown' based on OUI prefix."""
        prefix = mac.lower()[:8]  # first 3 octets e.g. 'aa:bb:cc'
        if prefix in self.ROUTER_OUIS:
            return "router"
        if prefix in self.LAPTOP_NIC_OUIS:
            return "laptop"
        return "unknown"

    def _score_evil_twin(self, ssid: str, bssid: str, channel, rssi) -> tuple:
        """
        Multi-signal confidence scorer. Returns (score 0-100, list of reason strings).

        Signals used:
          1. BSSID conflict        (+50) — required baseline
          2. Channel mismatch      (+20) — rogue often runs on different channel
          3. RSSI anomaly          (+20) — rogue usually has weaker or very different signal
          4. OUI / vendor class    (+10) — laptop/USB NIC OUI suggests a rogue device
        """
        reasons = []
        score = 0

        known_bssids = self.ssid_to_bssid.get(ssid, set()) - {bssid}
        if not known_bssids:
            return 0, []

        # ── Enterprise SSID Detection ────────────────────────────────────────
        is_enterprise = len(known_bssids) >= 3
        if is_enterprise:
            score -= 25
            reasons.append("Enterprise/Campus SSID (-25 score)")

        # ── Same-Vendor Detection ────────────────────────────────────────────
        my_vendor = bssid.lower()[:8]
        known_vendors = {b.lower()[:8] for b in known_bssids}
        is_same_vendor = my_vendor in known_vendors
        all_same_vendor = (len(known_vendors) == 1) and (my_vendor in known_vendors)

        if all_same_vendor and len(known_bssids) >= 1:
            score -= 10
            reasons.append("All APs share the same vendor prefix (-10 score)")

        # ── Signal 1: BSSID conflict (always present at this point) ──────────
        if is_same_vendor:
            score += 20
            reasons.append(f"SSID '{ssid}' broadcasted by multiple MACs (same vendor, reduced penalty)")
        else:
            score += 50
            reasons.append(f"SSID '{ssid}' broadcasted by multiple MACs")

        # ── Signal 2: Channel mismatch ───────────────────────────────────────
        other_channels = {self.bssid_channel[b] for b in known_bssids if b in self.bssid_channel}
        if channel and other_channels and int(channel) not in other_channels:
            score += 20
            reasons.append(f"Channel mismatch (this: {channel}, known: {sorted(other_channels)})")

        # ── Signal 3: RSSI anomaly ───────────────────────────────────────────
        if rssi is not None:
            try:
                rssi_val = int(rssi)
                other_rssi_avgs = []
                for b in known_bssids:
                    if b in self.bssid_rssi and self.bssid_rssi[b]:
                        other_rssi_avgs.append(sum(self.bssid_rssi[b]) / len(self.bssid_rssi[b]))
                if other_rssi_avgs:
                    avg_known = sum(other_rssi_avgs) / len(other_rssi_avgs)
                    diff = abs(rssi_val - avg_known)
                    if diff >= 15:  # 15 dBm difference is significant
                        score += 20
                        reasons.append(f"RSSI anomaly ({rssi_val} dBm vs known avg {avg_known:.0f} dBm, Δ{diff:.0f} dBm)")
            except (ValueError, TypeError):
                pass

        # ── Signal 4: OUI / vendor classification ────────────────────────────
        oui_class = self._classify_oui(bssid)
        known_oui_classes = [self._classify_oui(b) for b in known_bssids]
        if oui_class == "laptop" and "router" in known_oui_classes:
            score += 10
            reasons.append("MAC OUI belongs to a laptop/USB NIC (typical of rogue APs)")
        elif oui_class == "unknown" and "router" in known_oui_classes:
            score += 5
            reasons.append("MAC OUI is unrecognized (possibly randomized or custom firmware)")

        # ── Signal 5: Locally Administered Address ───────────────────────────
        if self._is_locally_administered(bssid):
            score += 30
            reasons.append("MAC is Locally Administered (highly indicative of a randomized MAC/mobile hotspot)")

        return min(score, 100), reasons

    # ── Rogue AP Identification ──────────────────────────────────────────────

    def _is_locally_administered(self, mac: str) -> bool:
        """Check if the MAC is locally administered (bit 1 of 1st octet set).
        Tools like hostapd, airbase-ng, and macchanger commonly produce these.
        Real hardware routers NEVER use locally administered MACs."""
        try:
            first_octet = int(mac.split(':')[0], 16)
            return bool(first_octet & 0x02)
        except (ValueError, IndexError):
            return False

    def _rogue_score_bssid(self, bssid: str, ssid: str) -> tuple:
        """
        Score a single BSSID for how likely it is to be the rogue AP.
        Returns (score, list_of_reasons). Higher score = more likely rogue.

        Signals:
          1. Locally Administered Address  (+40) — strongest indicator
          2. OUI is laptop / USB NIC       (+20)
          3. OUI is unknown (not a router) (+10)
          4. Appeared after SSID was known (+15) — late joiner
          5. Weaker RSSI than peers        (+15) — laptop antenna vs router
        """
        score = 0
        reasons = []
        other_bssids = self.ssid_to_bssid.get(ssid, set()) - {bssid}

        # ── Signal 1: Locally Administered Address ───────────────────────────
        if self._is_locally_administered(bssid):
            score += 40
            reasons.append("Locally administered MAC — strongly suggests MAC spoofing or a software AP (hostapd/airbase-ng)")

        # ── Signal 2 & 3: OUI vendor classification ──────────────────────────
        oui_class = self._classify_oui(bssid)
        other_oui_classes = [self._classify_oui(b) for b in other_bssids]
        if oui_class == "laptop":
            score += 20
            reasons.append("OUI matches a laptop/USB Wi-Fi adapter (not a router)")
        elif oui_class == "unknown" and "router" in other_oui_classes:
            score += 10
            reasons.append("OUI unrecognized — not a known router vendor")

        # ── Signal 4: Late joiner (appeared after SSID was already seen) ─────
        if bssid in self.bssid_first_seen and other_bssids:
            my_ts = self.bssid_first_seen[bssid]
            other_ts = [self.bssid_first_seen[b] for b in other_bssids if b in self.bssid_first_seen]
            if other_ts and my_ts > min(other_ts) + 5:  # 5+ seconds later
                score += 15
                reasons.append("Appeared after the other BSSID was already broadcasting")

        # ── Signal 5: Weaker RSSI ────────────────────────────────────────────
        if bssid in self.bssid_rssi and self.bssid_rssi[bssid]:
            my_rssi_list = list(self.bssid_rssi[bssid])
            my_avg_rssi = sum(my_rssi_list) / len(my_rssi_list)
            other_rssi_avgs = [
                sum(self.bssid_rssi[b]) / len(self.bssid_rssi[b])
                for b in other_bssids
                if b in self.bssid_rssi and self.bssid_rssi[b]
            ]
            if other_rssi_avgs:
                avg_other = sum(other_rssi_avgs) / len(other_rssi_avgs)
                if my_avg_rssi < avg_other - 10:  # 10 dBm weaker
                    score += 15
                    reasons.append(f"Weaker signal ({my_avg_rssi:.0f} dBm avg vs {avg_other:.0f} dBm — laptop antennas are typically weaker)")
            
            # ── Signal 6: High RSSI Variance (unstable/mobile transmitter) ──
            if len(my_rssi_list) >= 4:
                mean = my_avg_rssi
                variance = sum((x - mean) ** 2 for x in my_rssi_list) / len(my_rssi_list)
                if variance > 30:  # High variance = unstable signal source
                    score += 10
                    reasons.append(f"Unstable signal (variance {variance:.1f} dBm²) — fixed routers have stable RSSI")

        return score, reasons

    def _identify_rogue(self, ssid: str) -> tuple:
        """
        Among all known BSSIDs for an SSID, identify the most likely rogue.
        Returns (suspected_rogue_mac, suspected_legit_mac, rogue_reasons, is_likely_mesh).
        """
        all_bssids = list(self.ssid_to_bssid.get(ssid, set()))
        if len(all_bssids) < 2:
            return None, None, [], False

        scored = []
        for b in all_bssids:
            s, r = self._rogue_score_bssid(b, ssid)
            scored.append((s, b, r))

        scored.sort(reverse=True)  # highest rogue score first
        top_score = scored[0][0]
        bottom_score = scored[-1][0]
        suspected_rogue = scored[0][1]
        rogue_reasons = scored[0][2]
        suspected_legit = scored[-1][1]
        
        # Mesh/extender suppression: if both BSSIDs have router OUIs and
        # neither is locally administered, the score differential is low,
        # meaning there is no strong evidence of a rogue — likely a mesh/extender.
        both_router_oui = all(
            self._classify_oui(b) == "router" for b in all_bssids
        )
        neither_is_laa = all(
            not self._is_locally_administered(b) for b in all_bssids
        )
        all_same_vendor = len({b.lower()[:8] for b in all_bssids}) == 1
        is_enterprise = len(all_bssids) >= 4
        
        score_diff = top_score - bottom_score
        is_likely_mesh = neither_is_laa and (all_same_vendor or is_enterprise or (both_router_oui and score_diff < 20))

        return suspected_rogue, suspected_legit, rogue_reasons, is_likely_mesh

    # ── Whitelist persistence ────────────────────────────────────────────────

    def _load_whitelist(self) -> dict:
        """Load whitelist from JSON. Returns {ssid: [bssid, ...]}."""
        if os.path.exists(self.whitelist_path):
            try:
                with open(self.whitelist_path, "r") as f:
                    raw = json.load(f)
                    return {k: set(v) for k, v in raw.items()}
            except Exception:
                pass
        return {}

    def _save_whitelist(self):
        """Persist whitelist to JSON."""
        try:
            os.makedirs(os.path.dirname(self.whitelist_path), exist_ok=True)
            with open(self.whitelist_path, "w") as f:
                json.dump({k: list(v) for k, v in self.whitelist.items()}, f, indent=2)
        except Exception as e:
            print(f"[WIDS] Could not save whitelist: {e}")

    def _trust_ssid_bssids(self, ssid: str, bssids: list):
        """Add all given BSSIDs for an SSID to the whitelist."""
        if ssid not in self.whitelist:
            self.whitelist[ssid] = set()
        self.whitelist[ssid].update(bssids)
        self._save_whitelist()

    # ────────────────────────────────────────────────────────────────────────

    def _check_unacknowledged_alerts(self):
        unacknowledged = any(not a.get("acknowledged", False) for a in self.alerts_list)
        if unacknowledged:
            self._play_alert_sound("Unacknowledged")
        self.after(30000, self._check_unacknowledged_alerts)

    def _play_alert_sound(self, message="Alert Detected"):
        try:
            import ctypes, os
            
            # Map the message to the corresponding pre-recorded Jarvis mp3 file
            audio_file = None
            if "Evil Twin" in message:
                audio_file = r"voice_audios\Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-32-Warning-!!-Evil-twin-wifi-detected!!.mp3"
            elif "ARP Spoofing" in message:
                audio_file = r"voice_audios\Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-34-Warning-!!-MAC-Spoofing-detected-,-Sir!!!.mp3"
            elif "Deauth" in message:
                audio_file = r"voice_audios\Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-35-Warning-!!-Deauth-Attack-Frames-has-been-found-,.mp3"
            elif "Greeting" in message:
                audio_file = r"voice_audios\Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-40-Hello-,-Sir-,-Our-Intrusion-Detection-System-is.mp3"
            elif "Unacknowledged" in message:
                audio_file = r"voice_audios\Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-56-Sir-!!-please-check-the-alerts-history-carefully.mp3"
            
            if audio_file and os.path.exists(audio_file):
                path = os.path.abspath(audio_file)
                alias = "jarvis_voice"
                
                # Stop and close the alias to cancel any currently playing sound
                ctypes.windll.winmm.mciSendStringW(f'stop {alias}', None, 0, None)
                ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                
                # Open the new sound and play asynchronously (without 'wait')
                ctypes.windll.winmm.mciSendStringW(f'open "{path}" alias {alias}', None, 0, None)
                ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, None)
        except Exception:
            pass

    def _add_alert(self, alert):
        self.alert_count += 1
        alert_type_msg = alert.get("type", "Alert").split("[")[0].strip()
        self._play_alert_sound(f"{alert_type_msg} Detected")
        alert.setdefault("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        alert.setdefault("last_seen", alert["time"])
        self.alerts_list.append(alert)
        if len(self.alerts_list) > 2000:
            self.alerts_list.pop(0)
        return alert

    def _handle_deauth_packet(self, packet):
        self.deauth_count += 1
        target_mac = packet.get("mac_dst", "Unknown")
        now = time.time()

        if self.deauth_count == 1 and (now - self.last_deauth_alert_time) >= 15:
            self.last_deauth_alert_time = now
            self._add_alert({
                "type": "Deauth Activity",
                "severity": "Medium",
                "target_mac": target_mac,
                "deauth_count": 1,
                "details": f"Observed a deauthentication frame targeting {target_mac}."
            })
        elif self.deauth_count % 10 == 0:
            self.last_deauth_alert_time = now
            self._add_alert({
                "type": "Deauth Flood",
                "severity": "High",
                "target_mac": target_mac,
                "deauth_count": self.deauth_count,
                "details": f"Detected {self.deauth_count} deauthentication frames targeting {target_mac} in the current session."
            })

    def _find_serial_ports(self):
        try:
            return [port.device for port in list_ports.comports()]
        except Exception:
            return []

    def _try_auto_connect_serial(self):
        if self.is_connected:
            return

        baud_text = self.baud_entry.get().strip() or "115200"
        try:
            baud = int(baud_text)
        except ValueError:
            baud = 115200

        requested_port = self.com_port_entry.get().strip()
        ports = [requested_port] if requested_port else self._find_serial_ports()
        if not ports:
            return

        for port in ports:
            self.status_label.configure(text=f"● Trying {port}...", text_color="#f59e0b")
            success = self.start_serial_cb(port, baud)
            if success:
                self.com_port_entry.delete(0, tk.END)
                self.com_port_entry.insert(0, port)
                self.is_connected = True
                self.connect_btn.configure(text="DISCONNECT", fg_color="#ef4444", hover_color="#dc2626")
                self.status_label.configure(text=f"● Connected to {port}", text_color="#10b981")
                self._play_alert_sound("Greeting")
                return

        self.status_label.configure(text="● Auto-connect failed", text_color="#ef4444")
        self.after(5000, self._try_auto_connect_serial)

    def toggle_connection(self):
        if not self.is_connected:
            port = self.com_port_entry.get().strip()
            baud_text = self.baud_entry.get().strip() or "115200"
            if port:
                try:
                    baud = int(baud_text)
                except ValueError:
                    baud = 115200
                success = self.start_serial_cb(port, baud)
                if success:
                    self.is_connected = True
                    self.connect_btn.configure(text="DISCONNECT", fg_color="#ef4444", hover_color="#dc2626")
                    self.status_label.configure(text=f"● Connected to {port}", text_color="#10b981")
                    self._play_alert_sound("Greeting")
                else:
                    self.status_label.configure(text="● Connection Failed", text_color="#ef4444")
            else:
                self.status_label.configure(text="● Enter a COM port", text_color="#ef4444")
        else:
            self.stop_serial_cb()
            self.is_connected = False
            self.connect_btn.configure(text="CONNECT", fg_color=ThemeManager.get("primary"), hover_color=ThemeManager.get("primary_hover"))
            self.status_label.configure(text="● Disconnected", text_color=ThemeManager.get("danger"))

    def toggle_theme(self):
        ThemeManager.toggle()

    def _apply_theme(self):
        # Sidebar
        self.sidebar_frame.configure(fg_color=ThemeManager.get("bg_sidebar"))
        self.connect_btn.configure(fg_color=ThemeManager.get("danger") if self.is_connected else ThemeManager.get("primary"),
                                   hover_color=ThemeManager.get("danger_hover") if self.is_connected else ThemeManager.get("primary_hover"))
        self.status_frame.configure(fg_color=ThemeManager.get("bg_elevated"))
        self.view_alerts_btn.configure(fg_color=ThemeManager.get("danger"), hover_color=ThemeManager.get("danger_hover"))
        
        toggle_text = "☀️ Light Mode" if ThemeManager.is_dark() else "🌙 Dark Mode"
        self.theme_toggle_btn.configure(text=toggle_text, text_color=ThemeManager.get("text_muted"), hover_color=ThemeManager.get("bg_elevated"))
        self.switch_view_btn.configure(fg_color=ThemeManager.get("accent"), hover_color=ThemeManager.get("accent_hover"))

        # Main Content
        self.main_frame.configure(fg_color=ThemeManager.get("bg_root"))
        self.log_frame.configure(fg_color=ThemeManager.get("bg_card"))
        self.title_label.configure(text_color=ThemeManager.get("text_heading"))
        
        self.cb_beacons.configure(fg_color=ThemeManager.get("tag_beacon"))
        self.cb_probes.configure(fg_color=ThemeManager.get("tag_probe"))
        self.cb_deauths.configure(fg_color=ThemeManager.get("danger"))
        self.btn_pause.configure(fg_color=ThemeManager.get("btn_pause_fg"), hover_color=ThemeManager.get("btn_pause_hover"))
        self.btn_clear.configure(fg_color=ThemeManager.get("btn_clear_fg"), hover_color=ThemeManager.get("btn_clear_hover"))
        
        # Stat cards
        for card in self.stats_frame.winfo_children():
            if isinstance(card, ctk.CTkFrame):
                card.configure(fg_color=ThemeManager.get("bg_card"))
                for child in card.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        # The title label is the one that's not the value (which has the highlight color)
                        # So we only update text_muted labels
                        if child.cget("text") in ["TOTAL PACKETS", "DEAUTH FRAMES", "ALERTS TRIGGERED"]:
                            child.configure(text_color=ThemeManager.get("text_muted"))
        
        # Stat card values (highlight colors)
        self.stat_packets.configure(text_color=ThemeManager.get("success"))
        self.stat_deauth.configure(text_color=ThemeManager.get("warning"))
        self.stat_alerts.configure(text_color=ThemeManager.get("danger"))

        # Treeview
        self._apply_tree_style()
        self._apply_tree_tags()


    def toggle_view(self):
        if self.current_view == "technician":
            self.current_view = "user"
            self.main_frame.grid_remove()
            self.view_alerts_btn.grid_remove()
            self.user_view.grid(row=0, column=1, sticky="nsew")
            self.switch_view_btn.configure(text="\U0001F6E1  Switch to Technician View")
        else:
            self.show_technician_view()

    def show_technician_view(self):
        self.current_view = "technician"
        self.user_view.grid_remove()
        self.view_alerts_btn.grid(row=5, column=0, padx=20, pady=(10, 10), sticky="ew")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.switch_view_btn.configure(text="\U0001F464  Switch to User View")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.configure(text="▶ Resume", fg_color="#10b981", hover_color="#059669")
        else:
            self.btn_pause.configure(text="⏸ Pause", fg_color="#3f3f46", hover_color="#27272a")

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def add_packet(self, packet):
        self.packet_queue.put(packet)
        self.user_view.add_packet(packet)

    def process_packet_queue(self):
        packets_to_insert = []
        try:
            # Process up to 100 packets per batch to keep the stream readable
            for _ in range(100):
                packet = self.packet_queue.get_nowait()
                
                self.total_packets += 1
                subtype = packet.get('subtype', '')
                
                if subtype == "Deauthentication":
                    self._handle_deauth_packet(packet)
                        
                bssid = packet.get('bssid', '')
                ssid = packet.get('ssid', '')
                mac_src = packet.get('mac_src', '')
                mac_dst = packet.get('mac_dst', '')
                channel = packet.get('channel', None)
                rssi = packet.get('rssi', None)
                
                is_evil_twin = False
                
                # Update map if SSID is present
                if ssid and bssid:
                    self.network_map[bssid] = ssid
                    
                    # Track first seen timestamp
                    if bssid not in self.bssid_first_seen:
                        self.bssid_first_seen[bssid] = time.time()
                    
                    # Track channel and RSSI history per BSSID
                    if channel:
                        self.bssid_channel[bssid] = int(channel)
                    if rssi is not None:
                        try:
                            if bssid not in self.bssid_rssi:
                                self.bssid_rssi[bssid] = collections.deque(maxlen=20)
                            self.bssid_rssi[bssid].append(int(rssi))
                        except (ValueError, TypeError):
                            pass
                    
                    # Evil Twin Detection — multi-signal confidence scoring
                    if ssid not in self.ssid_to_bssid:
                        self.ssid_to_bssid[ssid] = set()
                    self.ssid_to_bssid[ssid].add(bssid)
                    
                    self.bssid_seen_count[bssid] = self.bssid_seen_count.get(bssid, 0) + 1
                    
                    # ── Gate 1: Skip if this BSSID is whitelisted ───────────────
                    trusted = self.whitelist.get(ssid, set())
                    if bssid in trusted:
                        pass  # Trusted — skip Evil Twin analysis
                    
                    # ── Gate 2: Minimum sightings before flagging ───
                    elif len(self.ssid_to_bssid[ssid]) > 1 and \
                         self.bssid_seen_count.get(bssid, 0) >= (10 if len(self.ssid_to_bssid[ssid]) >= 4 else 3):
                        
                        score, reasons = self._score_evil_twin(ssid, bssid, channel, rssi)
                        
                        if score > 0:
                            # Identify which BSSID is the rogue
                            rogue_mac, legit_mac, rogue_reasons, is_likely_mesh = self._identify_rogue(ssid)
                            
                            # ── Gate 3: Mesh/extender suppression ───────────────
                            if is_likely_mesh:
                                confidence_label = "LOW"
                                severity = "Low"
                                tag = "eviltwin_low"
                                score = max(score, 30)  # cap score for mesh
                            elif score >= 70:
                                confidence_label = "HIGH"
                                severity = "Critical"
                                tag = "eviltwin_high"
                            elif score >= 40:
                                confidence_label = "MEDIUM"
                                severity = "High"
                                tag = "eviltwin_medium"
                            else:
                                confidence_label = "LOW"
                                severity = "Low"
                                tag = "eviltwin_low"
                            
                            self.ssid_suspected_rogue[ssid] = rogue_mac
                            self.ssid_suspected_legit[ssid] = legit_mac
                            
                            packet['is_evil_twin'] = True
                            packet['et_confidence'] = confidence_label
                            packet['et_tag'] = tag
                            packet['et_rogue_mac'] = rogue_mac
                            packet['et_legit_mac'] = legit_mac
                            packet['et_is_mesh'] = is_likely_mesh
                            
                            current_time = time.time()
                            last_alert = self.last_eviltwin_alert_time.get(bssid, 0)
                            if is_likely_mesh:
                                pass # Suppress LOW-confidence mesh from creating alert cards
                            elif current_time - last_alert >= 10:
                                reason_str = " | ".join(reasons)
                                rogue_reason_str = "; ".join(rogue_reasons) if rogue_reasons else "No strong indicators — treat as suspicious"
                                alert_key = (ssid, rogue_mac)
                                
                                if alert_key in self.eviltwin_alert_index:
                                    # Update existing alert count instead of adding a new card
                                    idx = self.eviltwin_alert_index[alert_key]
                                    if idx < len(self.alerts_list):
                                        self.alerts_list[idx]["seen_count"] = \
                                            self.alerts_list[idx].get("seen_count", 1) + 1
                                        self.alerts_list[idx]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        self.alerts_list[idx]["score"] = score
                                        self.alerts_list[idx]["type"] = f"Evil Twin [{confidence_label} {score}%]"
                                        self.alerts_list[idx]["severity"] = severity
                                else:
                                    self.alert_count += 1
                                    self._play_alert_sound("Evil Twin Wifi Detected")
                                    new_alert = {
                                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "type": f"Evil Twin [{confidence_label} {score}%]",
                                        "severity": severity,
                                        "ssid": ssid,
                                        "rogue_mac": rogue_mac,
                                        "legit_mac": legit_mac,
                                        "details": reason_str,
                                        "rogue_why": rogue_reason_str,
                                        "is_mesh": is_likely_mesh,
                                        "seen_count": 1,
                                        "score": score,
                                        "all_bssids": list(self.ssid_to_bssid.get(ssid, set()))
                                    }
                                    self.alerts_list.append(new_alert)
                                    self.eviltwin_alert_index[alert_key] = len(self.alerts_list) - 1
                                    if len(self.alerts_list) > 2000:
                                        self.alerts_list.pop(0)
                                
                                self.last_eviltwin_alert_time[bssid] = current_time
                    
                # ─── ARP SPOOF DETECTION ───────────────────────────────────────
                packet_type = packet.get('type', '')
                if packet_type == "ARP" and packet.get('spoofed'):
                    ip = packet['source_ip']
                    new_mac = packet['mac_src']
                    old_mac = packet.get('old_mac', '?')
                    alert_key = (ip, new_mac)
                    
                    # Rate-limit: 1 alert per (ip, mac) per 10 seconds
                    now = time.time()
                    last_arp = self.arp_alerts_sent.get(alert_key, 0)
                    if now - last_arp >= 10:
                        self.alert_count += 1
                        self._play_alert_sound("ARP Spoofing Detected")
                        details = f"IP {ip} changed from {old_mac} to {new_mac}"
                        self.alerts_list.append({
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "type": "ARP Spoofing",
                            "severity": "Critical",
                            "details": details,
                            "source_ip": ip,
                            "rogue_mac": new_mac,
                            "legit_mac": old_mac,
                            "seen_count": 1
                        })
                        self.arp_alerts_sent[alert_key] = now
                        if len(self.alerts_list) > 2000:
                            self.alerts_list.pop(0)
                
                # Determine network name and rogue/legit label
                network_name = ""
                if bssid in self.network_map:
                    network_name = self.network_map[bssid]
                elif mac_src in self.network_map:
                    network_name = self.network_map[mac_src]
                elif mac_dst in self.network_map:
                    network_name = self.network_map[mac_dst]
                
                if packet.get('is_evil_twin'):
                    rogue_mac = packet.get('et_rogue_mac')
                    legit_mac = packet.get('et_legit_mac')
                    conf = packet.get('et_confidence', '?')
                    if bssid == rogue_mac:
                        network_name = f"🔴 ROGUE AP ({conf}) — {network_name}"
                    elif bssid == legit_mac:
                        network_name = f"✅ LEGITIMATE — {network_name}"
                    else:
                        network_name = f"[⚠ {conf}] {network_name}"
                
                if packet_type == "ARP":
                    network_name = f"📡 ARP: {packet.get('source_ip', '')}"
                    if packet.get('spoofed'):
                        network_name += " ⚠ SPOOF"
                elif bssid:
                    network_name = f"{network_name} [{bssid}]" if network_name else f"[{bssid}]"
                
                packet['network_name'] = network_name
                        
                if not self.is_paused:
                    if subtype == "Beacon" and not self.show_beacons.get():
                        continue
                    if subtype == "Probe Request" and not self.show_probes.get():
                        continue
                    if subtype == "Deauthentication" and not self.show_deauths.get():
                        continue
                        
                    # Filter by search term
                    search_term = self.search_entry.get().strip().lower()
                    if search_term:
                        match = False
                        if search_term in network_name.lower(): match = True
                        elif search_term in mac_src.lower(): match = True
                        elif search_term in mac_dst.lower(): match = True
                        elif search_term in bssid.lower(): match = True
                        if not match:
                            continue
                    
                    packets_to_insert.append(packet)
        except queue.Empty:
            pass
            
        if packets_to_insert:
            self.stat_packets.configure(text=str(self.total_packets))
            self.stat_deauth.configure(text=str(self.deauth_count))
            self.stat_alerts.configure(text=str(self.alert_count))
            
            for packet in packets_to_insert:
                subtype = packet.get('subtype', '')
                packet_type = packet.get('type', '')
                tags = ()
                if packet.get('is_evil_twin'):
                    tags = (packet.get('et_tag', 'eviltwin_medium'),)
                elif packet_type == "ARP" and packet.get('spoofed'):
                    tags = ("arp_spoof",)
                elif subtype == "Deauthentication":
                    tags = ("deauth",)
                elif subtype == "Probe Request":
                    tags = ("probe",)
                elif subtype == "Beacon":
                    tags = ("beacon",)
                    
                current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                
                if packet_type == "ARP":
                    values = (
                        current_time,
                        "",
                        "",
                        packet.get('network_name', ''),
                        packet.get('mac_src', ''),
                        packet.get('mac_dst', ''),
                        subtype
                    )
                else:
                    values = (
                        current_time,
                        f"{packet.get('rssi', '')} dBm",
                        packet.get('channel', ''),
                        packet.get('network_name', ''),
                        packet.get('mac_src', ''),
                        packet.get('mac_dst', ''),
                        subtype
                    )
                self.tree.insert("", "0", values=values, tags=tags)
                
            children = self.tree.get_children()
            if len(children) > self.max_rows:
                # Delete excess rows efficiently
                for child in children[self.max_rows:]:
                    self.tree.delete(child)
                    
        self.after(self.update_interval, self.process_packet_queue)

    def show_alerts_window(self):
        alerts_win = ctk.CTkToplevel(self)
        alerts_win.title("Sentinel WIDS — Alerts")
        alerts_win.geometry("960x600")
        alerts_win.configure(fg_color=ThemeManager.get("bg_root"))
        alerts_win.transient(self)
        
        # ── Header bar ──────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(alerts_win, fg_color=ThemeManager.get("bg_sidebar"), corner_radius=0, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        
        ctk.CTkLabel(hdr, text="🚨  ALERTS HISTORY", font=ctk.CTkFont(size=20, weight="bold"), text_color=ThemeManager.get("text_heading")).pack(side="left", padx=24, pady=14)
        
        total_lbl = ctk.CTkLabel(hdr, text=f"{len(self.alerts_list)} alert(s)  ·  {sum(1 for a in self.alerts_list if a.get('severity') == 'Critical')} critical",
                                  font=ctk.CTkFont(size=13), text_color=ThemeManager.get("text_dim"))
        total_lbl.pack(side="right", padx=24)
        
        # ── Scrollable cards ────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(alerts_win, fg_color=ThemeManager.get("bg_root"), corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        
        if not self.alerts_list:
            ctk.CTkLabel(scroll, text="✅  No alerts have been triggered yet.",
                         font=ctk.CTkFont(size=15), text_color=ThemeManager.get("text_dim")).pack(pady=60)
            return
        
        # Sort: Critical first, then High, then others; newest first within same severity
        order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        sorted_alerts = sorted(self.alerts_list,
                               key=lambda a: (order.get(a["severity"], 9), a["time"]),
                               reverse=False)
        sorted_alerts.reverse()  # newest first within each severity bucket
        
        for alert in sorted_alerts:
            sev = alert.get("severity", "Low")
            is_et = bool(alert.get("rogue_mac"))
            is_mesh = alert.get("is_mesh", False)
            seen_count = alert.get("seen_count", 1)
            
            stripe_color = {"Critical": ThemeManager.get("alert_stripe_critical"), "High": ThemeManager.get("alert_stripe_high"),
                            "Medium": ThemeManager.get("alert_stripe_medium"), "Low": ThemeManager.get("alert_stripe_low")}.get(sev, ThemeManager.get("alert_stripe_low"))
            text_color   = stripe_color
            
            # Outer wrapper gives left-border stripe effect
            wrapper = ctk.CTkFrame(scroll, fg_color=stripe_color, corner_radius=8)
            wrapper.pack(fill="x", padx=18, pady=5)
            
            inner = ctk.CTkFrame(wrapper, fg_color=ThemeManager.get("alert_inner"), corner_radius=6)
            inner.pack(fill="both", padx=(4, 0), pady=0)
            
            # ── Row 1: Type badge · seen count · time ────────────────────────
            r1 = ctk.CTkFrame(inner, fg_color="transparent")
            r1.pack(fill="x", padx=14, pady=(12, 2))
            
            ctk.CTkLabel(r1, text=alert["type"].upper(), font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=text_color).pack(side="left")
            
            if seen_count > 1:
                badge = ctk.CTkLabel(r1, text=f"  ×{seen_count} detected",
                                     font=ctk.CTkFont(size=12), text_color=ThemeManager.get("text_muted"))
                badge.pack(side="left", padx=8)
            
            ctk.CTkLabel(r1, text=f"First: {alert['time']}  ·  Last: {alert.get('last_seen', alert['time'])}",
                         font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_dim")).pack(side="right")
            
            # ── Evil-Twin specific body ───────────────────────────────────────
            if is_et:
                if is_mesh:
                    ctk.CTkLabel(inner,
                                 text="ℹ️  Both APs share router-vendor MACs — this may be a mesh network or Wi-Fi extender. Verify manually.",
                                 font=ctk.CTkFont(size=12), text_color=ThemeManager.get("primary"),
                                 justify="left", wraplength=840).pack(fill="x", padx=14, pady=(2, 4), anchor="w")
                
                ssid_val = alert.get('ssid', 'Unknown')
                ctk.CTkLabel(inner, text=f"🌐  SSID:  {ssid_val}",
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=ThemeManager.get("text_body")).pack(fill="x", padx=14, pady=(4, 0), anchor="w")
                
                all_bssids = alert.get("all_bssids", [])
                if all_bssids:
                    bssids_str = ", ".join(all_bssids)
                    ctk.CTkLabel(inner, text=f"📍 All Known BSSIDs for SSID: {bssids_str}",
                                 font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_muted"),
                                 justify="left", wraplength=840).pack(fill="x", padx=14, pady=(0, 4), anchor="w")
                
                mac_f = ctk.CTkFrame(inner, fg_color="transparent")
                mac_f.pack(fill="x", padx=14, pady=(6, 2))
                ctk.CTkLabel(mac_f, text=f"🔴  Suspected Rogue AP:",
                             font=ctk.CTkFont(size=12, weight="bold"), text_color=ThemeManager.get("danger")).pack(side="left")
                ctk.CTkLabel(mac_f, text=f"  {alert.get('rogue_mac', '?')}",
                             font=ctk.CTkFont(size=12, family="Courier"), text_color=ThemeManager.get("danger")).pack(side="left")
                
                mac_f2 = ctk.CTkFrame(inner, fg_color="transparent")
                mac_f2.pack(fill="x", padx=14, pady=(0, 2))
                ctk.CTkLabel(mac_f2, text=f"✅  Likely Legitimate AP:",
                             font=ctk.CTkFont(size=12, weight="bold"), text_color=ThemeManager.get("success")).pack(side="left")
                ctk.CTkLabel(mac_f2, text=f"  {alert.get('legit_mac', '?')}",
                             font=ctk.CTkFont(size=12, family="Courier"), text_color=ThemeManager.get("success")).pack(side="left")
                
                if alert.get("rogue_why"):
                    ctk.CTkLabel(inner, text=f"🔍  Why rogue: {alert['rogue_why']}",
                                 font=ctk.CTkFont(size=12), text_color=ThemeManager.get("warning"),
                                 justify="left", wraplength=840).pack(fill="x", padx=14, pady=(4, 0), anchor="w")
                
                if alert.get("details"):
                    ctk.CTkLabel(inner, text=f"📡  Signals: {alert['details']}",
                                 font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_dim"),
                                 justify="left", wraplength=840).pack(fill="x", padx=14, pady=(2, 4), anchor="w")
                
                # ── Action steps ─────────────────────────────────────────────
                action_f = ctk.CTkFrame(inner, fg_color=ThemeManager.get("bg_elevated"), corner_radius=6)
                action_f.pack(fill="x", padx=14, pady=(4, 4))
                ctk.CTkLabel(action_f, text="💡 Recommended Actions:  1) Do NOT connect to this SSID until verified.  2) Check your router's MAC in its admin page.  3) Report to your IT admin if persistent.",
                             font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_muted"),
                             justify="left", wraplength=840).pack(padx=10, pady=6, anchor="w")
                
                # ── Trust AP button ───────────────────────────────────────────
                btn_f = ctk.CTkFrame(inner, fg_color="transparent")
                btn_f.pack(fill="x", padx=14, pady=(4, 12))
                
                _ssid = alert.get("ssid", "")
                _all  = alert.get("all_bssids", [alert.get("rogue_mac", ""), alert.get("legit_mac", "")])
                
                def make_trust_cmd(s, bs, win=alerts_win):
                    def _cmd():
                        self._trust_ssid_bssids(s, bs)
                        win.destroy()
                        self.show_alerts_window()
                    return _cmd
                
                ctk.CTkButton(btn_f, text="✅ Trust — Mark as False Positive (Mesh/Extender)",
                              font=ctk.CTkFont(size=12), height=32,
                              fg_color=ThemeManager.get("trust_btn_fg"), hover_color=ThemeManager.get("trust_btn_hover"),
                              command=make_trust_cmd(_ssid, _all)).pack(side="left")
            elif alert["type"].startswith("ARP"):
                ip = alert.get("source_ip", "?")
                ctk.CTkLabel(inner, text=f"🌐  Target IP:  {ip}",
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=ThemeManager.get("text_body")).pack(fill="x", padx=14, pady=(4, 0), anchor="w")
                
                mac_f = ctk.CTkFrame(inner, fg_color="transparent")
                mac_f.pack(fill="x", padx=14, pady=(6, 2))
                ctk.CTkLabel(mac_f, text=f"🔴  New MAC (Spoofer):",
                             font=ctk.CTkFont(size=12, weight="bold"), text_color=ThemeManager.get("danger")).pack(side="left")
                ctk.CTkLabel(mac_f, text=f"  {alert.get('rogue_mac', '?')}",
                             font=ctk.CTkFont(size=12, family="Courier"), text_color=ThemeManager.get("danger")).pack(side="left")
                
                mac_f2 = ctk.CTkFrame(inner, fg_color="transparent")
                mac_f2.pack(fill="x", padx=14, pady=(0, 2))
                ctk.CTkLabel(mac_f2, text=f"✅  Old MAC (Legit):",
                             font=ctk.CTkFont(size=12, weight="bold"), text_color=ThemeManager.get("success")).pack(side="left")
                ctk.CTkLabel(mac_f2, text=f"  {alert.get('legit_mac', '?')}",
                             font=ctk.CTkFont(size=12, family="Courier"), text_color=ThemeManager.get("success")).pack(side="left")
                
                ctk.CTkLabel(inner, text=f"📡  Details: {alert.get('details', '')}",
                             font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_dim"),
                             justify="left", wraplength=840).pack(fill="x", padx=14, pady=(2, 4), anchor="w")
                             
                action_f = ctk.CTkFrame(inner, fg_color=ThemeManager.get("bg_elevated"), corner_radius=6)
                action_f.pack(fill="x", padx=14, pady=(4, 14))
                ctk.CTkLabel(action_f, text="💡 Tech Actions:  1) Trace new MAC to switch port.  2) Flush ARP cache on affected clients.  3) Implement Dynamic ARP Inspection (DAI).",
                             font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_muted"),
                             justify="left", wraplength=840).pack(padx=10, pady=6, anchor="w")

            elif alert["type"].startswith("Deauth"):
                target = alert.get("target_mac", "Unknown")
                count = alert.get("deauth_count", 1)
                
                ctk.CTkLabel(inner, text=f"🎯  Target MAC:  {target}",
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=ThemeManager.get("text_body")).pack(fill="x", padx=14, pady=(4, 0), anchor="w")
                
                ctk.CTkLabel(inner, text=f"📊  Frames Detected:  {count}",
                             font=ctk.CTkFont(size=12), text_color=ThemeManager.get("warning")).pack(fill="x", padx=14, pady=(2, 2), anchor="w")
                
                ctk.CTkLabel(inner, text=f"📡  Details: {alert.get('details', '')}",
                             font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_dim"),
                             justify="left", wraplength=840).pack(fill="x", padx=14, pady=(2, 4), anchor="w")
                             
                action_f = ctk.CTkFrame(inner, fg_color=ThemeManager.get("bg_elevated"), corner_radius=6)
                action_f.pack(fill="x", padx=14, pady=(4, 14))
                ctk.CTkLabel(action_f, text="💡 Tech Actions:  1) Check physical area for attackers (e.g. WiFi Pineapples).  2) Upgrade AP to WPA3 or enable 802.11w Protected Management Frames (PMF).",
                             font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_muted"),
                             justify="left", wraplength=840).pack(padx=10, pady=6, anchor="w")
                             
            else:
                ctk.CTkLabel(inner, text=alert.get("details", ""),
                             font=ctk.CTkFont(size=13), text_color=ThemeManager.get("text_body"),
                             justify="left", wraplength=840).pack(fill="x", padx=14, pady=(4, 14), anchor="w")

            # ── Acknowledgement Checkbox ─────────────────────────────────────
            ack_f = ctk.CTkFrame(inner, fg_color="transparent")
            ack_f.pack(fill="x", padx=14, pady=(4, 12))
            
            ack_var = ctk.StringVar(value="on" if alert.get("acknowledged", False) else "off")
            
            def make_ack_cmd(a=alert, v=ack_var):
                def _cmd():
                    a["acknowledged"] = (v.get() == "on")
                return _cmd
                
            ctk.CTkCheckBox(
                ack_f, text="Acknowledge Alert (Silence Reminder)", variable=ack_var,
                onvalue="on", offvalue="off", command=make_ack_cmd()
            ).pack(side="left")


