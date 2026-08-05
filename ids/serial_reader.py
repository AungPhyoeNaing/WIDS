import serial
import threading
import json
import time
import logging

logger = logging.getLogger(__name__)

class SerialReader:
    def __init__(self, callback):
        self.serial = None
        self.thread = None
        self.running = False
        self.callback = callback

    def connect(self, port, baudrate):
        try:
            self.serial = serial.Serial(port, baudrate, timeout=2)
            self.serial.reset_input_buffer()
            time.sleep(0.3)
            # Non-fatal initial check
            try:
                initial_line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                if initial_line:
                    logger.info(f"Serial data received on {port}: {initial_line[:120]}")
                else:
                    logger.info(f"Port {port} connected (waiting for serial data stream...)")
            except Exception:
                logger.info(f"Port {port} connected")

            self.running = True
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()
            return True
        except Exception as e:
            logger.error(f"Error connecting to serial: {e}")
            return False

    def send_command(self, cmd_dict):
        if self.serial and self.serial.is_open:
            try:
                cmd_str = json.dumps(cmd_dict) + "\n"
                self.serial.write(cmd_str.encode('utf-8'))
                logger.info(f"Sent command to ESP32: {cmd_str.strip()}")
                return True
            except Exception as e:
                logger.error(f"Error sending command to ESP32: {e}")
        return False

    def disconnect(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
            except serial.SerialException:
                pass

    def read_loop(self):
        retries = 0
        backoff = [1, 2, 4, 8, 16]
        while self.running:
            if not self.serial or not self.serial.is_open:
                time.sleep(1)
                continue
                
            try:
                line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            packet_data = json.loads(line)
                            self.callback(packet_data)
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON: {line}")
                    else:
                        # General debug output from ESP32
                        logger.info(f"ESP32: {line}")
                retries = 0  # reset on success
            except Exception as e:
                logger.error(f"Serial read error: {e}")
                if self.running:
                    try:
                        self.serial.close()
                    except Exception:
                        pass
                    
                    while self.running and retries < len(backoff):
                        time.sleep(backoff[retries])
                        retries += 1
                        try:
                            logger.info(f"Attempting to reconnect (attempt {retries})...")
                            self.serial.open()
                            logger.info("Reconnected successfully.")
                            break
                        except Exception as reconnect_err:
                            logger.error(f"Reconnect failed: {reconnect_err}")
                    
                    if retries >= len(backoff):
                        logger.error("Max retries reached, giving up.")
                        self.running = False
                else:
                    time.sleep(1)
