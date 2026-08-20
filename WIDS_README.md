# Sentinel WIDS — The Complete Beginner & Architecture Guide

> **Hello!** This guide assumes zero prior knowledge about Wi-Fi security, ESP32 microcontrollers, or Python.  
> We explain *everything* from scratch, covering the complete hardware-software architecture, intrusion detection algorithms, dual-view GUI dashboard, hardware audio alerts, and project codebase. If you get stuck on any term, check the [Glossary](#16-complete-glossary-a-z).

---

## 📖 Table of Contents

| Section | What You'll Learn |
|---------|-------------------|
| [1. The One-Paragraph Summary](#1-the-one-paragraph-summary) | High-level system overview in 3 sentences |
| [2. What Is Wi-Fi? (The 5-Minute Crash Course)](#2-what-is-wi-fi-the-5-minute-crash-course) | How 802.11 Wi-Fi networks and packets work |
| [3. What Attacks Does WIDS Catch?](#3-what-attacks-does-wids-catch) | Evil Twin, Deauth Floods, Probe Sniffing, ARP Spoofing & Gateway Impersonation |
| [4. Hardware Setup & Wiring](#4-hardware-setup--wiring) | ESP32 + MAX98357A I2S DAC Amplifier + Speaker Wiring |
| [5. Complete Setup Guide](#5-complete-setup-guide) | Step-by-step installation for Arduino IDE, Python, and Npcap/Scapy drivers |
| [6. How Data Flows: Air to Screen](#6-how-data-flows-air-to-screen) | Complete packet journey through ISR, FreeRTOS queue, USB serial, IDS engine, and GUI |
| [7. ESP32 Sniffer & Audio Firmware](#7-esp32-sniffer--audio-firmware) | Line-by-line explanation of `esp32_sniffer.ino` & FreeRTOS dual-core I2S audio (`audio_data.h`) |
| [8. Python Intrusion Detection System Engine](#8-python-intrusion-detection-system-engine) | In-depth breakdown of `ids/` backend modules (`serial_reader`, `deauth_detector`, `gateway_resolver`, `arp_sniffer`, `wifi_memory`, `oui_lookup`) |
| [9. Modern Dual-View Dashboard](#9-modern-dual-view-dashboard) | `gui/app.py` (Technician View), `gui/user_view.py` (User View), and `gui/theme.py` (Dark/Light engine) |
| [10. Evil Twin Detection Engine](#10-evil-twin-detection-engine) | Multi-heuristic scoring algorithm & legit Wi-Fi memory matching |
| [11. Deauthentication Attack Detection](#11-deauthentication-attack-detection) | 8-condition rate/burst/timing engine with anti-spam cooldowns |
| [12. ARP Spoofing & Gateway Impersonation](#12-arp-spoofing--gateway-impersonation) | Scapy ARP sniffer, ESP32 hardware BSSID cross-referencing, and subnet MAC scanning |
| [13. Audio Alert System](#13-audio-alert-system) | Dual audio pipeline: ESP32 MAX98357A I2S speaker alarms + Host PC voice alerts (`voice_audios/`) |
| [14. Automated Test Suite](#14-automated-test-suite) | Unit and integration testing (`tests/` directory) |
| [15. Whitelist: Managing False Positives](#15-whitelist-managing-false-positives) | Trusting mesh networks and extenders via `whitelist.json` |
| [16. Complete Glossary (A-Z)](#16-complete-glossary-a-z) | Every cybersecurity, networking, and programming term explained |
| [17. Troubleshooting Guide](#17-troubleshooting-guide) | Practical fixes for serial issues, audio noise, driver permissions, and false alarms |
| [18. File Reference & Project Tree](#18-file-reference--project-tree) | Exhaustive directory tree and file index for the entire repository |

---

## 1. The One-Paragraph Summary

**Sentinel WIDS (Wireless Intrusion Detection System)** turns a **$5 ESP32 chip** and a **MAX98357A I2S audio amplifier** into a real-time digital bodyguard for your Wi-Fi network. The ESP32 passively monitors 802.11 Wi-Fi management traffic across 13 channels and streams JSON packet telemetry over USB to your computer, while simultaneously playing physical voice alerts through an attached speaker when threats are detected. Your computer runs a Python IDS backend with Scapy ARP monitoring, dynamic gateway resolution, and a modern **CustomTkinter Dual-View GUI** (offering both an advanced **Technician View** and a non-technical **User View**) that automatically detects **Evil Twin Access Points**, **Deauthentication DoS Attacks**, and **ARP Spoofing / Man-in-the-Middle Attacks**.

---

## 2. What Is Wi-Fi? (The 5-Minute Crash Course)

### 2.1 Wi-Fi Is Like Walkie-Talkies
Wi-Fi devices communicate via **radio waves** in the 2.4GHz and 5GHz frequency bands. Because radio waves propagate in all directions, anyone with a receiver set to **Promiscuous Mode** can hear packets transmitted nearby.

### 2.2 Device Addresses (MAC Addresses)
Every Wi-Fi interface has a unique 12-character hexadecimal **MAC address** formatted as `AA:BB:CC:DD:EE:FF`.
- **OUI (Organizationally Unique Identifier)**: The first 6 characters (`AA:BB:CC`) identify the hardware vendor (e.g., `50:3E:AA` = TP-Link, `00:03:93` = Apple, `00:1A:2B` = Cisco).
- **NIC Identifier**: The last 6 characters (`DD:EE:FF`) are unique to that specific physical chip.

### 2.3 Network Names (SSID) vs. Router MACs (BSSID)
- **SSID (Service Set Identifier)**: The human-readable name of the network (e.g., "Starbucks_WiFi").
- **BSSID (Basic Service Set Identifier)**: The specific MAC address of the Access Point radio broadcasting that network. Multiple APs in a mesh network can share the same SSID, but each will have a unique BSSID.

### 2.4 Wi-Fi Packets (802.11 Frames)
Wi-Fi data is transmitted in discrete **frames**. Frames contain headers with Source MAC, Destination MAC, BSSID, Signal Strength (RSSI in dBm), and Channel info.

### 2.5 The Three Frame Types

| Type | What It Does | Monitored by ESP32? |
|------|-------------|--------------------|
| **Management** | Network discovery, connection establishment, authentication, deauthentication | **YES** — This is what WIDS analyzes |
| **Control** | Media access control, acknowledgments (ACK, RTS, CTS) | No — Low-level protocol traffic |
| **Data** | Encrypted internet payloads (HTTP, videos, emails) | No — Maintains user privacy |

### 2.6 Critical Management Frame Subtypes

| Subtype # | Name | Description | Security Relevance |
|-----------|------|-------------|--------------------|
| 4 | **Probe Request** | Client device asks "Is network X nearby?" | Exposes device history and location |
| 5 | **Probe Response** | Access Point replies "Yes, I am network X" | Maps local wireless infrastructure |
| 8 | **Beacon** | AP broadcasts "I exist! Join SSID X" | Primary mechanism for Evil Twin detection |
| 10 | **Disassociation** | AP or client terminates session | Can indicate network instability or attack |
| 12 | **Deauthentication** | Forced immediate disconnection order | **Primary vector for Wireless DoS attacks** |

### 2.7 Signal Strength (RSSI in dBm)
**RSSI (Received Signal Strength Indicator)** is measured in decibel-milliwatts (dBm), represented as negative numbers:
- **-30 dBm**: Exceptionally strong (device right next to sniffer)
- **-50 dBm**: Good, strong connection
- **-70 dBm**: Weak connection
- **-85 dBm to -90 dBm**: Barely audible signal boundary

---

## 3. What Attacks Does WIDS Catch?

Sentinel WIDS protects against **four major attack vectors**:

### 3.1 Evil Twin Attack (Rogue Access Point)
- **The Attack**: An attacker configures a rogue Access Point to broadcast an identical SSID to a legitimate network (e.g., "Home_WiFi"). Unwary devices auto-connect to the attacker's stronger signal.
- **The Threat**: Complete Man-in-the-Middle (MITM) compromise: credential sniffing, session hijacking, traffic manipulation, and malware injection.
- **How WIDS Catches It**: WIDS cross-references active SSIDs and BSSIDs against `ids/wifi_memory.py` (which queries Windows `netsh` interface state and stores trusted parameters in `legit_wifi.json`) as well as multi-heuristic checks (RSSI anomalies, channel mismatches, vendor OUI mismatches, and Locally Administered MAC address flags).

### 3.2 Deauthentication DoS Flood
- **The Attack**: An attacker broadcasts forged 802.11 Deauthentication frames (Subtype 12) targeting clients or Access Points.
- **The Threat**: Instantly disconnects target devices from Wi-Fi, rendering security cameras, smart locks, or laptop connections unusable. Often used as a precursor to force devices onto an Evil Twin.
- **How WIDS Catches It**: `ids/deauth_detector.py` evaluates deauth packet rates, untrusted source BSSIDs, broadcast destinations (`FF:FF:FF:FF:FF:FF`), victim counts, reason codes, attack duration, and fixed timing intervals.

### 3.3 ARP Spoofing / Local Subnet MITM
- **The Attack**: An attacker on the local network sends unsolicited ARP responses claiming that the default gateway's IP address belongs to the attacker's MAC address.
- **The Threat**: Reroutes all local LAN internet traffic through the attacker's machine.
- **How WIDS Catches It**: `ids/gateway_resolver.py` dynamically resolves the default gateway IP and MAC, cross-references it with ESP32 over-the-air BSSIDs (`HARDWARE_VERIFIED`), performs vendor OUI heuristics, and conducts background subnet ARP scans (`scan_subnet_async`) to identify duplicate MAC addresses. Simultaneously, `ids/arp_sniffer.py` listens via Scapy for real-time ARP table poison attempts.

### 3.4 Probe Sniffing & Client Tracking
- **The Attack**: Passive eavesdroppers record unencrypted Probe Requests sent by smartphones searching for previously connected Wi-Fi networks.
- **The Threat**: Exposes travel history, preferred places, and physical movements.
- **How WIDS Catches It**: Displays probe activity in real time with client MAC, RSSI, and requested SSIDs.

---

## 4. Hardware Setup & Wiring

Sentinel WIDS combines an ESP32 microcontroller with a hardware I2S audio DAC amplifier for physical audio alerts.

### 4.1 Component List
1. **ESP32 Development Board** (NodeMCU / ESP32 Dev Module, ~$6-8)
2. **MAX98357A I2S Mono DAC Amplifier Module** (~$3-5)
3. **4Ω or 8Ω Micro Speaker** (3W / 5W, ~$2-3)
4. **Breadboard & Jumper Wires**
5. **Micro-USB or USB-C Data Cable** (Must support data transfer, not charge-only)

### 4.2 MAX98357A I2S DAC Amplifier Wiring Diagram

```text
 ┌────────────────────────┐                   ┌────────────────────────┐
 │     ESP32 Dev Board    │                   │   MAX98357A I2S DAC    │
 │                        │                   │                        │
 │                   5V/VIN ├───────────────────┤ VIN                    │
 │                      GND ├───────────────────┤ GND                    │
 │             GPIO 26 (BCK)├───────────────────┤ BCLK (Bit Clock)       │
 │             GPIO 25 (LRC)├───────────────────┤ LRC (Left/Right Clock) │
 │            GPIO 27 (DOUT)├───────────────────┤ DIN (Data In)          │
 └────────────────────────┘                   └───────────┬────────────┘
                                                          │
                                                    ┌─────┴──────┐
                                                    │  SPEAKER   │
                                                    │  (+)  (-)  │
                                                    └────────────┘
```

#### Pin Connections Table

| ESP32 Pin | MAX98357A Pin | Function |
|-----------|---------------|----------|
| **VIN / 5V** | VIN | 5V Power Supply |
| **GND** | GND | Ground |
| **GPIO 26** | BCLK / BCK | Bit Clock |
| **GPIO 25** | LRC / LRCK | Word Select (Left/Right Clock) |
| **GPIO 27** | DIN / DOUT | Serial Data Input |
| *N/A* | SPEAKER OUT (+) (-) | Connected directly to 4Ω/8Ω speaker terminals |

---

## 5. Complete Setup Guide

### Step 1: Install Drivers & Arduino IDE
1. Download and install [Arduino IDE 2.x](https://www.arduino.cc/en/software).
2. Install the **CP210x** or **CH340** USB-to-UART driver for your ESP32 board (if Windows does not assign a COM port automatically).

### Step 2: Configure Arduino IDE for ESP32
1. Open Arduino IDE → **File → Preferences**.
2. Add the following URL to **Additional Boards Manager URLs**:
   ```text
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Open **Tools → Board → Boards Manager**, search for `esp32`, and install **esp32 by Espressif Systems**.

### Step 3: Flash the ESP32 Firmware
1. In Arduino IDE, open `esp32_sniffer/esp32_sniffer.ino`.
2. Connect your ESP32 to your computer via USB.
3. Select **Tools → Board → ESP32 Arduino → ESP32 Dev Module**.
4. Select the corresponding **Tools → Port** (e.g., `COM3`, `COM5`, or `/dev/ttyUSB0`).
5. Click **Upload** (If upload hangs at `Connecting...`, press and hold the physical **BOOT** button on the ESP32 until writing begins).

### Step 4: Install Python & Npcap / Packet Capture Drivers
1. Ensure **Python 3.8+** is installed on your computer.
2. **Windows Users (Crucial for ARP Sniffing)**: Install **Npcap** from [npcap.com](https://npcap.com/). During setup, make sure to check *"Install Npcap in WinPcap API-compatible Mode"*.
3. Open a terminal in the project directory and install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 5: Launch WIDS
```bash
python main.py
```

---

## 6. How Data Flows: Air to Screen

Below is the complete path taken by a Wi-Fi packet from transmission in the air to visualization in the GUI and hardware audio playback:

```text
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ 1. AIRWAVES: Wi-Fi Management Frame (Beacon / Deauth / Probe)           │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ 2. ESP32 HARDWARE RADIO (Promiscuous Mode, Channel Hopping 1-13)        │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ 3. CORE 0 ISR CALLBACK (wifi_promiscuous_cb in esp32_sniffer.ino)       │
 │    - Filters RSSI >= -80 dBm and Management type                          │
 │    - Extracts MACs, BSSID, RSSI, Channel, SSID into SniffPacket struct   │
 │    - Pushes struct to FreeRTOS Queue via xQueueSendFromISR()            │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ 4. CORE 0 MAIN LOOP (esp32_sniffer.ino)                                 │
 │    - Pops packets from FreeRTOS Queue                                   │
 │    - Formats telemetry as JSON line string                              │
 │    - Transmits over USB Serial at 115200 Baud                             │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │ (USB Cable)
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ 5. PYTHON SERIAL READER THREAD (ids/serial_reader.py)                   │
 │    - Asynchronously reads serial line, parses JSON                      │
 │    - Forwards packet to Controller callback                             │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ 6. SYSTEM CONTROLLER & IDS ENGINE (main.py + ids/ submodules)           │
 │    - ids/gateway_resolver.py: Cross-references BSSID with Default GW    │
 │    - ids/wifi_memory.py: Checks against netsh / legit_wifi.json         │
 │    - ids/deauth_detector.py: Evaluates 8-condition deauth score          │
 │    - ids/arp_sniffer.py: Sniffs local ARP traffic for spoofing          │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
 ┌───────────────────────────────────┐ ┌───────────────────────────────────┐
 │ 7. GUI RENDERING ENGINE           │ │ 8. AUDIO ALERT PIPELINE           │
 │    - Technician View (gui/app.py) │ │    - Host PC Voice (voice_audios/)│
 │    - User View (gui/user_view.py) │ │    - ESP32 Hardware Speaker    │
 │    - CustomTkinter ThemeManager   │ │      (Core 1 DMA I2S Task via   │
 └───────────────────────────────────┘ │      PLAY:<track> serial cmd)    │
                                       └───────────────────────────────────┘
```

---

## 7. ESP32 Sniffer & Audio Firmware

The firmware located in [`esp32_sniffer/esp32_sniffer.ino`](file:///c:/Users/stephen/Desktop/WIDS/esp32_sniffer/esp32_sniffer.ino) operates across both cores of the ESP32:

### 7.1 FreeRTOS Dual-Core Design
- **Core 0**: Executes the high-frequency Wi-Fi Promiscuous Receive Callback (`wifi_promiscuous_cb`) and channel hopping logic (channel changes every 200ms).
- **Core 1**: Dedicated `audioTask` pinned to Core 1 that streams 16-bit PCM audio chunks over DMA to the MAX98357A I2S peripheral without interrupting packet sniffing.

### 7.2 PCM Audio Gain Boost (`audio_data.h`)
Audio data is stored as raw PCM byte arrays in PROGMEM (`audio_data.h`). To guarantee clear audible warnings from a 3W micro speaker, the firmware converts 8-bit unsigned PCM to 16-bit signed PCM with a **2.0x volume gain boost**:
```cpp
// Convert 8-bit unsigned PCM (0..255) to 16-bit signed PCM with 2.0x Gain Boost
for (uint32_t i = 0; i < chunkSize; i++) {
    int32_t sample = ((int32_t)rawBuf[i] - 128) * 512;
    if (sample > 32767) sample = 32767;
    if (sample < -32768) sample = -32768;
    i2sBuf[i] = (int16_t)sample;
}
```

### 7.3 Serial Commands Handled by ESP32
The Python application can trigger hardware audio alerts by writing command strings to the serial stream:
- `PLAY:deauth` — Plays Deauth Attack warning track
- `PLAY:evil_twin` — Plays Evil Twin AP warning track
- `PLAY:mac_spoof` — Plays MAC Spoofing warning track
- `PLAY:greeting` — Plays System Initialization greeting
- `PLAY:history` — Plays Alert History warning track

---

## 8. Python Intrusion Detection System Engine

The backend detection engine resides within the [`ids/`](file:///c:/Users/stephen/Desktop/WIDS/ids) directory.

### 8.1 Serial Reader (`ids/serial_reader.py`)
- Manages connection lifecycle to serial ports with auto-reconnect logic.
- Executes an asynchronous background reading loop to prevent GUI freezing.
- Validates JSON line formats and dispatches parsed dictionaries to the system callback.
- Includes `send_command(cmd)` to write trigger strings back to the ESP32.

### 8.2 Deauth Attack Detector (`ids/deauth_detector.py`)
Applies an 8-condition scoring algorithm to evaluate deauthentication frame bursts:

```python
# Score calculation snippet from deauth_detector.py
if packet_count >= MAX_DEAUTH_PER_WINDOW: score += 3  # High rate
if bssid not in WHITELIST_BSSID:         score += 3  # Untrusted AP
if dst == "FF:FF:FF:FF:FF:FF":            score += 2  # Broadcast target
if victim_count >= MAX_VICTIMS_PER_AP:   score += 2  # Mass targeting
if len(victim_counter[dst]) >= REPEAT:    score += 2  # Repeated victim
if duration >= ATTACK_DURATION:           score += 2  # Sustained attack
if stable_fixed_interval:                score += 1  # Automated tool pattern
```

- **Anti-Spam Rate Limiting**: Features a 2-tier cooldown (per source/victim pair cooldown + a **30-second global cooldown**) to prevent alert floods during massive deauth storms.
- **Memory Management**: Runs automated cleanup every 5 seconds (`_cleanup_old_state`) to remove expired timestamps.

### 8.3 Gateway Resolver (`ids/gateway_resolver.py`)
Provides dynamic default gateway MAC resolution and verification:
- **Confidence Levels**:
  - `HARDWARE_VERIFIED`: Gateway MAC matches a BSSID seen live over-the-air by the ESP32.
  - `VENDOR_VERIFIED`: Gateway MAC matches a known router/networking hardware OUI (e.g., Cisco, TP-Link).
  - `FIRST_SEEN`: Resolved via ARP, but unverified.
- **Active Subnet ARP Scan**: `scan_subnet_async()` sends ARP requests across the local `/24` subnet using Scapy to discover duplicate MAC addresses (a key indicator of active ARP spoofing).

### 8.4 ARP Sniffer (`ids/arp_sniffer.py`)
- Passively sniffs local ARP traffic using Scapy.
- Tracks `(IP -> MAC)` bindings with automatic entry aging (5-minute ARP table timeout).
- **Adjacent MAC Heuristic (`_are_adjacent_macs`)**: Suppresses false positives caused by dual-band routers or mesh nodes (e.g., 2.4GHz and 5GHz interfaces that share the first 4 OUI bytes).

### 8.5 Wi-Fi Memory (`ids/wifi_memory.py`)
- Interrogates Windows network state via `netsh wlan show interfaces`.
- Manages `ids/legit_wifi.json` to store trusted SSID and BSSID pairings.
- Automatically handles legitimate network switches (updates `legit_wifi.json` when the user connects to a new SSID).

### 8.6 OUI Lookup Database (`ids/oui_lookup.py`)
- Hardcoded offline lookup module (~380 lines) categorizing MAC prefixes into `network_equipment`, `consumer_device`, `iot_device`, or `unknown`.

### 8.7 Config & Logger (`ids/config.py`, `ids/logger.py`)
- `config.py`: Stores detection parameters, thresholds, and 802.11 deauth reason code descriptions (Codes 1 through 45).
- `logger.py`: Centralized logging handler (`IDSLogger`).

---

## 9. Modern Dual-View Dashboard

The user interface supports two distinct operational modes:

### 9.1 Technician View (`gui/app.py`)
Targeted at security analysts and power users (~1638 lines):
- **Live Stream Table**: Real-time treeview showing packet timestamps, RSSI, channel, SSID, source MAC, destination MAC, and subtype.
- **Filter Controls**: Checkboxes to isolate Beacons, Probes, or Deauths, plus live search text filtering.
- **Network Statistics Cards**: Live counters for total packets, deauth counts, and active threat alert counts.
- **Active BSSID Table**: Complete list of observed Access Points with first seen time, last seen time, packet count, and RSSI.
- **Signal Quality Charts**: Live RSSI trendline visualization.
- **Controls**: COM port auto-connect dropdown, Baud selector, Host PC Mute toggle, ESP32 Speaker Mute toggle, and Theme Switcher.

### 9.2 User View (`gui/user_view.py`)
Targeted at non-technical users (~713 lines):
- **Security Health Status Badge**: Prominent status indicator:
  - `SECURE` (Green): No active threats detected.
  - `WARNING` (Amber): Elevated packet rate or unknown devices.
  - `CRITICAL THREAT` (Red): Active Evil Twin or Deauth attack underway.
- **Simplified Threat Cards**: Explains detected security issues in plain language.
- **Actionable Recommendations**: Step-by-step guidance ("What should I do?") instructing users to disconnect, verify network names, or contact network administrators.

### 9.3 Theme Manager (`gui/theme.py`)
- Centralized theming system (`ThemeManager`) supporting seamless runtime toggling between Dark Mode and Light Mode.

---

## 10. Evil Twin Detection Engine

The Evil Twin detection algorithm in `main.py` and `gui/app.py` enforces a strict 8-point check:

```text
               ┌──────────────────────────────────────────────┐
               │ Incoming Beacon Frame (SSID, BSSID, RSSI, Ch)│
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │ Is SSID stored in legit_wifi.json?           │
               └──────────────┬────────────────┬──────────────┘
                              │ YES            │ NO
                              ▼                ▼
            ┌───────────────────┐    ┌───────────────────────────┐
            │ Does BSSID match  │    │ Track BSSID in            │
            │ saved legit BSSID?│    │ self.ssid_to_bssid[ssid]  │
            └─────────┬─────────┘    └─────────────┬─────────────┘
                      │                            │
           ┌──────────┴──────────┐                 │ 2+ BSSIDs on
        MATCH                  MISMATCH            │ same SSID?
           │                      │                ▼
           ▼                      ▼     ┌────────────────────────┐
      [LEGITIMATE]          🔴 EVIL TWIN│ Run 8-Point Score Check│
                             [HIGH ALARM]└─────────┬──────────────┘
                                                   │
                                                   ▼
                                        Score >= 5 -> Trigger Alert
```

### The 8 Scoring Signals
1. **Legit BSSID Mismatch** (+5 points -> Instant HIGH Severity Alert)
2. **Locally Administered MAC (LAA)** (+3 points if 2nd character of MAC is 2, 6, A, or E)
3. **Channel Mismatch** (+2 points if same SSID appears on different channels)
4. **RSSI Anomaly** (+2 points if signal delta between BSSIDs > 25 dBm)
5. **Vendor OUI Mismatch** (+2 points if MAC vendors differ between BSSIDs)
6. **First-Seen Timestamp Delta** (+2 points if a new BSSID suddenly appears after a stable baseline)
7. **Sequence Number Discontinuity** (+1 point)
8. **Low Packet Count Baseline** (+1 point)

---

## 11. Deauthentication Attack Detection

Deauth detection evaluates management frame bursts:

- **Time Window**: Evaluates activity over a rolling `TIME_WINDOW` of 30 seconds.
- **Thresholds**:
  - `MAX_DEAUTH_PER_WINDOW = 10`
  - `MAX_VICTIMS_PER_AP = 3`
  - `ALERT_SCORE = 5`
- **Rate-Limiting Cooldowns**:
  - Per Pair (`src`, `dst`): 10 seconds.
  - Global Cooldown: **30 seconds** across all deauth alerts to prevent CPU exhaustion during widespread attacks.

---

## 12. ARP Spoofing & Gateway Impersonation

WIDS combines passive and active defense layers against ARP Man-in-the-Middle attacks:

```text
                   ┌──────────────────────────────────────────┐
                   │       GatewayResolver Initialization     │
                   └────────────────────┬─────────────────────┘
                                        │
                                        ▼
                   ┌──────────────────────────────────────────┐
                   │ Query OS Routing Table for Gateway IP    │
                   └────────────────────┬─────────────────────┘
                                        │
                                        ▼
                   ┌──────────────────────────────────────────┐
                   │ Lookup Gateway MAC via legit_wifi / ARP  │
                   └────────────────────┬─────────────────────┘
                                        │
                                        ▼
                   ┌──────────────────────────────────────────┐
                   │ ESP32 Over-the-Air Beacon Cross-Ref      │
                   │ BSSID Matches Gateway MAC?               │
                   └──────────┬────────────────────┬──────────┘
                              │ YES                │ NO
                              ▼                    ▼
                    [HARDWARE_VERIFIED]     [VENDOR_VERIFIED /
                     (Highest Trust)         FIRST_SEEN]
                                                   │
                                                   ▼
                                        Run scan_subnet_async()
                                        Detect Duplicate MACs
```

---

## 13. Audio Alert System

Sentinel WIDS features a **dual audio notification pipeline**:

```text
                                 ATTACK DETECTED!
                                        │
                   ┌────────────────────┴────────────────────┐
                   ▼                                         ▼
   ┌───────────────────────────────┐         ┌───────────────────────────────┐
   │ 1. HARDWARE AUDIO (ESP32)     │         │ 2. HOST PC AUDIO (Python)     │
   │    - Host sends PLAY:<track>  │         │    - Reads MP3 voice files    │
   │    - Core 1 DMA task streams  │         │      from voice_audios/       │
   │      16-bit PCM (2.0x Gain)   │         │    - Plays speech alerts      │
   │      to MAX98357A I2S Speaker │         │      through computer speakers│
   └───────────────────────────────┘         └───────────────────────────────┘
```

### Available Audio Assets (`voice_audios/`)
- `Jarvis-...-Evil-twin-wifi-detected!!.mp3`
- `Jarvis-...-MAC-Spoofing-detected-,-Sir!!!.mp3`
- `Jarvis-...-Deauth-Attack-Frames-has-been-found-,.mp3`
- `Jarvis-...-Hello-,-Sir-,-Our-Intrusion-Detection-System-is.mp3`
- `Jarvis-...-Sir-!!-please-check-the-alerts-history-carefully.mp3`

---

## 14. Automated Test Suite

The repository includes automated unit and integration test scripts in the [`tests/`](file:///c:/Users/stephen/Desktop/WIDS/tests) directory:

- [`tests/test_alerts.py`](file:///c:/Users/stephen/Desktop/WIDS/tests/test_alerts.py): Tests alert generation, logging formatting, and severity escalation.
- [`tests/test_arp_sniffer.py`](file:///c:/Users/stephen/Desktop/WIDS/tests/test_arp_sniffer.py): Tests Scapy ARP frame parsing, ARP table entry aging, and adjacent MAC heuristic filtering.
- [`tests/test_gateway_resolver.py`](file:///c:/Users/stephen/Desktop/WIDS/tests/test_gateway_resolver.py): Tests default gateway resolution, ESP32 BSSID verification, and subnet MAC scanning.

### Running Tests
To run the automated test suite:
```bash
python -m unittest discover -s tests
```

---

## 15. Whitelist: Managing False Positives

Mesh Wi-Fi systems (e.g., Google Nest, Eero, Netgear Orbi) broadcast the same SSID across multiple Access Points (BSSIDs). To prevent false alarms:

1. Click **VIEW ALERTS** in the Technician View or User View.
2. Click **"✅ Trust — Mark as False Positive (Mesh/Extender)"**.
3. The selection is stored persistently in [`ids/whitelist.json`](file:///c:/Users/stephen/Desktop/WIDS/ids/whitelist.json):

```json
{
    "Home_Mesh_Network": [
        "50:3E:AA:12:34:56",
        "50:3E:AA:12:34:57"
    ]
}
```

---

## 16. Complete Glossary (A-Z)

| Term | Category | Definition |
|------|----------|------------|
| **802.11** | Protocol | The IEEE standard defining wireless local area networks (Wi-Fi). |
| **AP** | Hardware | Access Point — A device creating a wireless network. |
| **ARP** | Networking | Address Resolution Protocol — Maps IP addresses to MAC addresses on a local LAN. |
| **BSSID** | Wi-Fi | Basic Service Set Identifier — Hardware MAC address of an AP's radio. |
| **CustomTkinter** | UI Framework | Modernized Python GUI library built on top of Tkinter. |
| **dBm** | Physics | Decibel-milliwatts — Logarithmic unit of radio signal power. |
| **Deauthentication** | Attack | Frame telling a Wi-Fi client to immediately terminate connection. |
| **DMA** | Hardware | Direct Memory Access — Hardware feature enabling I2S audio transfer without CPU overhead. |
| **ESP32** | Hardware | Dual-core 240MHz microcontroller chip with built-in Wi-Fi and Bluetooth. |
| **Evil Twin** | Attack | Rogue Access Point broadcasting an identical SSID to impersonate a legitimate network. |
| **FreeRTOS** | OS | Real-Time Operating System running multi-threaded tasks on the ESP32. |
| **I2S** | Protocol | Inter-IC Sound — Digital serial bus protocol for transferring audio data to DACs. |
| **ISR** | Embedded | Interrupt Service Routine — Ultra-fast function invoked hardware-side upon packet arrival. |
| **LAA** | Networking | Locally Administered Address — A MAC address with its 2nd bit set, indicating software spoofing. |
| **MAC Address** | Networking | Media Access Control — Unique 48-bit hardware identifier assigned to network cards. |
| **MAX98357A** | Hardware | Class D I2S DAC Audio Amplifier module for driving physical speakers. |
| **Npcap** | Driver | Windows packet capture library required by Scapy for raw network socket sniffing. |
| **OUI** | Networking | Organizationally Unique Identifier — First 24 bits of a MAC identifying the manufacturer. |
| **Promiscuous Mode** | Hardware | Wi-Fi mode configuring radio hardware to capture ALL frames broadcast in range. |
| **RSSI** | Wi-Fi | Received Signal Strength Indicator — Measurement of received signal power. |
| **Scapy** | Library | Powerful Python packet manipulation and network sniffing library. |
| **SSID** | Wi-Fi | Service Set Identifier — Human-readable name of a Wi-Fi network. |

---

## 17. Troubleshooting Guide

### 17.1 Serial Connection Issues
- **Symptoms**: "No serial data received on COM5" or drop-down list is empty.
- **Fixes**:
  1. Ensure USB cable supports data transfer (test with another USB device).
  2. Verify correct COM port in Device Manager (Windows) or `/dev/ttyUSB*` (Linux/Mac).
  3. Close any running instances of Arduino Serial Monitor or PuTTY.
  4. Ensure baud rate is set to `115200`.

### 17.2 Audio Output Issues (MAX98357A)
- **Symptoms**: Speaker is silent during alerts or emits buzzing noise.
- **Fixes**:
  1. Check wiring: `BCK -> GPIO 26`, `LRC -> GPIO 25`, `DIN -> GPIO 27`.
  2. Ensure MAX98357A `VIN` is connected to 5V (or 3.3V) and `GND` is shared with ESP32.
  3. Check if sound is muted via GUI toggles ("Mute Host PC" or "Mute Speaker").

### 17.3 ARP Sniffing & Scapy Permission Errors
- **Symptoms**: `Scapy_Exception: No working libpcap provider found!` or missing ARP alerts.
- **Fixes**:
  1. Download and install **Npcap** from [npcap.com](https://npcap.com/).
  2. Ensure *"WinPcap API-compatible Mode"* was checked during Npcap installation.
  3. On Linux/macOS, launch WIDS with `sudo python main.py`.

### 17.4 High False Positive Rate
- **Fixes**:
  1. Click **Trust — Mark as False Positive** for known home extenders or mesh nodes.
  2. Verify that `ids/whitelist.json` contains your trusted BSSIDs.

---

## 18. File Reference & Project Tree

### 18.1 File Purpose & LOC Index

| File Path | Purpose / Description | Lines | Language |
|-----------|───────────────────────|-------|----------|
| [`main.py`](file:///c:/Users/stephen/Desktop/WIDS/main.py) | Application entry point & system controller | 86 | Python |
| [`esp32_sniffer/esp32_sniffer.ino`](file:///c:/Users/stephen/Desktop/WIDS/esp32_sniffer/esp32_sniffer.ino) | ESP32 Wi-Fi sniffer & FreeRTOS I2S audio firmware | 287 | C++ |
| [`esp32_sniffer/audio_data.h`](file:///c:/Users/stephen/Desktop/WIDS/esp32_sniffer/audio_data.h) | 16-bit PCM voice audio byte arrays in PROGMEM | ~1.5MB | C/C++ Header |
| [`ids/serial_reader.py`](file:///c:/Users/stephen/Desktop/WIDS/ids/serial_reader.py) | Asynchronous USB serial reader thread | 68 | Python |
| [`ids/deauth_detector.py`](file:///c:/Users/stephen/Desktop/WIDS/ids/deauth_detector.py) | 8-condition deauth attack detection engine | 237 | Python |
| [`ids/gateway_resolver.py`](file:///c:/Users/stephen/Desktop/WIDS/ids/gateway_resolver.py) | Gateway resolution & active subnet ARP scanner | 300 | Python |
| [`ids/arp_sniffer.py`](file:///c:/Users/stephen/Desktop/WIDS/ids/arp_sniffer.py) | Scapy ARP packet sniffer & gateway spoof detector | 127 | Python |
| [`ids/wifi_memory.py`](file:///c:/Users/stephen/Desktop/WIDS/ids/wifi_memory.py) | Windows Wi-Fi netsh interface & legit_wifi storage | 94 | Python |
| [`ids/oui_lookup.py`](file:///c:/Users/stephen/Desktop/WIDS/ids/oui_lookup.py) | Offline MAC OUI vendor classification database | 380 | Python |
| [`ids/logger.py`](file:///c:/Users/stephen/Desktop/WIDS/ids/logger.py) | System logger configuration helper | 24 | Python |
| [`ids/config.py`](file:///c:/Users/stephen/Desktop/WIDS/ids/config.py) | Threshold parameters & deauth reason codes | 37 | Python |
| [`gui/app.py`](file:///c:/Users/stephen/Desktop/WIDS/gui/app.py) | CustomTkinter Technician View dashboard | 1638 | Python |
| [`gui/user_view.py`](file:///c:/Users/stephen/Desktop/WIDS/gui/user_view.py) | Simplified User View dashboard | 713 | Python |
| [`gui/theme.py`](file:///c:/Users/stephen/Desktop/WIDS/gui/theme.py) | Dynamic Light/Dark theme manager | ~150 | Python |
| [`voice_audios/`](file:///c:/Users/stephen/Desktop/WIDS/voice_audios) | Host PC J.A.R.V.I.S MP3 voice audio files | 5 files | MP3 Audio |
| [`tests/`](file:///c:/Users/stephen/Desktop/WIDS/tests) | Automated integration & unit testing suite | 4 files | Python |
| [`requirements.txt`](file:///c:/Users/stephen/Desktop/WIDS/requirements.txt) | Python dependency manifest | 2 | Text |
| [`README.md`](file:///c:/Users/stephen/Desktop/WIDS/README.md) | Standard repository summary documentation | 99 | Markdown |
| [`WIDS_README.md`](file:///c:/Users/stephen/Desktop/WIDS/WIDS_README.md) | Complete beginner & architecture master guide | This file | Markdown |

### 18.2 Directory Tree

```text
WIDS/
│
├── main.py                             # System Controller & Entry Point
├── requirements.txt                    # Dependencies (customtkinter, scapy, pyserial, pillow)
├── README.md                           # Overview documentation
├── WIDS_README.md                      # Comprehensive Master Guide (This document)
├── app_diff.txt                        # Application diff notes
│
├── esp32_sniffer/                      # ESP32 Firmware
│   ├── esp32_sniffer.ino               # Promiscuous Sniffer & I2S Audio Firmware
│   └── audio_data.h                    # PROGMEM PCM Audio Bytes
│
├── ids/                                # Intrusion Detection Engine
│   ├── serial_reader.py                # Asynchronous Serial Thread
│   ├── deauth_detector.py              # Deauth Attack Detection Module
│   ├── gateway_resolver.py             # Dynamic Gateway & Subnet ARP Scanner
│   ├── arp_sniffer.py                  # Scapy ARP Spoofing Detector
│   ├── wifi_memory.py                  # Windows netsh & Legit Wi-Fi Storage
│   ├── oui_lookup.py                   # OUI Vendor Classification Database
│   ├── logger.py                       # Logging Helper
│   ├── config.py                       # Detection Thresholds & Reason Codes
│   ├── legit_wifi.json                 # Saved Legitimate Wi-Fi Profile
│   ├── whitelist.json                  # Trusted BSSID Whitelist
│   └── theme_pref.json                 # Persistent Theme Preference
│
├── gui/                                # User Interface Package
│   ├── app.py                          # Technician View Dashboard
│   ├── user_view.py                    # Simplified Non-Technical User View
│   ├── theme.py                        # Theme Manager Engine
│   └── wids_logo.jpg                   # Application Branding Logo
│
├── voice_audios/                       # Host PC Voice Audio Alerts (J.A.R.V.I.S)
│   ├── Jarvis-...-Evil-twin-wifi-detected!!.mp3
│   ├── Jarvis-...-MAC-Spoofing-detected-,-Sir!!!.mp3
│   ├── Jarvis-...-Deauth-Attack-Frames-has-been-found-,.mp3
│   ├── Jarvis-...-Hello-,-Sir-,-Our-Intrusion-Detection-System-is.mp3
│   └── Jarvis-...-Sir-!!-please-check-the-alerts-history-carefully.mp3
│
├── tests/                              # Automated Unit & Integration Tests
│   ├── test_alerts.py                  # Alert System Tests
│   ├── test_arp_sniffer.py             # Scapy ARP Sniffer Tests
│   └── test_gateway_resolver.py        # Gateway Resolver & BSSID Verification Tests
│
├── logs/                               # Runtime Logs
│   └── wids.log                        # IDS Event Log
│
└── scratch/                            # Documentation & Report Generator Helpers
    ├── create_chapter2_docx.py
    ├── create_section3_docx.py
    └── create_section3_part1_docx.py
```

---

*Sentinel WIDS is an open educational and defensive cybersecurity system. Always ensure you have permission to monitor wireless network traffic in your environment.*
