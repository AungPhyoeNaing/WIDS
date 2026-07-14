# WIDS Presentation: Networking Theory & Knowledge

## Knowledge & Documentation

### Overview
A fundamental understanding of Wi-Fi (IEEE 802.11) and local network protocols is required to comprehend the threat vectors the WIDS is designed to protect against. This knowledge bridges the gap between raw packets and actionable security intelligence.

### Core Concepts
1. **The 802.11 Standard & Frame Types:** Wi-Fi traffic is categorized into three main frame types: Data, Control, and Management. 
   * **Management Frames** (Beacons, Probes, Authentication, Deauthentication) are the "administrative" messages that establish and maintain the network. Crucially, in standard WPA2 networks, these frames are **unencrypted and unauthenticated**. This lack of security makes it trivial for attackers to spoof the sender's MAC address and forge these frames.
2. **The ARP Protocol (Layer 2 to Layer 3):** The Address Resolution Protocol maps logical IP addresses (like `192.168.1.1`) to physical hardware MAC addresses (like `AA:BB:CC:DD:EE:FF`) on a local network.
   * ARP is inherently a trust-based protocol. It lacks any built-in authentication mechanism, meaning any device can claim to own any IP address simply by broadcasting an unsolicited ARP Reply.

### Threat Models Addressed
* **Denial of Service (DoS):** Attackers achieve this wirelessly by flooding a target with forged Deauthentication frames, repeatedly severing their connection to the access point.
* **Man-in-the-Middle (MitM):** 
  * **Wireless (Evil Twin):** Attackers deploy a Rogue Access Point mimicking a legitimate SSID to trick clients into connecting to them instead of the real network.
  * **Local Network (ARP Spoofing):** Attackers poison the local ARP cache, tricking the router and the victim into routing all traffic through the attacker's machine.

---

## Q&A Preparation

### 1. What is the difference between a MAC address, an IP address, an SSID, and a BSSID?

**Answer:** 
* **MAC Address (Media Access Control):** The physical, unique serial number burned into a network card at the factory (e.g., `A1:B2:C3:D4:E5:F6`). It is used for local delivery on a network.
* **IP Address:** A logical address assigned by the router (like `192.168.1.5`). It is used for routing traffic across the internet.
* **SSID (Service Set Identifier):** The human-readable name of the Wi-Fi network (e.g., "Starbucks_Guest").
* **BSSID (Basic Service Set Identifier):** This is simply the MAC address of the specific Router/Access Point broadcasting that SSID. 

> **Example:** A university might have 50 routers all broadcasting the SSID "Campus_WiFi". Your phone knows which specific router it is talking to because each of the 50 routers has a unique BSSID. 

### 2. What are 802.11 Management Frames? Why are they important to your WIDS?

**Answer:** The 802.11 (Wi-Fi) protocol has three types of frames: Data, Control, and Management. 
**Management Frames** are the "administrative" messages that keep the Wi-Fi network running. They are entirely unencrypted. We monitor them because almost all Wi-Fi attacks abuse these frames.
* **Beacon Frames:** Routers constantly shout these to say "I am here, my name is X". (Used to detect Evil Twins).
* **Probe Requests:** Your phone shouts these looking for networks it knows.
* **Deauthentication (Deauth) Frames:** A message saying "You are kicked off the network". (Used to detect Denial of Service attacks).

### 3. Explain how a Deauthentication (Deauth) Attack works.

**Answer:** Because Management frames are unencrypted and unauthenticated, anyone can forge them. 
In a Deauth attack, an attacker uses a tool (like aireplay-ng or an ESP8266/ESP32) to send a forged Deauth frame to a victim's laptop. The frame "spoofs" (fakes) the source MAC address to look like it came from the legitimate router. The victim's laptop believes the router just kicked it off, and immediately disconnects. 
By spamming these frames continuously, the attacker creates a targeted Denial of Service (DoS). Our WIDS detects this by seeing an abnormal spike in frames with the subtype `12` (Deauth).

