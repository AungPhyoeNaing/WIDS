# WIDS Presentation: Hardware & ESP32

## Knowledge & Documentation

### Overview
The hardware component of the WIDS acts as an independent, dedicated wireless probe. Unlike typical OS-level Wi-Fi drivers which filter out most traffic, the hardware probe is programmed to passively monitor the entire 2.4GHz spectrum for all Wi-Fi management frames and forward them to the backend for analysis.

### Core Technologies
* **ESP32 Microcontroller:** A low-cost, low-power system-on-chip with integrated Wi-Fi and dual-core processing capabilities.
* **Arduino Framework (C++):** The firmware is written using the Arduino IDE environment for ease of development and library support.
* **FreeRTOS:** A Real-Time Operating System that runs on the ESP32, allowing for advanced task scheduling, interrupt management, and safe inter-process communication via queues.
* **ESP-IDF Wi-Fi API:** The underlying Espressif IoT Development Framework provides the necessary low-level hooks (`esp_wifi_set_promiscuous`) to manipulate the radio state.

### Key Mechanics
1. **Promiscuous Mode Filtering:** The Wi-Fi radio is explicitly set to `WIFI_PROMISCUOUS_CTRL_FILTER_MGMT`. This tells the radio hardware to capture 802.11 management frames (Beacons, Probes, Deauths) in the air, bypassing standard OS destination filtering.
2. **Spectrum Sweeping (Channel Hopping):** Because a Wi-Fi radio can only listen to one frequency at a time, the firmware implements a non-blocking timer in its main loop. Every 200 milliseconds, it forces the radio to switch to the next channel (1 through 13), ensuring coverage across the entire 2.4GHz band.
3. **Memory Safety & Interrupts:** The function that receives packets from the radio antenna runs as a high-priority hardware interrupt. To prevent kernel panics and watchdog resets, no heavy processing (like JSON string formatting or Serial printing) is done inside this callback. Instead, the raw bytes are immediately pushed into a **FreeRTOS Queue** (`xQueueSendFromISR`). The main idle loop then safely reads from this queue and transmits the data over Serial.

---

## Q&A Preparation

### 1. Why did you choose the ESP32 for this project?

**Answer:** The ESP32 is an incredibly cost-effective, low-power microcontroller with a built-in 2.4GHz Wi-Fi radio. Crucially, its networking stack supports **Promiscuous Mode**, which is an absolute requirement for a wireless sniffer. Typical laptop Wi-Fi cards often lock this feature away at the driver or OS level (especially on Windows), making the ESP32 a much more reliable and dedicated sniffing probe.

### 2. What exactly is "Promiscuous Mode"?

**Answer:** Normally, a Wi-Fi card acts like a mailroom clerk who only looks at letters addressed specifically to them, ignoring everything else. This is "Managed Mode". 
**Promiscuous Mode** instructs the Wi-Fi radio to capture *every single radio packet* flying through the air on its current channel, regardless of who sent it or who it is destined for. This allows us to "eavesdrop" on the network and see all management frames (like Beacons, Probes, and Deauths).

### 3. How does the ESP32 monitor all Wi-Fi networks if it can only be on one channel at a time?

**Answer:** Wi-Fi in the 2.4GHz spectrum is divided into 13 channels. A Wi-Fi radio can physically only tune into one channel at a given millisecond. 
To solve this, we implemented **Channel Hopping** in the `loop()` function of our Arduino C++ code (`esp32_sniffer.ino`). 
Every 200 milliseconds, the code forces the ESP32 to switch to the next channel (1 -> 2 -> 3 ... 13 -> 1). This allows us to sweep the entire spectrum and detect attacks happening on any channel, albeit with a slight blind spot on channels we aren't currently tuned to.

### 4. The ESP32 is a small microcontroller. How do you prevent it from crashing when there are thousands of packets in a crowded area?

**Answer:** We employed three specific memory and performance optimizations:
1. **Filtering at the Radio level:** We only process `WIFI_PKT_MGMT` (Management frames). We ignore Data frames (like video streaming or web browsing), because intrusion detection relies almost entirely on management frames.
2. **RSSI Thresholding:** We drop packets with an RSSI (signal strength) lower than -80 dBm. This acts as a physical range limiter. We only care about attacks happening *near* us.
3. **FreeRTOS Queues:** The Wi-Fi callback function runs at a very high system priority. If we tried to format JSON and print to the Serial port inside that callback, the ESP32 would crash. Instead, we use `xQueueSendFromISR` to safely dump the raw data into a memory buffer. The main `loop()` then slowly reads from this buffer (max 10 packets per loop) and prints them to Serial.

