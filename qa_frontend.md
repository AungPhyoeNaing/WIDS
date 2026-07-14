# WIDS Presentation: Frontend Development

## Knowledge & Documentation

### Overview
The Graphical User Interface (GUI) serves as the central dashboard for the Wireless Intrusion Detection System. It is responsible for visualizing real-time network traffic, immediately displaying security alerts, managing the serial connection to the hardware sniffer, and presenting statistics to the user.

### Core Technologies
* **CustomTkinter:** A modern UI library built on top of standard Tkinter, providing contemporary widgets, rounded corners, and built-in theme support.
* **Pillow (PIL):** Used for image processing, specifically for rendering the application logo and handling transparency masks.
* **Python Threading & Queues:** Essential for concurrent processing, ensuring the UI remains responsive while handling thousands of packets per second.

### Key Mechanics
1. **Event Loop Integration:** The UI cannot be blocked while waiting for data. It uses the Tkinter `.after()` method to continuously poll a thread-safe `queue.Queue()`. The background sniffers push data into this queue, and the main thread periodically empties it to update the interface.
2. **State Management:** The application maintains several in-memory dictionaries to track the environment:
   * Topology mappings (BSSID to SSID).
   * Signal strength history (using `collections.deque` for rolling averages).
   * Device tracking and statistical counters.
3. **Theming System:** The visual styling (colors, fonts) is completely decoupled from the business logic via a centralized `ThemeManager` (`theme.py`), allowing for dynamic switching between Light and Dark modes.

---

## Q&A Preparation

### 1. What framework did you use for the Graphical User Interface and why?

**Answer:** We used **CustomTkinter**, which is a modern extension of Python's standard `Tkinter` library. 
* **Why not standard Tkinter?** Standard Tkinter looks very dated (like a Windows 95 app). CustomTkinter provides modern UI elements with rounded corners, modern fonts, and built-in support for Dark/Light themes.
* **Why not web technologies (React/Electron)?** Since this is a system-level tool requiring direct access to COM ports (Serial) and low-level network interfaces (via Scapy), a native Python desktop application is more efficient and easier to integrate with our backend logic without complex bridging.

> **Jargon:** *GUI (Graphical User Interface)* is the visual part of the software the user interacts with, as opposed to a command-line interface.

### 2. How is the frontend architecture structured?

**Answer:** The frontend is modularized in the `gui/` directory:
* **`app.py`**: The main dashboard and core application window. It manages state, packet queues, and the main technician view (live traffic, logs).
* **`user_view.py`**: A specialized, simplified view for standard users who might not need to see raw packet streams, focusing instead on high-level security status.
* **`theme.py`**: A centralized theme manager. Instead of hardcoding colors in `app.py`, all color hex codes (for dark and light modes) are stored here. This ensures design consistency.

### 3. How does the GUI handle the massive flood of network packets without freezing?

**Answer:** This is a critical performance challenge. We solve it using **Queues and Polling**, avoiding blocking the main thread.
1. When the backend sniffers (Serial or ARP) receive a packet, they run on background *threads*. They do not update the UI directly (which would cause a crash).
2. Instead, they place the packet data into a thread-safe `queue.Queue()`.
3. The main GUI thread runs a loop using the Tkinter `.after()` method (e.g., every 500 milliseconds) to check this queue.
4. It processes the packets in batches, updating the UI elements all at once.

> **Jargon:** *Blocking the Main Thread*. The "Main Thread" is the infinite loop that draws the GUI. If you do a heavy task (like waiting for a packet) on this thread, the GUI stops drawing and becomes "Unresponsive" or freezes.

### 4. How are you storing and managing the state of the network in the UI?

**Answer:** We use several dictionaries to keep a real-time state of the environment in `app.py`:
* `self.network_map`: Maps a BSSID (MAC address) to its SSID (Network Name).
* `self.bssid_rssi`: Keeps a rolling window (using a `deque`) of the signal strength for each device to track movement or distance.
* We also track statistics like `total_packets`, `deauth_count`, and `alert_count` which are bound to the metric cards at the top of the dashboard.

### 5. Explain how the UI filtering works (e.g., "Show Beacons", "Show Probes").

**Answer:** In the live traffic stream (the Treeview component), we have checkboxes bound to Tkinter `BooleanVar` variables. When a packet is processed from the queue, the UI checks its "subtype" (e.g., Beacon, Probe, Deauth). If the corresponding checkbox variable is False, the UI simply skips inserting that row into the visual table, keeping the display clean and focused on what the analyst wants to see.