### 4. Explain how an Evil Twin (Rogue AP) Attack works.

**Answer:** An attacker sets up their own Wi-Fi router and configures it to broadcast the exact same SSID (network name) as a legitimate network (e.g., "Free Airport Wi-Fi"). 
They often boost their transmit power so their signal is stronger than the real one. Victims' devices automatically connect to the strongest signal with the known name. Once connected, all the victim's internet traffic flows through the attacker's router, allowing them to steal passwords or inject malware.
Our system detects this by monitoring Beacons. If we see "Free Airport Wi-Fi" broadcast from a BSSID (MAC address) that is not on our whitelist, we flag it.

### 5. Explain ARP Spoofing (ARP Poisoning).

**Answer:** ARP (Address Resolution Protocol) is the system computers use to ask "Who has IP 192.168.1.1? Tell me your MAC address."
ARP is a trusting protocol. It accepts answers even if it never asked a question. 
In ARP Spoofing, an attacker constantly shouts unsolicited ARP Replies to the victim saying "I am the router (192.168.1.1), my MAC is [Attacker's MAC]". Simultaneously, they tell the real router "I am the victim, my MAC is [Attacker's MAC]". 
Both the victim and the router update their tables. Now, all traffic between the victim and the internet flows through the attacker. This is a **Man-in-the-Middle (MitM)** attack. Our software backend (`arp_sniffer.py`) detects this by watching for sudden, conflicting changes in IP-to-MAC mappings on the network.

---

## မြန်မာဘာသာပြန် (Burmese Translation)

### အနှစ်ချုပ် (Overview)
WIDS က ဘယ်လို တိုက်ခိုက်မှုတွေကို ကာကွယ်ပေးသလဲ ဆိုတာကို နားလည်ဖို့အတွက် Wi-Fi (IEEE 802.11) နဲ့ Local network protocol တွေရဲ့ အခြေခံကို နားလည်ထားဖို့ လိုအပ်ပါတယ်။ ဒီအသိပညာက raw packet တွေနဲ့ လုံခြုံရေးဆိုင်ရာ ခွဲခြမ်းစိတ်ဖြာမှုကြားက ကွာဟချက်ကို ချိတ်ဆက်ပေးပါတယ်။

### အဓိက အယူအဆများ (Core Concepts)
1. **The 802.11 Standard & Frame Types:** Wi-Fi traffic ကို Data, Control နဲ့ Management ဆိုပြီး အဓိက သုံးမျိုး ခွဲထားပါတယ်။
   * **Management Frames** (Beacons, Probes, Authentication, Deauthentication) တွေက network ကို တည်ဆောက်ဖို့နဲ့ ထိန်းသိမ်းဖို့ သုံးတဲ့ "အုပ်ချုပ်ရေးဆိုင်ရာ" မက်ဆေ့ချ်တွေပါ။ အရေးကြီးဆုံးအချက်က ပုံမှန် WPA2 network တွေမှာ ဒီ frame တွေဟာ **encrypt လုပ်မထားသလို၊ authenticate လည်း မလုပ်ထားပါဘူး**။ အဲဒီလို လုံခြုံရေး မရှိတဲ့အတွက် တိုက်ခိုက်သူတွေအနေနဲ့ ကိုယ့် MAC address ကို အတုလုပ်ပြီး ဒီ frame တွေကို ဖန်တီးပို့လွှတ်ဖို့ အရမ်းလွယ်ကူသွားပါတယ်။
