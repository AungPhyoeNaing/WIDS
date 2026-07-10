import customtkinter as ctk


# ──────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS — match Technician View (gui/app.py) exactly
# ──────────────────────────────────────────────────────────────────────────────
COLORS = {
    "bg_deep":      "#09090b",   # Zinc 950 — root background
    "bg_card":      "#18181b",   # Zinc 900 — card surfaces
    "bg_elevated":  "#27272a",   # Zinc 800 — nav bar, headers
    "border":       "#27272a",   # Zinc 800 — dividers
    "primary":      "#60a5fa",   # Blue 400 — brighter primary
    "primary_hover": "#3b82f6",  # Blue 500
    "success":      "#34d399",   # Emerald 400 — brighter success
    "warning":      "#fbbf24",   # Amber 400 — brighter warning
    "danger":       "#f87171",   # Red 400 — brighter danger
    "text_muted":   "#d4d4d8",   # Zinc 300 — brighter secondary
    "text_body":    "#e4e4e7",   # Zinc 200 — body text
    "text_heading": "#f4f4f5",   # Zinc 100 — headings
    "alert_inner":  "#1c1c1f",   # custom — alert card inner
}

SEVERITY_COLOR = {
    "Critical": COLORS["danger"],
    "High":     "#f97316",       # Orange 500
    "Medium":   COLORS["warning"],
    "Low":      COLORS["primary"],
}


