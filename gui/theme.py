import os
import json
import customtkinter as ctk

DARK_THEME = {
    "bg_root": "#09090b",
    "bg_sidebar": "#18181b",
    "bg_card": "#18181b",
    "bg_elevated": "#27272a",
    "bg_input": "#27272a",
    "border": "#27272a",
    
    "text_heading": "#f4f4f5",
    "text_body": "#e4e4e7",
    "text_muted": "#a1a1aa",
    "text_dim": "#71717a",
    "text_dark_only": "#18181b", # used for things that need to contrast in light mode
    
    "primary": "#3b82f6",
    "primary_hover": "#2563eb",
    "success": "#10b981",
    "success_hover": "#059669",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "danger_hover": "#dc2626",
    "accent": "#6c63ff",
    "accent_hover": "#5a52d5",
    
    "btn_pause_fg": "#3f3f46",
    "btn_pause_hover": "#27272a",
    "btn_clear_fg": "#b91c1c",
    "btn_clear_hover": "#991b1b",
    
    "tree_bg": "#18181b",
    "tree_odd_bg": "#18181b",
    "tree_even_bg": "#222226",
    "tree_header_bg": "#27272a",
    "tree_header_fg": "#a1a1aa",
    "tree_fg": "#e4e4e7",
    "tree_selected": "#3b82f6",
    "tree_border": "#18181b",
    
    "tag_deauth": "#ef4444",
    "tag_probe": "#8b5cf6",
    "tag_beacon": "#71717a",
    
    "tag_eviltwin_high_fg": "#ef4444",
    "tag_eviltwin_high_bg": "#3b0b0b",
    "tag_eviltwin_medium_fg": "#f97316",
    "tag_eviltwin_medium_bg": "#2d1500",
    "tag_eviltwin_low_fg": "#eab308",
    "tag_eviltwin_low_bg": "#2d2600",
    "tag_arp_spoof_fg": "#ef4444",
    "tag_arp_spoof_bg": "#1a0a2e",
    
    "alert_stripe_critical": "#ef4444",
    "alert_stripe_high": "#f97316",
    "alert_stripe_medium": "#eab308",
    "alert_stripe_low": "#3b82f6",
    "alert_inner": "#1c1c1f",
    
    "scrollbar": "#2a2a4a",
    "scrollbar_hover": "#3a3a5a",
    "trust_btn_fg": "#166534",
    "trust_btn_hover": "#14532d",
    
    "status_disconnected": "#ef4444",
    "status_connected": "#10b981",
    "status_trying": "#f59e0b",
    
    "user_view_text_muted": "#d4d4d8", # Slightly brighter for user view
}

LIGHT_THEME = {
    "bg_root": "#e2e8f0",      # Slate 200
    "bg_sidebar": "#cbd5e1",   # Slate 300
    "bg_card": "#f8fafc",      # Slate 50 (instead of pure white)
    "bg_elevated": "#cbd5e1",  # Slate 300
    "bg_input": "#cbd5e1",
    "border": "#94a3b8",       # Slate 400
    
    "text_heading": "#020617", # Slate 950
    "text_body": "#0f172a",    # Slate 900
    "text_muted": "#334155",   # Slate 700 (much higher contrast than 500)
    "text_dim": "#475569",     # Slate 600
    "text_dark_only": "#ffffff",
    
    "primary": "#1d4ed8",      # Blue 700
    "primary_hover": "#1e3a8a",# Blue 900
    "success": "#047857",      # Emerald 700
    "success_hover": "#064e3b",# Emerald 900
    "warning": "#b45309",      # Amber 700
    "danger": "#b91c1c",       # Red 700
    "danger_hover": "#7f1d1d", # Red 900
    "accent": "#4338ca",       # Indigo 700
    "accent_hover": "#312e81", # Indigo 900
    
    "btn_pause_fg": "#94a3b8",
    "btn_pause_hover": "#64748b",
    "btn_clear_fg": "#dc2626",
    "btn_clear_hover": "#b91c1c",
    
    "tree_bg": "#f8fafc",      # Slate 50
    "tree_odd_bg": "#f8fafc",
    "tree_even_bg": "#f1f5f9", # Slate 100
    "tree_header_bg": "#cbd5e1",# Slate 300
    "tree_header_fg": "#1e293b",# Slate 800
    "tree_fg": "#0f172a",      # Slate 900
    "tree_selected": "#bfdbfe",# Blue 200
    "tree_border": "#94a3b8",  # Slate 400
    
    "tag_deauth": "#b91c1c",
    "tag_probe": "#6d28d9",
    "tag_beacon": "#475569",
    
    "tag_eviltwin_high_fg": "#7f1d1d",
    "tag_eviltwin_high_bg": "#fecaca",
    "tag_eviltwin_medium_fg": "#7c2d12",
    "tag_eviltwin_medium_bg": "#fed7aa",
    "tag_eviltwin_low_fg": "#713f12",
    "tag_eviltwin_low_bg": "#fde68a",
    "tag_arp_spoof_fg": "#7f1d1d",
    "tag_arp_spoof_bg": "#e9d5ff",
    
    "alert_stripe_critical": "#b91c1c",
    "alert_stripe_high": "#c2410c",
    "alert_stripe_medium": "#b45309",
    "alert_stripe_low": "#1d4ed8",
    "alert_inner": "#f1f5f9",  # Slate 100
    
    "scrollbar": "#94a3b8",
    "scrollbar_hover": "#64748b",
    "trust_btn_fg": "#15803d",
    "trust_btn_hover": "#166534",
    
    "status_disconnected": "#b91c1c",
    "status_connected": "#047857",
    "status_trying": "#b45309",
    
    "user_view_text_muted": "#1e293b",
}

class ThemeManager:
    _current = "dark"
    _listeners = []
    _pref_path = os.path.join(os.path.dirname(__file__), "..", "ids", "theme_pref.json")

    @classmethod
    def init(cls):
        try:
            os.makedirs(os.path.dirname(cls._pref_path), exist_ok=True)
            if os.path.exists(cls._pref_path):
                with open(cls._pref_path, "r") as f:
                    pref = json.load(f)
                    cls._current = pref.get("theme", "dark")
        except Exception:
            cls._current = "dark"
        ctk.set_appearance_mode(cls._current)

    @classmethod
    def get(cls, key: str) -> str:
        palette = LIGHT_THEME if cls._current == "light" else DARK_THEME
        return palette.get(key, "#ff00ff") # magenta fallback to easily spot missing keys

    @classmethod
    def toggle(cls):
        cls._current = "light" if cls._current == "dark" else "dark"
        ctk.set_appearance_mode(cls._current)
        try:
            with open(cls._pref_path, "w") as f:
                json.dump({"theme": cls._current}, f)
        except Exception:
            pass
            
        for listener in cls._listeners:
            listener()

    @classmethod
    def on_change(cls, callback):
        cls._listeners.append(callback)

    @classmethod
    def is_dark(cls) -> bool:
        return cls._current == "dark"
