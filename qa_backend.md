# WIDS Presentation: Backend & System Logic

## Knowledge & Documentation

### Overview
The backend logic is the "brain" of the WIDS. It is responsible for orchestrating the different software components, interfacing with the hardware sniffer, analyzing raw network data, and executing intrusion detection algorithms to identify malicious activity.

### Core Technologies
* **Python 3:** The primary backend language.
* **Scapy:** A powerful Python-based interactive packet manipulation program and library. Used here to intercept and dissect low-level network packets (specifically ARP).
* **PySerial:** Provides the backend with access to the serial ports (COM ports), enabling communication with the ESP32 hardware via USB.
* **JSON:** Used for data serialization, allowing the C++ hardware to easily pass structured data to the Python backend.

### Key Mechanics
1. **Controller Pattern:** The `main.py` file acts as the central Controller. It instantiates the UI (`App`), the `SerialReader`, and the `ARPSniffer`. It sets up the callback pipeline so data flows seamlessly from the sniffers upwards to the UI, maintaining a clean separation of concerns.
2. **ARP Spoof Detection (`arp_sniffer.py`):** This module operates continuously in a background daemon thread. It builds an in-memory mapping table of IP addresses to MAC addresses. It actively monitors for conflicting ARP replies—a key indicator of a Man-in-the-Middle attack.
3. **Serial Data Ingestion (`serial_reader.py`):** This module manages the connection to the ESP32. It reads JSON-formatted strings line-by-line over the serial connection, decodes them into Python dictionaries, handles errors (like corrupted serial data), and passes the clean data to the Controller via callbacks.

---

## Q&A Preparation

### 1. What is the overall software architecture connecting the different components?

**Answer:** We used a centralized Controller architecture in `main.py`. The `Controller` class acts as the "glue". It initializes the hardware interface (`SerialReader`), the software network interface (`ARPSniffer`), and the Frontend (`App`). 
We use a **Callback Pattern**: When `main.py` creates the sniffers, it passes them a function (`self.on_packet_received`). Whenever a sniffer finds data, it calls this function, sending the data up to `main.py`, which then routes it to the GUI. This decouples the sniffers from the GUI.

### 2. How exactly do you detect an ARP Spoofing attack?

**Answer:** ARP spoofing is detected in `ids/arp_sniffer.py`. 
1. We maintain a dictionary called `arp_table` in memory. This maps IP addresses to MAC addresses.
2. We use the `scapy` library to listen for ARP packets (`op == 2`, which means ARP Reply).
3. When an ARP Reply arrives, we look at the Source IP and Source MAC.
4. We check our `arp_table`. If that IP address is already in our table, but the MAC address in the new packet is *different* from what we have stored, it means someone is trying to overwrite the network's ARP cache. We immediately trigger an ARP Spoof alert.

> **Example:** The router is IP `192.168.1.1` and MAC `AA:AA`. We store this. Later, an attacker sends an ARP reply saying "I am `192.168.1.1` and my MAC is `BB:BB`". Our system sees the MAC changed from `AA:AA` to `BB:BB` for the same IP, and flags it.

### 3. How do you handle communication with the ESP32 hardware?

**Answer:** We use the `pyserial` Python library (`ids/serial_reader.py`).
* We connect to the COM port that the ESP32 is plugged into (e.g., 115200 baud rate).
* The ESP32 sends data formatted as a JSON string over the serial cable.
* Our `SerialReader` runs a continuous `while` loop in a background thread, reading line by line.
* We use `json.loads()` to convert the text string into a Python dictionary, making it easy to access fields like `rssi` or `mac_src`.

> **Jargon:** *JSON (JavaScript Object Notation)* is a standard text format for exchanging data. It looks like a Python dictionary: `{"rssi": -50, "type": "Beacon"}`.

### 4. Why are `SerialReader` and `ARPSniffer` running in Threads, and what does `daemon=True` mean?