### 5. What data is the ESP32 actually sending to the computer?

**Answer:** To save memory, we defined a custom `SniffPacket` C++ struct. We extract and send only the essential metadata:
* **Timestamp**: When it was captured.
* **RSSI**: How strong the signal was.
* **Channel**: What frequency it was caught on.
* **MAC Addresses**: Source, Destination, and BSSID.
* **Subtype**: What *kind* of management frame it is (e.g., integer `8` means Beacon, `12` means Deauth).
* **SSID**: The network name (if it's a Beacon or Probe).
We format this into a JSON string before sending it over the Serial cable.

---

## မြန်မာဘာသာပြန် (Burmese Translation)

### အနှစ်ချုပ် (Overview)
WIDS ရဲ့ hardware အပိုင်းဟာ သီးသန့်လွတ်လပ်တဲ့ wireless probe တစ်ခုအနေနဲ့ အလုပ်လုပ်ပါတယ်။ သာမန် ကွန်ပျူတာမှာပါတဲ့ OS-level Wi-Fi driver တွေက ကိုယ်နဲ့မဆိုင်တဲ့ traffic တွေကို ဖြတ်ပစ်လေ့ရှိပေမယ့်၊ ဒီ hardware probe လေးကိုတော့ 2.4GHz spectrum တစ်ခုလုံးမှာရှိတဲ့ Wi-Fi management frame တွေကို ဖမ်းယူပြီး backend ကို ပို့ပေးဖို့ သီးသန့် program ရေးထားပါတယ်။

### အဓိက နည်းပညာများ (Core Technologies)
* **ESP32 Microcontroller:** စျေးနှုန်းသက်သာပြီး၊ ပါဝါစားသက်သာသလို Wi-Fi နဲ့ dual-core processor ကိုပါ တစ်ခါတည်း ထည့်သွင်းထားတဲ့ chip တစ်ခုပါ။
* **Arduino Framework (C++):** Firmware ကို Arduino IDE နဲ့ ရေးထားတဲ့အတွက် ရေးရလွယ်ကူပြီး library တွေ အများကြီး သုံးလို့ရပါတယ်။
* **FreeRTOS:** ESP32 မှာ အလုပ်လုပ်တဲ့ Real-Time Operating System တစ်ခုပါ။ Task တွေစီမံဖို့၊ interrupt တွေ ထိန်းချုပ်ဖို့နဲ့ queue တွေကနေတစ်ဆင့် data တွေကို လုံခြုံစွာ ပေးပို့ဖို့အတွက် သုံးထားပါတယ်။
* **ESP-IDF Wi-Fi API:** ရေဒီယိုလှိုင်းတွေကို လိုသလို ထိန်းချုပ်နိုင်ဖို့ (`esp_wifi_set_promiscuous` လိုမျိုး) Espressif ရဲ့ low-level API တွေကို သုံးထားပါတယ်။

### အဓိက လုပ်ဆောင်ပုံများ (Key Mechanics)
1. **Promiscuous Mode Filtering:** Wi-Fi ရေဒီယိုကို `WIFI_PROMISCUOUS_CTRL_FILTER_MGMT` အဖြစ် တမင်သတ်မှတ်ထားပါတယ်။ ဒါက OS ရဲ့ ကန့်သတ်ချက်တွေကို ကျော်လွန်ပြီး လေထဲမှာရှိနေတဲ့ 802.11 management frame (Beacons, Probes, Deauths) အားလုံးကို ဖမ်းယူဖို့ ညွှန်ကြားလိုက်တာပါ။
2. **Spectrum Sweeping (Channel Hopping):** Wi-Fi ရေဒီယိုတစ်ခုက တစ်ချိန်တည်းမှာ frequency တစ်ခုကိုပဲ နားထောင်နိုင်ပါတယ်။ ဒါကြောင့် firmware ထဲက main loop မှာ timer တစ်ခု သုံးထားပါတယ်။ မီလီစက္ကန့် ၂၀၀ ပြည့်တိုင်း Wi-Fi channel ကို (1 ကနေ 13 အထိ) အစဉ်လိုက် ပြောင်းပေးနေပါတယ်။ ဒါမှ 2.4GHz band တစ်ခုလုံးကို လွှမ်းခြုံနိုင်မှာပါ။
3. **Memory Safety & Interrupts:** အင်တင်နာကနေ packet တွေကို ဖမ်းယူတဲ့ function ဟာ high-priority hardware interrupt အနေနဲ့ အလုပ်လုပ်ပါတယ်။ ESP32 crash မဖြစ်အောင် အဲဒီ callback ထဲမှာ (JSON ပြောင်းတာတို့၊ Serial print ထုတ်တာတို့လို) အလုပ်ကြမ်းတွေ မလုပ်ပါဘူး။ အဲဒီအစား ရလာတဲ့ data အကြမ်းတွေကို **FreeRTOS Queue** (`xQueueSendFromISR`) ထဲကို ချက်ချင်း ထည့်လိုက်ပါတယ်။ ပြီးတော့မှ main idle loop က အဲဒီ queue ထဲက data ကို ဖြည်းဖြည်းချင်း ယူပြီး Serial ကနေတစ်ဆင့် ပို့ပေးပါတယ်။

---

### Q&A အတွက် ကြိုတင်ပြင်ဆင်ခြင်း

**၁။ ဒီ project အတွက် ဘာလို့ ESP32 ကို ရွေးချယ်ခဲ့တာလဲ။**
**အဖြေ:** ESP32 က စျေးအရမ်းသက်သာပြီး 2.4GHz Wi-Fi ပါတဲ့ microcontroller တစ်ခုဖြစ်လို့ပါ။ အရေးအကြီးဆုံးကတော့ သူ့ရဲ့ networking stack က **Promiscuous Mode** ကို အထောက်အပံ့ ပေးပါတယ်။ Wireless sniffer တစ်ခုလုပ်ဖို့ဆိုရင် ဒါက မရှိမဖြစ် လိုအပ်ပါတယ်။ သာမန် လက်တော့ပ် Wi-Fi ကတ်တွေမှာဆိုရင် Windows OS တွေက အဲဒီလုပ်ဆောင်ချက်ကို ပိတ်ထားတတ်တဲ့အတွက် ESP32 က ပိုစိတ်ချရတဲ့ sniffing probe တစ်ခုဖြစ်ပါတယ်။

**၂။ "Promiscuous Mode" ဆိုတာ အတိအကျ ဘာကို ပြောတာလဲ။**
**အဖြေ:** ပုံမှန်အားဖြင့် Wi-Fi ကတ်တစ်ခုဟာ သူ့ဆီကို တိုက်ရိုက် လိပ်မူထားတဲ့ packet တွေကိုပဲ ဖတ်ပြီး ကျန်တာတွေကို လျစ်လျူရှုပါတယ်။ (ဒါကို Managed Mode လို့ ခေါ်ပါတယ်)
**Promiscuous Mode** ကတော့ Wi-Fi ရေဒီယိုကို လေထဲမှာ ဖြတ်သွားနေတဲ့ *မည်သည့် ရေဒီယို packet ကိုမဆို* ဘယ်သူပဲပို့ပို့ ဘယ်သူ့ဆီသွားသွား ဖမ်းယူဖို့ ညွှန်ကြားလိုက်တာပါ။ ဒါကြောင့် ကျွန်တော်တို့က လေလှိုင်းထဲက network တွေကို ခိုးနားထောင် (eavesdrop) လို့ရသွားပြီး (Beacons, Probes နဲ့ Deauths လိုမျိုး) management frame တွေကို မြင်ရတာပါ။

**၃။ ESP32 က တစ်ကြိမ်မှာ channel တစ်ခုပဲ နားထောင်နိုင်တယ်ဆိုရင်၊ Wi-Fi network တွေ အားလုံးကို ဘယ်လို စောင့်ကြည့်လဲ။**
**အဖြေ:** 2.4GHz Wi-Fi spectrum ကို channel ၁၃ ခု ခွဲထားပါတယ်။ Wi-Fi ရေဒီယိုက တစ်ချိန်မှာ channel တစ်ခုကိုပဲ ရုပ်ပိုင်းဆိုင်ရာအရ ဖမ်းနိုင်ပါတယ်။
ဒါကို ဖြေရှင်းဖို့ Arduino C++ code ထဲမှာ **Channel Hopping** ကို သုံးထားပါတယ်။ မီလီစက္ကန့် ၂၀၀ ကြာတိုင်း၊ ESP32 ကို နောက်ထပ် channel တစ်ခု (1 -> 2 -> 3 ... 13 -> 1) ဆီ ကူးသွားဖို့ code ရေးထားပါတယ်။ ဒီနည်းနဲ့ spectrum တစ်ခုလုံးကို အလှည့်ကျ စောင့်ကြည့်နိုင်ပြီး ဘယ် channel မှာ တိုက်ခိုက်မှုဖြစ်ဖြစ် သိနိုင်ပါတယ်။

**၄။ ESP32 လို သေးငယ်တဲ့ microcontroller လေးက၊ လူရှုပ်တဲ့နေရာတွေမှာ packet တွေ ထောင်နဲ့ချီ ဝင်လာရင် မဟန်းသွားအောင် ဘယ်လို ကာကွယ်ထားလဲ။**
**အဖြေ:** Memory နဲ့ performance ကို အကောင်းဆုံးဖြစ်အောင် နည်းလမ်း ၃ ခု သုံးထားပါတယ်။
1. **Filtering at the Radio level:** ကျွန်တော်တို့ `WIFI_PKT_MGMT` (Management frames) တွေကိုပဲ ဖတ်ပါတယ်။ (Video ကြည့်တာ၊ web သုံးတာတို့လို Data frame တွေကို ကျော်ပစ်ပါတယ်)။ ဘာလို့လဲဆိုတော့ တိုက်ခိုက်မှု အများစုက management frame တွေကိုပဲ သုံးလို့ပါ။
2. **RSSI Thresholding:** Signal အား (RSSI) -80 dBm ထက် နည်းတဲ့ packet တွေကို ဖျက်ပစ်ပါတယ်။ ဒီနည်းနဲ့ ကိုယ့်အနီးအနားမှာ ဖြစ်နေတဲ့ တိုက်ခိုက်မှုတွေကိုပဲ အာရုံစိုက်ပါတယ်။
3. **FreeRTOS Queues:** Wi-Fi ရဲ့ callback function က အရမ်းမြန်တဲ့ အချိန်တိုအတွင်းမှာ အလုပ်လုပ်ရတာပါ။ အဲဒီအထဲမှာ JSON ဖွဲ့တာတွေ၊ Serial ကနေ စာထုတ်တာတွေ လုပ်လိုက်ရင် ESP32 က crash ဖြစ်သွားပါလိမ့်မယ်။ အဲဒီအစား `xQueueSendFromISR` ကိုသုံးပြီး ရလာတဲ့ data တွေကို memory ထဲ အမြန်ထည့်လိုက်ပါတယ်။ ပြီးတော့မှ main `loop()` က အဲဒီ memory ထဲကနေ (တစ်ခေါက်ကို 10 packets လောက်) ဖြည်းဖြည်းချင်း ယူပြီး Serial ကို ပို့ပေးပါတယ်။

**၅။ ESP32 ကနေ ကွန်ပျူတာဆီကို အတိအကျ ဘာ data တွေ ပို့ပေးနေတာလဲ။**
**အဖြေ:** Memory ချွေတာဖို့ C++ မှာ သီးသန့် `SniffPacket` struct လေး တစ်ခု တည်ဆောက်ထားပါတယ်။ တကယ် အရေးကြီးတဲ့ data တွေကိုပဲ ထုတ်ယူပြီး ပို့ပေးပါတယ်-
* **Timestamp**: Packet ကို ဖမ်းမိတဲ့ အချိန်
* **RSSI**: Signal ဘယ်လောက် ကောင်းလဲ
* **Channel**: ဘယ် channel မှာ မိတာလဲ
* **MAC Addresses**: Source, Destination, နဲ့ BSSID တွေ
* **Subtype**: ဘယ်လို အမျိုးအစား management frame လဲ (ဥပမာ `8` ဆိုရင် Beacon, `12` ဆိုရင် Deauth)
* **SSID**: Network နာမည် (Beacon သို့မဟုတ် Probe ဖြစ်ခဲ့ရင်)
အဲဒီ အချက်အလက်တွေကို JSON string အနေနဲ့ ပြင်ဆင်ပြီးမှ Serial cable ကနေတစ်ဆင့် ပို့ပေးပါတယ်။
