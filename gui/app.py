import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from datetime import datetime

class App(ctk.CTk):
    def __init__(self, start_serial_cb, stop_serial_cb):
        super().__init__()
        
        self.title("Sentinel WIDS - Dashboard")
        self.geometry("1100x700")
        
        # Premium dark mode theme
        ctk.set_appearance_mode("dark")
        
        self.start_serial_cb = start_serial_cb
        self.stop_serial_cb = stop_serial_cb
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Stats
        self.total_packets = 0
        self.deauth_count = 0
        self.alert_count = 0
        
        self.create_sidebar()
        self.create_main_content()
        
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#18181b") # Zinc 900
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🛡️ Sentinel WIDS", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        self.com_port_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="COM Port (e.g. COM5)", height=45, font=ctk.CTkFont(size=14))
        self.com_port_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.baud_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Baud Rate", height=45, font=ctk.CTkFont(size=14))
        self.baud_entry.insert(0, "115200")
        self.baud_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.connect_btn = ctk.CTkButton(
            self.sidebar_frame, text="CONNECT", height=45, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            fg_color="#3b82f6", hover_color="#2563eb", # Blue 500
            command=self.toggle_connection
        )
        self.connect_btn.grid(row=3, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Connection status indicator
        self.status_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#27272a", corner_radius=8, height=45)
        self.status_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.status_frame.pack_propagate(False)
        self.status_label = ctk.CTkLabel(self.status_frame, text="● Disconnected", text_color="#ef4444", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(expand=True)
        
        self.is_connected = False

    def create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#09090b", corner_radius=0) # Zinc 950
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Dashboard Stats Bar (Top)
        self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.stats_frame.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        self.stats_frame.grid_columnconfigure((0,1,2), weight=1)
        
        self.stat_packets = self.create_stat_card(self.stats_frame, "TOTAL PACKETS", "0", 0, "#10b981") # Emerald 500
        self.stat_deauth = self.create_stat_card(self.stats_frame, "DEAUTH FRAMES", "0", 1, "#f59e0b") # Amber 500
        self.stat_alerts = self.create_stat_card(self.stats_frame, "ALERTS TRIGGERED", "0", 2, "#ef4444") # Red 500
        
        # Log frame (Bottom)
        self.log_frame = ctk.CTkFrame(self.main_frame, fg_color="#18181b", corner_radius=12)
        self.log_frame.grid(row=1, column=0, padx=30, pady=(10, 30), sticky="nsew")
        self.log_frame.grid_rowconfigure(1, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self.log_frame, text="Live Traffic Stream", font=ctk.CTkFont(size=18, weight="bold"), text_color="#f4f4f5")
        self.title_label.grid(row=0, column=0, padx=25, pady=20, sticky="w")
        
        # Themed Treeview for dark mode
        style = ttk.Style()
        style.theme_use("default")
        
        # Modern Treeview Styling
        bg_color = "#18181b"
        header_color = "#27272a"
        text_color = "#a1a1aa"
        selected_bg = "#3b82f6"
        
        style.configure("Treeview", 
                        background=bg_color,
                        foreground="#e4e4e7",
                        rowheight=35,
                        fieldbackground=bg_color,
                        bordercolor=bg_color,
                        borderwidth=0,
                        font=("Helvetica", 11))
                        
        style.map('Treeview', background=[('selected', selected_bg)])
        
        style.configure("Treeview.Heading", 
                        background=header_color,
                        foreground=text_color,
                        relief="flat",
                        font=("Helvetica", 11, "bold"))
                        
        style.map("Treeview.Heading", background=[('active', '#3f3f46')])

        self.tree = ttk.Treeview(self.log_frame, columns=("time", "rssi", "ch", "src", "dst", "subtype"), show="headings")
        self.tree.heading("time", text="TIME")
        self.tree.heading("rssi", text="RSSI")
        self.tree.heading("ch", text="CH")
        self.tree.heading("src", text="SOURCE MAC")
        self.tree.heading("dst", text="DESTINATION MAC")
        self.tree.heading("subtype", text="FRAME SUBTYPE")
        
        self.tree.column("time", width=120, anchor="center")
        self.tree.column("rssi", width=70, anchor="center")
        self.tree.column("ch", width=50, anchor="center")
        self.tree.column("src", width=170, anchor="center")
        self.tree.column("dst", width=170, anchor="center")
        self.tree.column("subtype", width=190, anchor="w")

        self.tree.grid(row=1, column=0, padx=(25,0), pady=(0, 25), sticky="nsew")
        
        self.scrollbar = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=1, padx=(0,25), pady=(0,25), sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Setup tags for color coding rows
        self.tree.tag_configure("deauth", foreground="#ef4444")
        self.tree.tag_configure("probe", foreground="#8b5cf6")
        
        self.max_rows = 500

    def create_stat_card(self, parent, title, value, col, highlight_color):
        card = ctk.CTkFrame(parent, fg_color="#18181b", corner_radius=12, height=110)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        card.grid_propagate(False)
        card.grid_rowconfigure((0,1), weight=1)
        card.grid_columnconfigure(0, weight=1)
        
        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa")
        title_lbl.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        
        val_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=36, weight="bold"), text_color=highlight_color)
        val_lbl.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        return val_lbl

    def toggle_connection(self):
        if not self.is_connected:
            port = self.com_port_entry.get().strip()
            baud = self.baud_entry.get().strip()
            if port and baud:
                success = self.start_serial_cb(port, int(baud))
                if success:
                    self.is_connected = True
                    self.connect_btn.configure(text="DISCONNECT", fg_color="#ef4444", hover_color="#dc2626")
                    self.status_label.configure(text=f"● Connected to {port}", text_color="#10b981")
                else:
                    self.status_label.configure(text="● Connection Failed", text_color="#ef4444")
        else:
            self.stop_serial_cb()
            self.is_connected = False
            self.connect_btn.configure(text="CONNECT", fg_color="#3b82f6", hover_color="#2563eb")
            self.status_label.configure(text="● Disconnected", text_color="#ef4444")

    def add_packet(self, packet):
        self.total_packets += 1
        self.stat_packets.configure(text=str(self.total_packets))
        
        subtype = packet.get('subtype', '')
        tags = ()
        
        if subtype == "Deauthentication":
            self.deauth_count += 1
            self.stat_deauth.configure(text=str(self.deauth_count))
            tags = ("deauth",)
            
            # Temporary logic to increment alerts if we see Deauths
            if self.deauth_count % 10 == 0:
                self.alert_count += 1
                self.stat_alerts.configure(text=str(self.alert_count))
                
        elif subtype == "Probe Request":
            tags = ("probe",)
            
        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        values = (
            current_time,
            f"{packet.get('rssi', '')} dBm",
            packet.get('channel', ''),
            packet.get('mac_src', ''),
            packet.get('mac_dst', ''),
            subtype
        )
        self.tree.insert("", "0", values=values, tags=tags)
        
        children = self.tree.get_children()
        if len(children) > self.max_rows:
            self.tree.delete(children[-1])