**Answer:** Both `SerialReader` and `ARPSniffer` involve infinite loops (reading serial ports or sniffing network interfaces). If we ran these on the main program thread, the program would stop on that line of code forever and the GUI would never open. We put them in separate threads so they can work in the background simultaneously.
* `daemon=True` means these threads are "background tasks" tied to the main program. If the user clicks the "X" to close the GUI window (the main thread), the daemon threads will automatically be killed, ensuring a clean shutdown without leaving rogue processes running in the background.

### 5. How do you detect Evil Twin attacks?

**Answer:** We manage this by comparing incoming Beacon frames against a known state or a `whitelist.json`. 
An Evil Twin attack relies on broadcasting the same SSID (network name) as a legitimate network. When our ESP32 captures Beacon frames, the backend looks at the SSID and the BSSID (the MAC address of the router). If we see the SSID "Campus_WiFi" coming from a BSSID that is *not* in our trusted whitelist, we flag it as a potential Rogue AP or Evil Twin.

---

## မြန်မာဘာသာပြန် (Burmese Translation)

### အနှစ်ချုပ် (Overview)
Backend က WIDS ရဲ့ "ဦးနှောက်" လို့ ပြောလို့ရပါတယ်။ ဆော့ဖ်ဝဲ အစိတ်အပိုင်းတွေကို ချိတ်ဆက်ပေးတာ၊ hardware sniffer နဲ့ စကားပြောတာ၊ ဝင်လာတဲ့ raw data တွေကို ခွဲခြမ်းစိတ်ဖြာတာနဲ့ intrusion detection (ကျူးကျော်ဝင်ရောက်မှု ရှာဖွေခြင်း) အယ်လ်ဂိုရီသမ်တွေကို လုပ်ဆောင်ပေးပါတယ်။

### အဓိက နည်းပညာများ (Core Technologies)
* **Python 3:** အဓိက သုံးထားတဲ့ backend programming language ပါ။
* **Scapy:** Network packet တွေကို ဖမ်းယူပြီး ခွဲခြမ်းစိတ်ဖြာဖို့ သုံးတဲ့ Python library တစ်ခုပါ။ (ဒီမှာ ARP packet တွေအတွက် သုံးထားပါတယ်)
* **PySerial:** ESP32 hardware နဲ့ USB ကနေတစ်ဆင့် စကားပြောနိုင်ဖို့ COM port တွေကို အသုံးပြုနိုင်အောင် ကူညီပေးပါတယ်။
* **JSON:** C++ hardware ကနေ Python backend ဆီကို data တွေ ပို့တဲ့အခါ စနစ်တကျ ရှိစေဖို့ (data serialization) သုံးထားပါတယ်။

### အဓိက လုပ်ဆောင်ပုံများ (Key Mechanics)
1. **Controller Pattern:** `main.py` က အရာအားလုံးကို ထိန်းချုပ်ပေးတဲ့ (Orchestrator) နေရာမှာ ရှိပါတယ်။ သူက UI (`App`)၊ `SerialReader` နဲ့ `ARPSniffer` တို့ကို စတင်ပေးပါတယ်။ ပြီးတော့ sniffer တွေကနေ UI ဆီကို data တွေ ချောချောမွေ့မွေ့ ရောက်သွားအောင် callback တွေနဲ့ သေချာချိတ်ဆက်ပေးပါတယ်။
2. **ARP Spoof Detection (`arp_sniffer.py`):** ဒီကောင်လေးက နောက်ကွယ်က daemon thread အနေနဲ့ အမြဲအလုပ်လုပ်နေပါတယ်။ သူက IP နဲ့ MAC address တွဲထားတဲ့ စာရင်း (mapping table) တစ်ခုကို မှတ်ထားပြီး၊ အချင်းချင်း ကွဲလွဲနေတဲ့ ARP reply တွေ ဝင်လာလားဆိုတာကို အမြဲစောင့်ကြည့်နေပါတယ်။ (Man-in-the-Middle attack ကို သိနိုင်ဖို့ပါ)
3. **Serial Data Ingestion (`serial_reader.py`):** ESP32 နဲ့ ချိတ်ဆက်မှုကို တာဝန်ယူပါတယ်။ Serial ကနေ ဝင်လာတဲ့ JSON စာသားတွေကို ဖတ်တယ်၊ Python dictionary အဖြစ် ပြောင်းတယ်၊ အမှားအယွင်း (corrupted data) တွေကို ရှင်းပေးပြီး ရလာတဲ့ data အသန့်တွေကို Controller ဆီ callback နဲ့ ပို့ပေးပါတယ်။

