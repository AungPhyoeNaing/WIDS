# Wireless Intrusion Detection System (WIDS)

## Overview
WIDS (Wireless Intrusion Detection System) is a hybrid hardware-software cybersecurity project designed to monitor, detect, and alert users of wireless network attacks in real-time. It acts as a digital bodyguard for your Wi-Fi network by passively sniffing 802.11 management frames and actively monitoring ARP traffic on the local subnet.

## Features
- **Deauthentication Attack Detection:** Identifies forged deauthentication frames aimed at disconnecting clients. It uses a scoring algorithm based on packet bursts, fixed timing intervals, and broadcast destinations.
- **Evil Twin Detection:** Remembers the MAC address (BSSID) of your legitimate Wi-Fi network and instantly flags any rogue Access Point broadcasting the same SSID with a different BSSID.
- **ARP Spoofing / Man-in-the-Middle Detection:** Dynamically resolves the default gateway MAC address and cross-references it with hardware-verified BSSIDs. Scans the local subnet for duplicate MAC addresses to identify spoofing attempts.
- **Hardware-Level Audio Alerts:** Utilizes an I2S Audio Module (MAX98357A) connected to the ESP32 to play physical audio alarms and warnings when an attack is detected.
- **Real-Time GUI:** A modern, visually appealing graphical user interface built with CustomTkinter that displays network traffic, active threats, and detailed attack logs.

## Architecture

The project is split into two main components:

### 1. Hardware Sniffer (ESP32)
Located in the `esp32_sniffer/` directory.
- **Microcontroller:** ESP32 (configured in Promiscuous / Monitor mode).
- **Audio Output:** MAX98357A I2S Amplifier for audio alerts.
- **Functionality:** 
  - Rapidly hops through Wi-Fi channels (1-13).
  - Captures 802.11 Management Frames (Beacons, Probes, Deauths, etc.).
  - Filters out weak signals and forwards relevant packet data via Serial to the host computer in JSON format.
  - Receives serial commands from the host computer to trigger specific audio tracks (e.g., Deauth Alarm, Evil Twin Alarm).

### 2. Software Backend & GUI (Python)
Located in the `ids/` and `gui/` directories.
- **IDS Engine (`ids/`):**
  - `serial_reader.py`: Interfaces with the ESP32 to parse incoming JSON packets.
  - `deauth_detector.py`: Analyzes deauth packet rates and targets to identify DoS attacks.
  - `arp_sniffer.py`: Uses `scapy` to sniff local network traffic for ARP anomalies.
  - `gateway_resolver.py`: Resolves and verifies the true gateway MAC to prevent ARP spoofing.
  - `wifi_memory.py`: Stores legitimate Wi-Fi configurations to defend against Evil Twin attacks.
- **Graphical Interface (`gui/`):** Built with `customtkinter` to provide a dashboard containing packet logs, alert feeds, and network statistics.

## Project Structure
```text
WIDS/
├── esp32_sniffer/
│   ├── esp32_sniffer.ino   # Arduino code for ESP32 packet sniffing and I2S audio
│   └── audio_data.h        # Hexadecimal PCM audio data for I2S playback
├── ids/
│   ├── arp_sniffer.py      # Scapy-based ARP spoofing detection
│   ├── deauth_detector.py  # Algorithm for identifying deauth floods
│   ├── gateway_resolver.py # Dynamic gateway resolution and subnet scanning
│   ├── wifi_memory.py      # Evil Twin reference storage
│   ├── serial_reader.py    # ESP32 serial communication handler
│   └── oui_lookup.py       # MAC Address Vendor lookup utilities
├── gui/
│   ├── app.py              # Main CustomTkinter application logic
│   └── theme.py            # UI theming configurations
├── logs/                   # Directory for storing application and alert logs
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── README.md               # This documentation file
```

## Prerequisites

### Hardware Requirements
- ESP32 Development Board
- MAX98357A I2S Audio Amplifier Module
- Speaker (4Ω or 8Ω)
- Micro-USB / USB-C Cable for data transfer

### Software Requirements
- Python 3.8 or higher
- Npcap (Windows) or libpcap (Linux/macOS) for Scapy to function properly.
- Arduino IDE (to flash the ESP32) with ESP32 board definitions installed.

## Installation & Setup

### 1. Flash the ESP32
1. Open `esp32_sniffer/esp32_sniffer.ino` in the Arduino IDE.
2. Install necessary libraries if prompted.
3. Connect your ESP32 to the computer.
4. Select the correct COM port and ESP32 Dev Module as the board.
5. Compile and upload the code to the ESP32.

### 2. Set up the Python Environment
1. Navigate to the project root directory.
2. (Optional) Create a virtual environment: `python -m venv venv` and activate it.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Run the Application
1. Ensure the ESP32 is connected via USB.
2. Run the main Python script:
   ```bash
   python main.py
   ```
3. Use the GUI to select the correct COM port and connect to the ESP32.

## Disclaimer
This project is developed for educational and defensive purposes only. Do not use this tool on networks you do not own or have explicit permission to monitor.
