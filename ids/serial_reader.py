import serial
import threading
import json
import time

class SerialReader:
    def __init__(self, callback):
        self.serial = None
        self.thread = None
        self.running = False
        self.callback = callback

    def connect(self, port, baudrate):
        try:
            self.serial = serial.Serial(port, baudrate, timeout=1)
            self.running = True
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()
            return True
        except Exception as e:
            print(f"Error connecting to serial: {e}")
            return False

    def disconnect(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.serial and self.serial.is_open:
            self.serial.close()

    def read_loop(self):
        while self.running and self.serial and self.serial.is_open:
            try:
                line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            packet_data = json.loads(line)
                            self.callback(packet_data)
                        except json.JSONDecodeError:
                            print(f"Failed to parse JSON: {line}")
                    else:
                        # General debug output from ESP32
                        print(f"ESP32: {line}")
            except Exception as e:
                print(f"Serial read error: {e}")
                time.sleep(1)