2. **The ARP Protocol (Layer 2 to Layer 3):** Address Resolution Protocol ဆိုတာ Local network ပေါ်မှာ (ဥပမာ `192.168.1.1` လိုမျိုး) IP address ကနေ (ဥပမာ `AA:BB:CC:DD:EE:FF` လိုမျိုး) MAC address အဖြစ် ပြောင်းပေးတဲ့ စနစ်ပါ။
   * ARP ဟာ အခြေခံအားဖြင့် အချင်းချင်း ယုံကြည်မှု (trust-based) ပေါ်မှာ အလုပ်လုပ်ပါတယ်။ သူ့မှာ စစ်မှန်ကြောင်း အတည်ပြုတဲ့ (authentication) စနစ် မပါဝင်တဲ့အတွက်၊ မည်သည့် device မဆို ARP Reply တွေကို လွှင့်ပြီး "ဒီ IP address က ငါ့ဟာပါ" လို့ လွယ်လွယ်ကူကူ လိမ်ညာလို့ ရပါတယ်။ (ဒါကို ARP cache poisoning လို့ ခေါ်ပါတယ်)

### ကာကွယ်ပေးနိုင်သော တိုက်ခိုက်မှုများ (Threat Models Addressed)
* **Denial of Service (DoS):** တိုက်ခိုက်သူက အတုလုပ်ထားတဲ့ Deauthentication frame တွေကို ပစ်မှတ်ဆီ အများအပြား ပို့ပြီး၊ access point နဲ့ ချိတ်ဆက်မှုကို အဆက်မပြတ် ဖြတ်တောက်လိုက်တဲ့ နည်းလမ်းပါ။
* **Man-in-the-Middle (MitM):**
  * **Wireless (Evil Twin):** တိုက်ခိုက်သူက အစစ်အမှန် SSID နာမည်အတိုင်း Rogue Access Point ကို လွှင့်ပြီး၊ သုံးစွဲသူတွေကို အစစ်နဲ့ မချိတ်ဘဲ သူတို့ဆီ ချိတ်အောင် လှည့်စားတဲ့ နည်းလမ်းပါ။
  * **Local Network (ARP Spoofing):** တိုက်ခိုက်သူက Local network ရဲ့ ARP cache ကို အဆိပ်ခတ်ပြီး (လိမ်ညာပြီး)၊ router နဲ့ သုံးစွဲသူကြားက data တွေ အားလုံးကို သူ့ရဲ့ စက်ကနေ ဖြတ်သွားအောင် လုပ်တဲ့ နည်းလမ်းပါ။

---

### Q&A အတွက် ကြိုတင်ပြင်ဆင်ခြင်း

**၁။ MAC address, IP address, SSID နဲ့ BSSID တို့ရဲ့ ကွာခြားချက်တွေက ဘာတွေလဲ။**
**အဖြေ:**
* **MAC Address (Media Access Control):** Network card ကို စက်ရုံက ထုတ်ကတည်းက ထည့်သွင်းထားတဲ့ ထူးခြားတဲ့ (unique) ရုပ်ပိုင်းဆိုင်ရာ နံပါတ်ပါ။ (ဥပမာ `A1:B2:C3:D4:E5:F6`)။ သူ့ကို local network ပေါ်မှာ ဆက်သွယ်ဖို့ သုံးပါတယ်။
* **IP Address:** Router က ချထားပေးတဲ့ လိပ်စာပါ။ (ဥပမာ `192.168.1.5`)။ အင်တာနက်ပေါ်မှာ traffic တွေ လမ်းကြောင်းရှာဖို့ သုံးပါတယ်။
* **SSID (Service Set Identifier):** လူတွေ ဖတ်လို့ရတဲ့ Wi-Fi network နာမည်ပါ။ (ဥပမာ "Starbucks_Guest")။
* **BSSID (Basic Service Set Identifier):** အဲဒီ SSID ကို လွှင့်နေတဲ့ သီးခြား Router/Access Point ရဲ့ MAC address ပဲ ဖြစ်ပါတယ်။

> **ဥပမာ:** တက္ကသိုလ်တစ်ခုမှာ "Campus_WiFi" ဆိုတဲ့ SSID ကို လွှင့်နေတဲ့ router အလုံး ၅၀ ရှိနိုင်ပါတယ်။ သင့်ဖုန်းက အဲဒီ ၅၀ ထဲက ဘယ် router နဲ့ ချိတ်ထားလဲဆိုတာကို ခွဲခြားသိနိုင်ဖို့အတွက်၊ router တစ်လုံးစီတိုင်းမှာ မတူညီတဲ့ BSSID ကိုယ်စီ ရှိကြပါတယ်။

