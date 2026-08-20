# 🛡️ Sentinel WIDS — 7-Minute Screen Recording & Voiceover Script

---

## ⏱️ အချိန်နှင့် ဇယား အနှစ်ချုပ် (Quick Summary Table)

| အချိန် | အပိုင်း (Section) | မျက်နှာပြင်တွင် ပြသရန် (Screen Action) |
| :--- | :--- | :--- |
| **0:00 - 1:00** | ၁။ Title & Wi-Fi Security Problem | Slide 1 ပုံ (Overview & Threat Landscape) |
| **1:00 - 2:15** | ၂။ Hardware & Architecture | Slide 2 ပုံ (Hardware & Software Architecture Diagram) |
| **2:15 - 3:30** | ၃။ Core Detection Engines | Slide 3 (Evil Twin, Deauth, ARP Detection Flowchart) |
| **3:30 - 5:15** | ၄။ Live GUI Application Demo | WIDS Application Window (`main.py` Full Screen) |
| **5:15 - 6:15** | ၅။ Testing & Project Values | Terminal (Unit Tests Output) / Benefits Slide |
| **6:15 - 7:00** | ၆။ Roadmap & Conclusion | Future Roadmap & Thank You Slide |

---

## 🕒 [0:00 - 1:00] (၁ မိနစ်) — Title & The Wi-Fi Security Problem

> 🖥️ **SCREEN ACTION:**  
> Slide 1 ပုံ (WIDS Overview & Threat Landscape) ကို ပြထားပါ။ "Deauthentication Attack" နှင့် "Evil Twin" စာသားများကို Mouse ဖြင့် ညွှန်ပြပါ။

🎙️ **ပြောရမည့် စကား (SPOKEN SCRIPT):**
> "မင်္ဂလာပါ ခင်ဗျာ။ ဒီကနေ့ ကျွန်တော် တင်ဆက်ပေးသွားမယ့် ပရောဂျက်ကတော့ **Sentinel WIDS — Wireless Intrusion Detection System** ဖြစ်ပါတယ်။
> 
> ယနေ့ခေတ်မှာ ကျွန်တော်တို့ အသုံးပြုနေတဲ့ Wi-Fi ကွန်ရက်တွေဟာ အင်တာနက် Data Payload တွေကို ကုဒ်ဝှက် (Encrypt) ထားပေမဲ့ ကွန်ရက် ချိတ်ဆက်မှု ထိန်းချုပ်တဲ့ **802.11 Management Frames (ဥပမာ- Beacons, Probes, Deauthentications)** တွေကတော့ လေထဲမှာ Unencrypted အနေနဲ့ ပျံလွင့်နေပါတယ်။
> 
> ဒါကြောင့် Hacker တစ်ယောက်အနေနဲ့-
> ၁။ **Deauthentication Attack** လုပ်ပြီး သင့်ဖုန်းနဲ့ ကွန်ပျူတာကို Wi-Fi ကနေ ပြုတ်ကျအောင် အချိန်မရွေး လုပ်နိုင်ပါတယ်။
> ၂။ အဲ့ဒီနောက် နာမည်တူ **Evil Twin Access Point အတု** ဖွင့်ပြီး သင့်ရဲ့ Data တွေ၊ Password တွေကို ကြားဖြတ်ခိုးယူ (MITM) သွားနိုင်ပါတယ်။
> ၃။ Local Network ထဲ ရောက်သွားပါကလည်း **ARP Spoofing** လုပ်ပြီး Traffic အားလုံးကို သူ့ဆီ လမ်းကြောင်းလွှဲနိုင်ပါတယ်။
> 
> ရိုးရိုး ကွန်ပျူတာ Firewall တွေက ဒီ Layer-2 Wi-Fi တိုက်ခိုက်မှုတွေကို မသိနိုင်ပါဘူး။ ဒါကို ဖြေရှင်းဖို့ ကျွန်တော်တို့က Hardware နဲ့ Software ပေါင်းစပ်ထားတဲ့ **Sentinel WIDS** ကို ဖန်တီးခဲ့တာ ဖြစ်ပါတယ်။"

