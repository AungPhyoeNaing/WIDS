# Sentinel WIDS — The Complete Beginner's Guide

> **Hello!** This guide assumes you know NOTHING about Wi-Fi security, ESP32s, or Python.  
> We will explain *everything* from zero. If you get stuck on a word, check the Glossary.

---

## 📖 Table of Contents

| Section | What You'll Learn |
|---------|-------------------|
| [1. The One-Paragraph Summary](#1-the-one-paragraph-summary) | What this whole thing does, in 3 sentences |
| [2. What Is Wi-Fi? (The 5-Minute Crash Course)](#2-what-is-wi-fi-the-5-minute-crash-course) | How Wi-Fi actually works under the hood |
| [3. What Is This Project Actually For?](#3-what-is-this-project-actually-for) | 3 real attacks this system catches |
| [4. The Two Pieces of Hardware](#4-the-two-pieces-of-hardware) | ESP32 + Your Computer |
| [5. Complete Setup Guide (With Pictures)](#5-complete-setup-guide-with-pictures) | Step-by-step from zero to running |
| [6. How Data Flows: Air to Screen](#6-how-data-flows-air-to-screen) | Follow one packet's journey |
| [7. ESP32 Firmware Explained Line-by-Line](#7-esp32-firmware-explained-line-by-line) | The C++ code that runs on the ESP32 |
| [8. Python Serial Reader Explained Line-by-Line](#8-python-serial-reader-explained-line-by-line) | How Python reads from USB |
| [9. The Dashboard Explained Line-by-Line](#9-the-dashboard-explained-line-by-line) | The CustomTkinter GUI |
| [10. Evil Twin Detection (The Smart Part)](#10-evil-twin-detection-the-smart-part) | How we spot fake Wi-Fi networks |
| [11. Deauth Attack Detection](#11-deauth-attack-detection) | How we spot kick-off attacks |
| [12. Whitelist: How to Stop False Alarms](#12-whitelist-how-to-stop-false-alarms) | Trusting legitimate networks |
| [13. Complete Glossary (A-Z)](#13-complete-glossary-a-z) | Every term explained like you're 5 |
| [14. Troubleshooting: Everything That Can Go Wrong](#14-troubleshooting-everything-that-can-go-wrong) | Fixes for every common problem |

---

## 1. The One-Paragraph Summary

This project turns a **$5 ESP32 chip** into a **Wi-Fi security camera**. The ESP32 listens to all Wi-Fi traffic in the air (like a radio scanner) and sends what it hears to your computer over USB. Your computer runs a **dashboard app** that shows you every Wi-Fi packet in real time, and — most importantly — **automatically detects attacks** like fake Wi-Fi hotspots (Evil Twins) and people trying to kick devices off the network (Deauth attacks). Think of it as a home security system, but for Wi-Fi instead of doors.

---

## 2. What Is Wi-Fi? (The 5-Minute Crash Course)

If you already know how Wi-Fi works, skip to Section 3. If not, read this.

### 2.1 Wi-Fi Is Like Walkie-Talkies

Imagine you and your friend have walkie-talkies. When you talk, your friend hears it — but so does anyone else on the same channel within range. Wi-Fi is the same: data travels through the air as **radio waves**, and anyone with the right receiver can hear it.

### 2.2 Devices Have Addresses (MAC Addresses)

Just like your house has a street address, every Wi-Fi device has a **MAC address** — a 12-character code that looks like this:

```
AA:BB:CC:DD:EE:FF
```

The first 6 characters (`AA:BB:CC`) tell you the **manufacturer** (this is called the **OUI** — Organizationally Unique Identifier). For example:
- `50:3E:AA` = TP-Link (makes routers)
- `00:21:5C` = Intel (makes laptop Wi-Fi chips)

The last 6 characters (`DD:EE:FF`) are unique to that specific device.

### 2.3 Networks Have Names (SSIDs)

When you open your phone's Wi-Fi list, you see names like "Starbucks_WiFi" or "Home_Network_5G". That's the **SSID** — Service Set Identifier. It's the human-readable name.

### 2.4 Wi-Fi Packets (Like Letters)

Everything on Wi-Fi is sent in **packets** — small chunks of data. Think of a packet like a letter in an envelope:

```
┌─────────────────────────────────────────┐
│  ENVELOPE                               │
│  From: (Source MAC)                     │
│  To:   (Destination MAC)                │
│  What kind: Management / Data / Control │
│  Signal strength: -45 dBm (how close)   │
│  Channel: 6 (which frequency)           │
│  ┌─────────────────────────────────────┐│
│  │  LETTER INSIDE:                     ││
│  │  "Hello, here is the actual data..." ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### 2.5 Three Types of Wi-Fi Packets

| Type | What It Does | Do We Care? |
|------|-------------|-------------|
| **Management** | Handles connections (join, leave, find networks) | **YES** — this is what we monitor |
| **Control** | Makes sure data arrives (ACK, RTS, CTS) | No — boring but essential |
| **Data** | Actual internet traffic (web pages, videos) | No — we don't spy on data |

**Our ESP32 ONLY captures Management frames** — not data. This means we can see what's happening in the neighborhood without invading anyone's privacy.

### 2.6 Management Frame Types (0-15)

Management frames have subtypes (0 through 15). Here are the important ones:

| Number | Name | Description | Why We Care |
|--------|------|-------------|-------------|
| 4 | **Probe Request** | Your phone says "Is anyone there named 'HomeWiFi'?" | Shows what networks devices are looking for |
| 5 | **Probe Response** | An AP says "Yes, I'm 'HomeWiFi', join me!" | Maps nearby networks |
| 8 | **Beacon** | An AP shouts "I exist! I'm 'CoffeeWiFi'!" every 100ms | Maps nearby networks |
| 10 | **Disassociation** | "You're fired — leave the network" | Can be an attack |
| 12 | **Deauthentication** | "GET OFF the network NOW" | **This is a common attack** |

### 2.7 What Is dBm? (Signal Strength)

**dBm** stands for decibel-milliwatts. It measures how strong a signal is. The scale is weird:

| Value | Meaning | Example |
|-------|---------|---------|
| -30 dBm | Very strong signal | Standing right next to the router |
| -50 dBm | Good signal | Same room as the router |
| -67 dBm | Okay signal | One room away |
| -80 dBm | Weak signal | Far away or through walls |
| -90 dBm | Barely detectable | The limit of hearing |

Higher numbers (closer to 0) = stronger signal. -40 is stronger than -80.

---

## 3. What Is This Project Actually For?

This system catches **3 types of attacks**:

### 3.1 Evil Twin Attack (The Most Dangerous)

**What happens:** A hacker sits in a coffee shop with a laptop. They create a Wi-Fi network named exactly "Starbucks_WiFi" — the same name as the real Starbucks Wi-Fi. Your phone sees two networks with the same name and might automatically connect to the hacker's (especially if it has stronger signal or you've connected before).

**The danger:** Once connected, the hacker can:
- Steal passwords you type
- See every website you visit
- Inject fake pages (like a fake login screen)
- Redirect you to malware sites

**How we catch it:** Our system sees that "Starbucks_WiFi" is being broadcast by **two different MAC addresses**. We run 8 checks to determine which one is fake, then flag it.

### 3.2 Deauth Attack (The Annoying One)

**What happens:** A hacker sends "Deauthentication" packets to a Wi-Fi network. These packets tell every device "LEAVE NOW!" The devices comply and disconnect. Then they reconnect. Then the hacker sends more. The network becomes unusable.

**The danger:** This can:
- Kick everyone off a business's Wi-Fi (losing customers)
- Disrupt IoT devices (security cameras, smart locks)
- Be combined with an Evil Twin (when devices reconnect, they might connect to the hacker's fake network)

**How we catch it:** We count Deauth frames. When we see 10+ in a short time, we trigger an alert.

### 3.3 Probe Sniffing (The Privacy Problem)

**What happens:** Your phone constantly sends out "Probe Requests" that say "Is anyone there named 'HomeWiFi'? What about 'CoffeeWiFi'?" — even when you're not on Wi-Fi. Anyone with a sniffer can hear these.

**The danger:** Hackers can:
- Track where you've been (your phone reveals the names of networks it remembers)
- Track your physical location (signal strength reveals distance)
- Create targeted Evil Twins based on networks your phone trusts

**How we catch it:** We display every Probe Request in the live stream. You can see which networks nearby devices are searching for.

---

## 4. The Two Pieces of Hardware

### 4.1 The ESP32 ($5-10)

```
ESP32 Dev Board (physical appearance)
┌──────────────────────────────────────────────┐
│                                              │
│  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐       │
│  │  │  │  │  │  │  │  │  │  │  │  │  ESP32  │
│  └──┘  └──┘  └──┘  └──┘  └──┘  └──┘  Chip  │
│                                              │
│  [USB Port] ←──── connects to your computer │
│                                              │
│  [ON/OFF]  [EN]  (small buttons)             │
└──────────────────────────────────────────────┘
```

**What it is:** A tiny computer with Wi-Fi built in. It costs about the same as a coffee.

**What it does in this project:**
1. Listens to **all** Wi-Fi traffic within range (like a police scanner)
2. Filter: only keeps **Management frames** (Beacons, Probes, Deauths, etc.)
3. Extracts important info from each packet
4. Sends that info over USB to your computer as JSON text
5. Changes channel every 200ms (so it hears all 13 channels, not just one)

**Why an ESP32?** It's cheap, has built-in Wi-Fi, and the manufacturer (Espressif) provides a function called "promiscuous mode" that lets you hear everything.

### 4.2 Your Computer (The Dashboard)

**What it does:**
1. Reads the JSON data coming over USB
2. Parses it into Python dictionaries
3. Shows everything in a real-time GUI dashboard
4. **Detects attacks** using smart algorithms

---

## 5. Complete Setup Guide (With Pictures)

### Step 0: What You Need

```
□ ESP32 board               (Amazon: ~$8)
□ USB cable (data capable)  (the one that came with it works)
□ Computer with Python 3.8+ (Windows/Mac/Linux)
□ Internet connection        (to download software)
□ 15 minutes of your time
```

### Step 1: Install Arduino IDE

1. Go to https://www.arduino.cc/en/software
2. Download the version for your operating system
3. Install it (click Next → I Agree → Install → Finish)

### Step 2: Add ESP32 Support to Arduino IDE

1. Open Arduino IDE
2. Go to **File → Preferences**
3. Find "Additional Boards Manager URLs"
4. Paste this URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
5. Click OK
6. Go to **Tools → Board → Board Manager**
7. Search for "esp32"
8. Click **Install** on "ESP32 by Espressif Systems"
9. Wait 5 minutes (it downloads a lot)

### Step 3: Open and Upload the Firmware

1. In Arduino IDE: **File → Open**
2. Navigate to your WIDS folder → `esp32_sniffer` → `esp32_sniffer.ino`
3. Connect your ESP32 to your computer via USB
4. Go to **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
5. Go to **Tools → Port** and select the COM port with "USB" or "CP2102" in the name
   - Windows: Usually `COM3`, `COM4`, or `COM5`
   - Mac: Usually `/dev/cu.usbserial-XXXX`
   - Linux: Usually `/dev/ttyUSB0`
6. Click the **→ (Upload)** button (top left, looks like an arrow)
7. **IMPORTANT:** If it says "Connecting..." and hangs, press and hold the **BOOT** button on the ESP32 until the upload starts (you'll see percentage numbers)

```
After successful upload, you'll see:
"Hard resetting via RTS pin..."
```

### Step 4: Install Python

1. Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux)
2. Navigate to your WIDS folder:
```bash
cd C:\Users\YourName\Desktop\WIDS   # Windows example
cd ~/Desktop/WIDS                    # Mac/Linux example
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
   - If `pip` doesn't work, try `pip3` or `python -m pip install customtkinter pyserial`

### Step 5: Run the Dashboard

```bash
python main.py
```

You should see a dark-themed dashboard window appear.

### Step 6: Connect

1. In the sidebar, type your COM port (e.g., `COM5`)
2. Baud rate should be `115200` (it's filled in already)
3. Click **CONNECT**
4. The status should change from "● Disconnected" (red) to "● Connected" (green)
5. Packets should appear in the main area

**If no packets appear**, see the Troubleshooting section.

---

## 6. How Data Flows: Air to Screen

Let's follow **one single Wi-Fi packet** from the moment it travels through the air to the moment it appears on your screen. We'll use a Beacon frame (a router announcing itself) as our example.

### Step 1: A Router Sends a Beacon

```
Imagine: A TP-Link router in the apartment next door.
It sends out a Beacon every 100ms saying:
  "I'm here! My name is 'Smith_Family_WiFi'!"
  "My MAC address is 50:3E:AA:12:34:56"
  "I'm on Channel 6"
  "My signal level is -45 dBm"
```

### Step 2: The ESP32 Hears It

The ESP32 is in **promiscuous mode** — it hears every packet within range, not just packets addressed to itself. The Wi-Fi chip on the ESP32 detects the packet and immediately calls a special function called an **Interrupt Service Routine (ISR)**.

**What is an ISR?** Imagine you're reading a book and someone taps your shoulder. You stop reading instantly, deal with the tap, then go back to reading. That's an interrupt. The ISR is the "deal with the tap" part — it runs instantly, does the minimum work possible, and returns.

### Step 3: The ISR Does Quick Work (Microseconds)

The ISR cannot spend much time — it has microseconds, not milliseconds. It:

1. Checks the packet type (is it a Management frame? Yes!)
2. Copies only the important bytes into a small struct (36 bytes total):
   - Timestamp (when did we hear it)
   - RSSI (how strong was the signal)
   - Channel (which channel was it on)
   - Source MAC (who sent it)
   - Destination MAC (who was it for)
   - BSSID (the access point's MAC)
   - Frame subtype (Beacon = 8)
   - SSID (the network name, if it's a Beacon or Probe Response)
3. Pushes this struct into a **queue** (a buffer) using `xQueueSendFromISR()`
4. Returns

**Why a queue?** The ISR runs at the highest priority. If we printed to Serial inside the ISR, it would take too long and the ESP32 would crash (Watchdog Timer reset). The queue lets the ISR finish in microseconds; the main loop can take its time printing.

```
ISR (FAST)                QUEUE (buffer)          MAIN LOOP (slow)
───────                   ─────────────           ─────────────────
Packet arrives ──►     [packet 1]              │
                    ──► [packet 2]              │
                    ──► [packet 3]     ◄───────── Serial.printf()
                    ──► [ ... ]                   (takes ~1ms)
                      (up to 50 slots)
```

If the queue is full (50 packets), the new packet is **dropped**. This is intentional — better to drop a packet than crash the ESP32.

### Step 4: The Main Loop Sends It Over USB

The main loop runs over and over, forever. Each time it:

1. Tries to pull packets from the queue (up to 10 per loop)
2. For each packet, builds a JSON string and prints it to Serial:
```json
{"timestamp": 123456, "rssi": -45, "channel": 6, "mac_src": "50:3E:AA:12:34:56", "mac_dst": "FF:FF:FF:FF:FF:FF", "bssid": "50:3E:AA:12:34:56", "type": "Management", "subtype": "Beacon", "ssid": "Smith_Family_WiFi"}
```
3. Checks if it's time to hop to the next channel (every 200ms)

### Step 5: USB Cable Carries the Data

The JSON text travels over the USB cable from the ESP32 to your computer at **115200 baud** (bits per second). That's about 11,500 characters per second — plenty for Wi-Fi management frames.

### Step 6: Python Reads the Serial Port

In Python, there's a **background thread** running the `SerialReader` class. This thread does:

```python
while self.running:
    # This line WAITS until a full line arrives (blocks here)
    line = self.serial.readline()
    
    # Convert bytes to text
    text = line.decode('utf-8', errors='ignore').strip()
    
    # If it looks like JSON, parse it
    if text.startswith('{') and text.endswith('}'):
        packet = json.loads(text)
        
        # Send to the GUI (via a thread-safe queue)
        self.callback(packet)
```

**Why a background thread?** `serial.readline()` is a blocking call — it sits and waits for data to arrive. If we ran this in the main GUI thread, the entire window would freeze every time it waited for a packet. By putting it in a background thread, the GUI stays responsive.

### Step 7: The Thread-Safe Bridge Queue

The `SerialReader` thread calls `app.add_packet(packet)`, which does:

```python
def add_packet(self, packet):
    self.packet_queue.put(packet)   # Put in thread-safe queue (instant!)
```

This queue (`queue.Queue`) is specially designed to be used by multiple threads. It handles all the locking internally.

### Step 8: The GUI Processes the Packet (250ms Later)

Every 250 milliseconds (4 times per second), the GUI wakes up and processes packets from the queue:

```python
def process_packet_queue(self):
    # Try to get up to 100 packets from the queue
    for _ in range(100):
        try:
            packet = self.packet_queue.get_nowait()
        except queue.Empty:
            break  # No more packets
        
        # === DO ALL THE WORK HERE ===
        
        # 1. Update packet counter
        self.total_packets += 1
        
        # 2. If it's a Deauth, count it
        if packet['subtype'] == 'Deauthentication':
            self.deauth_count += 1
            if self.deauth_count % 10 == 0:
                self.alert_count += 1
        
        # 3. Track this BSSID (for evil twin detection)
        self.track_bssid(packet)
        
        # 4. Run evil twin detection
        self.check_for_evil_twin(packet)
        
        # 5. Add a row to the table
        self.tree.insert("", 0, values=(
            current_time,
            f"{rssi} dBm",
            channel,
            network_name,
            src_mac,
            dst_mac,
            subtype
        ), tags=color_tags)
    
    # Schedule the next batch
    self.after(250, self.process_packet_queue)
```

**Why batch?** Processing one packet at a time would update the UI 1000+ times per second, making the app laggy. Batching (max 100 packets every 250ms = max 400 packets/second) keeps it smooth.

### Step 9: You See It on Screen

The packet appears as a row in the table with color coding:
- **Gray rows** = Beacons (normal AP announcements)
- **Purple rows** = Probe Requests (devices searching for networks)
- **Red rows** = Deauthentication (possible attack!)
- **Red background rows** = HIGH confidence Evil Twin detected!
- **Orange background** = MEDIUM confidence Evil Twin
- **Yellow background** = LOW confidence Evil Twin

---

## 7. ESP32 Firmware Explained Line-by-Line

This section explains every meaningful line in `esp32_sniffer/esp32_sniffer.ino`. If you don't know C++, don't worry — we explain everything.

### 7.1 The Top Part (Includes and Configuration)

```cpp
#include "esp_wifi.h"       // Gives access to Wi-Fi functions (including promiscuous mode)
#include <WiFi.h>           // Standard Wi-Fi library for ESP32
#include <freertos/FreeRTOS.h>  // FreeRTOS = Free Real-Time Operating System
#include <freertos/queue.h>     // Queue functions (the buffer between ISR and main loop)

// Configuration
const int CHANNEL_HOP_INTERVAL = 200; // milliseconds between channel changes
unsigned long lastHopTime = 0;        // stores the last time we changed channels
int currentChannel = 1;               // start on channel 1
```

**What is FreeRTOS?** It's a tiny operating system that runs on the ESP32. It handles multiple tasks, timing, and queues. Think of it as the "conductor" that makes sure everything runs in order.

### 7.2 The Packet Struct

```cpp
typedef struct {
    uint32_t timestamp;    // When was this packet captured? (milliseconds since boot)
    int8_t rssi;           // Signal strength (-30 to -90 dBm)
    uint8_t channel;       // Which Wi-Fi channel (1-13)
    uint8_t macSrc[6];     // Source MAC address (who sent it) — 6 bytes
    uint8_t macDst[6];     // Destination MAC (who was it for)
    uint8_t bssid[6];      // BSSID = the AP's MAC (Address 3 in the header)
    uint8_t frameSubtype;  // 0-15 (Beacon=8, Deauth=12, etc.)
    char ssid[33];         // Network name (max 32 chars + null terminator)
} SniffPacket;             // Total: 4+1+1+6+6+6+1+33 = 58 bytes, actually 36 packed
```

**Why so small?** This struct is copied into the queue. Smaller = faster = less chance of dropping packets. We only store what we absolutely need.

### 7.3 The Queue

```cpp
QueueHandle_t packetQueue;     // A "handle" (pointer) to our queue
const int QUEUE_SIZE = 50;     // Maximum 50 packets in the buffer
```

Think of the queue as a **bucket** that holds 50 packets. The ISR (fast) fills the bucket from the top. The main loop (slow) empties it from the bottom. If the bucket gets full, new packets spill out (are dropped) rather than overflowing and crashing the system.

### 7.4 The ISR Callback (The "Fast Hands")

```cpp
void wifi_promiscuous_cb(void *buf, wifi_promiscuous_pkt_type_t type) {
    // STEP 1: Only care about Management frames
    if (type != WIFI_PKT_MGMT) return;
    
    // STEP 2: Point to the raw packet data
    wifi_promiscuous_pkt_t *pkt = (wifi_promiscuous_pkt_t *)buf;
    uint8_t *payload = pkt->payload;
    
    // STEP 3: Parse the Frame Control byte to get type and subtype
    // The first 2 bytes of every 802.11 frame tell us what kind it is
    uint16_t fc = payload[0] | (payload[1] << 8);
    uint8_t frameType = (fc & 0x0C) >> 2;     // Bits 2-3 (0=Management, 1=Control, 2=Data)
    uint8_t frameSubtype = (fc & 0xF0) >> 4;  // Bits 4-7 (specific type)
    
    // STEP 4: Double-check it's Management (Type 0)
    if (frameType != 0) return;
    
    // STEP 5: Fill our struct
    SniffPacket p;
    p.timestamp = millis();                    // Time since ESP32 booted
    p.rssi = pkt->rx_ctrl.rssi;               // Signal strength from radio
    p.channel = pkt->rx_ctrl.channel;          // Channel from radio
    p.frameSubtype = frameSubtype;
    
    // Copy MAC addresses from the packet header
    // 802.11 header layout: ... | Addr1 (6) | Addr2 (6) | Addr3 (6) | ...
    // Addr1 = Destination (offset 4), Addr2 = Source (offset 10), Addr3 = BSSID (offset 16)
    memcpy(p.macDst, &payload[4], 6);    // Copy 6 bytes starting at offset 4
    memcpy(p.macSrc, &payload[10], 6);   // Copy 6 bytes starting at offset 10
    memcpy(p.bssid,  &payload[16], 6);   // Copy 6 bytes starting at offset 16
    
    // STEP 6: Try to extract SSID (only in Beacon and Probe Response frames)
    p.ssid[0] = '\0';  // Set to empty string by default
    
    if (frameSubtype == 8 || frameSubtype == 5) {
        // Beacon (8) and Probe Response (5) have tagged parameters
        // The format is: Tag Number (1 byte) | Tag Length (1 byte) | Value (N bytes)
        // Tag 0 = SSID, Tag 1 = Supported Rates, Tag 3 = Channel, etc.
        
        int offset = 36;  // Tagged parameters start at byte 36
        if (offset + 1 < pkt->rx_ctrl.sig_len) {  // Make sure we don't read past the packet
            if (payload[offset] == 0) {  // Is this Tag 0? (SSID tag)
                int ssid_len = payload[offset + 1];  // Next byte = length of SSID
                if (ssid_len > 0 && ssid_len <= 32) {  // SSID can't be longer than 32
                    memcpy(p.ssid, &payload[offset + 2], ssid_len);  // Copy the name
                    p.ssid[ssid_len] = '\0';  // Add string terminator
                }
            }
        }
    }
    
    // STEP 7: Push to queue (non-blocking — returns immediately)
    // If queue is full, the packet is simply dropped (no crash!)
    xQueueSendFromISR(packetQueue, &p, NULL);
}
```

**Key rule about ISRs:** NEVER do heavy work here. No printing, no complex calculations, no memory allocation. Copy what you need, push to a queue, and get out. The "real work" happens in the main loop.

### The Setup Function

```cpp
void setup() {
    // STEP 1: Open Serial communication at 115200 baud
    // This is the USB connection to your computer
    Serial.begin(115200);
    
    // STEP 2: Create the queue (bucket for 50 packets)
    packetQueue = xQueueCreate(QUEUE_SIZE, sizeof(SniffPacket));
    
    // STEP 3: Put ESP32 in "station mode" (like a phone, not a router)
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();          // Don't connect to any network
    
    // STEP 4: Turn on promiscuous mode — hear EVERYTHING
    esp_wifi_set_promiscuous(true);
    // Register our callback function to be called for every packet
    esp_wifi_set_promiscuous_rx_cb(&wifi_promiscuous_cb);
    
    // STEP 5: Print a startup message
    Serial.println("{\"log\": \"ESP32 Sniffer initialized. Waiting for packets...\"}");
}
```

**What is 115200?** It's the speed of the USB serial connection in bits per second. 115200 baud = about 11,500 characters per second. This was chosen because it's fast enough for Wi-Fi management frames but slow enough to be stable.

### The Main Loop

```cpp
void loop() {
    // TASK 1: Channel Hopping
    // If 200ms have passed since the last hop, change channels
    if (millis() - lastHopTime > CHANNEL_HOP_INTERVAL) {
        lastHopTime = millis();
        currentChannel++;
        if (currentChannel > 13) currentChannel = 1;  // Wrap around after 13
        esp_wifi_set_channel(currentChannel, WIFI_SECOND_CHAN_NONE);
    }
    
    // TASK 2: Process packets from the queue
    SniffPacket p;
    int packetsProcessed = 0;  // Limit to 10 per loop
    
    while (xQueueReceive(packetQueue, &p, 0) == pdTRUE && packetsProcessed < 10) {
        // Convert subtype number to human-readable name
        const char* subtypeStr;
        switch(p.frameSubtype) {
            case 0:  subtypeStr = "Association Request"; break;
            case 1:  subtypeStr = "Association Response"; break;
            case 2:  subtypeStr = "Reassociation Request"; break;
            case 3:  subtypeStr = "Reassociation Response"; break;
            case 4:  subtypeStr = "Probe Request"; break;
            case 5:  subtypeStr = "Probe Response"; break;
            case 6:  subtypeStr = "Timing Advertisement"; break;
            case 7:  subtypeStr = "Reserved (7)"; break;
            case 8:  subtypeStr = "Beacon"; break;
            case 9:  subtypeStr = "ATIM"; break;
            case 10: subtypeStr = "Disassociation"; break;
            case 11: subtypeStr = "Authentication"; break;
            case 12: subtypeStr = "Deauthentication"; break;
            case 13: subtypeStr = "Action"; break;
            case 14: subtypeStr = "Action No Ack"; break;
            case 15: subtypeStr = "Reserved (15)"; break;
            default: subtypeStr = "Unknown";
        }
        
        // Print the packet as JSON
        // Serial.printf is SAFE here (in main loop, not in ISR)
        Serial.printf(
            "{\"timestamp\": %lu, \"rssi\": %d, \"channel\": %d, "
            "\"mac_src\": \"%02X:%02X:%02X:%02X:%02X:%02X\", "
            "\"mac_dst\": \"%02X:%02X:%02X:%02X:%02X:%02X\", "
            "\"bssid\": \"%02X:%02X:%02X:%02X:%02X:%02X\", "
            "\"type\": \"Management\", \"subtype\": \"%s\", \"ssid\": \"%s\"}\n",
            p.timestamp, p.rssi, p.channel,
            p.macSrc[0], p.macSrc[1], p.macSrc[2], p.macSrc[3], p.macSrc[4], p.macSrc[5],
            p.macDst[0], p.macDst[1], p.macDst[2], p.macDst[3], p.macDst[4], p.macDst[5],
            p.bssid[0], p.bssid[1], p.bssid[2], p.bssid[3], p.bssid[4], p.bssid[5],
            subtypeStr, p.ssid
        );
        
        packetsProcessed++;
    }
    
    // TASK 3: Small delay to let FreeRTOS do its thing
    delay(1);
}
```

**Why limit to 10 packets per loop?** If we processed ALL packets in one loop, we might never get to channel hopping, and the ESP32 would miss everything on other channels. Processing 10 packets (takes about 10ms), then looping back around, keeps things balanced.

### Channel Hopping Explained

Wi-Fi 2.4GHz has 13 channels (1 through 13). If we only listened on channel 1, we'd miss everything on channels 2-13. By hopping every 200ms, we hear a sample of ALL traffic:

```
Time:    0ms    200ms   400ms   600ms   800ms   1000ms
         Ch1    Ch2     Ch3     Ch4     Ch5     Ch6 ...
         │      │       │       │       │       │
Traffic: ████   ██     █████   █       ███     ██
         (sample)(sample)(sample)(sample)(sample)(sample)
```

We don't hear everything, but we get a good picture of what's happening across all channels.

---

## 8. Python Serial Reader Explained Line-by-Line

This file runs in a **background thread** and handles all USB serial communication.

```python
import serial    # Library for reading/writing serial ports (USB)
import threading # Library for running code in parallel
import json      # Library for parsing JSON text
import time      # Library for delays

class SerialReader:
    """
    A class that reads data from a serial port in a background thread.
    When a JSON packet arrives, it calls a 'callback' function.
    """
    
    def __init__(self, callback):
        """
        Prepare the reader but don't connect yet.
        'callback' is a function that will be called with each packet.
        """
        self.serial = None       # The serial port object (not opened yet)
        self.thread = None       # The background thread (not started yet)
        self.running = False     # Not running yet
        self.callback = callback # Store the callback function

    def connect(self, port, baudrate):
        """
        Open a serial connection to the ESP32.
        'port' is like 'COM5' (Windows) or '/dev/ttyUSB0' (Linux/Mac).
        'baudrate' is the speed (115200).
        """
        try:
            # Open the serial port
            # timeout=1 means: when reading, wait at most 1 second for data
            self.serial = serial.Serial(port, baudrate, timeout=1)
            self.running = True
            
            # Create and start a 'daemon' thread
            # Daemon = automatically stops when the main program exits
            # target=self.read_loop = the function this thread will run
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()
            
            return True  # Success!
        except Exception as e:
            print(f"Error connecting to serial: {e}")
            return False  # Failed

    def disconnect(self):
        """Close the serial connection and stop the thread."""
        self.running = False  # Signal the thread to stop
        
        if self.thread:
            self.thread.join(timeout=2)  # Wait up to 2 seconds for it to stop
        
        if self.serial and self.serial.is_open:
            self.serial.close()  # Close the USB port

    def read_loop(self):
        """
        This function runs in a SEPARATE THREAD forever.
        It reads lines from serial and parses them as JSON.
        """
        while self.running and self.serial and self.serial.is_open:
            try:
                # Read ONE line from the serial port
                # This BLOCKS (waits) until a full line (ending with \n) arrives
                # The GUI is NOT blocked because this is in a separate thread!
                line = self.serial.readline()
                
                # Convert bytes to text, remove whitespace
                text = line.decode('utf-8', errors='ignore').strip()
                
                if text:
                    # Check if this looks like JSON (starts with { and ends with })
                    if text.startswith('{') and text.endswith('}'):
                        try:
                            # Parse JSON string into a Python dictionary
                            packet_data = json.loads(text)
                            
                            # Call the callback function (which sends to GUI)
                            self.callback(packet_data)
                        except json.JSONDecodeError:
                            # JSON was malformed — print error and continue
                            print(f"Failed to parse JSON: {text}")
                    else:
                        # Not JSON — probably a debug message from ESP32
                        print(f"ESP32: {text}")
            except Exception as e:
                print(f"Serial read error: {e}")
                time.sleep(1)  # Wait before retrying
```

### Threading Explained

```
MAIN THREAD (GUI):                    SERIAL THREAD:
─────────────────────────             ────────────────────────
Draw window                          Open serial port
Create widgets                       Start infinite loop:
│                                    │
├── click CONNECT                    ├── readline() ← BLOCKS here
│                                    │
├── on_click:                        │   (waiting for data...)
│   create SerialReader              │
│   reader.connect()                 │
│       start thread ───────────────►│
│                                    │   Data arrives!
│   return immediately                │   json.loads(line)
│   (thread runs in background)      │   callback(packet)
│                                    │       │
│   ┌──────────────────────────────┐ │       │
│   │  UI stays RESPONSIVE         │ │       │
│   │  (buttons, scroll, etc.)     │ │       ▼
│   └──────────────────────────────┘ │   packet_queue.put(packet)
│                                    │
│   (250ms later)                    │   readline() ← BLOCKS again
│   process_packet_queue()           │
│   packet_queue.get_nowait() ◄──────┤
│   update treeview                  │
│   update stats                     │
│   detect evil twin                 │
│                                    │
│   (250ms later)                    │
│   process_packet_queue() ──────────┤ (keeps running)
│                                    │
```

**Why is this needed?** `serial.readline()` waits for data. If the ESP32 hasn't sent anything yet (quiet channel, or it's in between transmissions), `readline()` would sit there waiting... and waiting... and the entire GUI would freeze. By putting the serial reading in a different thread, the GUI stays alive and clickable.

---

## 9. The Dashboard Explained Line-by-Line

This is the biggest file (`gui/app.py`, 864 lines). Let's break it down into logical sections.

### 9.1 The Window Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  SIDEBAR (fixed 240px)         │     MAIN CONTENT (fills rest)      │
│  ───────────────────────       │  ┌────────────────────────────────┐ │
│  🛡️ Sentinel WIDS              │  │  STATS CARDS (top bar)         │ │
│                                 │  │  ┌────────┐ ┌────────┐ ┌────┐ │ │
│  [COM Port: ________]          │  │  │TOTAL   │ │DEAUTH  │ │ALRT│ │ │
│  [Baud Rate: 115200]           │  │  │ 1,234  │ │   56   │ │  3 │ │ │
│                                 │  │  └────────┘ └────────┘ └────┘ │ │
│  [ CONNECT  ]                   │  ├────────────────────────────────┤ │
│                                 │  │  LIVE TRAFFIC STREAM           │ │
│  ● Disconnected                 │  │  [Search...] ☑B ☑P ☑D ⏸ 🗑   │ │
│                                 │  │  ┌───────────────────────────┐ │ │
│  [ VIEW ALERTS ]               │  │  │TIME   RSSI CH NETWORK ... │ │ │
│                                 │  │  │12:01  -45  6 Coffee  ... │ │ │
│                                 │  │  │12:01  -67  1 Home    ... │ │ │
│                                 │  │  │12:01  -55 11 Office  ... │ │ │
│                                 │  │  │...                        │ │ │
│                                 │  │  └───────────────────────────┘ │ │
└─────────────────────────────────────┴────────────────────────────────┘
```

### 9.2 Data Structures (The "Memory" of the App)

```python
# === These are like the app's notebooks ===

# 1. Network name lookup: MAC address → Network Name
self.network_map = {
    "50:3E:AA:12:34:56": "Smith_Family_WiFi",
    "AA:BB:CC:DD:EE:FF": "CoffeeShop"
}

# 2. Reverse lookup: Network Name → Set of MACs using it
self.ssid_to_bssid = {
    "Smith_Family_WiFi": {"50:3E:AA:12:34:56", "02:00:00:AB:CD:EF"},
    "CoffeeShop":        {"AA:BB:CC:DD:EE:FF"}
}

# 3. Which channel is each AP on?
self.bssid_channel = {
    "50:3E:AA:12:34:56": 6,
    "02:00:00:AB:CD:EF": 11
}

# 4. Signal history (last 20 readings per MAC)
# deque = a list with a max size; old values fall off
self.bssid_rssi = {
    "50:3E:AA:12:34:56": deque([-45, -44, -46, -43, -45, ...], maxlen=20),
    "02:00:00:AB:CD:EF": deque([-72, -68, -75, -70, -71, ...], maxlen=20)
}

# 5. When did we first see each MAC?
self.bssid_first_seen = {
    "50:3E:AA:12:34:56": 1234567890.5,  # Unix timestamp
    "02:00:00:AB:CD:EF": 1234567898.2   # 8 seconds later!
}

# 6. How many packets have we seen from each MAC?
self.bssid_seen_count = {
    "50:3E:AA:12:34:56": 152,
    "02:00:00:AB:CD:EF": 37
}

# 7. Whitelist (persisted to file) — MACs we trust
self.whitelist = {
    "Starbucks_WiFi": {"AA:AA:AA:BB:BB:BB", "CC:CC:CC:DD:DD:DD"}
}

# 8. Alert history
self.alerts_list = [
    {
        "time": "2024-01-15 12:01:23",
        "type": "Evil Twin [HIGH 85%]",
        "severity": "Critical",
        "ssid": "CoffeeShop",
        "rogue_mac": "02:00:00:AB:CD:EF",
        "legit_mac": "50:3E:AA:12:34:56",
        "details": "Channel mismatch | RSSI anomaly | LAA MAC",
        "seen_count": 7
    },
    ...
]

# 9. Thread-safe packet queue (bridge between threads)
self.packet_queue = queue.Queue()
```

### 9.3 The Stats Cards

```python
def create_stat_card(self, parent, title, value, col, highlight_color):
    """
    Creates a single "card" showing a statistic.
    parent = the frame to put it in
    title = "TOTAL PACKETS"
    value = "0" (will be updated)
    col = which column (0, 1, or 2)
    highlight_color = color for the number (green, amber, red)
    """
    card = ctk.CTkFrame(parent, fg_color="#18181b", corner_radius=12, height=110)
    card.grid(row=0, column=col, padx=10, sticky="ew")
    card.grid_propagate(False)  # Don't let content resize the card
    
    # Title label (small, gray)
    title_lbl = ctk.CTkLabel(card, text=title, 
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color="#a1a1aa")
    title_lbl.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
    
    # Value label (big, colored number)
    val_lbl = ctk.CTkLabel(card, text=value,
                           font=ctk.CTkFont(size=36, weight="bold"),
                           text_color=highlight_color)
    val_lbl.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
    
    return val_lbl  # Return the label so we can update it later
```

### 9.4 The Packet Processing Engine

This is the heart of the app. It runs every 250ms and processes packets.

```python
def process_packet_queue(self):
    """Called every 250ms by the GUI main loop."""
    packets_to_insert = []  # Accumulate packets for batch insert
    
    try:
        # Process up to 100 packets per batch (to avoid UI lag)
        for _ in range(100):
            packet = self.packet_queue.get_nowait()  # Non-blocking get
            
            # ─── UPDATE COUNTERS ───
            self.total_packets += 1
            subtype = packet.get('subtype', '')
            
            # ─── DEAUTH DETECTION ───
            if subtype == "Deauthentication":
                self.deauth_count += 1
                # Alert every 10 deauths (anti-flooding)
                if self.deauth_count % 10 == 0:
                    self.alert_count += 1
                    self.alerts_list.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Deauth Flood",
                        "severity": "High",
                        "details": f"Target MAC: {packet.get('mac_dst', 'Unknown')}"
                    })
            
            # ─── EXTRACT PACKET FIELDS ───
            bssid = packet.get('bssid', '')
            ssid = packet.get('ssid', '')
            mac_src = packet.get('mac_src', '')
            mac_dst = packet.get('mac_dst', '')
            channel = packet.get('channel', None)
            rssi = packet.get('rssi', None)
            
            # ─── TRACK NETWORKS ───
            if ssid and bssid:
                self.network_map[bssid] = ssid  # MAC → name
                
                # First time seeing this MAC?
                if bssid not in self.bssid_first_seen:
                    self.bssid_first_seen[bssid] = time.time()
                
                # Track channel
                if channel:
                    self.bssid_channel[bssid] = int(channel)
                
                # Track RSSI history (rolling window of 20)
                if rssi is not None:
                    try:
                        if bssid not in self.bssid_rssi:
                            self.bssid_rssi[bssid] = collections.deque(maxlen=20)
                        self.bssid_rssi[bssid].append(int(rssi))
                    except (ValueError, TypeError):
                        pass
                
                # Track which SSID uses which BSSIDs
                if ssid not in self.ssid_to_bssid:
                    self.ssid_to_bssid[ssid] = set()
                self.ssid_to_bssid[ssid].add(bssid)
                
                # Increment packet count for this BSSID
                self.bssid_seen_count[bssid] = self.bssid_seen_count.get(bssid, 0) + 1
                
                # ─── EVIL TWIN DETECTION ───
                # (Explained in detail in Section 10)
                if self.should_check_evil_twin(ssid, bssid):
                    score, reasons = self._score_evil_twin(ssid, bssid, channel, rssi)
                    if score > 0:
                        self.handle_evil_twin_alert(ssid, bssid, score, reasons)
            
            # ─── PREPARE ROW FOR DISPLAY ───
            # Determine network name to show
            network_name = self.network_map.get(bssid, "")
            
            # Apply evil twin label if applicable
            if packet.get('is_evil_twin'):
                if bssid == packet.get('et_rogue_mac'):
                    network_name = f"🔴 ROGUE AP — {network_name}"
                elif bssid == packet.get('et_legit_mac'):
                    network_name = f"✅ LEGITIMATE — {network_name}"
            
            packet['network_name'] = network_name
            
            # Check if this packet should be shown (filtering)
            if not self.should_show_packet(packet):
                continue
            
            packets_to_insert.append(packet)
            
    except queue.Empty:
        pass  # No more packets in queue — normal
    
    # ─── UPDATE DISPLAY ───
    if packets_to_insert:
        # Update stat cards
        self.stat_packets.configure(text=str(self.total_packets))
        self.stat_deauth.configure(text=str(self.deauth_count))
        self.stat_alerts.configure(text=str(self.alert_count))
        
        # Insert rows into treeview
        for packet in packets_to_insert:
            self.insert_packet_row(packet)
        
        # Trim treeview to 500 rows maximum
        children = self.tree.get_children()
        if len(children) > 500:
            for child in children[500:]:
                self.tree.delete(child)
    
    # Schedule the next batch
    self.after(250, self.process_packet_queue)
```

---

## 10. Evil Twin Detection (The Smart Part)

This is the most sophisticated part of the system. It uses **8 different signals** (pieces of evidence) to determine if a BSSID is a fake version of a real network.

### 10.1 The Core Problem

```
LEGITIMATE AP (Router):                  SUSPICIOUS BSSID (Hacker):
  SSID: "CoffeeShop_Free"                  SSID: "CoffeeShop_Free"
  BSSID: 50:3E:AA:12:34:56                 BSSID: 02:00:00:AB:CD:EF
  OUI: TP-Link ✓                           OUI: Locally Administered ✗
  Channel: 6                               Channel: 11
  Avg RSSI: -45 dBm                        Avg RSSI: -72 dBm
  First seen: 12:00:00                     First seen: 12:05:30 (5 min later)
  RSSI variance: 2.1 (stable)              RSSI variance: 35.8 (unstable)
```

**Question:** Is `02:00:00:AB:CD:EF` an evil twin of `50:3E:AA:12:34:56`?  
**Answer:** Probably yes. Let's score it!

### 10.2 Signal 1: BSSID Conflict (+50 Base)

```python
# If an SSID has MORE THAN ONE BSSID, that's suspicious
known_bssids = self.ssid_to_bssid.get(ssid, set()) - {bssid}
if not known_bssids:
    # Only one BSSID for this SSID — no conflict, not an evil twin
    return 0, []

# Base score: there IS a conflict
score += 50
reasons.append(f"SSID '{ssid}' broadcasted by multiple MACs")
```

**Analogy:** You see two stores with the same name on the same street. One is the real store, one is a fake. The fact that there are TWO is suspicious.

### 10.3 Signal 2: Channel Mismatch (+20)

```python
other_channels = {self.bssid_channel[b] for b in known_bssids if b in self.bssid_channel}
if channel and other_channels and int(channel) not in other_channels:
    score += 20
    reasons.append(f"Channel mismatch (this: {channel}, known: {sorted(other_channels)})")
```

**Analogy:** The real store is on the first floor. The "fake" store is on the third floor. Why would a real store move floors? Suspicious.

**Why this works:** Real routers pick a channel and stay there. A hacker's laptop running a fake AP can be on any channel.

### 10.4 Signal 3: RSSI Anomaly (+20)

```python
if rssi is not None:
    try:
        rssi_val = int(rssi)
        other_rssi_avgs = []
        for b in known_bssids:
            if b in self.bssid_rssi and self.bssid_rssi[b]:
                other_rssi_avgs.append(sum(self.bssid_rssi[b]) / len(self.bssid_rssi[b]))
        if other_rssi_avgs:
            avg_known = sum(other_rssi_avgs) / len(other_rssi_avgs)
            diff = abs(rssi_val - avg_known)
            if diff >= 15:  # 15 dBm = significant difference
                score += 20
                reasons.append(f"RSSI anomaly ({rssi_val} dBm vs known avg {avg_known:.0f} dBm, Δ{diff:.0f} dBm)")
    except (ValueError, TypeError):
        pass
```

**Analogy:** The real store's cash register is 5 feet away. The fake store's register sounds like it's 50 feet away. They're not in the same place.

**Why this works:** The hacker's laptop and the real router are in different physical locations. The signal strength difference reveals this.

### 10.5 Signal 4: OUI Classification (+10 or +5)

```python
# What kind of hardware is this MAC from?
oui_class = self._classify_oui(bssid)
known_oui_classes = [self._classify_oui(b) for b in known_bssids]

if oui_class == "laptop" and "router" in known_oui_classes:
    score += 10
    reasons.append("MAC OUI belongs to a laptop/USB NIC (typical of rogue APs)")
elif oui_class == "unknown" and "router" in known_oui_classes:
    score += 5
    reasons.append("MAC OUI is unrecognized (possibly randomized or custom firmware)")
```

**Why this works:** Real routers have MAC addresses from known router manufacturers (TP-Link, Netgear, ASUS, Cisco). Hackers use laptops with Intel/Realtek Wi-Fi chips or USB dongles (Alfa, Atheros). If ALL known BSSIDs are "router" type and THIS one is "laptop" type, it's likely the hacker.

```python
def _classify_oui(self, mac: str) -> str:
    """Returns 'router', 'laptop', or 'unknown' based on first 3 MAC octets."""
    prefix = mac.lower()[:8]  # e.g., "50:3e:aa"
    if prefix in self.ROUTER_OUIS:
        return "router"
    if prefix in self.LAPTOP_NIC_OUIS:
        return "laptop"
    return "unknown"
```

The OUI tables contain hundreds of known vendor prefixes. Examples:
```python
# Router OUIs (partial list):
ROUTER_OUIS = {
    "50:3e:aa",  # TP-Link
    "00:14:6c",  # Netgear
    "00:1a:a1",  # Cisco/Linksys
    "00:0c:42",  # MikroTik
    "00:27:22",  # Ubiquiti
    ...
}

# Laptop NIC OUIs:
LAPTOP_NIC_OUIS = {
    "00:21:5c",  # Intel
    "00:e0:4c",  # Realtek
    "00:c0:ca",  # Alfa Network (popular pentest adapter)
    "00:03:7f",  # Atheros
    ...
}
```

### 10.6 Signal 5: Locally Administered Address (+40)

```python
def _is_locally_administered(self, mac: str) -> bool:
    """
    Check if the MAC was spoofed by software.
    Real hardware MACs never have bit 1 of the first byte set.
    """
    try:
        first_octet = int(mac.split(':')[0], 16)  # First byte as number
        return bool(first_octet & 0x02)  # Check if bit 1 is set
    except (ValueError, IndexError):
        return False
```

**How MAC addresses work:**
```
MAC:  02:00:00:AB:CD:EF
First byte: 0x02
Binary:     0000 0010
                   ↑
                   Bit 1 = 1 → Locally Administered!
```

**Analogy:** Every real product has a serial number from the factory. But you can also write your own serial number with a marker. Locally Administered MACs are the "written with a marker" version.

**Why this is the STRONGEST signal (+40):**
- Real routers NEVER use locally administered MACs
- Hacking tools like `airbase-ng`, `hostapd`, `macchanger` commonly produce them
- If a MAC is locally administered, it is almost certainly spoofed

### 10.7 Signal 6: Late Joiner (+15)

```python
if bssid in self.bssid_first_seen and other_bssids:
    my_ts = self.bssid_first_seen[bssid]
    other_ts = [self.bssid_first_seen[b] for b in other_bssids if b in self.bssid_first_seen]
    if other_ts and my_ts > min(other_ts) + 5:  # 5+ seconds later
        score += 15
        reasons.append("Appeared after the other BSSID was already broadcasting")
```

**Analogy:** The real store opened at 8 AM. At 8:05 AM, a second store with the same name suddenly appears. That's suspicious — real stores don't duplicate in 5 minutes.

**Why this works:** Hackers typically start their Evil Twin AFTER seeing the real network. If both BSSIDs appeared at the exact same time, they might be legitimate (dual-band, mesh, etc.).

### 10.8 Signal 7: Weaker RSSI (+15)

```python
if bssid in self.bssid_rssi and self.bssid_rssi[bssid]:
    my_rssi_list = list(self.bssid_rssi[bssid])
    my_avg_rssi = sum(my_rssi_list) / len(my_rssi_list)
    other_rssi_avgs = [
        sum(self.bssid_rssi[b]) / len(self.bssid_rssi[b])
        for b in other_bssids if b in self.bssid_rssi and self.bssid_rssi[b]
    ]
    if other_rssi_avgs:
        avg_other = sum(other_rssi_avgs) / len(other_rssi_avgs)
        if my_avg_rssi < avg_other - 10:  # 10 dBm weaker
            score += 15
            reasons.append(f"Weaker signal ({my_avg_rssi:.0f} dBm vs {avg_other:.0f} dBm)")
```

**Analogy:** The real radio station broadcasts at 50,000 watts. The pirate radio station broadcasts at 100 watts from someone's basement. You can hear both, but one is much weaker.

**Why this works:** A real router has proper antennas designed for maximum coverage. A hacker's laptop has tiny internal antennas or a USB dongle. The signal from the laptop will almost always be weaker.

### 10.9 Signal 8: High RSSI Variance (+10)

```python
if len(my_rssi_list) >= 4:
    mean = my_avg_rssi
    variance = sum((x - mean) ** 2 for x in my_rssi_list) / len(my_rssi_list)
    if variance > 30:  # High variance = unstable signal
        score += 10
        reasons.append(f"Unstable signal (variance {variance:.1f} dBm²)")
```

**What is variance?** It measures how much the signal is bouncing around.

| RSSI Readings | Variance | Meaning |
|---------------|----------|---------|
| -45, -44, -46, -45, -43 | 0.8 | Very stable (mounted router) |
| -72, -68, -75, -70, -71 | 5.1 | Slightly unstable |
| -55, -45, -70, -60, -50 | **95** | Very unstable (laptop moving!) |

**Analogy:** A lamp on a table has a steady light. A lamp being carried around the room has a flickering, changing light. The router is the steady lamp; the hacker's laptop is the moving lamp.

**Why this works:** Routers are stationary. Their signal is consistent. A hacker with a laptop might shift position, or the USB dongle might wiggle, causing signal fluctuations.

### 10.10 Putting It All Together: The Full Score

```
SCORE CARD for BSSID 02:00:00:AB:CD:EF
SSID: "CoffeeShop_Free"

+50  BSSID Conflict (2 BSSIDs for same SSID)
     → "SSID 'CoffeeShop_Free' broadcasted by multiple MACs"

+20  Channel Mismatch
     → "Channel mismatch (this: 11, known: [6])"

+20  RSSI Anomaly
     → "RSSI anomaly (-72 dBm vs known avg -45 dBm, Δ27 dBm)"

+10  OUI = Laptop NIC
     → "MAC OUI belongs to a laptop/USB NIC (typical of rogue APs)"

+40  Locally Administered MAC
     → "Locally administered MAC — strongly suggests MAC spoofing"

+15  Late Joiner
     → "Appeared after the other BSSID was already broadcasting"

+15  Weaker RSSI
     → "Weaker signal (-72 dBm vs -45 dBm)"

+10  High RSSI Variance
     → "Unstable signal (variance 35.8 dBm²)"

═══════════════════════════════════════════════════════════
RAW SCORE: 180 → CAPPED AT 100 → HIGH CONFIDENCE (Critical)
```

### 10.11 Confidence Levels

```python
if score >= 70:
    label = "HIGH"
    severity = "Critical"
    tag = "eviltwin_high"      # Red background in treeview
elif score >= 40:
    label = "MEDIUM"
    severity = "High"
    tag = "eviltwin_medium"    # Orange background
else:
    label = "LOW"
    severity = "Low"
    tag = "eviltwin_low"       # Yellow background
```

### 10.12 Mesh/Extender Suppression

Sometimes, legitimate networks have multiple BSSIDs for the same SSID:
- **Mesh networks** (Google Nest, Eero): Multiple nodes, one network name
- **Wi-Fi extenders**: Repeat the signal with a different MAC
- **Dual-band routers**: 2.4GHz and 5GHz bands (but our ESP32 only captures 2.4GHz, so this doesn't apply)

To avoid false positives:

```python
# Are ALL BSSIDs from router manufacturers?
both_router_oui = all(
    self._classify_oui(b) == "router" for b in all_bssids
)

# Are NONE locally administered?
neither_is_laa = all(
    not self._is_locally_administered(b) for b in all_bssids
)

# Is the score difference small?
score_diff = top_score - bottom_score

# If all three are true → likely a mesh/extender, not an attack
is_likely_mesh = both_router_oui and neither_is_laa and score_diff < 20
```

If it's likely mesh, we:
- Cap the score at 30
- Set severity to "Low"
- Show a note: "This may be a mesh network or Wi-Fi extender. Verify manually."

### 10.13 The Alert Throttle

To avoid a flood of alerts for the same evil twin (the ESP32 sees packets from the same networks many times per second):

```python
current_time = time.time()
last_alert = self.last_eviltwin_alert_time.get(bssid, 0)

# Only alert every 10 seconds for the same MAC
if current_time - last_alert >= 10:
    # ... create or update alert ...
    self.last_eviltwin_alert_time[bssid] = current_time
```

Also: if the same alert is already in the list, we **update** its `seen_count` and `last_seen` time instead of creating a new card:

```python
alert_key = (ssid, rogue_mac)
if alert_key in self.eviltwin_alert_index:
    idx = self.eviltwin_alert_index[alert_key]
    self.alerts_list[idx]["seen_count"] += 1
    self.alerts_list[idx]["last_seen"] = datetime.now()
    self.alerts_list[idx]["score"] = score
```

### 10.14 Identifying Which Is the Rogue

When we have multiple BSSIDs for one SSID, we need to figure out WHICH one is the fake. The `_identify_rogue` function scores every BSSID and picks the highest scorer as the rogue:

```python
def _identify_rogue(self, ssid: str):
    all_bssids = list(self.ssid_to_bssid.get(ssid, set()))
    if len(all_bssids) < 2:
        return None, None, [], False
    
    # Score every BSSID
    scored = []
    for b in all_bssids:
        s, r = self._rogue_score_bssid(b, ssid)
        scored.append((s, b, r))
    
    # Sort: highest rogue score first
    scored.sort(reverse=True)
    suspected_rogue = scored[0][1]   # Highest score = most likely rogue
    suspected_legit = scored[-1][1]  # Lowest score = most likely legit
    rogue_reasons = scored[0][2]
    
    return suspected_rogue, suspected_legit, rogue_reasons, is_likely_mesh
```

---

## 11. Deauth Attack Detection

```python
if subtype == "Deauthentication":
    self.deauth_count += 1
    
    # Alert every 10 deauths (prevents alert flooding)
    if self.deauth_count % 10 == 0:
        self.alert_count += 1
        self.alerts_list.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Deauth Flood",
            "severity": "High",
            "details": f"Target MAC: {packet.get('mac_dst', 'Unknown')}"
        })
```

**Why every 10 deauths?** A single deauth packet can be legitimate (e.g., a router kicking off a device that's no longer connected). But a flood of deauths (10+) is almost certainly an attack. The threshold prevents false positives from occasional legitimate deauths.

---

## 12. Whitelist: How to Stop False Alarms

### 12.1 What Is Whitelisting?

If our system flags a network as an Evil Twin, but it's actually a legitimate mesh network or extender, you can **trust** it. The whitelist remembers your decision across app restarts.

### 12.2 How to Trust a Network

1. In the dashboard, click **VIEW ALERTS** (red button in sidebar)
2. Find the alert card for the network
3. Click **"✅ Trust — Mark as False Positive (Mesh/Extender)"**

### 12.3 What Happens When You Trust

```python
def _trust_ssid_bssids(self, ssid: str, bssids: list):
    # Add all BSSIDs for this SSID to the whitelist
    if ssid not in self.whitelist:
        self.whitelist[ssid] = set()
    self.whitelist[ssid].update(bssids)
    self._save_whitelist()  # Save to file!
```

This creates (or updates) `ids/whitelist.json`:

```json
{
  "CoffeeShop_Free_WiFi": [
    "AA:BB:CC:DD:EE:FF",
    "11:22:33:44:55:66"
  ],
  "Home_Network": [
    "AA:AA:AA:AA:AA:AA",
    "BB:BB:BB:BB:BB:BB"
  ]
}
```

### 12.4 How the Whitelist Is Used

Every time a packet arrives, before running Evil Twin detection:

```python
# Check whitelist FIRST
trusted = self.whitelist.get(ssid, set())
if bssid in trusted:
    pass  # Skip — this is trusted!
elif len(self.ssid_to_bssid[ssid]) > 1 and self.bssid_seen_count.get(bssid, 0) >= 3:
    # Only then run evil twin detection
    score, reasons = self._score_evil_twin(ssid, bssid, channel, rssi)
    ...

```

**Why minimum 3 sightings?** The system waits for 3 packets from a BSSID before flagging it. This prevents a single stray packet from triggering a false alarm.

---

## 13. Complete Glossary (A-Z)

### A
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **AP** | Access Point | A device that creates a Wi-Fi network | Router, hotspot |
| **Arduino** | — | A platform for programming microcontrollers | We use it to program the ESP32 |

### B
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **Baud** | — | Speed of data transfer over serial | 115200 baud ≈ 11,500 characters/second |
| **BSSID** | Basic Service Set ID | The MAC address of a Wi-Fi access point | `50:3E:AA:12:34:56` |

### C
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **Callback** | — | A function that gets called when something happens | Our callback runs when a packet arrives |
| **Channel** | — | A specific frequency range within 2.4GHz Wi-Fi | Channels 1-13 |
| **COM port** | Communications Port | A name for a serial connection on Windows | `COM5`, `COM3` |
| **CustomTkinter** | — | A Python library that creates modern-looking GUIs | Our dashboard is built with it |

### D
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **Daemon thread** | — | A background thread that auto-stops when the program exits | Our SerialReader thread |
| **dBm** | Decibel-milliwatts | How strong a Wi-Fi signal is (measured in negative numbers) | -30 = strong, -90 = weak |
| **Deauth** | Deauthentication | A frame that tells a device to leave the network | Attackers flood these to disrupt Wi-Fi |
| **Deque** | Double-ended queue | A list with a maximum size (oldest items removed automatically) | We store last 20 RSSI readings in a deque |

### E
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **ESP32** | — | A $5 microcontroller chip with built-in Wi-Fi and Bluetooth | Our sniffer hardware |
| **Evil Twin** | — | A fake Wi-Fi network that impersonates a real one | Hacker's "Starbucks_WiFi" near a Starbucks |

### F
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **Frame** | — | Another name for a Wi-Fi packet | Beacon frame, Deauth frame |
| **FreeRTOS** | Free Real-Time Operating System | A tiny OS for microcontrollers that handles multiple tasks | Manages our queue and timing |

### I
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **IDE** | Integrated Development Environment | A program for writing and uploading code | Arduino IDE |
| **ISR** | Interrupt Service Routine | A function that runs instantly when hardware needs attention | Called for every Wi-Fi packet |

### J
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **JSON** | JavaScript Object Notation | A text format for storing data as key-value pairs | `{"rssi": -45, "channel": 6}` |

### L
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **LAA** | Locally Administered Address | A MAC address that was spoofed by software, not from a factory | `02:00:00:XX:XX:XX` |

### M
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **MAC** | Media Access Control | A unique hardware address assigned to every Wi-Fi chip | `AA:BB:CC:DD:EE:FF` |
| **Management Frame** | — | Wi-Fi packets that handle connections (not data) | Beacon, Probe, Deauth, Auth |
| **Mesh Network** | — | Multiple APs that share one network name (legitimate multi-BSSID) | Google Nest, Eero |

### O
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **OUI** | Organizationally Unique Identifier | First 3 bytes of a MAC that identify the manufacturer | `50:3E:AA` = TP-Link |

### P
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **Promiscuous Mode** | — | A Wi-Fi mode where the card hears ALL packets, not just its own | The ESP32's "spy mode" |
| **pyserial** | — | A Python library for reading/writing serial ports | Used to communicate with ESP32 |

### Q
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **Queue** | — | A "buffer" that holds items between two processes | FreeRTOS queue (50 packets), Python queue (thread-safe) |

### R
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **RSSI** | Received Signal Strength Indicator | How strong a signal is | -45 dBm (good), -80 dBm (weak) |

### S
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **Serial** | — | A way to transfer data one bit at a time over USB | ESP32 sends JSON over Serial |
| **SSID** | Service Set Identifier | The human-readable name of a Wi-Fi network | "Starbucks_WiFi", "Home_Network" |

### T
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **Thread** | — | A way to run multiple pieces of code at the same time | SerialReader runs in a background thread |
| **Treeview** | — | A table widget that shows data in rows and columns | Our packet display table |
| **ttyUSB** | — | A serial port name on Linux/Mac | `/dev/ttyUSB0` |

### W
| Term | Full Name | Simple Explanation | Example |
|------|-----------|-------------------|---------|
| **WDT** | Watchdog Timer | A safety timer that resets the ESP32 if the program hangs | Prevents the ESP32 from freezing forever |

---

## 14. Troubleshooting: Everything That Can Go Wrong

### Problem 1: "No packets appear in the dashboard"

**Checklist (in order):**

| # | Check | How to Fix |
|---|-------|------------|
| 1 | Is the ESP32 plugged in? | Check USB connection; try a different USB port |
| 2 | Is the COM port correct? | In Arduino IDE: **Tools → Port** — that's your COM port |
| 3 | Is another app using the port? | Close Arduino Serial Monitor, Putty, etc. |
| 4 | Is the baud rate 115200? | Change if different (both code and GUI must match) |
| 5 | Is the firmware uploaded? | Re-upload `esp32_sniffer.ino` |
| 6 | Is the USB cable data-capable? | Some cables are "charge only" — use a different cable |
| 7 | Is there Wi-Fi traffic? | Move near a router or turn on your phone's hotspot |

### Problem 2: "ESP32 keeps restarting / serial prints garbage"

```
Message: "ets Jun  8 2016 00:22:57"
         "rst:0x1 (POWERON_RESET),boot:0x13..."
```

This is a **Watchdog Timer (WDT) reset** or a bad serial connection.

| Cause | Fix |
|-------|-----|
| ESP32 running too slow | You may have changed the CPU speed — set it back to 240MHz in Arduino IDE |
| Serial.println in ISR | Make sure you're NOT printing in the ISR function |
| Queue overflow | Normal — the code drops packets instead of crashing |
| Bad baud rate | Make sure both ESP32 and GUI use 115200 |
| USB power insufficient | Try a powered USB hub or a different USB port |

### Problem 3: "Error: No module named 'customtkinter'"

```bash
# Make sure you ran this in the WIDS folder:
pip install -r requirements.txt

# If that doesn't work, try:
python -m pip install customtkinter pyserial
```

### Problem 4: "The GUI is laggy"

The code already batches packets (100 every 250ms). If you're still seeing lag:

1. Reduce channel hopping frequency (on ESP32): Change `CHANNEL_HOP_INTERVAL` from 200 to 500ms
2. Reduce batch size (in Python): Change `for _ in range(100)` to `for _ in range(50)`
3. Reduce treeview max rows: Change `self.max_rows = 500` to `self.max_rows = 200`

### Problem 5: "No Evil Twin detections"

Evil Twin detection requires:

1. **Same SSID from 2+ BSSIDs** — your environment must have multi-AP networks
2. **Minimum 3 sightings** of the candidate BSSID (prevents false positives)
3. **A non-empty SSID** — Beacons and Probe Responses only

Test it yourself:
- Open your phone's hotspot with a common name like "TestWiFi"
- Wait for the ESP32 to see it
- Then open a second hotspot with the SAME name on another device

### Problem 6: "Too many false Evil Twin alerts"

Some real networks look like Evil Twins:

| Network Type | Why It Looks Suspicious | Our Solution |
|-------------|------------------------|--------------|
| Mesh network (Google Nest, Eero) | Multiple nodes, same SSID, different BSSIDs | Mesh suppression logic marks these LOW |
| Wi-Fi extender | Extends network with its own MAC | Same as mesh — LOW confidence |
| Dual-band router (2.4+5GHz) | Different BSSIDs for each band | Our ESP32 only listens to 2.4GHz, so only one BSSID is seen — not an issue |

**Solution:** Click "Trust — Mark as False Positive" in the Alerts window. The whitelist persists across restarts.

### Problem 7: "I see lots of Deauth alerts"

Deauth frames in small numbers can be normal:
- A phone leaving the network
- A router cleaning up stale connections
- Channel interference

But a flood of 10+ deauths in a short time is an attack. Our system only alerts every 10 deauths to avoid false positives.

### Problem 8: "Upload fails / 'Connecting...' hangs forever"

This is the most common ESP32 issue. Fix:

1. **Press and HOLD the BOOT button** on the ESP32
2. While holding, click **Upload** in Arduino IDE
3. When you see `Connecting...` and then `...`, release the button
4. The upload should proceed

If that doesn't work:
- Disconnect and reconnect the USB
- Try a different USB cable
- Try a different USB port
- Make sure you selected the right board (ESP32 Dev Module)

### Problem 9: "Permission denied on Linux/Mac"

```bash
# Add your user to the dialout group (for serial port access):
sudo usermod -a -G dialout $USER

# Then log out and back in (or restart)
```

---

## Quick Reference: File Purposes

| File | What It Does | Lines | Language |
|------|-------------|-------|----------|
| `main.py` | Starts everything, connects components | 24 | Python |
| `ids/serial_reader.py` | Reads USB serial in background thread | 47 | Python |
| `gui/app.py` | Dashboard + detection logic | 864 | Python |
| `esp32_sniffer/esp32_sniffer.ino` | Firmware for the ESP32 | 141 | C++ |
| `requirements.txt` | Python packages needed | 2 | Text |
| `.gitignore` | Files to ignore in git | 4 | Text |
| `README.md` | Original short readme | 66 | Markdown |
| `WIDS_README.md` | This document | — | Markdown |

---

## Project Tree

```
WIDS/
│
├── main.py                    # Entry point — run with: python main.py
├── requirements.txt           # pip install -r requirements.txt
├── .gitignore                 # Ignores __pycache__ and .pyc files
├── README.md                  # Original short documentation
├── WIDS_README.md             # This complete beginner guide
│
├── esp32_sniffer/             # ← ESP32 firmware
│   └── esp32_sniffer.ino      #   Upload this to the ESP32
│
├── ids/                       # ← Intrusion Detection System modules
│   ├── serial_reader.py       #   Background serial reader thread
│   └── whitelist.json         #   Created automatically when you trust networks
│
└── gui/                       # ← Graphical User Interface
    └── app.py                 #   CustomTkinter dashboard
```

---

## Final Words

You now understand the entire Sentinel WIDS project:

- **What it does:** Listens to Wi-Fi traffic and detects attacks
- **How the hardware works:** ESP32 in promiscuous mode with FreeRTOS queue
- **How the software works:** Background thread + thread-safe queue + batch processing
- **How evil twin detection works:** 8 signals scored to find fake networks
- **How to fix problems:** Troubleshooting every common issue

Happy detecting! 🛡️

---

*This project is for educational and defensive purposes only. Only monitor networks you own or have explicit permission to analyze.*