**၂။ 802.11 Management Frames ဆိုတာ ဘာလဲ၊ WIDS အတွက် ဘာလို့ အရေးကြီးတာလဲ။**
**အဖြေ:** 802.11 (Wi-Fi) protocol မှာ frame အမျိုးအစား ၃ ခု ရှိပါတယ်- Data, Control, နဲ့ Management ပါ။
**Management Frames** တွေဟာ Wi-Fi network လည်ပတ်ဖို့အတွက် လိုအပ်တဲ့ "အုပ်ချုပ်ရေးဆိုင်ရာ" မက်ဆေ့ချ်တွေပါ။ အဲဒီ frame တွေမှာ လုံခြုံရေး (encryption) မရှိပါဘူး။ Wi-Fi တိုက်ခိုက်မှု အများစုက ဒီ frame တွေကို အသုံးချတာဖြစ်လို့ ကျွန်တော်တို့က ဒါတွေကို အဓိကထား စောင့်ကြည့်ရတာပါ။
* **Beacon Frames:** Router တွေက "ငါဒီမှာ ရှိတယ်၊ ငါ့နာမည်က X ပါ" လို့ အမြဲအော်ပြောနေတဲ့ frame တွေပါ။ (Evil Twin တွေကို ရှာဖို့ သုံးပါတယ်)။
* **Probe Requests:** သင့်ဖုန်းက သူသိတဲ့ network တွေကို ရှာဖွေဖို့ အော်ပြောနေတဲ့ frame တွေပါ။
* **Deauthentication (Deauth) Frames:** "မင်းကို network ထဲက ထုတ်လိုက်ပြီ" လို့ ပြောတဲ့ မက်ဆေ့ချ်ပါ။ (DoS တိုက်ခိုက်မှုတွေကို ရှာဖို့ သုံးပါတယ်)။

**၃။ Deauthentication (Deauth) Attack ဘယ်လို အလုပ်လုပ်လဲ ရှင်းပြပါ။**
**အဖြေ:** Management frame တွေဟာ encrypt မလုပ်ထားသလို authenticate လည်း မလုပ်ထားတဲ့အတွက် ဘယ်သူမဆို အတုလုပ်လို့ ရပါတယ်။
Deauth attack မှာ တိုက်ခိုက်သူက (aireplay-ng သို့မဟုတ် ESP8266/ESP32 လို) tool တစ်ခုကို သုံးပြီး အတုလုပ်ထားတဲ့ Deauth frame ကို သားကောင်ရဲ့ လက်တော့ပ်ဆီ ပို့လိုက်ပါတယ်။ အဲဒီ frame မှာ ပါတဲ့ MAC address ကို အစစ်အမှန် router ရဲ့ MAC address အတိုင်း spoof (အတုလုပ်) ထားပါတယ်။ ဒါကြောင့် သားကောင်ရဲ့ လက်တော့ပ်က router က သူ့ကို တကယ် ကန်ထုတ်လိုက်တယ် ထင်ပြီး ချက်ချင်း disconnect ဖြစ်သွားပါတယ်။
ဒီလို frame တွေကို အဆက်မပြတ် ပို့နေခြင်းအားဖြင့် တိုက်ခိုက်သူဟာ Denial of Service (DoS) ကို ဖန်တီးလိုက်တာပါ။ ကျွန်တော်တို့ရဲ့ WIDS က subtype `12` (Deauth) frame တွေ ပုံမှန်မဟုတ်ဘဲ ရုတ်တရက် များလာတာကို ကြည့်ပြီး ဒါကို ရှာဖွေဖော်ထုတ်ပါတယ်။

