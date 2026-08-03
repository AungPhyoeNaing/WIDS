import logging
import signal
import sys
from gui.app import App
from ids.serial_reader import SerialReader
from ids.arp_sniffer import ARPSniffer
from ids.gateway_resolver import GatewayResolver

# Configure logging for gateway resolver output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)

class Controller:
    def __init__(self):
        # Initialize the gateway resolver first (dynamic gateway detection)
        self.gateway_resolver = GatewayResolver()
        self.gateway_resolver.resolve()

        # Pass gateway_resolver to ARP sniffer for gateway-aware detection
        self.serial_reader = SerialReader(self.on_packet_received)
        self.arp_sniffer = ARPSniffer(self.on_packet_received, self.gateway_resolver)
        
        # Initialize app BEFORE starting the sniffers to avoid AttributeError
        # if a packet is received immediately
        self.app = App(self.start_serial, self.stop_serial)

        self.arp_sniffer.start()

        # Start subnet scan in background (duplicate MAC detection)
        self.gateway_resolver.scan_subnet_async()

        # Log gateway info at startup
        gw_info = self.gateway_resolver.get_gateway_info()
        if gw_info["gateway_ip"]:
            print(f"[+] Gateway: {gw_info['gateway_ip']} -> {gw_info['gateway_mac']}")
            print(f"   Vendor: {gw_info['vendor']} ({gw_info['vendor_category']})")
            print(f"   Confidence: {gw_info['confidence']}")

    def start_serial(self, port, baud):
        return self.serial_reader.connect(port, baud)

    def stop_serial(self):
        self.serial_reader.disconnect()

    def on_packet_received(self, packet):
        # Feed ESP32 Beacon BSSIDs to the gateway resolver for cross-referencing
        if (packet.get("type") == "Management"
                and packet.get("subtype") == "Beacon"):
            bssid = packet.get("bssid")
            if bssid:
                self.gateway_resolver.verify_with_bssid(bssid)

        self.app.add_packet(packet)

    def shutdown(self):
        """Gracefully stop all background threads."""
        logging.info("Shutting down WIDS...")
        self.arp_sniffer.stop()
        self.serial_reader.disconnect()
        logging.info("WIDS shutdown complete.")

    def run(self):
        # Register the cleanup for when the Tk window is closed
        self.app.protocol("WM_DELETE_WINDOW", self._on_close)
        self.app.mainloop()

    def _on_close(self):
        """Handle window close: stop threads, then destroy GUI."""
        self.shutdown()
        self.app.destroy()

if __name__ == "__main__":
    controller = Controller()
    
    # Handle Ctrl+C gracefully
    def _signal_handler(sig, frame):
        controller.shutdown()
        sys.exit(0)
    signal.signal(signal.SIGINT, _signal_handler)
    
    controller.run()