---

## 🕒 [1:00 - 2:15] (၁ မိနစ် ၁၅ စက္ကန့်) — Hardware & Software Architecture

> 🖥️ **SCREEN ACTION:**  
> Slide 2 ပုံ (Hardware & Software Architecture Diagram) သို့ ပြောင်းပါ။ ESP32 -> I2S DAC Audio -> USB JSON Stream မြှားများကို ညွှန်ပြပါ။

🎙️ **ပြောရမည့် စကား (SPOKEN SCRIPT):**
> "ကျွန်တော်တို့ စနစ်ရဲ့ Architecture ကို Hardware နဲ့ Software အပိုင်း (၂) ပိုင်းနဲ့ တွဲဖက် တည်ဆောက်ထားပါတယ်-
> 
> **၁။ Hardware Sniffer & Audio Alarm (ESP32):**
> ကွန်ပျူတာ Operating System တွေရဲ့ Wi-Fi Card ကန့်သတ်ချက်ကို ကျော်လွှားဖို့အတွက် ကုန်ကျစရိတ် သက်သာတဲ့ **ESP32 Microcontroller** ကို သုံးထားပါတယ်။ ESP32 ဟာ 2.4GHz Wi-Fi Channel 1 ကနေ 13 အထိ ၂၀၀ မီလီစက္ကန့်တစ်ကြိမ် Channel Hopping လုပ်ပြီး လေထဲက Management Frame တွေကို **Promiscuous Mode** နဲ့ တိုက်ရိုက် ဖမ်းယူပါတယ်။
> 
> ထူးခြားချက်ကတော့ ESP32 ရဲ့ Core 0 ကနေ Packet တွေကို Queue ထဲထည့်ပြီး USB Serial ကတစ်ဆင့် ကွန်ပျူတာဆီ JSON format နဲ့ ပို့ပေးနေချိန်မှာ၊ Core 1 ကတော့ **MAX98357A I2S DAC Amplifier** နဲ့ ချိတ်ဆက်ထားတဲ့ Speaker ကတစ်ဆင့် တိုက်ခိုက်မှုတွေ့ရင် Hardware အသံ အချက်ပေးသံ ထုတ်ပေးနိုင်အောင် FreeRTOS DMA Task နဲ့ အလုပ်လုပ်ပါတယ်။
> 
> **၂။ Python IDS Backend:**
> ကွန်ပျူတာဘက်ခြမ်းမှာတော့ Serial Data တွေကို ဖတ်ယူပြီး Multi-Heuristic Scoring Engines တွေနဲ့ Attack တွေကို Real-Time စစ်ဆေးပေးပါတယ်။"

---

## 🕒 [2:15 - 3:30] (၁ မိနစ် ၁၅ စက္ကန့်) — Core Detection Engines (Logic ၃ မျိုး)

> 🖥️ **SCREEN ACTION:**  
> Slide / Architecture Flowchart ရှိ Evil Twin, Deauth, ARP Spoof Logic များကို တစ်ချက်ချင်းစီ ထောက်ပြပါ။

🎙️ **ပြောရမည့် စကား (SPOKEN SCRIPT):**
> "Sentinel WIDS မှာ အဓိက တိုက်ခိုက်မှု (၃) မျိုးကို အဆင့်မြင့် Logic တွေနဲ့ ထောက်လှမ်းပေးပါတယ်-
> 
> **ပထမတစ်ခုက Evil Twin Detection:**
> စနစ်က တကယ့် Legit Wi-Fi ရဲ့ MAC Address (BSSID) ကို မှတ်သားထားပါတယ်။ Attacker က နာမည်တူ SSID နဲ့ လာလွှင့်ရင် Signal Delta (RSSI)၊ Channel ကွဲလွဲမှု၊ OUI Vendor Database နဲ့ Locally Administered MAC Address စတဲ့ အချက် (၆) ချက်ပါ Multi-Heuristic Scorer နဲ့ တိကျစွာ ခွဲခြားဖမ်းဆီးပါတယ်။
> 
> **ဒုတိယတစ်ခုက Deauth DoS Flood Detection:**
> Packet Rate၊ Broadcast Target၊ Victim Count၊ Reason Code ပုံစံနဲ့ Attack Tool တွေရဲ့ Fixed Interval Timing စတဲ့ အချက် (၈) ချက်ပါ Engine နဲ့ စစ်ဆေးပြီး Spam Alert တွေ မဖြစ်အောင် Cooldown စနစ်နဲ့ ထိန်းချုပ်ထားပါတယ်။
> 
> **တတိယတစ်ခုက ARP Spoofing & Gateway Impersonation:**
> Local Subnet မှာ Gateway MAC အတုလုပ်တာကို Scapy နဲ့ ဖမ်းယူရုံသာမက ESP32 လေထဲက ဖမ်းမိတဲ့ BSSID နဲ့ Cross-Reference လုပ်ပြီး **`HARDWARE_VERIFIED`** အဆင့် ရောက်မှသာ Gateway အစစ်အဖြစ် သတ်မှတ်ပေးပါတယ်။"