**၄။ Evil Twin (Rogue AP) Attack ဘယ်လို အလုပ်လုပ်လဲ ရှင်းပြပါ။**
**အဖြေ:** တိုက်ခိုက်သူဟာ ကိုယ်ပိုင် Wi-Fi router တစ်ခုကို တည်ဆောက်ပြီး၊ အစစ်အမှန် network (ဥပမာ "Free Airport Wi-Fi") ရဲ့ SSID နာမည်အတိုင်း အတိအကျ ပေးပြီး လွှင့်ပါတယ်။
သူတို့က အစစ်ထက် signal ပိုကောင်းအောင် သူတို့ရဲ့ transmit power ကို မြှင့်ထားလေ့ ရှိပါတယ်။ သားကောင်တွေရဲ့ device တွေဟာ နာမည်တူရင် signal အကောင်းဆုံးကို အလိုအလျောက် ရွေးချိတ်တတ်ပါတယ်။ ချိတ်မိသွားတာနဲ့ သားကောင်ရဲ့ အင်တာနက် အသုံးပြုမှု အားလုံးဟာ တိုက်ခိုက်သူရဲ့ router ကနေ ဖြတ်သွားရတဲ့အတွက်၊ password တွေ ခိုးယူခံရတာ၊ malware အသွင်းခံရတာတွေ ဖြစ်လာနိုင်ပါတယ်။
ကျွန်တော်တို့ စနစ်က Beacon တွေကို စောင့်ကြည့်ပြီး ဒါကို ကာကွယ်ပါတယ်။ "Free Airport Wi-Fi" ဆိုတဲ့ နာမည်က ကျွန်တော်တို့ whitelist ထဲမှာ မပါတဲ့ BSSID (MAC address) တစ်ခုဆီကနေ လာနေတာ တွေ့ရင် ချက်ချင်း သတိပေးပါတယ်။

**၅။ ARP Spoofing (ARP Poisoning) ကို ရှင်းပြပါ။**
**အဖြေ:** ARP (Address Resolution Protocol) ဆိုတာ ကွန်ပျူတာတွေက "IP 192.168.1.1 က ဘယ်သူလဲ၊ မင်းရဲ့ MAC address ကို ပြောပါ" လို့ မေးတဲ့ စနစ်ပါ။
ARP ဟာ ယုံကြည်မှုအပေါ် အခြေခံပါတယ်။ သူက မေးခွန်း မမေးထားဘဲ အဖြေလာပေးရင်လည်း လက်ခံပါတယ်။
ARP Spoofing မှာ တိုက်ခိုက်သူက သားကောင်ဆီကို မတောင်းဆိုထားတဲ့ ARP Reply တွေ အဆက်မပြတ် ပို့ပြီး "ငါက router (192.168.1.1) ပါ၊ ငါ့ရဲ့ MAC က [တိုက်ခိုက်သူရဲ့ MAC] ပါ" လို့ ပြောပါတယ်။ တစ်ချိန်တည်းမှာပဲ အစစ်အမှန် router ဆီကို သွားပြီး "ငါက သားကောင်ပါ၊ ငါ့ရဲ့ MAC က [တိုက်ခိုက်သူရဲ့ MAC] ပါ" လို့ သွားပြောပါတယ်။
ဒါကြောင့် သားကောင်ရော router ပါ သူတို့ရဲ့ table တွေကို ပြင်မှတ်လိုက်ကြပါတယ်။ အခုဆိုရင် သားကောင်နဲ့ အင်တာနက် ကြားက ဆက်သွယ်မှုအားလုံးဟာ တိုက်ခိုက်သူရဲ့ စက်ကို ဖြတ်သွားနေပါပြီ။ ဒါကို **Man-in-the-Middle (MitM)** attack လို့ ခေါ်ပါတယ်။ ကျွန်တော်တို့ရဲ့ ဆော့ဖ်ဝဲ backend (`arp_sniffer.py`) က network ပေါ်မှာ IP နဲ့ MAC တွဲထားတာတွေ ရုတ်တရက် အချင်းချင်း ကွဲလွဲလာတာကို စောင့်ကြည့်ပြီး ဒါကို ဖော်ထုတ်ပါတယ်။