---

## မြန်မာဘာသာပြန် (Burmese Translation)

### အနှစ်ချုပ် (Overview)
Graphical User Interface (GUI) ဟာ Wireless Intrusion Detection System (WIDS) အတွက် အဓိက Dashboard အဖြစ် အလုပ်လုပ်ပါတယ်။ သူက network traffic တွေကို real-time ပြသပေးဖို့၊ security alert တွေကို ချက်ချင်းပြပေးဖို့၊ hardware sniffer နဲ့ ချိတ်ဆက်မှုကို ထိန်းချုပ်ပေးဖို့နဲ့ အချက်အလက် (statistics) တွေကို အသုံးပြုသူဆီ ပြသပေးဖို့ တာဝန်ယူထားပါတယ်။

### အဓိက နည်းပညာများ (Core Technologies)
* **CustomTkinter:** Python ရဲ့ ရိုးရိုး Tkinter ကို အဆင့်မြှင့်ထားတဲ့ UI library ပါ။ ခေတ်မီတဲ့ widget တွေ၊ ထောင့်ဝိုင်းဒီဇိုင်းတွေနဲ့ Light/Dark theme ကို အလွယ်တကူ ပြောင်းသုံးလို့ရပါတယ်။
* **Pillow (PIL):** Application logo တွေနဲ့ ပုံတွေကို စီမံဖို့ သုံးထားပါတယ်။
* **Python Threading & Queues:** တစ်စက္ကန့်ကို packet ထောင်နဲ့ချီ ဝင်လာတဲ့အချိန်မှာ UI မဟန်း (freeze မဖြစ်) သွားအောင် နောက်ကွယ်ကနေ အလုပ်လုပ်ပေးတဲ့ စနစ်ဖြစ်ပါတယ်။

### အဓိက လုပ်ဆောင်ပုံများ (Key Mechanics)
1. **Event Loop Integration:** UI က data ဝင်လာဖို့ စောင့်နေရင်း ရပ်နေလို့မရပါဘူး။ ဒါကြောင့် Tkinter ရဲ့ `.after()` method ကို သုံးပြီး thread-safe ဖြစ်တဲ့ `queue.Queue()` ထဲကို အမြဲလှမ်းစစ်နေပါတယ်။ နောက်ကွယ်က sniffer တွေက data တွေကို ဒီ queue ထဲ ထည့်ပေးပြီး၊ main thread က queue ထဲက data တွေကို ယူပြီး UI ကို update လုပ်ပေးပါတယ်။
2. **State Management:** Network အခြေအနေကို မှတ်ထားဖို့ memory ထဲမှာ dictionary တွေ သုံးထားပါတယ်။
   * Topology mappings (BSSID ကနေ SSID သို့)
   * Signal strength history (rolling average အတွက် `collections.deque` ကို သုံးထားပါတယ်)
   * Device တွေကို ခြေရာခံခြင်းနဲ့ အရေအတွက် မှတ်သားခြင်း
3. **Theming System:** အရောင်နဲ့ font တွေကို `theme.py` (ThemeManager) မှာ သီးသန့်ခွဲရေးထားတဲ့အတွက် Light နဲ့ Dark mode ပြောင်းရတာ အရမ်းလွယ်ကူသွားပါတယ်။

---

### Q&A အတွက် ကြိုတင်ပြင်ဆင်ခြင်း

**၁။ GUI အတွက် ဘာ framework သုံးထားလဲ၊ ဘာကြောင့်လဲ။**
**အဖြေ:** ကျွန်တော်တို့ **CustomTkinter** ကို သုံးထားပါတယ်။
* **ဘာလို့ ရိုးရိုး Tkinter မသုံးတာလဲ။** ရိုးရိုး Tkinter က Windows 95 ခေတ်ကလို အဟောင်းကြီး ဖြစ်နေလို့ပါ။ CustomTkinter ကတော့ ခေတ်မီတဲ့ UI၊ rounded corner တွေနဲ့ Dark/Light theme တွေကို အလွယ်တကူ သုံးလို့ရပါတယ်။
* **ဘာလို့ Web technology တွေ (React/Electron) မသုံးတာလဲ။** ဒီ project က COM port (Serial) တွေနဲ့ Scapy လိုမျိုး low-level network interface တွေကို တိုက်ရိုက်ခေါ်သုံးရတဲ့ စနစ်ဖြစ်လို့ Python desktop application က ပိုမြန်ပြီး backend နဲ့ ချိတ်ဆက်ရတာ ပိုလွယ်ကူလို့ပါ။