---

## 🕒 [3:30 - 5:15] (၁ မိနစ် ၄၅ စက္ကန့်) — Live GUI Application Demo

> 🖥️ **SCREEN ACTION:**  
> WIDS App (main.py) ကို Full Screen ပြပါ။  
> • 3:30 -> User View Shield & Radar ကို ပြပါ  
> • 3:55 -> Technician View သို့ Switch လုပ်ပါ  
> • 4:15 -> Live Packet Table မှ Packet ကို Click ပြပြီး Inspector အောက်က OUI Vendor ကို ပြပါ  
> • 4:40 -> Dark/Light Theme Switcher နှိပ်ပြပါ  
> • 4:55 -> Threat/Packet Counter လေးများ Live တက်နေပုံကို ပြပါ။

🎙️ **ပြောရမည့် စကား (SPOKEN SCRIPT):**
> "အခု ကျွန်တော်တို့ရဲ့ CustomTkinter Modern GUI ကို တိုက်ရိုက် ကြည့်ရှုကြပါမယ်။
> 
> ပထမဆုံး မြင်တွေ့ရတာကတော့ **User View** ဖြစ်ပါတယ်။ ဒီ View ဟာ သာမန်အသုံးပြုသူတွေအတွက် ရည်ရွယ်ပြီး Network ရဲ့ လုံခြုံရေးအခြေအနေကို Shield အရောင်နဲ့ ရှင်းရှင်းလင်းလင်း ပြသထားသလို Radar Animation နဲ့ စောင့်ကြည့်နေပါတယ်။ Alert ဖြစ်ပေါ်လာပါကလည်း နားလည်လွယ်တဲ့ ရှင်းလင်းချက်တွေနဲ့ ပြသပေးပါတယ်။
> 
> ဆက်လက်ပြီး Network Engineer တွေအတွက် **Technician View** ကို ပြောင်းပြပါမယ်။ *(View Switch ခလုတ်ကို နှိပ်ပြပါ)*
> 
> ဒီ Technician Dashboard မှာ-
> - လေထဲက ဖမ်းယူရရှိတဲ့ 802.11 Packets (Beacons, Probes, Deauths) တွေကို Signal ခွန်အား၊ Channel၊ Vendor Name တွေနဲ့ Live Stream အနေနဲ့ တွေ့မြင်နိုင်ပါတယ်။
> - Packet တစ်ခုကို နှိပ်လိုက်ရင် အသေးစိတ် အချက်အလက်တွေကို Packet Inspector မှာ ကြည့်ရှုနိုင်သလို OUI Database ကနေပြီး ဒါဟာ Router လား၊ Phone လား၊ Laptop လားဆိုတာ ခွဲခြားပေးပါတယ်။
> - စုစုပေါင်း Packets နဲ့ Threats အရေအတွက်ကိုလည်း Animated Counters တွေနဲ့ ပြသပေးထားပါတယ်။
> - Dashboard Theme ကိုလည်း မိမိစိတ်ကြိုက် **Dark Mode သို့မဟုတ် Light Mode** အလွယ်တကူ ပြောင်းလဲနိုင်ပါတယ်။ *(Theme ပြောင်းပြပါ)*
> 
> တိုက်ခိုက်မှု တွေ့ရှိပါက Host PC မှ J.A.R.V.I.S Voice အသံ သတိပေးသလို ESP32 Speaker မှလည်း Hardware Alarm အသံ ချက်ချင်း ထွက်ပေါ်လာမှာ ဖြစ်ပါတယ်။"