class UserView(ctk.CTkFrame):
    def __init__(self, master, switch_to_technician_cb, app_ref):
        super().__init__(master, fg_color=COLORS["bg_deep"], corner_radius=0)
        self.switch_to_technician = switch_to_technician_cb
        self.app = app_ref

        self.grid_rowconfigure(0, weight=0)   # nav bar
        self.grid_rowconfigure(1, weight=1)   # content
        self.grid_columnconfigure(0, weight=1)

        self.page = "home"
        self._alert_widgets = {}
        self._stat_labels = {}
        self._status_badges = {}

        self._build_nav()
        self._switch("home")
        self.after(1000, self._live_update)

    def add_packet(self, packet):
        """Receive packet notification from App (stats polled live from self.app)."""
        pass

    # ═══════════════════════════════════════════════════════════════════════════
    # NAV BAR — built ONCE
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_nav(self):
        self._nav_frame = ctk.CTkFrame(
            self, fg_color=COLORS["bg_card"], corner_radius=0, height=64
        )
        self._nav_frame.grid(row=0, column=0, sticky="ew")
        self._nav_frame.grid_columnconfigure(0, weight=1)
        self._nav_frame.pack_propagate(False)

        self._nav_buttons = {}
        for page_id, label, icon in [
            ("alert", "Alerts", "🚨"),
            ("home", "Home", "🏠"),
        ]:
            btn = ctk.CTkButton(
                self._nav_frame,
                text=f"{icon}  {label}",
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color="transparent",
                hover_color="#3f3f46",
                text_color=COLORS["text_muted"],
                corner_radius=8,
                height=40,
                width=130,
                command=lambda p=page_id: self._switch(p),
            )
            btn.pack(side="right", padx=8, pady=12)
            self._nav_buttons[page_id] = btn

    def _switch(self, page):
        self.page = page
        for pid, btn in self._nav_buttons.items():
            active = (pid == page)
            btn.configure(
                fg_color=COLORS["primary"] if active else "transparent",
                text_color="#ffffff" if active else COLORS["text_muted"],
            )
        self._clear_content()
        {"home": self._home, "alert": self._alert}[page]()

    def _clear_content(self):
        for w in self.grid_slaves():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
        self._alert_widgets.clear()
        self._stat_labels.clear()
        self._status_badges.clear()
        self._secure_label = None

    # ═══════════════════════════════════════════════════════════════════════════
    # SHARED UI FACTORIES
    # ═══════════════════════════════════════════════════════════════════════════
    def _make_container(self):
        c = ctk.CTkFrame(self, fg_color=COLORS["bg_deep"], corner_radius=0)
        c.grid(row=1, column=0, sticky="nsew")
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(1, weight=1)
        return c

    def _create_stat_card(self, parent, title, col, color):
        """Exact clone of Technician View create_stat_card."""
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12, height=110)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_muted"]
        ).grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        val = ctk.CTkLabel(
            card, text="0",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=color
        )
        val.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        return val

    def _make_header(self, parent, title, action_widget=None):
        h = ctk.CTkFrame(parent, fg_color="transparent")
        h.grid(row=0, column=0, padx=25, pady=(16, 6), sticky="ew")
        h.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            h, text=title,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_heading"]
        ).grid(row=0, column=0, sticky="w")
        if action_widget:
            action_widget.grid(row=0, column=1, sticky="e")
        return h

    # ═══════════════════════════════════════════════════════════════════════════
    # ALERT WIDGET — single source of truth (compact + full)
    # ═══════════════════════════════════════════════════════════════════════════
    def _create_alert_widget(self, key, alert, compact=False):
        sev = alert.get("severity", "Low")
        is_et = bool(alert.get("rogue_mac"))
        is_mesh = alert.get("is_mesh", False)
        seen = alert.get("seen_count", 1)
        stripe = SEVERITY_COLOR.get(sev, COLORS["primary"])

        wrapper = ctk.CTkFrame(
            self._alerts_scroll if not compact else self._home_preview_scroll,
            fg_color=stripe, corner_radius=8
        )
        wrapper.pack(fill="x", padx=18 if not compact else 12, pady=5 if not compact else 4)

        inner = ctk.CTkFrame(wrapper, fg_color=COLORS["alert_inner"], corner_radius=6)
        inner.pack(fill="both", padx=(4, 0), pady=0)

        # ── Header row: TYPE + seen count + times
        hdr = ctk.CTkFrame(inner, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            hdr, text=alert["type"].upper(),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=stripe
        ).pack(side="left")
        if seen > 1:
            ctk.CTkLabel(
                hdr, text=f"  ×{seen} detected",
                font=ctk.CTkFont(size=13), text_color="#d4d4d8"
            ).pack(side="left", padx=8)
        ctk.CTkLabel(
            hdr,
            text=f"First: {alert['time']}  ·  Last: {alert.get('last_seen', alert['time'])}",
            font=ctk.CTkFont(size=12), text_color="#787880"
        ).pack(side="right")

        if compact:
            # One-line summary for Home preview
            ssid = alert.get('ssid', '')
            if ssid:
                ctk.CTkLabel(
                    inner, text=f"🌐 {ssid}",
                    font=ctk.CTkFont(size=14), text_color=COLORS["text_body"],
                    anchor="w"
                ).pack(fill="x", padx=14, pady=(0, 8))
            return wrapper

        # ── Full detail (Alerts tab)
        if is_et:
            if is_mesh:
                ctk.CTkLabel(
                    inner,
                    text="ℹ️  Both APs use router-vendor MACs — likely a mesh network or extender. Verify manually.",
                    font=ctk.CTkFont(size=14), text_color="#60a5fa",
                    justify="left", wraplength=840
                ).pack(fill="x", padx=14, pady=(2, 4), anchor="w")

            ssid = alert.get('ssid', 'Unknown')
            ctk.CTkLabel(
                inner, text=f"🌐  SSID:  {ssid}",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#e4e4e7"
            ).pack(fill="x", padx=14, pady=(4, 0), anchor="w")

            # Rogue MAC
            mf = ctk.CTkFrame(inner, fg_color="transparent")
            mf.pack(fill="x", padx=14, pady=(6, 2))
            ctk.CTkLabel(mf, text="🔴  Suspected Rogue AP:",
                         font=ctk.CTkFont(size=14, weight="bold"), text_color="#f87171").pack(side="left")
            ctk.CTkLabel(mf, text=f"  {alert.get('rogue_mac', '?')}",
                         font=ctk.CTkFont(size=14, family="Courier"), text_color="#fca5a5").pack(side="left")

            # Legit MAC
            mf2 = ctk.CTkFrame(inner, fg_color="transparent")
            mf2.pack(fill="x", padx=14, pady=(0, 2))
            ctk.CTkLabel(mf2, text="✅  Likely Legitimate AP:",
                         font=ctk.CTkFont(size=14, weight="bold"), text_color="#34d399").pack(side="left")
            ctk.CTkLabel(mf2, text=f"  {alert.get('legit_mac', '?')}",
                         font=ctk.CTkFont(size=14, family="Courier"), text_color="#6ee7b7").pack(side="left")

            if alert.get("rogue_why"):
                ctk.CTkLabel(
                    inner, text=f"🔍  Why rogue: {alert['rogue_why']}",
                    font=ctk.CTkFont(size=14), text_color="#fb923c",
                    justify="left", wraplength=840
                ).pack(fill="x", padx=14, pady=(4, 0), anchor="w")

            if alert.get("details"):
                ctk.CTkLabel(
                    inner, text=f"📡  Signals: {alert['details']}",
                    font=ctk.CTkFont(size=13), text_color="#a1a1aa",
                    justify="left", wraplength=840
                ).pack(fill="x", padx=14, pady=(2, 4), anchor="w")

            # Action box
            act = ctk.CTkFrame(inner, fg_color="#27272a", corner_radius=6)
            act.pack(fill="x", padx=14, pady=(4, 4))
            ctk.CTkLabel(
                act,
                text="💡 Recommended:  1) Do NOT connect to this SSID until verified.  2) Check your router's MAC in its admin page.  3) Report to IT admin if persistent.",
                font=ctk.CTkFont(size=13), text_color="#d4d4d8",
                justify="left", wraplength=840
            ).pack(padx=10, pady=6, anchor="w")

            # Trust button
            btn_f = ctk.CTkFrame(inner, fg_color="transparent")
            btn_f.pack(fill="x", padx=14, pady=(4, 12))
            _ssid = alert.get("ssid", "")
            _all = alert.get("all_bssids", [alert.get("rogue_mac", ""), alert.get("legit_mac", "")])

            def make_trust_cmd(s, bs, w=wrapper):
                def _cmd():
                    self.app._trust_ssid_bssids(s, bs)
                    w.destroy()
                    self._refresh_alerts()
                return _cmd

            ctk.CTkButton(
                btn_f, text="✅ Trust — Mark as False Positive (Mesh/Extender)",
                font=ctk.CTkFont(size=14), height=36,
                fg_color="#166534", hover_color="#14532d",
                command=make_trust_cmd(_ssid, _all)
            ).pack(side="left")
        else:
            # Non-Evil-Twin (deauth flood, etc.)
            ctk.CTkLabel(
                inner, text=alert.get("details", ""),
                font=ctk.CTkFont(size=15), text_color="#e4e4e7",
                justify="left", wraplength=840
            ).pack(fill="x", padx=14, pady=(4, 14), anchor="w")

        return wrapper

    # ═══════════════════════════════════════════════════════════════════════════
    # HOME TAB
    # ═══════════════════════════════════════════════════════════════════════════
    def _home(self):
        c = self._make_container()

        # Top cards row (row 0): TOTAL DEVICES + SECURE STATUS side by side
        top_frame = ctk.CTkFrame(c, fg_color="transparent")
        top_frame.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        top_frame.grid_columnconfigure((0, 1), weight=1)

        self._stat_labels["devices"] = self._create_stat_card(
            top_frame, "TOTAL DEVICES", 0, COLORS["primary"]
        )
        self._secure_label = self._create_stat_card(
            top_frame, "SECURITY STATUS", 1, COLORS["success"]
        )

        # Recent alerts area (row 1) — fills remaining space
        log_frame = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=12)
        log_frame.grid(row=1, column=0, padx=30, pady=(10, 30), sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        log_hdr = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_hdr.grid(row=0, column=0, padx=25, pady=(20, 10), sticky="ew")
        log_hdr.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            log_hdr, text="Recent Alerts",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_heading"]
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            log_hdr, text="View All \u2192",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent", hover_color=COLORS["bg_elevated"],
            text_color=COLORS["primary"], height=36, width=100,
            command=lambda: self._switch("alert")
        ).grid(row=0, column=1, sticky="e")

        self._home_preview_scroll = ctk.CTkScrollableFrame(
            log_frame, fg_color="transparent",
            scrollbar_button_color="#2a2a4a", scrollbar_button_hover_color="#3a3a5a"
        )
        self._home_preview_scroll.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        self._home_preview_scroll.grid_columnconfigure(0, weight=1)

        self._refresh_home_preview()
        self._update_home_stats()
        self._update_security_status()

    def _update_security_status(self):
        if self._secure_label is None or not self._secure_label.winfo_exists():
            return
        alerts = self.app.alerts_list
        critical = sum(1 for a in alerts if a.get("severity") == "Critical")
        high = sum(1 for a in alerts if a.get("severity") == "High")
        if critical > 0:
            txt, clr = f"⚠  {critical} critical alert(s)", COLORS["danger"]
        elif high > 0:
            txt, clr = f"⚠  {high} high alert(s)", COLORS["warning"]
        elif alerts:
            txt, clr = f"⚠  {len(alerts)} alert(s)", COLORS["warning"]
        else:
            txt, clr = "✅  Secure", COLORS["success"]
        self._secure_label.configure(text=txt, text_color=clr)

    def _update_secure_status(self):
        if self._secure_label is None or not self._secure_label.winfo_exists():
            return

        alerts = self.app.alerts_list
        critical = sum(1 for a in alerts if a.get("severity") == "Critical")
        high = sum(1 for a in alerts if a.get("severity") == "High")
        if critical > 0:
            txt, clr = f"⚠️  {critical} critical alert(s)", COLORS["danger"]
        elif high > 0:
            txt, clr = f"⚠️  {high} high alert(s)", COLORS["warning"]
        elif alerts:
            txt, clr = f"⚠️  {len(alerts)} alert(s)", COLORS["warning"]
        else:
            txt, clr = "✅  Secure \u2014 No threats detected", COLORS["success"]
        self._secure_label.configure(text=txt, text_color=clr)

    def _update_devices_count(self):
        if self._devices_label is None or not self._devices_label.winfo_exists():
            return
        count = len(self.app.network_map)
        self._devices_label.configure(text=str(count), text_color=COLORS["primary"])

    def _update_home_stats(self):
        lbl = self._stat_labels.get("devices")
        if lbl is not None and lbl.winfo_exists():
            lbl.configure(text=str(len(self.app.network_map)))

    def _refresh_home_preview(self):
        if not hasattr(self, "_home_preview_scroll") or not self._home_preview_scroll.winfo_exists():
            return

        alerts = list(self.app.alerts_list)
        order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        alerts.sort(key=lambda a: (order.get(a.get("severity", "Low"), 9), a.get("time", "")), reverse=True)
        top3 = alerts[:3]

        # Diff + update
        current = set((a.get("ssid",""), a.get("rogue_mac",""), a.get("legit_mac",""), a.get("type","")) for a in top3)
        existing = set(self._alert_widgets.keys())

        for key in existing - current:
            w = self._alert_widgets.pop(key)
            if w.winfo_exists():
                w.destroy()

        for alert in top3:
            key = (alert.get("ssid",""), alert.get("rogue_mac",""), alert.get("legit_mac",""), alert.get("type",""))
            if key in self._alert_widgets:
                continue  # compact widgets not updated live; good enough
            self._create_alert_widget(key, alert, compact=True)
            self._alert_widgets[key] = None  # mark exists

        # Empty state
        if not top3:
            for w in self._home_preview_scroll.winfo_children():
                w.destroy()
            ctk.CTkLabel(
                self._home_preview_scroll,
                text="🛡️  No alerts — your network is secure",
                font=ctk.CTkFont(size=16), text_color=COLORS["text_muted"]
            ).pack(pady=40)

    # ═══════════════════════════════════════════════════════════════════════════
    # ALERTS TAB
    # ═══════════════════════════════════════════════════════════════════════════
    def _alert(self):
        container = self._make_container()

        # Header with count
        count_lbl = ctk.CTkLabel(
            container, text="",
            font=ctk.CTkFont(size=15), text_color=COLORS["text_muted"]
        )
        def make_header():
            self._make_header(container, "Security Alerts", count_lbl)
        make_header()

        # Scrollable full list
        container.grid_rowconfigure(1, weight=1)
        self._alerts_scroll = ctk.CTkScrollableFrame(
            container, fg_color="transparent",
            scrollbar_button_color="#2a2a4a", scrollbar_button_hover_color="#3a3a5a"
        )
        self._alerts_scroll.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        self._alerts_scroll.grid_columnconfigure(0, weight=1)

        self._refresh_alerts()

    def _refresh_alerts(self):
        if not hasattr(self, "_alerts_scroll") or not self._alerts_scroll.winfo_exists():
            return

        alerts = list(self.app.alerts_list)
        # Update count badge in header (find it)
        for w in self._alerts_scroll.master.winfo_children():
            if isinstance(w, ctk.CTkFrame) and w.grid_info().get("row") == 0:
                for sub in w.winfo_children():
                    if isinstance(sub, ctk.CTkLabel) and "alert" in sub.cget("text").lower():
                        sub.configure(text=f"{len(alerts)} alert(s)")
                        break

        order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        alerts.sort(key=lambda a: (order.get(a.get("severity", "Low"), 9), a.get("time", "")), reverse=True)

        current_keys = set()
        for alert in alerts:
            key = (alert.get("ssid",""), alert.get("rogue_mac",""), alert.get("legit_mac",""), alert.get("type",""))
            current_keys.add(key)
            if key in self._alert_widgets:
                continue  # full widgets not live-updated; acceptable
            self._create_alert_widget(key, alert, compact=False)
            self._alert_widgets[key] = None

        for key in set(self._alert_widgets.keys()) - current_keys:
            w = self._alert_widgets.pop(key)
            if w and w.winfo_exists():
                w.destroy()

        # Empty state
        if not alerts:
            for w in self._alerts_scroll.winfo_children():
                w.destroy()
            ctk.CTkLabel(
                self._alerts_scroll,
                text="🛡️  No alerts recorded — your network looks secure",
                font=ctk.CTkFont(size=16), text_color=COLORS["text_muted"]
            ).pack(pady=60)

    # ═══════════════════════════════════════════════════════════════════════════
    # LIVE UPDATE ROUTER
    # ═══════════════════════════════════════════════════════════════════════════
    def _live_update(self):
        if not self.winfo_exists():
            return
        try:
            if self.page == "home":
                self._update_home_stats()
                self._update_security_status()
                self._refresh_home_preview()
            elif self.page == "alert":
                self._refresh_alerts()
        except Exception:
            pass
        self.after(1000, self._live_update)