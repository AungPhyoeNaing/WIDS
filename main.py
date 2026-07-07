from gui.app import App
from ids.serial_reader import SerialReader

class Controller:
    def __init__(self):
        self.serial_reader = SerialReader(self.on_packet_received)
        self.app = App(self.start_serial, self.stop_serial)

    def start_serial(self, port, baud):
        return self.serial_reader.connect(port, baud)

    def stop_serial(self):
        self.serial_reader.disconnect()

    def on_packet_received(self, packet):
        # The GUI now uses a thread-safe queue internally
        self.app.add_packet(packet)

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    controller = Controller()
    controller.run()