---

## 🕒 [5:15 - 6:15] (၁ မိနစ်) — Testing & Project Values

> 🖥️ **SCREEN ACTION:**  
> Terminal Window (Unit Tests 30+ Tests OK) သို့မဟုတ် Key Benefits Summary Slide ကို ပြပါ။

🎙️ **ပြောရမည့် စကား (SPOKEN SCRIPT):**
> "Sentinel WIDS ရဲ့ တိကျစိတ်ချရမှုအတွက် Automated Unit Tests ပေါင်း ၃၀ ကျော်နဲ့ Deauth Scoring Engine၊ ARP Sniffer နဲ့ Gateway Resolver တွေကို အဆင့်တိုင်း စနစ်တကျ စစ်ဆေးတည်ဆောက်ထားပါတယ်။
> 
> ဒီ ပရောဂျက်ရဲ့ ထူးခြားတဲ့ အားသာချက် (၃) ချက်ကတော့-
> ၁။ **Zero-Cloud & Privacy First:** အင်တာနက် Cloud လုံးဝ မလိုပါဘူး။ Data Payload တွေကို မဖမ်းဘဲ Management Headers တွေကိုသာ စစ်ဆေးတာကြောင့် အသုံးပြုသူရဲ့ Privacy ကို ၁၀၀% အပြည့်အဝ ကာကွယ်ပေးပါတယ်။
> ၂။ **Low Cost & Accessible:** စျေးကြီးတဲ့ Enterprise IDS Appliance တွေ မလိုဘဲ ၁၅ ဒေါ်လာဝန်းကျင် Component လေးတွေနဲ့ အဆင့်မြင့် ကာကွယ်ရေးစနစ်ကို တည်ဆောက်နိုင်ပါတယ်။
> 3။ **Dual-Layer Alerting:** ကွန်ပျူတာ ပိတ်ထားရင်တောင် ESP32 Hardware Speaker ကနေ အသံနဲ့ တိုက်ရိုက် သတိပေးနိုင်စွမ်း ရှိပါတယ်။"

---

## 🕒 [6:15 - 7:00] (၄၅ စက္ကန့်) — Future Roadmap & Conclusion

> 🖥️ **SCREEN ACTION:**  
> Roadmap & Thank You Slide ကို ပြသထားပါ။

🎙️ **ပြောရမည့် စကား (SPOKEN SCRIPT):**
> "ရှေ့ဆက်ပြီးတော့ ကျွန်တော်တို့စနစ်ကို **ESP32-C6 Chipset** တွေ အသုံးပြုကာ **5GHz နဲ့ Wi-Fi 6 (802.11ax)** Band တွေအထိ တိုးချဲ့စောင့်ကြည့်နိုင်အောင် ပြုလုပ်သွားမှာ ဖြစ်သလို၊ Rogue AP တွေ့ပါက အလိုအလျောက် Jamming ပြုလုပ်ပြီး တားဆီးမယ့် Active Countermeasure Feature တွေကိုပါ ထပ်မံ ထည့်သွင်းသွားမှာ ဖြစ်ပါတယ်။
> 
> နိဂုံးချုပ်အနေနဲ့ Sentinel WIDS ဟာ ခေတ်သစ် Wi-Fi ခြိမ်းခြောက်မှုတွေကို လျင်မြန်တိကျစွာ စောင့်ကြည့်ဖော်ထုတ်ပေးနိုင်တဲ့ ယုံကြည်စိတ်ချရသော Wireless Intrusion Detection System တစ်ခု ဖြစ်ပါတယ်။
> 
> အားလုံးကို အထူးပင် ကျေးဇူးတင်ရှိပါတယ် ခင်ဗျာ။"