---

### Q&A အတွက် ကြိုတင်ပြင်ဆင်ခြင်း

**၁။ အစိတ်အပိုင်း တွေကို ချိတ်ဆက်ထားတဲ့ ဆော့ဖ်ဝဲ တည်ဆောက်ပုံ (Architecture) က ဘယ်လိုလဲ။**
**အဖြေ:** ကျွန်တော်တို့ `main.py` မှာ ဗဟိုကနေ ထိန်းချုပ်တဲ့ (Centralized Controller) ပုံစံကို သုံးထားပါတယ်။ `Controller` class က အားလုံးကို ချိတ်ဆက်ပေးတဲ့ "ကော်" လိုမျိုးပါ။ သူက Hardware interface (`SerialReader`)၊ Software network interface (`ARPSniffer`) နဲ့ Frontend (`App`) တို့ကို စတင်ပေးပါတယ်။
ချိတ်ဆက်တဲ့အခါ **Callback Pattern** ကို သုံးထားပါတယ်။ `main.py` က sniffer တွေကို စခေါ်တဲ့အခါ `self.on_packet_received` ဆိုတဲ့ function ကိုပါ ထည့်ပေးလိုက်ပါတယ်။ Sniffer တွေက data ရလာတိုင်း အဲဒီ function ကို ခေါ်ပြီး `main.py` ဆီကို data လှမ်းပို့ပါတယ်။ `main.py` ကမှ တစ်ဆင့် GUI ကို ဆက်ပို့ပေးပါတယ်။ ဒါကြောင့် sniffer နဲ့ GUI က တိုက်ရိုက်ကြီး ငြိမနေပါဘူး။

**၂။ ARP Spoofing attack ကို အတိအကျ ဘယ်လို သိနိုင်လဲ။**
**အဖြေ:** `ids/arp_sniffer.py` ထဲမှာ စစ်ပါတယ်။
1. Memory ထဲမှာ `arp_table` ဆိုတဲ့ dictionary တစ်ခု ဆောက်ထားပါတယ်။ အဲဒီမှာ IP နဲ့ သူနဲ့ဆိုင်တဲ့ MAC address ကို တွဲမှတ်ထားပါတယ်။
2. `scapy` ကိုသုံးပြီး ARP packet တွေကို နားထောင်ပါတယ်။ (`op == 2` ဆိုတာ ARP Reply ကို ပြောတာပါ)
3. ARP Reply ဝင်လာတဲ့အခါ၊ Source IP နဲ့ Source MAC ကို ကြည့်ပါတယ်။
4. ကျွန်တော်တို့ရဲ့ `arp_table` ထဲမှာ အဲဒီ IP ရှိပြီးသားဖြစ်ပေမယ့်၊ အခုဝင်လာတဲ့ MAC က မှတ်ထားတဲ့ MAC နဲ့ *မတူရင်* တစ်ယောက်ယောက်က network ရဲ့ ARP cache ကို ဝင်ဖျက်ဖို့ ကြိုးစားနေပြီဆိုတာ သိလိုက်ပါတယ်။ အဲဒီအချိန်မှာ ARP Spoof alert ကို ချက်ချင်း ပြပေးလိုက်ပါတယ်။

