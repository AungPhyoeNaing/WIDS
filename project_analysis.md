# Wireless Intrusion Detection System (WIDS) - Project Analysis

## Overview
This project implements a hybrid **Wireless Intrusion Detection System (WIDS)**. It leverages an ESP32 microcontroller as a hardware packet sniffer and a Python-based desktop application for data processing, packet inspection, and user interface.

## Technology Stack
- **Hardware Controller**: C++/Arduino (`esp32_sniffer.ino`) for the ESP32 microcontroller.
- **Backend Core**: Python 3
- **Network Processing**: 
  - `scapy`: Used for local network packet manipulation (ARP sniffing).
  - `pyserial`: Used for serial communication with the ESP32.
- **Graphical User Interface (GUI)**:
  - `customtkinter`: A modern and customizable UI library based on Tkinter.
  - `pillow`: For image processing in the UI (e.g., handling `wids_logo.jpg`).

## Project Architecture & Structure

The codebase follows a modular MVC-like architecture, glued together by `main.py`.

### 1. Main Entry Point (`main.py`)
- Acts as the central `Controller`.
- Initializes the `SerialReader` (hardware sniffer) and `ARPSniffer` (local network sniffer).
- Initializes the `App` (GUI).
- Routes packets received from the sniffers to the GUI for display and analysis.

### 2. Intrusion Detection System (`ids/` directory)
This module handles the core networking and data ingestion.
- `serial_reader.py`: Manages the serial connection to the ESP32 to read captured 802.11 frames over Wi-Fi.
- `arp_sniffer.py`: Utilizes `scapy` to capture and inspect ARP packets directly on the host machine's network interface.
- `whitelist.json`: A configuration file likely used to define known/trusted MAC addresses to filter out false positives.
- `theme_pref.json`: Saves user theme preferences.

### 3. Graphical User Interface (`gui/` directory)
This module contains the frontend components built with `customtkinter`.
- `app.py`: The main window and primary application logic for the UI. It's the largest file (65KB) and likely contains the dashboard, packet lists, and alert displays.
- `user_view.py`: Contains a specialized view, potentially for a normal user mode versus an admin mode, or specific data visualization.
- `theme.py`: Defines the visual aesthetics (colors, fonts, styles) of the custom tkinter components.
- `wids_logo.jpg`: Application logo asset.

### 4. Hardware Sniffer (`esp32_sniffer/` directory)
- `esp32_sniffer.ino`: The Arduino sketch that flashes onto the ESP32. It puts the ESP32's Wi-Fi interface into promiscuous mode to capture raw 802.11 management/data frames and forwards them over the Serial port to the Python application.

## Key Takeaways
- The project elegantly splits the workload: raw wireless sniffing is offloaded to inexpensive ESP32 hardware, while complex analysis and UI are handled by a Python desktop app.
- It seems capable of analyzing both local network threats (via ARP spoofing detection) and wireless threats (via 802.11 management frame analysis from the ESP32).