**၂။ Frontend architecture ကို ဘယ်လို တည်ဆောက်ထားလဲ။**
**အဖြေ:** `gui/` directory ထဲမှာ အပိုင်းတွေ ခွဲရေးထားပါတယ်။
* **`app.py`**: အဓိက dashboard ပါ။ State တွေ၊ packet queue တွေနဲ့ live traffic ပြပေးတဲ့ နေရာဖြစ်ပါတယ်။
* **`user_view.py`**: သာမန် အသုံးပြုသူတွေအတွက် ရိုးရှင်းတဲ့ view ပါ။ Raw packet တွေ မပြဘဲ အဓိက security status ကိုပဲ ပြပေးပါတယ်။
* **`theme.py`**: Theme တွေကို ထိန်းချုပ်တဲ့နေရာပါ။ အရောင် (hex codes) တွေကို `app.py` မှာ တိုက်ရိုက်မရေးဘဲ ဒီမှာ စုရေးထားတဲ့အတွက် ဒီဇိုင်းပြောင်းရတာ လွယ်ကူပါတယ်။

**၃။ Packet တွေ အများကြီး ဝင်လာရင် UI မဟန်းအောင် ဘယ်လိုလုပ်ထားလဲ။**
**အဖြေ:** ဒါက အရမ်းအရေးကြီးတဲ့ အပိုင်းပါ။ Main thread ကို မပိတ်သွားအောင် **Queues နဲ့ Polling** ကို သုံးထားပါတယ်။
1. Backend sniffer (Serial သို့မဟုတ် ARP) က packet ရလာရင်၊ သူတို့က background *threads* တွေနဲ့ အလုပ်လုပ်ပါတယ်။ UI ကို တိုက်ရိုက် သွားမပြောင်းပါဘူး (တိုက်ရိုက်ပြောင်းရင် crash ဖြစ်တတ်လို့ပါ)။
2. အဲဒီအစား packet data တွေကို thread-safe ဖြစ်တဲ့ `queue.Queue()` ထဲကို ထည့်လိုက်ပါတယ်။
3. Main GUI thread က Tkinter ရဲ့ `.after()` ကို သုံးပြီး (ဥပမာ မီလီစက္ကန့် ၅၀၀ တိုင်း) အဲဒီ queue ကို သွားသွားစစ်ပါတယ်။
4. ပြီးတော့မှ data တွေကို အစုလိုက် (batches) ယူပြီး UI ကို တစ်ခါတည်း update လုပ်ပေးပါတယ်။

**၄။ Network အခြေအနေ (State) ကို UI မှာ ဘယ်လို သိမ်းထားလဲ။**
**အဖြေ:** `app.py` ထဲမှာ dictionary တွေ သုံးပြီး real-time မှတ်ထားပါတယ်။
* `self.network_map`: BSSID (MAC address) နဲ့ SSID (Network Name) ကို တွဲမှတ်ထားပါတယ်။
* `self.bssid_rssi`: Device တွေရဲ့ signal strength အပြောင်းအလဲကို သိဖို့ `deque` သုံးပြီး မှတ်ထားပါတယ်။
* ပြီးတော့ dashboard အပေါ်မှာပြဖို့ `total_packets`, `deauth_count`, `alert_count` စတဲ့ စာရင်းတွေကိုလည်း မှတ်ထားပါတယ်။

**၅။ UI မှာ Filter (ဥပမာ "Show Beacons", "Show Probes") လုပ်တာ ဘယ်လို အလုပ်လုပ်လဲ။**
**အဖြေ:** Live traffic ပြတဲ့ ဇယား (Treeview) နေရာမှာ Tkinter ရဲ့ `BooleanVar` တွေနဲ့ ချိတ်ထားတဲ့ checkbox တွေ ရှိပါတယ်။ Queue ထဲကနေ packet ကို ယူလိုက်တဲ့အခါ၊ UI က အဲဒီ packet ရဲ့ "subtype" (ဥပမာ Beacon, Probe, Deauth) ကို စစ်ပါတယ်။ အကယ်၍ အဲဒီ subtype ကို ပြဖို့ checkbox ပိတ်ထားရင် (False ဖြစ်နေရင်)၊ အဲဒီ packet ကို ဇယားထဲ မထည့်ဘဲ ကျော်သွားပါတယ်။ ဒါကြောင့် ဇယားက ရှင်းလင်းနေပြီး ကိုယ်ကြည့်ချင်တာကိုပဲ မြင်ရပါတယ်။
