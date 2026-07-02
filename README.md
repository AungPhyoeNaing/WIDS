# Sentinel WIDS (Wi-Fi Intrusion Detection System)

Sentinel WIDS is a host-based Wi-Fi Intrusion Detection System that leverages a dual-component architecture: an **ESP32 microcontroller** acting as an over-the-air raw packet sniffer, and a **Python desktop application** featuring a modern dashboard for real-time traffic analysis and threat detection.

## Features
- **Raw Packet Sniffing:** Utilizes ESP32 promiscuous mode to capture 802.11 management frames (Deauthentication, Probes, Beacons, etc.) across the 2.4GHz spectrum via automatic channel hopping.
- **Hardware Decoupling:** Implements FreeRTOS queues on the ESP32 to safely buffer packets and prevent Watchdog Timer (WDT) crashes during heavy Wi-Fi traffic.
- **Real-Time Dashboard:** A premium, dark-themed UI built with CustomTkinter.
- **Live Traffic Stream:** Visualizes live packets with color-coded tagging (e.g., Red for Deauths, Purple for Probes).
- **Dynamic Statistics:** Live counters for Total Packets, Deauth Frames, and Alerts Triggered.

## Hardware Requirements
- **ESP32 Development Board** (e.g., ESP32-WROOM-32, ESP32 Dev Module).
- Micro-USB or USB-C cable capable of data transfer.
- A host PC running Windows, macOS, or Linux.

## Software Requirements
- **Arduino IDE** (or VS Code with PlatformIO) to flash the ESP32.
- **Python 3.8+** installed on the host PC.

## Installation & Setup

### 1. Flash the ESP32 Sniffer
1. Open the file `esp32_sniffer/esp32_sniffer.ino` in the Arduino IDE.
2. Ensure you have the ESP32 board package installed (`Tools > Board > Board Manager`).
3. Select your board (e.g., **ESP32 Dev Module**) from the `Tools > Board` menu.
4. Apply the following settings in the `Tools` menu to ensure a stable flash:
   - **Upload Speed:** `115200`
   - **Flash Frequency:** `40MHz`
5. Connect your ESP32, select its COM port, and click **Upload**. *(Note: If the upload hangs at `Connecting...`, press and hold the physical `BOOT` button on the ESP32 until the progress percentage begins).*

### 2. Set Up the Python Host Environment
1. Open a terminal in the root directory of this project (`WIDS`).
2. Install the required Python dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```
   *(This installs `customtkinter` and `pyserial`)*

## Usage
1. Keep the ESP32 plugged into your PC via USB. Make sure no other programs (like the Arduino Serial Monitor) are currently using the COM port.
2. Launch the dashboard by running:
   ```bash
   python main.py
   ```
3. In the sidebar of the UI, enter the COM port corresponding to your ESP32 (e.g., `COM5` on Windows, or `/dev/ttyUSB0` on Linux/Mac).
4. Ensure the Baud Rate is set to `115200`.
5. Click **CONNECT**. 
6. The dashboard will immediately begin displaying real-time 802.11 management frames in the Live Traffic Stream.

## Project Structure
```text
WIDS/
├── esp32_sniffer/
│   └── esp32_sniffer.ino   # ESP32 C++ firmware (FreeRTOS optimized)
├── gui/
│   └── app.py              # CustomTkinter UI implementation
├── ids/
│   └── serial_reader.py    # Background thread for parsing Serial JSON data
├── main.py                 # Main entry point for the Python application
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

## Disclaimer
This project is developed for educational, defensive, and network analysis purposes only. Do not use this tool to monitor networks you do not own or do not have explicit authorization to monitor.
