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
import subprocess
import logging
from serial.tools import list_ports
from PIL import Image, ImageDraw
from gui.user_view import UserView
from gui.theme import ThemeManager
from ids.deauth_detector import DeauthDetector
from ids import config as ids_config


class App(ctk.CTk):
    def __init__(self, start_serial_cb, stop_serial_cb, send_serial_cmd_cb=None):
        super().__init__()
        
        self.title("WIDS - Dashboard")
        self.geometry("1100x700")
        
        # Premium dark mode theme
        ThemeManager.init()
        ThemeManager.on_change(self._apply_theme)
        
        self.start_serial_cb = start_serial_cb
        self.stop_serial_cb = stop_serial_cb
        self.send_serial_cmd_cb = send_serial_cmd_cb
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Stats
        self.total_packets = 0
        self.deauth_count = 0
        self.alert_count = 0
        self.target_ssid = self._detect_current_ssid()
        
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
        self.last_eviltwin_audio_time = {} # (ssid, rogue_mac) -> timestamp
        self.eviltwin_alert_map = {} # (ssid, rogue_mac) -> alert dict
        
        # Host Wi-Fi state
        self.host_ssid = None
        self.last_host_ssid_check = 0
        self.bssid_last_seen = {} # BSSID -> timestamp of last packet
        self.last_bssid_cleanup_time = 0 # timestamp of last cleanup
        self.deauth_history = {} # target_mac -> deque of timestamps
        self.deauth_alert_cooldown = {} # target_mac -> timestamp of last alert
        
        # ARP tracking
        self.arp_alerts_sent = {} # (ip, mac) -> timestamp, rate-limit ARP alerts
        
        # Persistent whitelist: ssid -> set of trusted BSSIDs
        self.whitelist_path = os.path.join(os.path.dirname(__file__), "..", "ids", "whitelist.json")
        self.whitelist = self._load_whitelist()

        # Deauthentication detector
        self.deauth_detector = DeauthDetector()
        self._sync_deauth_whitelist()
        self.deauth_alert_map = {} # (src, bssid, victim) -> alert dict

        self.packet_queue = queue.Queue()
        self.update_interval = 100 # ms
        
        self.create_sidebar()
        self.create_main_content()

        self.current_view = "technician"
        self.user_view = UserView(self, self.show_technician_view, self)
        self.user_view.grid(row=0, column=1, sticky="nsew")
        self.user_view.grid_remove()
        
        self._after_ids = []
        self._after_ids.append(self.after(self.update_interval, self.process_packet_queue))
        self._after_ids.append(self.after(1000, self._try_auto_connect_serial))
        self._after_ids.append(self.after(30000, self._check_unacknowledged_alerts))
        
    def destroy(self):
        """Cancel all pending after() callbacks before destroying."""
        for after_id in getattr(self, '_after_ids', []):
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        super().destroy()

    def _detect_current_ssid(self):
        try:
            if os.name == 'nt':
                # Use creationflags=0x08000000 (CREATE_NO_WINDOW) to prevent flashing console on Windows
                output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], 
                                                 creationflags=0x08000000).decode('utf-8', errors='ignore')
                for line in output.split('\n'):
                    if "SSID" in line and "BSSID" not in line:
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            ssid = parts[1].strip()
                            if ssid:
                                return ssid
        except Exception as e:
            logging.warning(f"Failed to detect SSID: {e}")
        return None

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
        except Exception as e:
            logging.warning(f"Failed to load logo: {e}")
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="WIDS", font=ctk.CTkFont(family="Consolas", size=26, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        target_text = f"🛡️ Target: {self.target_ssid}" if self.target_ssid else "🛡️ Target: All Networks"
        self.target_label = ctk.CTkLabel(self.sidebar_frame, text=target_text, font=ctk.CTkFont(size=12, weight="bold"), text_color=ThemeManager.get("accent"))
        # self.target_label.grid(row=0, column=0, padx=20, pady=(90, 0), sticky="n") # Hidden for now
        
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

        # Desktop Audio Mute toggle button
        self.mute_laptop_audio = False
        self.mute_desktop_btn = ctk.CTkButton(
            self.sidebar_frame, text="🔊 PC Sound: ON", height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ThemeManager.get("bg_elevated"), text_color=ThemeManager.get("text_main"),
            hover_color=ThemeManager.get("primary_hover"),
            command=self.toggle_desktop_mute
        )
        self.mute_desktop_btn.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Theme toggle button
        toggle_text = "☀️ Light Mode" if ThemeManager.is_dark() else "🌙 Dark Mode"
        self.theme_toggle_btn = ctk.CTkButton(
            self.sidebar_frame, text=toggle_text, height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent", text_color=ThemeManager.get("text_muted"),
            hover_color=ThemeManager.get("bg_elevated"),
            command=self.toggle_theme
        )
        self.theme_toggle_btn.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="s")

        self.switch_view_btn = ctk.CTkButton(
            self.sidebar_frame, text="\U0001F464  Switch to User View", height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ThemeManager.get("accent"), hover_color=ThemeManager.get("accent_hover"),
            command=self.toggle_view
        )
        self.switch_view_btn.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="ew")

    def toggle_desktop_mute(self):
        self.mute_laptop_audio = not getattr(self, "mute_laptop_audio", False)
        if self.mute_laptop_audio:
            self.mute_desktop_btn.configure(text="🔇 PC Sound: MUTED", fg_color=ThemeManager.get("danger"))
        else:
            self.mute_desktop_btn.configure(text="🔊 PC Sound: ON", fg_color=ThemeManager.get("bg_elevated"))

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

        current_time = time.time()
        bssid_last_seen = getattr(self, 'bssid_last_seen', {})
        # Look back up to 10 minutes (600s) so legitimate APs are not forgotten during deauth jamming
        known_bssids = {b for b in self.ssid_to_bssid.get(ssid, set()) if current_time - bssid_last_seen.get(b, 0) < 600} - {bssid}
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
        
        # Mesh/extender suppression: Many real routers use Realtek/Atheros chips, so we no longer penalize "laptop" OUIs for mesh suppression.
        # If neither is locally administered, and the score discrepancy isn't extreme (score_diff < 40), it's likely a mesh network.
        is_likely_mesh = neither_is_laa and (all_same_vendor or is_enterprise or score_diff < 40)

        logging.warning(
            f"[EVIL TWIN DIAGNOSTIC] SSID: '{ssid}' | BSSIDs: {all_bssids} | "
            f"Scores: {scored} | LAA Check (neither_is_laa): {neither_is_laa} | "
            f"Same Vendor (all_same_vendor): {all_same_vendor} | Enterprise: {is_enterprise} | "
            f"Score Diff: {score_diff} | is_likely_mesh: {is_likely_mesh}"
        )

        return suspected_rogue, suspected_legit, rogue_reasons, is_likely_mesh

    # ── Whitelist persistence ────────────────────────────────────────────────

    def _load_whitelist(self) -> dict:
        """Load whitelist from JSON. Returns {ssid: [bssid, ...]}."""
        if os.path.exists(self.whitelist_path):
            try:
                with open(self.whitelist_path, "r") as f:
                    raw = json.load(f)
                    return {k: {mac.upper() for mac in v} for k, v in raw.items()}
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
            logging.warning(f"[WIDS] Could not save whitelist: {e}")

    def _trust_ssid_bssids(self, ssid: str, bssids: list):
        """Add all given BSSIDs for an SSID to the whitelist."""
        if ssid not in self.whitelist:
            self.whitelist[ssid] = set()
        self.whitelist[ssid].update(mac.upper() for mac in bssids)
        self._save_whitelist()
        self._sync_deauth_whitelist()

    def _sync_deauth_whitelist(self):
        """Flatten per-SSID whitelist into a flat set for the deauth detector."""
        all_trusted = set()
        for bssids in self.whitelist.values():
            all_trusted.update(mac.upper() for mac in bssids)
        ids_config.WHITELIST_BSSID = all_trusted

    # ────────────────────────────────────────────────────────────────────────

    def _check_unacknowledged_alerts(self):
        unacknowledged = any(not a.get("acknowledged", False) for a in self.alerts_list)
        if unacknowledged:
            self._play_alert_sound("Unacknowledged")
        self.after(30000, self._check_unacknowledged_alerts)

    def _play_alert_sound(self, message="Alert Detected"):
        try:
            import ctypes
            import os
            
            _audio_dir = os.path.join(os.path.dirname(__file__), "..", "voice_audios")
            now = time.time()
            # Audio debouncing: limit audio playback to once every 5 seconds per category
            if not hasattr(self, "_last_audio_play_time"):
                self._last_audio_play_time = {}
            if now - self._last_audio_play_time.get(message, 0) < 5:
                return
            self._last_audio_play_time[message] = now
            

            # Map the message to the corresponding pre-recorded Jarvis mp3 file
            audio_file = None
            track = None
            if "Evil Twin" in message:
                audio_file = os.path.join(_audio_dir, "Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-32-Warning-!!-Evil-twin-wifi-detected!!.mp3")
                track = "evil_twin"
            elif "ARP Spoofing" in message:
                audio_file = os.path.join(_audio_dir, "Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-34-Warning-!!-MAC-Spoofing-detected-,-Sir!!!.mp3")
                track = "mac_spoof"
            elif "Deauth" in message:
                audio_file = os.path.join(_audio_dir, "Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-35-Warning-!!-Deauth-Attack-Frames-has-been-found-,.mp3")
                track = "deauth"
            elif "Greeting" in message:
                audio_file = os.path.join(_audio_dir, "Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-40-Hello-,-Sir-,-Our-Intrusion-Detection-System-is.mp3")
                track = "greeting"
            elif "Unacknowledged" in message:
                audio_file = os.path.join(_audio_dir, "Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-56-Sir-!!-please-check-the-alerts-history-carefully.mp3")
                track = "history"

            # Trigger hardware ESP32 speaker
            if track and getattr(self, "send_serial_cmd_cb", None):
                self.send_serial_cmd_cb({"cmd": "play", "track": track})
            
            # Play on PC sound card unless PC sound is muted by the user
            if not getattr(self, "mute_laptop_audio", False) and audio_file and os.path.exists(audio_file):
                path = os.path.abspath(audio_file)
                
                # Get short path to prevent MCI path parsing errors with spaces/special characters
                buf_size = ctypes.windll.kernel32.GetShortPathNameW(path, None, 0)
                if buf_size > 0:
                    buf = ctypes.create_unicode_buffer(buf_size)
                    ctypes.windll.kernel32.GetShortPathNameW(path, buf, buf_size)
                    path = buf.value
                
                alias = "jarvis_voice"
                
                # Stop and close the alias to cancel any currently playing sound
                ctypes.windll.winmm.mciSendStringW(f'stop {alias}', None, 0, None)
                ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                
                # Open the new sound and play asynchronously
                res_open = ctypes.windll.winmm.mciSendStringW(f'open {path} alias {alias}', None, 0, None)
                if res_open != 0:
                    err_buf = ctypes.create_unicode_buffer(256)
                    ctypes.windll.winmm.mciGetErrorStringW(res_open, err_buf, 256)
                    logging.warning(f"Audio open error: {err_buf.value}")
                
                res_play = ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, None)
                if res_play != 0:
                    err_buf = ctypes.create_unicode_buffer(256)
                    ctypes.windll.winmm.mciGetErrorStringW(res_play, err_buf, 256)
                    logging.warning(f"Audio play error: {err_buf.value}")
        except Exception as e:
            logging.warning(f"Audio playback error: {e}")

    def _add_alert(self, alert):
        self.alert_count += 1
        alert_type_msg = alert.get("type", "Alert").split("[")[0].strip()
        self._play_alert_sound(f"{alert_type_msg} Detected")
        alert.setdefault("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        alert.setdefault("last_seen", alert["time"])
        self.alerts_list.append(alert)
        if len(self.alerts_list) > 2000:
            self.alerts_list.pop(0)
        
        # Log the alert details
        logging.warning(
            f"[ALERT TRIGGERED] Type: {alert.get('type')} | Severity: {alert.get('severity')} | "
            f"Details: {alert.get('details') or alert.get('ssid') or ''}"
        )
        return alert

    def _cleanup_stale_state(self):
        """Periodically prune stale tracking state to prevent memory exhaustion."""
        now = time.time()
        if now - getattr(self, '_last_state_cleanup', 0) < 60:
            return
        self._last_state_cleanup = now
        
        # Cap eviltwin_alert_map to 500 entries
        if len(self.eviltwin_alert_map) > 500:
            keys = sorted(self.eviltwin_alert_map.keys(), 
                           key=lambda k: self.eviltwin_alert_map[k].get('last_seen', ''), 
                           reverse=True)
            for key in keys[500:]:
                del self.eviltwin_alert_map[key]
        
        # Cap last_eviltwin_alert_time to 500 entries
        if len(self.last_eviltwin_alert_time) > 500:
            sorted_keys = sorted(self.last_eviltwin_alert_time.keys(), 
                                  key=lambda k: self.last_eviltwin_alert_time[k], reverse=True)
            for key in sorted_keys[500:]:
                del self.last_eviltwin_alert_time[key]
        
        # Cap arp_alerts_sent — remove entries older than 60 seconds
        stale_arp = [k for k, t in self.arp_alerts_sent.items() if now - t > 60]
        for k in stale_arp:
            del self.arp_alerts_sent[k]
        
        # Cap deauth_alert_cooldown — remove entries older than 60 seconds  
        stale_deauth = [k for k, t in self.deauth_alert_cooldown.items() if now - t > 60]
        for k in stale_deauth:
            del self.deauth_alert_cooldown[k]

    def _handle_deauth_packet(self, packet):
        self.deauth_count += 1

        # Map project packet format to detector format
        detector_packet = {
            "src": packet.get("mac_src"),
            "dst": packet.get("mac_dst"),
            "bssid": packet.get("bssid"),
            "reason": packet.get("reason", 0),
            "subtype": packet.get("subtype"),
            "timestamp": time.time(),
        }

        alert = self.deauth_detector.process(detector_packet)

        if alert:
            score = alert.get("score", 0)
            if score >= 8:
                severity = "Critical"
            elif score >= 6:
                severity = "High"
            elif score >= 4:
                severity = "Medium"
            else:
                severity = "Low"

            reasons_str = " | ".join(alert.get("reasons", []))
            src_mac = alert.get("source", "Unknown")
            victim_mac = alert.get("victim", "Unknown")
            bssid_mac = alert.get("bssid", "Unknown")
            deauth_key = (src_mac, bssid_mac, victim_mac)

            if not hasattr(self, 'deauth_alert_map'):
                self.deauth_alert_map = {}
            if not hasattr(self, 'deauth_alert_cooldown'):
                self.deauth_alert_cooldown = {}

            now = time.time()
            if deauth_key in self.deauth_alert_map:
                existing_alert = self.deauth_alert_map[deauth_key]
                existing_alert["seen_count"] = existing_alert.get("seen_count", 1) + 1
                existing_alert["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                existing_alert["score"] = max(existing_alert.get("score", 0), score)
                existing_alert["details"] = reasons_str
                existing_alert["deauth_count"] = self.deauth_count
                
                # Audio debouncing check
                if now - self.deauth_alert_cooldown.get(deauth_key, 0) >= 5:
                    self.deauth_alert_cooldown[deauth_key] = now
                    self._play_alert_sound("Deauth Attack Detected")
            else:
                self.deauth_alert_cooldown[deauth_key] = now
                new_alert = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": f"Deauth Attack [{severity}]",
                    "severity": severity,
                    "target_mac": victim_mac,
                    "source_mac": src_mac,
                    "bssid": bssid_mac,
                    "deauth_count": self.deauth_count,
                    "details": reasons_str,
                    "score": score,
                    "reasons": alert.get("reasons", []),
                    "seen_count": 1,
                }
                self._add_alert(new_alert)
                self.deauth_alert_map[deauth_key] = new_alert

    def _find_serial_ports(self):
        try:
            return [port.device for port in list_ports.comports()]
        except Exception:
            return []

    def _try_auto_connect_serial(self):
        if self.is_connected or getattr(self, "_connecting_in_progress", False):
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

        self._connecting_in_progress = True

        def _bg_connect():
            connected_port = None
            for port in ports:
                self.after(0, lambda p=port: self.status_label.configure(text=f"● Trying {p}...", text_color="#f59e0b"))
                success = self.start_serial_cb(port, baud)
                if success:
                    connected_port = port
                    break

            def _on_finish():
                self._connecting_in_progress = False
                if connected_port:
                    self.com_port_entry.delete(0, tk.END)
                    self.com_port_entry.insert(0, connected_port)
                    self.is_connected = True
                    self.connect_btn.configure(text="DISCONNECT", fg_color="#ef4444", hover_color="#dc2626")
                    self.status_label.configure(text=f"● Connected to {connected_port}", text_color="#10b981")
                    self._play_alert_sound("Greeting")
                else:
                    self.status_label.configure(text="● Disconnected", text_color="#ef4444")

            self.after(0, _on_finish)

        import threading
        threading.Thread(target=_bg_connect, daemon=True).start()

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

    def _update_host_ssid(self):
        """Update the currently connected Wi-Fi SSID (Windows only)."""
        import subprocess
        try:
            # Hide the console window when running subprocess on Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True, startupinfo=startupinfo)
            for line in output.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    self.host_ssid = line.split(":", 1)[1].strip()
                    return
            self.host_ssid = None
        except Exception:
            pass

    def process_packet_queue(self):
        current_time = time.time()
        if current_time - self.last_host_ssid_check > 5.0:
            self.last_host_ssid_check = current_time
            self._update_host_ssid()

        packets_to_insert = []
        self._cleanup_stale_state()
        qsize = self.packet_queue.qsize()
        # Flow control: if queue is overflowing (>1000 items), drop non-essential frames to maintain responsiveness
        high_load = qsize > 1000
        
        try:
            # Drain up to 200 packets per batch
            for _ in range(200):
                packet = self.packet_queue.get_nowait()
                
                self.total_packets += 1
                subtype = packet.get('subtype', '')
                
                if high_load and subtype in ("Beacon", "Probe Request") and not packet.get('is_evil_twin'):
                    continue

                if subtype == "Deauthentication":
                    self._handle_deauth_packet(packet)
                        
                bssid = packet.get('bssid', '')
                ssid = packet.get('ssid', '')
                mac_src = packet.get('mac_src', '')
                mac_dst = packet.get('mac_dst', '')
                channel = packet.get('channel', None)
                rssi = packet.get('rssi', None)
                
                is_evil_twin = False
                
                # ── BSSID State Cleanup ──
                current_time = time.time()
                if current_time - getattr(self, 'last_bssid_cleanup_time', 0) > 10:
                    self.last_bssid_cleanup_time = current_time
                    # Retain known BSSIDs for 1 hour (3600s) so APs are not forgotten during attacks
                    stale_bssids = [b for b, t in getattr(self, 'bssid_last_seen', {}).items() if current_time - t > 3600]
                    for stale_b in stale_bssids:
                        self.bssid_last_seen.pop(stale_b, None)
                        self.bssid_channel.pop(stale_b, None)
                        self.bssid_rssi.pop(stale_b, None)
                        self.bssid_first_seen.pop(stale_b, None)
                        self.bssid_seen_count.pop(stale_b, None)
                        self.network_map.pop(stale_b, None)
                        for s, b_set in list(self.ssid_to_bssid.items()):
                            if stale_b in b_set:
                                b_set.remove(stale_b)
                                if not b_set:
                                    del self.ssid_to_bssid[s]

                # Update map if SSID is present
                if ssid and bssid:
                    self.network_map[bssid] = ssid
                    if not hasattr(self, 'bssid_last_seen'):
                        self.bssid_last_seen = {}
                    self.bssid_last_seen[bssid] = current_time
                    
                    # Track first seen timestamp
                    if bssid not in self.bssid_first_seen:
                        self.bssid_first_seen[bssid] = current_time
                    
                    # Track channel and RSSI history per BSSID
                    prev_channel = self.bssid_channel.get(bssid)
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
                    
                    # Track channel history for spoof detection
                    if not hasattr(self, 'bssid_channel_history'):
                        self.bssid_channel_history = {}
                    if bssid not in self.bssid_channel_history:
                        self.bssid_channel_history[bssid] = []
                    
                    is_channel_bounce = False
                    # Channel bounce disabled: ESP32 channel hopping receives RF leakage from wide 20/40MHz channels across multiple channels, causing false positive Evil Twin alerts.
                    
                    # ── Gate 0: Only check connected Wi-Fi for Evil Twin ───────────────
                    if not self.host_ssid or ssid != self.host_ssid:
                        pass # Ignore other Wi-Fis, or wait until host_ssid is known
                    
                    # ── Gate 1: Skip if this BSSID is whitelisted ───────────────
                    elif bssid.upper() in self.whitelist.get(ssid, set()):
                        pass  # Trusted — skip Evil Twin analysis
                    
                    # ── Gate 2: Flag immediately on BSSID conflict ───
                    elif len(self.ssid_to_bssid[ssid]) > 1:
                        
                        score, reasons = self._score_evil_twin(ssid, bssid, channel, rssi)
                        
                        if score > 0:
                            # Identify which BSSID is the rogue
                            rogue_mac, legit_mac, rogue_reasons, is_likely_mesh = self._identify_rogue(ssid)
                            
                            # ── Gate 3: Mesh/extender suppression ───────────────
                            if is_likely_mesh:
                                confidence_label = "LOW"
                                severity = "Low"
                                tag = "eviltwin_low"
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
                            
                            packet['is_evil_twin'] = not is_likely_mesh
                            packet['et_confidence'] = confidence_label
                            packet['et_tag'] = tag if not is_likely_mesh else ""
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
                                
                                if alert_key in self.eviltwin_alert_map:
                                    # Update existing alert dict directly instead of index lookup
                                    existing_alert = self.eviltwin_alert_map[alert_key]
                                    existing_alert["seen_count"] = existing_alert.get("seen_count", 1) + 1
                                    existing_alert["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    existing_alert["score"] = score
                                    existing_alert["type"] = f"Evil Twin [{confidence_label} {score}%]"
                                    existing_alert["severity"] = severity
                                    
                                    if current_time - self.last_eviltwin_audio_time.get(alert_key, 0) >= 60:
                                        self._play_alert_sound("Evil Twin Wifi Detected")
                                        self.last_eviltwin_audio_time[alert_key] = current_time
                                else:
                                    self.alert_count += 1
                                    self._play_alert_sound("Evil Twin Wifi Detected")
                                    self.last_eviltwin_audio_time[alert_key] = current_time
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
                                    self.eviltwin_alert_map[alert_key] = new_alert
                                    if len(self.alerts_list) > 2000:
                                        popped = self.alerts_list.pop(0)
                                        p_key = (popped.get("ssid"), popped.get("rogue_mac"))
                                        if p_key in self.eviltwin_alert_map and self.eviltwin_alert_map[p_key] is popped:
                                            del self.eviltwin_alert_map[p_key]
                                
                                self.last_eviltwin_alert_time[bssid] = current_time

                    # ── Gate 3: Single-BSSID Channel Mismatch (Spoofed MAC Rogue AP) ───
                    elif is_channel_bounce:
                        score = 85
                        confidence_label = "HIGH"
                        severity = "Critical"
                        tag = "eviltwin_high"
                        reason_str = f"BSSID '{bssid}' broadcasting on conflicting channels (original: Ch {prev_channel}, current: Ch {channel}) — MAC Spoofed Rogue AP"
                        alert_key = (ssid, bssid)
                        
                        packet['is_evil_twin'] = True
                        packet['et_confidence'] = confidence_label
                        packet['et_tag'] = tag
                        packet['et_rogue_mac'] = bssid
                        packet['et_legit_mac'] = bssid
                        packet['et_is_mesh'] = False

                        current_time = time.time()
                        if current_time - self.last_eviltwin_alert_time.get(bssid, 0) >= 10:
                            if alert_key in self.eviltwin_alert_map:
                                existing_alert = self.eviltwin_alert_map[alert_key]
                                existing_alert["seen_count"] = existing_alert.get("seen_count", 1) + 1
                                existing_alert["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                self.alert_count += 1
                                self._play_alert_sound("Evil Twin Wifi Detected")
                                new_alert = {
                                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "type": f"Evil Twin (Spoofed MAC) [{confidence_label} 85%]",
                                    "severity": severity,
                                    "ssid": ssid,
                                    "rogue_mac": bssid,
                                    "legit_mac": bssid,
                                    "details": reason_str,
                                    "rogue_why": "BSSID is transmitting on multiple channels simultaneously (MAC spoofing attack)",
                                    "is_mesh": False,
                                    "seen_count": 1,
                                    "score": 85,
                                    "all_bssids": [bssid]
                                }
                                self.alerts_list.append(new_alert)
                                self.eviltwin_alert_map[alert_key] = new_alert
                            self.last_eviltwin_alert_time[bssid] = current_time
                    
                # ─── ARP SPOOF DETECTION ───────────────────────────────────────
                packet_type = packet.get('type', '')
                if packet_type == "ARP" and packet.get('spoofed'):
                    ip = packet['source_ip']
                    new_mac = packet['mac_src']
                    old_mac = packet.get('old_mac', '?')
                    alert_key = (ip, new_mac)
                    confidence = packet.get('confidence', 'FIRST_SEEN')
                    alert_type = packet.get('alert_type', 'ip_mac_change')
                    
                    # Rate-limit: 1 alert per (ip, mac) per 10 seconds
                    now = time.time()
                    last_arp = self.arp_alerts_sent.get(alert_key, 0)
                    if now - last_arp >= 10:
                        self.alert_count += 1
                        self._play_alert_sound("ARP Spoofing Detected")
                        
                        # Build details string with confidence context
                        if alert_type == "gateway_spoof":
                            details = (
                                f"Gateway {ip} spoofed! Expected MAC: {old_mac}, "
                                f"got: {new_mac} [Confidence: {confidence}]"
                            )
                            alert_label = "ARP Spoofing (Gateway Hijack)"
                        else:
                            details = (
                                f"IP {ip} changed from {old_mac} to {new_mac} "
                                f"[Confidence: {confidence}]"
                            )
                            alert_label = "ARP Spoofing"
                        
                        self.alerts_list.append({
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "type": alert_label,
                            "severity": "Critical",
                            "details": details,
                            "source_ip": ip,
                            "rogue_mac": new_mac,
                            "legit_mac": old_mac,
                            "confidence": confidence,
                            "alert_type": alert_type,
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
            
            # Limit GUI Treeview insertions to 50 items per update tick to prevent Tkinter freezes
            for packet in packets_to_insert[:50]:
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
                _rogue_mac = alert.get("rogue_mac", "")
                
                is_trusted = _rogue_mac in self.whitelist.get(_ssid, set())
                
                if is_trusted:
                    ctk.CTkLabel(btn_f, text="✅ Trusted Device (Marked as Safe)",
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 text_color=ThemeManager.get("success")).pack(side="left")
                else:
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
                source = alert.get("source_mac", "Unknown")
                bssid_val = alert.get("bssid", "Unknown")
                count = alert.get("deauth_count", 1)
                score_val = alert.get("score", 0)
                reasons_list = alert.get("reasons", [])

                ctk.CTkLabel(inner, text=f"🎯  Target MAC:  {target}",
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=ThemeManager.get("text_body")).pack(fill="x", padx=14, pady=(4, 0), anchor="w")

                src_f = ctk.CTkFrame(inner, fg_color="transparent")
                src_f.pack(fill="x", padx=14, pady=(4, 2))
                ctk.CTkLabel(src_f, text=f"🔴  Source (Attacker):",
                             font=ctk.CTkFont(size=12, weight="bold"), text_color=ThemeManager.get("danger")).pack(side="left")
                ctk.CTkLabel(src_f, text=f"  {source}",
                             font=ctk.CTkFont(size=12, family="Courier"), text_color=ThemeManager.get("danger")).pack(side="left")

                ctk.CTkLabel(inner, text=f"📡  BSSID:  {bssid_val}",
                             font=ctk.CTkFont(size=12), text_color=ThemeManager.get("text_dim")).pack(fill="x", padx=14, pady=(2, 2), anchor="w")

                ctk.CTkLabel(inner, text=f"📊  Frames Detected:  {count}  ·  Suspicion Score:  {score_val}",
                             font=ctk.CTkFont(size=12), text_color=ThemeManager.get("warning")).pack(fill="x", padx=14, pady=(2, 2), anchor="w")

                if reasons_list:
                    reasons_text = "\n".join(f"    * {r}" for r in reasons_list)
                    ctk.CTkLabel(inner, text=f"🔍  Triggered Conditions:\n{reasons_text}",
                                 font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_dim"),
                                 justify="left", wraplength=840).pack(fill="x", padx=14, pady=(2, 4), anchor="w")

                ctk.CTkLabel(inner, text=f"📡  Details: {alert.get('details', '')}",
                             font=ctk.CTkFont(size=11), text_color=ThemeManager.get("text_dim"),
                             justify="left", wraplength=840).pack(fill="x", padx=14, pady=(2, 4), anchor="w")

                action_f = ctk.CTkFrame(inner, fg_color=ThemeManager.get("bg_elevated"), corner_radius=6)
                action_f.pack(fill="x", padx=14, pady=(4, 14))
                ctk.CTkLabel(action_f, text="💡 Tech Actions:  1) Check physical area for attackers (e.g. WiFi Pineapples).  2) Upgrade AP to WPA3 or enable 802.11w Protected Management Frames (PMF).  3) Identify and isolate the source device.",
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