**၃။ ESP32 hardware နဲ့ ဆက်သွယ်ဖို့ ဘယ်လို လုပ်ထားလဲ။**
**အဖြေ:** Python ရဲ့ `pyserial` library ကို သုံးထားပါတယ်။
* ESP32 ထိုးထားတဲ့ COM port (ဥပမာ 115200 baud rate) ကို ချိတ်ပါတယ်။
* ESP32 က data တွေကို JSON string အနေနဲ့ serial cable ကနေ လှမ်းပို့ပါတယ်။
* `SerialReader` က background thread ထဲမှာ `while` loop အမြဲပတ်ပြီး တစ်ကြောင်းချင်းစီ ဖတ်နေပါတယ်။
* ရလာတဲ့ စာသား (text) တွေကို `json.loads()` သုံးပြီး Python dictionary အဖြစ် ပြောင်းလိုက်ပါတယ်။ ဒါမှ `rssi` တို့ `mac_src` တို့ကို အလွယ်တကူ ခေါ်သုံးလို့ ရမှာပါ။

**၄။ `SerialReader` နဲ့ `ARPSniffer` ကို ဘာလို့ Thread တွေထဲမှာ run ထားတာလဲ၊ `daemon=True` က ဘာကိုဆိုလိုတာလဲ။**
**အဖြေ:** `SerialReader` ရော `ARPSniffer` ရောက အဆုံးမရှိတဲ့ (infinite) loop တွေနဲ့ အလုပ်လုပ်နေတာပါ။ (Serial port ဖတ်တာနဲ့ network နားထောင်တာ)။ အကယ်၍ အဲဒါတွေကို main thread မှာသာ run လိုက်ရင်၊ program ကြီးက အဲဒီနေရာမှာ ရပ်သွားပြီး GUI ပွင့်လာမှာ မဟုတ်တော့ပါဘူး။ ဒါကြောင့် အလုပ်တွေကို တပြိုင်နက် လုပ်နိုင်အောင် သီးသန့် thread တွေခွဲပြီး နောက်ကွယ်မှာ run ခိုင်းထားတာပါ။
* `daemon=True` ဆိုတာကတော့ အဲဒီ thread တွေဟာ main program နဲ့ တွဲနေတဲ့ "background tasks" တွေဖြစ်တယ်လို့ ဆိုလိုတာပါ။ User က GUI ကို ပိတ်လိုက်ရင် (main thread သေသွားရင်)၊ အဲဒီ daemon thread တွေလည်း အလိုလို သေသွားမှာပါ။ ဒါကြောင့် နောက်ကွယ်မှာ program ကြီး ဆက်ပွင့်မနေအောင် ကာကွယ်ပေးပါတယ်။

**၅။ Evil Twin attack တွေကို ဘယ်လို ရှာဖွေလဲ။**
**အဖြေ:** ဝင်လာတဲ့ Beacon frame တွေကို `whitelist.json` (ယုံကြည်ရတဲ့ စာရင်း) နဲ့ တိုက်စစ်ပြီး ရှာပါတယ်။
Evil Twin attack ဆိုတာက တကယ့် network ရဲ့ SSID (နာမည်) အတိုင်း အတုလုပ်ပြီး လွှင့်တာပါ။ ESP32 က Beacon frame တွေကို ဖမ်းမိတဲ့အခါ၊ backend က SSID နဲ့ BSSID (router ရဲ့ MAC address) ကို စစ်ပါတယ်။ ဥပမာ "Campus_WiFi" ဆိုတဲ့ နာမည်နဲ့ ဝင်လာတဲ့ BSSID က ကျွန်တော်တို့ သတ်မှတ်ထားတဲ့ whitelist ထဲမှာ *မပါရင်*၊ အဲဒါကို Rogue AP (သို့) Evil Twin အနေနဲ့ ယူဆပြီး သတိပေးပါတယ်။
