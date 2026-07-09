from gui.app import App
from ids.serial_reader import SerialReader
from ids.arp_sniffer import ARPSniffer

class Controller:
    def __init__(self):
        self.serial_reader = SerialReader(self.on_packet_received)
        self.arp_sniffer = ARPSniffer(self.on_packet_received)
        self.arp_sniffer.start()
        self.app = App(self.start_serial, self.stop_serial)

    def start_serial(self, port, baud):
        return self.serial_reader.connect(port, baud)

    def stop_serial(self):
        self.serial_reader.disconnect()

    def on_packet_received(self, packet):
        self.app.add_packet(packet)

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    controller = Controller()
    controller.run()
