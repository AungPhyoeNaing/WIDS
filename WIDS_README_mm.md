# Sentinel WIDS — အစပြုသူများအတွက် ပြီးပြည့်စုံသော လမ်းညွှန်

> **မင်္ဂလာပါ!** ဤလမ်းညွှန်သည် သင် Wi-Fi လုံခြုံရေး၊ ESP32၊ သို့မဟုတ် Python အကြောင်း မည်သည့်အရာမျှ မသိသေးဟု ယူဆထားပါသည်။  
> ကျွန်ုပ်တို့သည် *အရာအားလုံးကို* သုညမှစတင်ပြီး ရှင်းပြပေးပါမည်။ စကားလုံးတစ်လုံးလုံးတွင် နားမလည်ဘဲ တန့်နေပါက၊ ဝေါဟာရများ (Glossary) တွင် ဝင်ရောက်ကြည့်ရှုပါ။

---

## 📖 မာတိကာ (Table of Contents)

| အပိုင်း | သင်လေ့လာရမည့်အရာ |
|---------|-------------------|
| [၁။ အပိုဒ်တစ်ပိုဒ်တည်းဖြင့် အကျဉ်းချုပ် (The One-Paragraph Summary)](#1-the-one-paragraph-summary) | ဤစနစ်တစ်ခုလုံး ဘာလုပ်သလဲဆိုသည်ကို စာကြောင်း ၃ ကြောင်းဖြင့် |
| [၂။ Wi-Fi ဆိုတာ ဘာလဲ? (၅ မိနစ်စာ အခြေခံသင်ခန်းစာ)](#2-what-is-wi-fi-the-5-minute-crash-course) | Wi-Fi တကယ်တမ်း အလုပ်လုပ်ပုံ |
| [၃။ ဤပရောဂျက်က တကယ်တမ်း ဘာအတွက်လဲ?](#3-what-is-this-project-actually-for) | ဤစနစ်က ဖမ်းဆီးပေးမည့် အမှန်တကယ် တိုက်ခိုက်မှု ၃ မျိုး |
| [၄။ ဟာ့ဒ်ဝဲ အစိတ်အပိုင်း နှစ်ခု](#4-the-two-pieces-of-hardware) | ESP32 + သင့်ကွန်ပျူတာ |
| [၅။ အဆင့်ဆင့် ထည့်သွင်းနည်း လမ်းညွှန် (ပုံများပါဝင်သည်)](#5-complete-setup-guide-with-pictures) | သုညမှစပြီး အလုပ်လုပ်သည်အထိ အဆင့်ဆင့် |
| [၆။ အချက်အလက် (Data) သွားရာလမ်းကြောင်း - လေထဲမှ စခရင်ပေါ်သို့](#6-how-data-flows-air-to-screen) | Packet တစ်ခု၏ ခရီးစဉ်ကို လိုက်ကြည့်ခြင်း |
| [၇။ ESP32 Firmware ကို တစ်ကြောင်းချင်းစီ ရှင်းလင်းချက်](#7-esp32-firmware-explained-line-by-line) | ESP32 ပေါ်တွင် အလုပ်လုပ်သော C++ ကုဒ် |
| [၈။ Python Serial Reader ကို တစ်ကြောင်းချင်းစီ ရှင်းလင်းချက်](#8-python-serial-reader-explained-line-by-line) | USB မှ Python က မည်သို့ဖတ်သနည်း |
| [၉။ Dashboard ကို တစ်ကြောင်းချင်းစီ ရှင်းလင်းချက်](#9-the-dashboard-explained-line-by-line) | CustomTkinter GUI |
| [၁၀။ Evil Twin ကို ထောက်လှမ်းခြင်း (ဉာဏ်ကောင်းသော အပိုင်း)](#10-evil-twin-detection-the-smart-part) | အတုအယောင် Wi-Fi ကွန်ရက်များကို ကျွန်ုပ်တို့ မည်သို့ရှာဖွေမည်နည်း |
| [၁၁။ Deauth Attack ကို ထောက်လှမ်းခြင်း](#11-deauth-attack-detection) | ကွန်ရက်မှ ကန်ထုတ်သည့် တိုက်ခိုက်မှုများကို ကျွန်ုပ်တို့ မည်သို့ရှာဖွေမည်နည်း |
| [၁၂။ Whitelist (ချွင်းချက်စာရင်း) - မှားယွင်းသော သတိပေးချက်များကို မည်သို့ရပ်တန့်မည်နည်း](#12-whitelist-how-to-stop-false-alarms) | တရားဝင် ကွန်ရက်များကို ယုံကြည်ခြင်း |
| [၁၃။ ပြီးပြည့်စုံသော ဝေါဟာရများ (A-Z)](#13-complete-glossary-a-z) | ၅ နှစ်အရွယ် ကလေးတစ်ယောက်ကို ရှင်းပြသလို ဝေါဟာရတိုင်းကို ရှင်းပြထားချက် |
| [၁၄။ ပြဿနာဖြေရှင်းခြင်း - မှားယွင်းနိုင်သမျှ အရာအားလုံး](#14-troubleshooting-everything-that-can-go-wrong) | အဖြစ်များသော ပြဿနာတိုင်းအတွက် ဖြေရှင်းနည်းများ |

---

## ၁။ အပိုဒ်တစ်ပိုဒ်တည်းဖြင့် အကျဉ်းချုပ်

ဤပရောဂျက်သည် **$5 တန် ESP32 ချစ်ပ်** တစ်ခုကို **Wi-Fi လုံခြုံရေးကင်မရာ** အဖြစ် ပြောင်းလဲပေးမည်ဖြစ်သည်။ ESP32 သည် လေထဲတွင်ရှိသော Wi-Fi အသွားအလာ အားလုံးကို (ရေဒီယို စကင်နာကဲ့သို့) နားထောင်ပြီး ၎င်းကြားရသမျှကို သင်၏ ကွန်ပျူတာဆီသို့ USB မှတစ်ဆင့် ပေးပို့မည်ဖြစ်သည်။ သင့်ကွန်ပျူတာတွင် Wi-Fi packet တိုင်းကို အချိန်နှင့်တပြေးညီ ပြသပေးမည့် **dashboard app** တစ်ခု အလုပ်လုပ်နေမည်ဖြစ်ပြီး၊ အရေးအကြီးဆုံးအချက်မှာ အတုအယောင် Wi-Fi hotspots (Evil Twins) များနှင့် စက်ပစ္စည်းများကို ကွန်ရက်မှ ကန်ထုတ်ရန် ကြိုးစားသူများ (Deauth attacks) ကဲ့သို့သော **တိုက်ခိုက်မှုများကို အလိုအလျောက် ထောက်လှမ်းပေးမည်** ဖြစ်သည်။ ၎င်းကို တံခါးများအတွက်မဟုတ်ဘဲ Wi-Fi အတွက် အသုံးပြုသော အိမ်လုံခြုံရေးစနစ် (Home security system) တစ်ခုအဖြစ် မှတ်ယူပါ။

---

## ၂။ Wi-Fi ဆိုတာ ဘာလဲ? (၅ မိနစ်စာ အခြေခံသင်ခန်းစာ)

အကယ်၍ သင် Wi-Fi အလုပ်လုပ်ပုံကို သိပြီးသားဆိုလျှင် အပိုင်း ၃ သို့ ကျော်သွားပါ။ မသိသေးပါက ဤအရာကို ဖတ်ပါ။

### ၂.၁ Wi-Fi ဟာ Walkie-Talkies တွေလိုပါပဲ

သင်နဲ့ သင့်သူငယ်ချင်းမှာ walkie-talkies (စကားပြောစက်) တွေ ရှိတယ်လို့ မြင်ယောင်ကြည့်ပါ။ သင်စကားပြောတဲ့အခါ သင့်သူငယ်ချင်းက ကြားရပါတယ် — ဒါပေမယ့် အကွာအဝေးအတွင်းမှာရှိတဲ့ တူညီတဲ့လိုင်း (channel) ပေါ်က မည်သူမဆို ကြားနိုင်ပါတယ်။ Wi-Fi ဟာလည်း အတူတူပါပဲ - အချက်အလက် (data) တွေဟာ လေထဲကနေ **ရေဒီယိုလှိုင်းများ (radio waves)** အဖြစ် ခရီးသွားကြပြီး မှန်ကန်တဲ့ လက်ခံစက် (receiver) ရှိသူတိုင်း ၎င်းကို ကြားနိုင်ပါတယ်။

### ၂.၂ စက်ပစ္စည်းတွေမှာ လိပ်စာတွေ ရှိတယ် (MAC Addresses)

သင့်အိမ်မှာ လမ်းလိပ်စာရှိသလိုပဲ၊ Wi-Fi စက်ပစ္စည်းတိုင်းမှာ အောက်ပါအတိုင်း ပုံစံရှိတဲ့ ဇာတ်ကောင် ၁၂ လုံးပါ ကုဒ်တစ်ခုဖြစ်တဲ့ **MAC address** တစ်ခု ရှိပါတယ် -

```
AA:BB:CC:DD:EE:FF
```

ပထမ ဇာတ်ကောင် ၆ လုံး (`AA:BB:CC`) က သင့်ကို **ထုတ်လုပ်သူ (manufacturer)** ကို ပြောပြပါတယ် (၎င်းကို **OUI** — Organizationally Unique Identifier ဟုခေါ်ပါသည်)။ ဥပမာ -
- `50:3E:AA` = TP-Link (ရောက်တာများ ထုတ်လုပ်သည်)
- `00:21:5C` = Intel (လက်ပ်တော့ Wi-Fi ချစ်ပ်များ ထုတ်လုပ်သည်)

နောက်ဆုံး ဇာတ်ကောင် ၆ လုံး (`DD:EE:FF`) က ထိုစက်ပစ္စည်းတစ်ခုတည်းအတွက် သီးသန့်ဖြစ်ပါတယ်။

### ၂.၃ ကွန်ရက်တွေမှာ နာမည်တွေ ရှိတယ် (SSIDs)

သင့်ဖုန်းရဲ့ Wi-Fi စာရင်းကို ဖွင့်လိုက်တဲ့အခါ "Starbucks_WiFi" ဒါမှမဟုတ် "Home_Network_5G" ဆိုတဲ့ နာမည်တွေကို တွေ့ရပါလိမ့်မယ်။ အဲဒါက **SSID** — Service Set Identifier ဖြစ်ပါတယ်။ အဲဒါက လူတွေဖတ်လို့ရတဲ့ နာမည်ပါ။

### ၂.၄ Wi-Fi Packets (စာတွေလိုပါပဲ)

Wi-Fi ပေါ်က အရာအားလုံးကို အချက်အလက် အစုအဝေး သေးသေးလေးတွေဖြစ်တဲ့ **packets** တွေအနေနဲ့ ပေးပို့ပါတယ်။ packet တစ်ခုကို စာအိတ်ထဲက စာတစ်စောင်လို့ မြင်ယောင်ကြည့်ပါ -

```
┌─────────────────────────────────────────┐
│  ENVELOPE (စာအိတ်)                       │
│  From (ဘယ်သူ့ဆီက): (Source MAC)        │
│  To (ဘယ်သူ့ဆီကို):   (Destination MAC)   │
│  What kind (ဘယ်အမျိုးအစား): Management / Data / Control │
│  Signal strength (လှိုင်းအား): -45 dBm (ဘယ်လောက်နီးလဲ) │
│  Channel (လိုင်း): 6 (ဘယ် frequency လဲ)  │
│  ┌─────────────────────────────────────┐│
│  │  LETTER INSIDE (အတွင်းထဲက စာ):        ││
│  │  "Hello, here is the actual data..." ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### ၂.၅ Wi-Fi Packet အမျိုးအစား သုံးခု

| အမျိုးအစား (Type) | ဘာလုပ်သလဲ (What It Does) | ကျွန်ုပ်တို့ ဂရုစိုက်ဖို့လိုသလား? (Do We Care?) |
|------|-------------|-------------|
| **Management** | ချိတ်ဆက်မှုများကို ကိုင်တွယ်သည် (join, leave, find networks) | **YES** — ဒါကို ကျွန်ုပ်တို့ စောင့်ကြည့်မှာပါ |
| **Control** | Data များ ရောက်ရှိကြောင်း သေချာစေသည် (ACK, RTS, CTS) | No — ပျင်းစရာကောင်းပေမယ့် မရှိမဖြစ်ပါ |
| **Data** | အင်တာနက် အသွားအလာ အစစ်အမှန် (web pages, videos) | No — ကျွန်ုပ်တို့ data တွေကို ခိုးမကြည့်ပါဘူး |

**ကျွန်ုပ်တို့၏ ESP32 သည် Management frames များကိုသာ ဖမ်းယူပါသည်** — data ကို မဖမ်းယူပါ။ ဆိုလိုသည်မှာ ကျွန်ုပ်တို့သည် မည်သူတစ်ဦးတစ်ယောက်၏ ကိုယ်ရေးကိုယ်တာ (privacy) ကိုမျှ မကျူးကျော်ဘဲ ပတ်ဝန်းကျင်တွင် ဘာတွေဖြစ်နေလဲဆိုတာကို မြင်နိုင်စွမ်းရှိသည်။

### ၂.၆ Management Frame အမျိုးအစားများ (၀-၁၅)

Management frames များတွင် အမျိုးအစားခွဲများ (subtypes) (၀ မှ ၁၅ အထိ) ရှိသည်။ ဤအရာများသည် အရေးကြီးသော အမျိုးအစားများဖြစ်သည် -

| နံပါတ် | အမည် (Name) | ဖော်ပြချက် (Description) | ကျွန်ုပ်တို့ ဘာကြောင့် ဂရုစိုက်ရသလဲ |
|--------|------|-------------|-------------|
| 4 | **Probe Request** | သင့်ဖုန်းက "'HomeWiFi' ဆိုတဲ့ နာမည်နဲ့ ဘယ်သူရှိလဲ?" လို့ မေးခြင်း | စက်ပစ္စည်းတွေက ဘယ်ကွန်ရက်တွေကို ရှာနေလဲဆိုတာ ပြပါတယ် |
| 5 | **Probe Response** | AP တစ်ခုက "ဟုတ်တယ်၊ ငါက 'HomeWiFi' ပါ၊ ငါနဲ့ လာချိတ်ပါ!" လို့ ပြန်ဖြေခြင်း | အနီးနားရှိ ကွန်ရက်များကို မြေပုံဆွဲပေးပါတယ် |
| 8 | **Beacon** | AP တစ်ခုက "ငါ ဒီမှာရှိတယ်! ငါက 'CoffeeWiFi' ပါ!" လို့ ၁၀၀ မီလီစက္ကန့်တိုင်း အော်ပြောခြင်း | အနီးနားရှိ ကွန်ရက်များကို မြေပုံဆွဲပေးပါတယ် |
| 10 | **Disassociation** | "မင်းကို အလုပ်ဖြုတ်လိုက်ပြီ — ကွန်ရက်ထဲက ထွက်သွားပါ" | တိုက်ခိုက်မှုတစ်ခု ဖြစ်နိုင်ပါတယ် |
| 12 | **Deauthentication** | "ကွန်ရက်ထဲက အခုချက်ချင်း ထွက်သွားစမ်း!" | **ဒါက အဖြစ်များတဲ့ တိုက်ခိုက်မှုတစ်ခုပါ** |

### ၂.၇ dBm ဆိုတာ ဘာလဲ? (Signal Strength)

**dBm** ဆိုတာ decibel-milliwatts ကို ကိုယ်စားပြုပါတယ်။ ၎င်းက လှိုင်း (signal) ဘယ်လောက် အားကောင်းလဲဆိုတာကို တိုင်းတာပါတယ်။ တိုင်းတာမှုစကေးက နည်းနည်းထူးဆန်းပါတယ် -

| တန်ဖိုး (Value) | အဓိပ္ပါယ် (Meaning) | ဥပမာ (Example) |
|-------|---------|---------|
| -30 dBm | အလွန်အားကောင်းသော လှိုင်း | Router ရဲ့ ဘေးနားမှာ ရပ်နေခြင်း |
| -50 dBm | ကောင်းသော လှိုင်း | Router နဲ့ အခန်းတစ်ခန်းတည်းမှာ ရှိနေခြင်း |
| -67 dBm | သင့်တင့်သော လှိုင်း | တစ်ခန်းကျော်မှာ ရှိနေခြင်း |
| -80 dBm | အားနည်းသော လှိုင်း | အဝေးမှာ (သို့) နံရံတွေခံနေခြင်း |
| -90 dBm | မပြတ်တမ်းလောက်သာ ထောက်လှမ်းနိုင်ခြင်း | ကြားနိုင်စွမ်းရဲ့ အဆုံးစွန် |

ဂဏန်းပိုကြီးလေ (၀ နဲ့ ပိုနီးလေ) = လှိုင်းပိုအားကောင်းလေ ဖြစ်ပါတယ်။ -40 ဟာ -80 ထက် ပိုအားကောင်းပါတယ်။

---

## ၃။ ဤပရောဂျက်က တကယ်တမ်း ဘာအတွက်လဲ?

ဤစနစ်သည် **တိုက်ခိုက်မှု ၃ မျိုး** ကို ဖမ်းဆီးပေးသည် -

### ၃.၁ Evil Twin Attack (အန္တရာယ်အများဆုံး)

**ဘာတွေဖြစ်သလဲ -** ဟက်ကာတစ်ယောက်က ကော်ဖီဆိုင်မှာ လက်ပ်တော့တစ်လုံးနဲ့ ထိုင်နေပါတယ်။ သူတို့က "Starbucks_WiFi" ဆိုတဲ့ နာမည်နဲ့ (အစစ်အမှန် Starbucks Wi-Fi ရဲ့ နာမည်နဲ့ အတိအကျတူတဲ့) Wi-Fi ကွန်ရက်တစ်ခုကို ဖန်တီးလိုက်ပါတယ်။ သင့်ဖုန်းက နာမည်တူ ကွန်ရက်နှစ်ခုကို မြင်ရပြီး (အထူးသဖြင့် လှိုင်းပိုအားကောင်းနေရင် ဒါမှမဟုတ် အရင်က ချိတ်ဆက်ဖူးရင်) ဟက်ကာရဲ့ ကွန်ရက်ကို အလိုအလျောက် ချိတ်ဆက်သွားနိုင်ပါတယ်။

**အန္တရာယ် -** ချိတ်ဆက်မိသွားတာနဲ့ ဟက်ကာက အောက်ပါတို့ကို လုပ်နိုင်ပါတယ် -
- သင်ရိုက်ထည့်တဲ့ စကားဝှက်တွေကို ခိုးယူခြင်း
- သင်ဝင်ကြည့်တဲ့ ဝဘ်ဆိုက်တိုင်းကို ကြည့်ရှုခြင်း
- စာမျက်နှာ အတုတွေ ဝင်ရောက်ပြသခြင်း (ဥပမာ login screen အတု)
- သင့်ကို မဲလ်ဝဲလ် (malware) ဝဘ်ဆိုက်တွေဆီ လမ်းကြောင်းလွှဲခြင်း

**ကျွန်ုပ်တို့ ဘယ်လိုဖမ်းမလဲ -** ကျွန်ုပ်တို့ရဲ့ စနစ်က "Starbucks_WiFi" ကို **မတူညီတဲ့ MAC addresses နှစ်ခု** ကနေ လွှင့်နေတာကို တွေ့ရပါမယ်။ ဘယ်ဟာက အတုလဲဆိုတာကို ဆုံးဖြတ်ဖို့ ကျွန်ုပ်တို့က စစ်ဆေးမှု (checks) ၈ ခုကို လုပ်ဆောင်ပြီး အသိပေး (flag) ပါမယ်။

### ၃.၂ Deauth Attack (အနှောင့်အယှက်အပေးဆုံး)

**ဘာတွေဖြစ်သလဲ -** ဟက်ကာတစ်ယောက်က "Deauthentication" packet တွေကို Wi-Fi ကွန်ရက်တစ်ခုဆီ ပို့လိုက်ပါတယ်။ ဒီ packet တွေက စက်ပစ္စည်းတိုင်းကို "အခုချက်ချင်း ထွက်သွား!" လို့ ပြောပါတယ်။ စက်တွေက လိုက်နာပြီး အဆက်အသွယ်ပြတ်သွားပါတယ်။ ပြီးတော့ ပြန်ချိတ်ဆက်ပါတယ်။ ပြီးတော့ ဟက်ကာက ထပ်ပို့ပါတယ်။ ဒီလိုနဲ့ ကွန်ရက်ကြီးဟာ အသုံးပြုလို့ မရတော့ပါဘူး။

**အန္တရာယ် -** ဤအရာက အောက်ပါတို့ကို ဖြစ်စေနိုင်ပါတယ် -
- စီးပွားရေးလုပ်ငန်းတစ်ခုရဲ့ Wi-Fi ကနေ လူတိုင်းကို ကန်ထုတ်ခြင်း (ဖောက်သည်တွေ ဆုံးရှုံးခြင်း)
- IoT စက်ပစ္စည်းတွေကို အနှောင့်အယှက်ပေးခြင်း (လုံခြုံရေးကင်မရာများ၊ စမတ်သော့များ)
- Evil Twin နဲ့ တွဲဖက်အသုံးပြုခြင်း (စက်ပစ္စည်းတွေ ပြန်ချိတ်ဆက်တဲ့အခါ၊ ဟက်ကာရဲ့ ကွန်ရက်အတုဆီ ချိတ်ဆက်သွားနိုင်ပါတယ်)

**ကျွန်ုပ်တို့ ဘယ်လိုဖမ်းမလဲ -** ကျွန်ုပ်တို့က Deauth frames တွေကို ရေတွက်ပါတယ်။ အချိန်တိုအတွင်းမှာ ၁၀ ခုနဲ့အထက် တွေ့ရတဲ့အခါ သတိပေးချက် (alert) ပြသပါမယ်။

### ၃.၃ Probe Sniffing (ကိုယ်ရေးကိုယ်တာ ပြဿနာ)

**ဘာတွေဖြစ်သလဲ -** သင့်ဖုန်းဟာ Wi-Fi နဲ့ မချိတ်ဆက်ထားရင်တောင်မှ "'HomeWiFi' နာမည်နဲ့ ဘယ်သူရှိလဲ? 'CoffeeWiFi' ရော ရှိလား?" လို့ပြောတဲ့ "Probe Requests" တွေကို အမြဲတမ်း ပေးပို့နေပါတယ်။ sniffer ရှိတဲ့သူတိုင်း ဒါတွေကို ကြားနိုင်ပါတယ်။

**အန္တရာယ် -** ဟက်ကာတွေက အောက်ပါတို့ကို လုပ်နိုင်ပါတယ် -
- သင် ဘယ်နေရာတွေ သွားခဲ့လဲဆိုတာကို ခြေရာခံခြင်း (သင့်ဖုန်းက မှတ်မိနေတဲ့ ကွန်ရက်တွေရဲ့ နာမည်တွေကို ဖွင့်ဟနေပါတယ်)
- သင့်ရဲ့ ရုပ်ပိုင်းဆိုင်ရာ တည်နေရာကို ခြေရာခံခြင်း (signal strength က အကွာအဝေးကို ဖော်ပြနေပါတယ်)
- သင့်ဖုန်းက ယုံကြည်တဲ့ ကွန်ရက်တွေအပေါ် အခြေခံပြီး ရည်ရွယ်ချက်ရှိရှိ Evil Twins တွေကို ဖန်တီးခြင်း

**ကျွန်ုပ်တို့ ဘယ်လိုဖမ်းမလဲ -** ရှင်သန်နေတဲ့ traffic လွှင့်ထုတ်မှု (live stream) မှာ Probe Request တိုင်းကို ကျွန်ုပ်တို့ ပြသပါမယ်။ အနီးနားက စက်ပစ္စည်းတွေက ဘယ်ကွန်ရက်တွေကို ရှာဖွေနေလဲဆိုတာကို သင် မြင်နိုင်ပါတယ်။

---

## ၄။ ဟာ့ဒ်ဝဲ အစိတ်အပိုင်း နှစ်ခု

### ၄.၁ ESP32 ($5-10)

```
ESP32 Dev Board (ရုပ်ပိုင်းဆိုင်ရာ အသွင်အပြင်)
┌──────────────────────────────────────────────┐
│                                              │
│  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐       │
│  │  │  │  │  │  │  │  │  │  │  │  │  ESP32  │
│  └──┘  └──┘  └──┘  └──┘  └──┘  └──┘  Chip  │
│                                              │
│  [USB Port] ←──── သင့်ကွန်ပျူတာကို ချိတ်ဆက်သည် │
│                                              │
│  [ON/OFF]  [EN]  (ခလုတ်ငယ်များ)              │
└──────────────────────────────────────────────┘
```

**၎င်းသည် ဘာလဲ -** Wi-Fi တပ်ဆင်ထားပြီးဖြစ်သော ကွန်ပျူတာအသေးစားလေး တစ်ခုဖြစ်သည်။ ကော်ဖီတစ်ခွက်စာလောက်သာ တန်ဖိုးရှိပါသည်။

**ဤပရောဂျက်တွင် ၎င်းဘာလုပ်သနည်း -**
၁။ အကွာအဝေးအတွင်းရှိ Wi-Fi အသွားအလာ **အားလုံး** ကို နားထောင်သည် (ရဲသုံး စကင်နာကဲ့သို့)
၂။ စစ်ထုတ်ခြင်း (Filter): **Management frames** များကိုသာ သိမ်းဆည်းသည် (Beacons, Probes, Deauths, စသည်)
၃။ packet တိုင်းမှ အရေးကြီးသော အချက်အလက်များကို ထုတ်ယူသည်
၄။ ၎င်းအချက်အလက်များကို USB မှတစ်ဆင့် သင့်ကွန်ပျူတာသို့ JSON စာသားအဖြစ် ပေးပို့သည်
၅။ လိုင်း (channel) ၁ ခုတည်းမဟုတ်ဘဲ လိုင်း ၁၃ ခုလုံးကို ကြားနိုင်ရန် မီလီစက္ကန့် ၂၀၀ တိုင်း channel ကို ပြောင်းလဲသည်

**ဘာကြောင့် ESP32 ကို သုံးရသလဲ?** ၎င်းက စျေးပေါတယ်၊ Wi-Fi ပါပြီးသားဖြစ်တယ်၊ ပြီးတော့ ထုတ်လုပ်သူ (Espressif) က အရာအားလုံးကို ကြားနိုင်စေတဲ့ "promiscuous mode" လို့ခေါ်တဲ့ လုပ်ဆောင်ချက် (function) တစ်ခုကို ထည့်ပေးထားလို့ပါ။

### ၄.၂ သင့်ကွန်ပျူတာ (Dashboard)

**၎င်းဘာလုပ်သနည်း -**
၁။ USB မှတစ်ဆင့် ဝင်လာသော JSON data ကို ဖတ်သည်
၂။ ၎င်းကို Python dictionaries အဖြစ်သို့ ခွဲခြမ်းစိတ်ဖြာသည်
၃။ အချိန်နှင့်တပြေးညီ GUI dashboard တွင် အရာအားလုံးကို ပြသသည်
၄။ ဉာဏ်ကောင်းသော အယ်လ်ဂိုရီသမ်များကို အသုံးပြု၍ **တိုက်ခိုက်မှုများကို ထောက်လှမ်းသည်**

---

## ၅။ အဆင့်ဆင့် ထည့်သွင်းနည်း လမ်းညွှန် (ပုံများပါဝင်သည်)

### အဆင့် ၀ - သင် ဘာတွေလိုအပ်လဲ

```
□ ESP32 board               (Amazon: ~$8)
□ USB ကြိုး (data ပို့နိုင်သော)  (၎င်းနှင့်အတူပါလာသော ကြိုးက အလုပ်လုပ်သည်)
□ Python 3.8+ ပါသော ကွန်ပျူတာ (Windows/Mac/Linux)
□ အင်တာနက် ချိတ်ဆက်မှု        (ဆော့ဖ်ဝဲ ဒေါင်းလုဒ်ဆွဲရန်)
□ သင့်အချိန် ၁၅ မိနစ်
```

### အဆင့် ၁ - Arduino IDE ကို Install လုပ်ပါ

၁။ https://www.arduino.cc/en/software သို့သွားပါ
၂။ သင့် လည်ပတ်မှုစနစ် (operating system) အတွက် ဗားရှင်းကို ဒေါင်းလုဒ်ဆွဲပါ
၃။ ၎င်းကို install လုပ်ပါ (Next → I Agree → Install → Finish ကိုနှိပ်ပါ)

### အဆင့် ၂ - Arduino IDE တွင် ESP32 Support ကို ထည့်ပါ

၁။ Arduino IDE ကို ဖွင့်ပါ
၂။ **File → Preferences** သို့သွားပါ
၃။ "Additional Boards Manager URLs" ကို ရှာပါ
၄။ ဤ URL ကို paste လုပ်ပါ: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
၅။ OK ကိုနှိပ်ပါ
၆။ **Tools → Board → Board Manager** သို့သွားပါ
၇။ "esp32" ဟု ရှာပါ
၈။ "ESP32 by Espressif Systems" တွင် **Install** ကိုနှိပ်ပါ
၉။ ၅ မိနစ်ခန့် စောင့်ပါ (ဒေါင်းလုဒ်ဆွဲစရာ များစွာရှိပါသည်)

### အဆင့် ၃ - Firmware ကိုဖွင့်ပြီး Upload လုပ်ပါ

၁။ Arduino IDE တွင်: **File → Open**
၂။ သင့် WIDS folder → `esp32_sniffer` → `esp32_sniffer.ino` သို့ သွားပါ
၃။ သင့် ESP32 ကို USB မှတစ်ဆင့် ကွန်ပျူတာသို့ ချိတ်ဆက်ပါ
၄။ **Tools → Board → ESP32 Arduino → ESP32 Dev Module** သို့သွားပါ
၅။ **Tools → Port** သို့သွားပြီး နာမည်တွင် "USB" သို့မဟုတ် "CP2102" ပါသော COM port ကို ရွေးချယ်ပါ
   - Windows: များသောအားဖြင့် `COM3`, `COM4`, သို့မဟုတ် `COM5`
   - Mac: များသောအားဖြင့် `/dev/cu.usbserial-XXXX`
   - Linux: များသောအားဖြင့် `/dev/ttyUSB0`
၆။ **→ (Upload)** ခလုတ်ကို နှိပ်ပါ (ဘယ်ဘက်အပေါ်ထောင့်၊ မြှားပုံစံ)
၇။ **အရေးကြီးသည်:** အကယ်၍ "Connecting..." ဟု ပြပြီး ရပ်နေပါက၊ upload စတင်သည်အထိ ESP32 ပေါ်ရှိ **BOOT** ခလုတ်ကို ဖိနှိပ်ထားပါ (ရာခိုင်နှုန်း ဂဏန်းများကို သင်တွေ့ရပါမည်)

```
Upload အောင်မြင်သွားပြီးနောက်၊ ဤသို့တွေ့ရပါမည်:
"Hard resetting via RTS pin..."
```

### အဆင့် ၄ - Python ကို Install လုပ်ပါ

၁။ terminal တစ်ခုကို ဖွင့်ပါ (Windows တွင် Command Prompt၊ Mac/Linux တွင် Terminal)
၂။ သင့် WIDS folder သို့ သွားပါ:
```bash
cd C:\Users\YourName\Desktop\WIDS   # Windows ဥပမာ
cd ~/Desktop/WIDS                    # Mac/Linux ဥပမာ
```
၃။ လိုအပ်သော packages များကို install လုပ်ပါ:
```bash
pip install -r requirements.txt
```
   - အကယ်၍ `pip` အလုပ်မလုပ်ပါက၊ `pip3` သို့မဟုတ် `python -m pip install customtkinter pyserial` ကို စမ်းကြည့်ပါ

### အဆင့် ၅ - Dashboard ကို ဖွင့်ပါ

```bash
python main.py
```

အမည်းရောင်နောက်ခံ (dark-themed) dashboard window တစ်ခု ပေါ်လာသည်ကို သင်တွေ့ရပါမည်။

### အဆင့် ၆ - ချိတ်ဆက်ပါ (Connect)

၁။ ဘေးဘက်ဘား (sidebar) တွင်၊ သင့် COM port (ဥပမာ `COM5`) ကို ရိုက်ထည့်ပါ
၂။ Baud rate သည် `115200` ဖြစ်သင့်သည် (၎င်းကို ဖြည့်ထားပြီးဖြစ်သည်)
၃။ **CONNECT** ကိုနှိပ်ပါ
၄။ အခြေအနေသည် "● Disconnected" (အနီရောင်) မှ "● Connected" (အစိမ်းရောင်) သို့ ပြောင်းလဲသွားသင့်သည်
၅။ ပင်မဧရိယာတွင် Packets များ ပေါ်လာသင့်သည်

**အကယ်၍ Packets များ မပေါ်လာပါက**၊ ပြဿနာဖြေရှင်းခြင်း (Troubleshooting) အပိုင်းကို ကြည့်ပါ။

---

## ၆။ အချက်အလက် သွားရာလမ်းကြောင်း - လေထဲမှ စခရင်ပေါ်သို့

လေထဲကိုဖြတ်သွားတဲ့ အချိန်ကနေ သင့်စခရင်ပေါ် ရောက်လာတဲ့အချိန်အထိ **Wi-Fi packet တစ်ခုတည်း** ကို လိုက်ကြည့်ကြရအောင်။ ကျွန်ုပ်တို့ဟာ (router တစ်ခုက သူ့ကိုယ်သူ ကြေညာနေတဲ့) Beacon frame ကို ဥပမာအနေနဲ့ သုံးပါမယ်။

### အဆင့် ၁ - Router တစ်ခုက Beacon ကို လွှင့်တယ်

```
မြင်ယောင်ကြည့်ပါ - ဘေးခန်းက တိုက်ခန်းမှာ TP-Link router တစ်ခုရှိတယ်။
၎င်းက ၁၀၀ မီလီစက္ကန့်တိုင်း Beacon တစ်ခုကို အပြင်ကို လွှင့်နေပါတယ်:
  "ငါ ဒီမှာရှိတယ်! ငါ့နာမည်က 'Smith_Family_WiFi'!"
  "ငါ့ရဲ့ MAC address က 50:3E:AA:12:34:56"
  "ငါ Channel 6 မှာရှိတယ်"
  "ငါ့ရဲ့ လှိုင်းအားက -45 dBm ပါ"
```

### အဆင့် ၂ - ESP32 က ၎င်းကို ကြားတယ်

ESP32 ဟာ **promiscuous mode** မှာရှိပါတယ် — ၎င်းက သူ့ဆီကို လိပ်မူထားတဲ့ packets တွေကိုတင်မဟုတ်ဘဲ၊ အကွာအဝေးအတွင်းမှာရှိတဲ့ packet တိုင်းကို ကြားနိုင်ပါတယ်။ ESP32 ပေါ်က Wi-Fi ချစ်ပ်က packet ကို ထောက်လှမ်းမိပြီး **Interrupt Service Routine (ISR)** လို့ခေါ်တဲ့ အထူး function တစ်ခုကို ချက်ချင်း ခေါ်လိုက်ပါတယ်။

**ISR ဆိုတာ ဘာလဲ?** သင် စာအုပ်ဖတ်နေတုန်း တစ်ယောက်ယောက်က သင့်ပခုံးကို လာပုတ်တယ်လို့ မြင်ယောင်ကြည့်ပါ။ သင် စာဖတ်တာကို ချက်ချင်းရပ်လိုက်ပြီး၊ လာပုတ်တဲ့ကိစ္စကို ဖြေရှင်းတယ်၊ ပြီးမှ စာဖတ်တာကို ပြန်ဆက်လုပ်တယ်။ အဲဒါက interrupt တစ်ခုပါပဲ။ ISR ဆိုတာက "လာပုတ်တဲ့ကိစ္စကို ဖြေရှင်းတဲ့" အပိုင်းပါ — ၎င်းက ချက်ချင်း အလုပ်လုပ်တယ်၊ လုပ်နိုင်သမျှ အနည်းဆုံးအလုပ်ကို လုပ်တယ်၊ ပြီးတော့ ပြန်သွားတယ်။

### အဆင့် ၃ - ISR က အလုပ်ကို မြန်မြန်လုပ်တယ် (မိုက်ခရိုစက္ကန့်များ)

ISR ဟာ အချိန်အများကြီး မပေးနိုင်ပါဘူး — သူ့မှာ မီလီစက္ကန့်တွေမဟုတ်ဘဲ မိုက်ခရိုစက္ကန့်တွေပဲ ရှိပါတယ်။ ၎င်းက -

၁။ packet အမျိုးအစားကို စစ်ဆေးတယ် (Management frame ဟုတ်လား? ဟုတ်တယ်!)
၂။ အရေးကြီးတဲ့ ဘိုက် (bytes) တွေကိုပဲ သေးငယ်တဲ့ struct (စုစုပေါင်း ၃၆ ဘိုက်) ထဲကို ကူးယူတယ်:
   - Timestamp (ဘယ်အချိန်မှာ ဖမ်းမိတာလဲ)
   - RSSI (လှိုင်းဘယ်လောက်အားကောင်းလဲ)
   - Channel (ဘယ် Wi-Fi လိုင်းလဲ)
   - Source MAC (ဘယ်သူပို့တာလဲ)
   - Destination MAC (ဘယ်သူ့အတွက်လဲ)
   - BSSID (Access point ရဲ့ MAC)
   - Frame subtype (Beacon = 8)
   - SSID (Beacon သို့မဟုတ် Probe Response ဖြစ်ပါက ကွန်ရက်အမည်)
၃။ ဤ struct ကို `xQueueSendFromISR()` ကို အသုံးပြု၍ **queue** (buffer တစ်ခု) ထဲသို့ ထည့်သွင်း (push) လိုက်သည်
၄။ Return ပြန်သည်

**ဘာကြောင့် queue လဲ?** ISR ဟာ အမြင့်ဆုံး ဦးစားပေး (highest priority) အနေနဲ့ အလုပ်လုပ်ပါတယ်။ အကယ်၍ ကျွန်ုပ်တို့က ISR ထဲမှာ Serial ကို print ထုတ်မယ်ဆိုရင် အချိန်အရမ်းကြာသွားပြီး ESP32 က crash ဖြစ် (Watchdog Timer reset ဖြစ်) သွားပါလိမ့်မယ်။ queue က ISR ကို မိုက်ခရိုစက္ကန့်ပိုင်းအတွင်း ပြီးစီးစေပါတယ်; main loop ကတော့ print ထုတ်ဖို့ သူ့အချိန်နဲ့သူ ယူနိုင်ပါတယ်။

```
ISR (မြန်သည်)                QUEUE (buffer)          MAIN LOOP (နှေးသည်)
───────                   ─────────────           ─────────────────
Packet ရောက်လာသည် ──►   [packet 1]              │
                     ──► [packet 2]              │
                     ──► [packet 3]     ◄───────── Serial.printf()
                     ──► [ ... ]                   (၁ မီလီစက္ကန့်ခန့် ကြာသည်)
                       (နေရာ ၅၀ အထိ)
```

အကယ်၍ queue ပြည့်နေပါက (packet ၅၀)၊ packet အသစ်ကို **ပစ်ချလိုက် (dropped)** ပါသည်။ ၎င်းကို ရည်ရွယ်ချက်ရှိရှိ လုပ်ဆောင်ခြင်းဖြစ်သည် — ESP32 ကို crash ဖြစ်စေမည့်အစား packet တစ်ခုကို လွှင့်ပစ်လိုက်ခြင်းက ပိုကောင်းသည်။

### အဆင့် ၄ - Main Loop က ၎င်းကို USB မှတစ်ဆင့် ပို့သည်

main loop ဟာ အမြဲတမ်း၊ ထပ်ခါတလဲလဲ အလုပ်လုပ်နေပါတယ်။ အကြိမ်တိုင်းမှာ ၎င်းက -

၁။ queue ထဲကနေ packets တွေကို ဆွဲထုတ်ဖို့ ကြိုးစားပါတယ် (တစ်ကြိမ်ကို ၁၀ ခုအထိ)
၂။ packet တစ်ခုချင်းစီအတွက် JSON စာသားတစ်ခု တည်ဆောက်ပြီး Serial သို့ print ထုတ်ပါတယ်:
```json
{"timestamp": 123456, "rssi": -45, "channel": 6, "mac_src": "50:3E:AA:12:34:56", "mac_dst": "FF:FF:FF:FF:FF:FF", "bssid": "50:3E:AA:12:34:56", "type": "Management", "subtype": "Beacon", "ssid": "Smith_Family_WiFi"}
```
၃။ နောက်ထပ် channel တစ်ခုကို ကူးပြောင်းဖို့ အချိန်ရောက်မရောက် စစ်ဆေးပါတယ် (၂၀၀ မီလီစက္ကန့်တိုင်း)

### အဆင့် ၅ - USB ကြိုးက ဒေတာတွေကို သယ်ဆောင်သွားတယ်

JSON စာသားဟာ ESP32 ကနေ သင့်ကွန်ပျူတာဆီကို USB ကြိုးပေါ်ကနေ **115200 baud** (တစ်စက္ကန့်လျှင် bits အရေအတွက်) နဲ့ ခရီးသွားပါတယ်။ ဒါဟာ တစ်စက္ကန့်ကို ဇာတ်ကောင် (characters) ၁၁,၅၀၀ ခန့်ဖြစ်ပြီး — Wi-Fi management frames တွေအတွက် အများကြီး လုံလောက်ပါတယ်။

### အဆင့် ၆ - Python က Serial Port ကို ဖတ်တယ်

Python မှာ၊ `SerialReader` class ကို ဖွင့်ထားတဲ့ **background thread** တစ်ခု အလုပ်လုပ်နေပါတယ်။ ဤ thread က လုပ်ဆောင်ပေးတာက -

```python
while self.running:
    # ဤစာကြောင်းက အပြည့်အစုံ တစ်ကြောင်း မရောက်လာမချင်း စောင့်နေပါတယ် (ဒီနေရာမှာ blocks ဖြစ်တယ်)
    line = self.serial.readline()
    
    # Bytes ကို စာသား (text) အဖြစ် ပြောင်းတယ်
    text = line.decode('utf-8', errors='ignore').strip()
    
    # အကယ်၍ JSON နဲ့တူရင်၊ ၎င်းကို parse လုပ်တယ်
    if text.startswith('{') and text.endswith('}'):
        packet = json.loads(text)
        
        # GUI ဆီကို ပို့တယ် (thread-safe queue ကတစ်ဆင့်)
        self.callback(packet)
```

**ဘာကြောင့် background thread လဲ?** `serial.readline()` ဟာ blocking call တစ်ခုပါ — ဒေတာရောက်လာဖို့ သူက ထိုင်စောင့်နေပါတယ်။ ဒါကို ပင်မ GUI thread ထဲမှာသာ အလုပ်လုပ်ခိုင်းရင်၊ packet တစ်ခုကို စောင့်နေတိုင်း window တစ်ခုလုံး အေးခဲ (freeze) သွားပါလိမ့်မယ်။ နောက်ကွယ်က thread တစ်ခုမှာ ထားခြင်းအားဖြင့် GUI က ဆက်လက် တုံ့ပြန်နိုင် (responsive ဖြစ်) ပါတယ်။

### အဆင့် ၇ - Thread-Safe Bridge Queue

`SerialReader` thread က `app.add_packet(packet)` ကို ခေါ်ပါတယ်၊ ၎င်းက -

```python
def add_packet(self, packet):
    self.packet_queue.put(packet)   # Thread-safe queue ထဲသို့ ထည့်သည် (ချက်ချင်း!)
```

ဒီ queue (`queue.Queue`) ကို threads အများကြီးက အသုံးပြုဖို့ အထူးဒီဇိုင်းထုတ်ထားတာပါ။ ၎င်းက locking အားလုံးကို အတွင်းပိုင်းမှာ ကိုင်တွယ်ပေးပါတယ်။

### အဆင့် ၈ - GUI က Packet ကို လုပ်ဆောင်တယ် (၂၅၀ မီလီစက္ကန့် အကြာမှာ)

၂၅၀ မီလီစက္ကန့် (တစ်စက္ကန့်မှာ ၄ ကြိမ်) တိုင်း GUI က နိုးလာပြီး queue ထဲက packets တွေကို အလုပ်လုပ်ပါတယ် -

```python
def process_packet_queue(self):
    # queue ထဲကနေ packet အခု ၁၀၀ အထိ ယူဖို့ ကြိုးစားတယ်
    for _ in range(100):
        try:
            packet = self.packet_queue.get_nowait()
        except queue.Empty:
            break  # packet မရှိတော့ပါ
        
        # === အလုပ်အားလုံးကို ဤနေရာတွင် လုပ်ပါ ===
        
        # ၁။ packet အရေအတွက်ကို အပ်ဒိတ်လုပ်တယ်
        self.total_packets += 1
        
        # ၂။ အကယ်၍ Deauth ဖြစ်နေရင် ၎င်းကို ရေတွက်တယ်
        if packet['subtype'] == 'Deauthentication':
            self.deauth_count += 1
            if self.deauth_count % 10 == 0:
                self.alert_count += 1
        
        # ၃။ ဤ BSSID ကို ခြေရာခံတယ် (evil twin detection အတွက်)
        self.track_bssid(packet)
        
        # ၄။ evil twin ကို စစ်ဆေးတယ်
        self.check_for_evil_twin(packet)
        
        # ၅။ ဇယားထဲမှာ အတန်းတစ်တန်း ထည့်တယ်
        self.tree.insert("", 0, values=(
            current_time,
            f"{rssi} dBm",
            channel,
            network_name,
            src_mac,
            dst_mac,
            subtype
        ), tags=color_tags)
    
    # နောက်ထပ်အသုတ်ကို စီစဉ်တယ်
    self.after(250, self.process_packet_queue)
```

**ဘာကြောင့် batch (အသုတ်လိုက်) လုပ်တာလဲ?** တစ်ကြိမ်ကို packet တစ်ခုစီ အလုပ်လုပ်ရင် UI ကို တစ်စက္ကန့်မှာ အကြိမ် ၁၀၀၀ ကျော် update လုပ်ရမှာဖြစ်လို့ app က လေးသွားပါလိမ့်မယ်။ Batching (အများဆုံး packet ၁၀၀ ကို ၂၅၀ms တိုင်း = အများဆုံး ၄၀၀ packets/second) က ၎င်းကို ချောမွေ့စေပါတယ်။

### အဆင့် ၉ - သင် ၎င်းကို စခရင်ပေါ်မှာ မြင်ရတယ်

packet တွေကို အရောင်ကုဒ်တွေနဲ့အတူ ဇယားထဲမှာ အတန်းတစ်ခုအနေနဲ့ ပေါ်လာပါတယ် -
- **မီးခိုးရောင် အတန်းများ** = Beacons (ပုံမှန် AP ကြေညာချက်များ)
- **ခရမ်းရောင် အတန်းများ** = Probe Requests (ကွန်ရက်များကို ရှာဖွေနေသော စက်များ)
- **အနီရောင် အတန်းများ** = Deauthentication (တိုက်ခိုက်မှု ဖြစ်နိုင်သည်!)
- **နောက်ခံ အနီရောင် အတန်းများ** = သေချာမှု မြင့်မားသော (HIGH confidence) Evil Twin ထောက်လှမ်းတွေ့ရှိသည်!
- **နောက်ခံ လိမ္မော်ရောင်** = သေချာမှု အလယ်အလတ် (MEDIUM confidence) ရှိသော Evil Twin
- **နောက်ခံ အဝါရောင်** = သေချာမှု နည်းပါးသော (LOW confidence) Evil Twin

---

## ၇။ ESP32 Firmware ကို တစ်ကြောင်းချင်းစီ ရှင်းလင်းချက်

ဤအပိုင်းသည် `esp32_sniffer/esp32_sniffer.ino` ထဲရှိ အရေးပါသော စာကြောင်းတိုင်းကို ရှင်းပြပေးပါသည်။ သင် C++ ကို မသိရင်တောင် စိတ်မပူပါနဲ့ — အရာအားလုံးကို ကျွန်ုပ်တို့ ရှင်းပြပေးပါမယ်။

### ၇.၁ ထိပ်ပိုင်း (Includes နှင့် Configuration)

```cpp
#include "esp_wifi.h"       // Wi-Fi functions များကို ဝင်ရောက်အသုံးပြုခွင့်ပေးသည် (promiscuous mode အပါအဝင်)
#include <WiFi.h>           // ESP32 အတွက် စံ (Standard) Wi-Fi library
#include <freertos/FreeRTOS.h>  // FreeRTOS = Free Real-Time Operating System
#include <freertos/queue.h>     // Queue functions (ISR နှင့် main loop ကြားရှိ buffer)

// Configuration
const int CHANNEL_HOP_INTERVAL = 200; // channel များပြောင်းလဲသည့်ကြားရှိ မီလီစက္ကန့်များ
unsigned long lastHopTime = 0;        // နောက်ဆုံး channel ပြောင်းခဲ့သည့်အချိန်ကို မှတ်သားသည်
int currentChannel = 1;               // channel 1 မှ စတင်သည်
```

**FreeRTOS ဆိုတာ ဘာလဲ?** ၎င်းက ESP32 ပေါ်မှာ အလုပ်လုပ်တဲ့ လည်ပတ်မှုစနစ် (operating system) သေးသေးလေးတစ်ခုပါ။ ၎င်းက tasks (အလုပ်) တွေ အများကြီး၊ အချိန်နဲ့ တပြေးညီဖြစ်မှု (timing) နဲ့ queues တွေကို ကိုင်တွယ်ပေးပါတယ်။ ၎င်းကို အရာအားလုံး အစီအစဉ်တကျဖြစ်အောင် လုပ်ပေးတဲ့ "စပယ်ယာ (conductor)" လို့ မှတ်ယူနိုင်ပါတယ်။

### ၇.၂ The Packet Struct

```cpp
typedef struct {
    uint32_t timestamp;    // ဤ packet ကို ဘယ်အချိန်မှာ ဖမ်းမိတာလဲ? (စက်ပွင့်ပြီးနောက် မီလီစက္ကန့်များ)
    int8_t rssi;           // Signal strength (-30 to -90 dBm)
    uint8_t channel;       // ဘယ် Wi-Fi channel (1-13)
    uint8_t macSrc[6];     // Source MAC address (ဘယ်သူပို့တာလဲ) — 6 bytes
    uint8_t macDst[6];     // Destination MAC (ဘယ်သူ့အတွက်လဲ)
    uint8_t bssid[6];      // BSSID = AP ရဲ့ MAC (header ထဲက Address 3)
    uint8_t frameSubtype;  // 0-15 (Beacon=8, Deauth=12, စသည်)
    char ssid[33];         // ကွန်ရက်အမည် (အများဆုံး 32 chars + null terminator)
} SniffPacket;             // စုစုပေါင်း: 4+1+1+6+6+6+1+33 = 58 bytes, တကယ်တမ်း 36 packed
```

**ဘာကြောင့် ဒီလောက် သေးရတာလဲ?** ဤ struct ကို queue ထဲသို့ ကူးယူပါသည်။ သေးငယ်လေ = ပိုမြန်လေ = packets များ ကျကျန်ရစ်မည့် အခွင့်အရေး ပိုနည်းလေ ဖြစ်သည်။ ကျွန်ုပ်တို့ တကယ်လိုအပ်တာကိုသာ သိမ်းဆည်းထားပါသည်။

### ၇.၃ The Queue

```cpp
QueueHandle_t packetQueue;     // ကျွန်ုပ်တို့၏ queue အတွက် "handle" (pointer) တစ်ခု
const int QUEUE_SIZE = 50;     // buffer ထဲရှိ အများဆုံး packet ၅၀
```

queue ကို packet ၅၀ ဆံ့တဲ့ **ပုံး (bucket)** တစ်ခုအနေနဲ့ မြင်ယောင်ကြည့်ပါ။ ISR (မြန်သည်) က ပုံးကို အပေါ်ကနေ ဖြည့်ပါတယ်။ main loop (နှေးသည်) က အောက်ကနေ ပြန်ထုတ်ပါတယ်။ ပုံးပြည့်သွားရင်တော့ လျှံကျပြီး စနစ်ကို crash ဖြစ်စေမယ့်အစား packets အသစ်တွေက အပြင်ဘက်ကို (dropped ဖြစ်) ထွက်သွားပါတယ်။

### ၇.၄ ISR Callback ("လက်မြန်သူ")

```cpp
void wifi_promiscuous_cb(void *buf, wifi_promiscuous_pkt_type_t type) {
    // အဆင့် ၁: Management frames များကိုသာ ဂရုစိုက်ပါ
    if (type != WIFI_PKT_MGMT) return;
    
    // အဆင့် ၂: packet အကြမ်းထည် ဒေတာဆီသို့ ညွှန်ပါ
    wifi_promiscuous_pkt_t *pkt = (wifi_promiscuous_pkt_t *)buf;
    uint8_t *payload = pkt->payload;
    
    // အဆင့် ၃: type နှင့် subtype ကိုရယူရန် Frame Control byte ကို Parse လုပ်ပါ
    // 802.11 frame တိုင်းရဲ့ ပထမဆုံး ၂ ဘိုက်က ဘယ်အမျိုးအစားဆိုတာ ကျွန်ုပ်တို့ကို ပြောပြတယ်
    uint16_t fc = payload[0] | (payload[1] << 8);
    uint8_t frameType = (fc & 0x0C) >> 2;     // Bits 2-3 (0=Management, 1=Control, 2=Data)
    uint8_t frameSubtype = (fc & 0xF0) >> 4;  // Bits 4-7 (တိကျသောအမျိုးအစား)
    
    // အဆင့် ၄: Management (Type 0) ဟုတ်မဟုတ် နှစ်ခါပြန်စစ်ပါ
    if (frameType != 0) return;
    
    // အဆင့် ၅: ကျွန်ုပ်တို့၏ struct ကို ဖြည့်ပါ
    SniffPacket p;
    p.timestamp = millis();                    // ESP32 ပွင့်ပြီးကတည်းက အချိန်
    p.rssi = pkt->rx_ctrl.rssi;               // ရေဒီယိုမှ Signal strength
    p.channel = pkt->rx_ctrl.channel;          // ရေဒီယိုမှ Channel
    p.frameSubtype = frameSubtype;
    
    // packet header မှ MAC addresses များကို ကူးယူပါ
    // 802.11 header layout: ... | Addr1 (6) | Addr2 (6) | Addr3 (6) | ...
    // Addr1 = Destination (offset 4), Addr2 = Source (offset 10), Addr3 = BSSID (offset 16)
    memcpy(p.macDst, &payload[4], 6);    // offset 4 မှစ၍ ၆ ဘိုက် ကူးယူပါ
    memcpy(p.macSrc, &payload[10], 6);   // offset 10 မှစ၍ ၆ ဘိုက် ကူးယူပါ
    memcpy(p.bssid,  &payload[16], 6);   // offset 16 မှစ၍ ၆ ဘိုက် ကူးယူပါ
    
    // အဆင့် ၆: SSID (Beacon နှင့် Probe Response frames များတွင်သာ) ထုတ်ယူရန် ကြိုးစားပါ
    p.ssid[0] = '\0';  // ပုံသေအားဖြင့် အလွတ်အဖြစ် သတ်မှတ်ပါ
    
    if (frameSubtype == 8 || frameSubtype == 5) {
        // Beacon (8) နှင့် Probe Response (5) တွင် tagged parameters များရှိသည်
        // ပုံစံမှာ: Tag Number (1 byte) | Tag Length (1 byte) | Value (N bytes)
        // Tag 0 = SSID, Tag 1 = Supported Rates, Tag 3 = Channel, စသည်.
        
        int offset = 36;  // Tagged parameters များသည် 36 byte မှစသည်
        if (offset + 1 < pkt->rx_ctrl.sig_len) {  // packet ထက်ပိုမဖတ်မိစေရန် သေချာစေပါ
            if (payload[offset] == 0) {  // ၎င်းသည် Tag 0 (SSID tag) လား?
                int ssid_len = payload[offset + 1];  // နောက် byte = SSID ၏အရှည်
                if (ssid_len > 0 && ssid_len <= 32) {  // SSID သည် 32 ထက်ပိုမရှည်နိုင်ပါ
                    memcpy(p.ssid, &payload[offset + 2], ssid_len);  // နာမည်ကို ကူးယူပါ
                    p.ssid[ssid_len] = '\0';  // string terminator ထည့်ပါ
                }
            }
        }
    }
    
    // အဆင့် ၇: queue ထဲသို့ push လုပ်ပါ (non-blocking — ချက်ချင်း return ပြန်သည်)
    // queue ပြည့်နေပါက packet ကို အလွယ်တကူ ပစ်ချလိုက်သည် (crash မဖြစ်ပါ!)
    xQueueSendFromISR(packetQueue, &p, NULL);
}
```

**ISRs နဲ့ ပတ်သက်တဲ့ အဓိက စည်းမျဉ်း:** ဤနေရာတွင် လေးလံသော (heavy) အလုပ်များကို ဘယ်တော့မှ မလုပ်ပါနှင့်။ print ထုတ်ခြင်းမရှိ၊ ရှုပ်ထွေးသော တွက်ချက်မှုမရှိ၊ memory ယူသုံးခြင်း မရှိစေရ။ သင်လိုအပ်တာကို ကူးယူပါ၊ queue ထဲကို push လုပ်ပါ၊ ပြီးတာနဲ့ ချက်ချင်း ထွက်လိုက်ပါ။ "အလုပ်အစစ်အမှန်" က main loop ထဲမှာ ဖြစ်ပျက်တာပါ။

### Setup Function

```cpp
void setup() {
    // အဆင့် ၁: 115200 baud ဖြင့် Serial ဆက်သွယ်ရေးကို ဖွင့်ပါ
    // ၎င်းသည် သင့်ကွန်ပျူတာနှင့် USB ချိတ်ဆက်မှုဖြစ်သည်
    Serial.begin(115200);
    
    // အဆင့် ၂: queue ကို ဖန်တီးပါ (packet ၅၀ အတွက် ပုံး)
    packetQueue = xQueueCreate(QUEUE_SIZE, sizeof(SniffPacket));
    
    // အဆင့် ၃: ESP32 ကို "station mode" တွင် ထားပါ (router ကဲ့သို့မဟုတ်ဘဲ ဖုန်းတစ်လုံးကဲ့သို့)
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();          // မည်သည့်ကွန်ရက်ကိုမှ မချိတ်ဆက်ပါနှင့်
    
    // အဆင့် ၄: promiscuous mode ကိုဖွင့်ပါ — အရာအားလုံးကို ကြားပါ
    esp_wifi_set_promiscuous(true);
    // packet တိုင်းအတွက် ခေါ်ရန် ကျွန်ုပ်တို့၏ callback function ကို မှတ်ပုံတင်ပါ
    esp_wifi_set_promiscuous_rx_cb(&wifi_promiscuous_cb);
    
    // အဆင့် ၅: စတင်ခြင်း မက်ဆေ့ချ်တစ်ခုကို Print ထုတ်ပါ
    Serial.println("{\"log\": \"ESP32 Sniffer initialized. Waiting for packets...\"}");
}
```

**115200 ဆိုတာ ဘာလဲ?** ၎င်းသည် တစ်စက္ကန့်လျှင် USB serial connection ၏ မြန်နှုန်း (bits per second) ဖြစ်သည်။ 115200 baud = တစ်စက္ကန့်လျှင် ဇာတ်ကောင် (characters) ၁၁,၅၀၀ ခန့်။ Wi-Fi management frames များအတွက် လုံလောက်စွာ မြန်ဆန်သော်လည်း တည်ငြိမ်ရန်အတွက် လုံလောက်စွာ နှေးကွေးသောကြောင့် ၎င်းကို ရွေးချယ်ခဲ့ခြင်းဖြစ်သည်။

### Main Loop

```cpp
void loop() {
    // အလုပ် ၁: Channel ကို ပြောင်းလဲခြင်း
    // နောက်ဆုံးပြောင်းခဲ့ပြီးနောက် ၂၀၀ မီလီစက္ကန့် ကြာပြီးပါက၊ channel ကို ပြောင်းပါ
    if (millis() - lastHopTime > CHANNEL_HOP_INTERVAL) {
        lastHopTime = millis();
        currentChannel++;
        if (currentChannel > 13) currentChannel = 1;  // 13 ပြီးနောက် ပြန်ပတ်သည်
        esp_wifi_set_channel(currentChannel, WIFI_SECOND_CHAN_NONE);
    }
    
    // အလုပ် ၂: queue မှ packets များကို အလုပ်လုပ်ပါ
    SniffPacket p;
    int packetsProcessed = 0;  // တစ်ခေါက်လျှင် ၁၀ ခုဟု ကန့်သတ်ပါ
    
    while (xQueueReceive(packetQueue, &p, 0) == pdTRUE && packetsProcessed < 10) {
        // subtype နံပါတ်ကို လူဖတ်လို့ရမည့် နာမည်အဖြစ် ပြောင်းပါ
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
        
        // packet ကို JSON အဖြစ် Print ထုတ်ပါ
        // Serial.printf သည် ဤနေရာတွင် (ISR တွင်မဟုတ်ဘဲ main loop တွင်) SAFE ဖြစ်သည်
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
    
    // အလုပ် ၃: FreeRTOS ကို ၎င်း၏အလုပ်လုပ်ရန် အနည်းငယ် နှောင့်နှေး (delay) ပေးပါ
    delay(1);
}
```

**ဘာကြောင့် loop တစ်ခုမှာ 10 packets လို့ ကန့်သတ်ထားတာလဲ?** အကယ်၍ ကျွန်ုပ်တို့က loop တစ်ခုမှာ packet အားလုံးကို အလုပ်လုပ်မယ်ဆိုရင် channel hopping ကို ဘယ်တော့မှ မရောက်နိုင်ဘဲ၊ တခြား channel တွေက အရာအားလုံးကို ESP32 က လွတ်သွားပါလိမ့်မယ်။ (အချိန် ၁၀ms ခန့်ယူတဲ့) packet ၁၀ ခုကို အလုပ်လုပ်ပြီးနောက် ပြန်ပတ်ခြင်းက အရာအားလုံးကို မျှတမှုရှိစေပါတယ်။

### Channel Hopping ရှင်းလင်းချက်

Wi-Fi 2.4GHz တွင် လိုင်း ၁၃ ခု (၁ မှ ၁၃ အထိ) ရှိသည်။ အကယ်၍ ကျွန်ုပ်တို့က channel 1 တစ်ခုတည်းကိုပဲ နားထောင်နေရင်၊ channels 2-13 မှာရှိတဲ့ အရာအားလုံး လွတ်သွားမှာပါ။ ၂၀၀ms တိုင်း ပြောင်းလဲခြင်းဖြင့် အသွားအလာ (traffic) အားလုံးရဲ့ နမူနာကို ကျွန်ုပ်တို့ ကြားရပါတယ် -

```
အချိန်:    0ms    200ms   400ms   600ms   800ms   1000ms
         Ch1    Ch2     Ch3     Ch4     Ch5     Ch6 ...
         │      │       │       │       │       │
Traffic: ████   ██     █████   █       ███     ██
         (sample)(sample)(sample)(sample)(sample)(sample)
```

ကျွန်ုပ်တို့က အရာအားလုံးကိုတော့ မကြားရပါဘူး၊ ဒါပေမယ့် channels အားလုံးမှာ ဘာတွေဖြစ်နေလဲဆိုတာကို ကောင်းကောင်း မြင်သာစေပါတယ်။

---

## ၈။ Python Serial Reader ကို တစ်ကြောင်းချင်းစီ ရှင်းလင်းချက်

ဤဖိုင်သည် **နောက်ကွယ်ရှိ thread တစ်ခု (background thread)** အဖြစ် အလုပ်လုပ်ပြီး USB serial ဆက်သွယ်ရေး အားလုံးကို ကိုင်တွယ်ပေးသည်။

```python
import serial    # serial ports (USB) ဖတ်/ရေးရန် စာကြည့်တိုက် (Library)
import threading # ကုဒ်များကို တပြိုင်နက်အလုပ်လုပ်စေရန် စာကြည့်တိုက်
import json      # JSON စာသားများကို parse လုပ်ရန် စာကြည့်တိုက်
import time      # delays အတွက် စာကြည့်တိုက်

class SerialReader:
    """
    Serial port မှ ဒေတာများကို background thread တွင် ဖတ်ပေးသော class တစ်ခု။
    JSON packet တစ်ခု ရောက်လာသောအခါ၊ 'callback' function ကို ခေါ်သည်။
    """
    
    def __init__(self, callback):
        """
        Reader ကို ပြင်ဆင်ပါ၊ သို့သော် မချိတ်ဆက်သေးပါ။
        'callback' သည် packet တိုင်းနှင့်အတူ ခေါ်ခံရမည့် function ဖြစ်သည်။
        """
        self.serial = None       # serial port object (မဖွင့်ရသေးပါ)
        self.thread = None       # background thread (မစရသေးပါ)
        self.running = False     # မစတင်သေးပါ
        self.callback = callback # callback function ကို သိမ်းဆည်းပါ

    def connect(self, port, baudrate):
        """
        ESP32 သို့ serial ဆက်သွယ်မှု ဖွင့်ပါ။
        'port' သည် 'COM5' (Windows) သို့မဟုတ် '/dev/ttyUSB0' (Linux/Mac) ကဲ့သို့ဖြစ်သည်။
        'baudrate' သည် အမြန်နှုန်း (115200) ဖြစ်သည်။
        """
        try:
            # serial port ကို ဖွင့်ပါ
            # timeout=1 ဆိုသည်မှာ: ဖတ်သည့်အခါ ဒေတာအတွက် အများဆုံး ၁ စက္ကန့် စောင့်ပါ
            self.serial = serial.Serial(port, baudrate, timeout=1)
            self.running = True
            
            # 'daemon' thread ကို ဖန်တီးပြီး စတင်ပါ
            # Daemon = ပင်မပရိုဂရမ် (main program) ထွက်သွားသည့်အခါ အလိုအလျောက် ရပ်တန့်သည်
            # target=self.read_loop = ဤ thread အလုပ်လုပ်မည့် function
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()
            
            return True  # အောင်မြင်သည်!
        except Exception as e:
            print(f"Error connecting to serial: {e}")
            return False  # ကျရှုံးသည်

    def disconnect(self):
        """serial ဆက်သွယ်မှုကို ပိတ်ပြီး thread ကို ရပ်ပါ။"""
        self.running = False  # ရပ်ရန် thread ကို အချက်ပြပါ
        
        if self.thread:
            self.thread.join(timeout=2)  # ရပ်ရန် ၂ စက္ကန့်အထိ စောင့်ပါ
        
        if self.serial and self.serial.is_open:
            self.serial.close()  # USB port ကို ပိတ်ပါ

    def read_loop(self):
        """
        ဤ function သည် သီးခြား THREAD တစ်ခုတွင် အမြဲတမ်း အလုပ်လုပ်သည်။
        ၎င်းသည် serial မှ စာကြောင်းများကို ဖတ်ပြီး JSON အဖြစ် parse လုပ်သည်။
        """
        while self.running and self.serial and self.serial.is_open:
            try:
                # serial port မှ စာတစ်ကြောင်း ဖတ်ပါ
                # ဤအရာက (\n နှင့်ဆုံးသော) အပြည့်အစုံ တစ်ကြောင်း မရောက်လာမချင်း BLOCKS (စောင့်) နေပါသည်
                # ၎င်းသည် သီးခြား thread တွင်ရှိသောကြောင့် GUI ကို BLOCK မလုပ်ပါ!
                line = self.serial.readline()
                
                # Bytes ကို စာသား (text) သို့ ပြောင်းပါ၊ အပို space များကို ဖယ်ရှားပါ
                text = line.decode('utf-8', errors='ignore').strip()
                
                if text:
                    # JSON လားဆိုတာ စစ်ဆေးပါ ({ ဖြင့်စပြီး } ဖြင့်ဆုံးသည်)
                    if text.startswith('{') and text.endswith('}'):
                        try:
                            # JSON string ကို Python dictionary အဖြစ် Parse လုပ်ပါ
                            packet_data = json.loads(text)
                            
                            # (GUI သို့ ပို့ပေးသော) callback function ကို ခေါ်ပါ
                            self.callback(packet_data)
                        except json.JSONDecodeError:
                            # JSON မှားယွင်းနေသည် — error ကို print ထုတ်ပြီး ဆက်လုပ်ပါ
                            print(f"Failed to parse JSON: {text}")
                    else:
                        # JSON မဟုတ်ပါ — ESP32 မှ debug message ဖြစ်နိုင်သည်
                        print(f"ESP32: {text}")
            except Exception as e:
                print(f"Serial read error: {e}")
                time.sleep(1)  # ပြန်မစမ်းမီ အနည်းငယ် စောင့်ပါ
```

### Threading ရှင်းလင်းချက်

```
ပင်မ THREAD (GUI):                    SERIAL THREAD:
─────────────────────────             ────────────────────────
ပြတင်းပေါက် ဆွဲပါ                        serial port ဖွင့်ပါ
widgets များကို ဖန်တီးပါ                  အဆုံးမရှိသော loop ကို စတင်ပါ:
│                                    │
├── CONNECT ကို နှိပ်ပါ                    ├── readline() ← ဒီနေရာမှာ BLOCKS ဖြစ်တယ်
│                                    │
├── on_click:                        │   (ဒေတာစောင့်နေသည်...)
│   SerialReader ဖန်တီးပါ             │
│   reader.connect()                 │
│       thread စတင်ပါ ───────────────►│
│                                    │   ဒေတာ ရောက်လာပြီ!
│   ချက်ချင်း return ပြန်ပါ               │   json.loads(line)
│   (thread က နောက်ကွယ်မှာ အလုပ်လုပ်) │   callback(packet)
│                                    │       │
│   ┌──────────────────────────────┐ │       │
│   │  UI တုံ့ပြန်မှု ရှိနေဆဲ             │ │       │
│   │  (ခလုတ်များ၊ ရွှေ့ခြင်း စသည်)     │ │       ▼
│   └──────────────────────────────┘ │   packet_queue.put(packet)
│                                    │
│   (၂၅၀ မီလီစက္ကန့် အကြာတွင်)            │   readline() ← ထပ်ပြီး BLOCKS ဖြစ်တယ်
│   process_packet_queue()           │
│   packet_queue.get_nowait() ◄──────┤
│   treeview ကို အပ်ဒိတ်လုပ်ပါ             │
│   stats ကို အပ်ဒိတ်လုပ်ပါ               │
│   evil twin ကို ထောက်လှမ်းပါ             │
│                                    │
│   (၂၅၀ မီလီစက္ကန့် အကြာတွင်)            │
│   process_packet_queue() ──────────┤ (ဆက်လုပ်နေသည်)
│                                    │
```

**ဘာကြောင့် ဒါက လိုအပ်တာလဲ?** `serial.readline()` က ဒေတာကို စောင့်ပါတယ်။ အကယ်၍ ESP32 က ဘာမှ မပို့သေးဘူးဆိုရင် (channel က တိတ်ဆိတ်နေတာပဲဖြစ်ဖြစ်)၊ `readline()` က အဲဒီမှာ ထိုင်ပြီး စောင့်နေလိမ့်မယ်... စောင့်နေလိမ့်မယ်... အဲဒီအခါ GUI တစ်ခုလုံးက freeze ဖြစ်သွားပါလိမ့်မယ်။ serial ဖတ်ခြင်းကို တခြား thread တစ်ခုမှာ ထားခြင်းအားဖြင့်၊ GUI ကို သက်ဝင်နေစေပြီး နှိပ်လို့ရနေစေပါတယ်။

---

## ၉။ Dashboard ကို တစ်ကြောင်းချင်းစီ ရှင်းလင်းချက်

၎င်းသည် (စာကြောင်းရေ ၈၆၄ ကြောင်းရှိသော `gui/app.py`) အကြီးဆုံး ဖိုင်ဖြစ်သည်။ ၎င်းကို ယုတ္တိကျသော အပိုင်းများအဖြစ် ခွဲကြည့်ကြပါစို့။

### ၉.၁ ပြတင်းပေါက် ဖွဲ့စည်းပုံ (Window Layout)

```
┌─────────────────────────────────────────────────────────────────────┐
│  SIDEBAR (ပုံသေ 240px)         │     MAIN CONTENT (ကျန်နေရာအပြည့်)  │
│  ───────────────────────       │  ┌────────────────────────────────┐ │
│  🛡️ Sentinel WIDS              │  │  STATS CARDS (အပေါ်ဆုံးဘား)     │ │
│                                 │  │  ┌────────┐ ┌────────┐ ┌────┐ │ │
│  [COM Port: ________]          │  │  │TOTAL   │ │DEAUTH  │ │ALRT│ │ │
│  [Baud Rate: 115200]           │  │  │ 1,234  │ │   56   │ │  3 │ │ │
│                                 │  │  └────────┘ └────────┘ └────┘ │ │
│  [ CONNECT  ]                   │  ├────────────────────────────────┤ │
│                                 │  │  LIVE TRAFFIC STREAM (တိုက်ရိုက်လွှင့်ချက်) │ │
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

### ၉.၂ ဒေတာ တည်ဆောက်ပုံများ (App ၏ "မှတ်ဉာဏ်")

```python
# === ဤအရာများသည် app ၏ မှတ်စုစာအုပ်များကဲ့သို့ဖြစ်သည် ===

# ၁။ ကွန်ရက်အမည် ရှာဖွေခြင်း: MAC address → Network Name
self.network_map = {
    "50:3E:AA:12:34:56": "Smith_Family_WiFi",
    "AA:BB:CC:DD:EE:FF": "CoffeeShop"
}

# ၂။ ပြောင်းပြန် ရှာဖွေခြင်း: Network Name → ၎င်းကိုအသုံးပြုနေသော MACs အစု
self.ssid_to_bssid = {
    "Smith_Family_WiFi": {"50:3E:AA:12:34:56", "02:00:00:AB:CD:EF"},
    "CoffeeShop":        {"AA:BB:CC:DD:EE:FF"}
}

# ၃။ AP တစ်ခုချင်းစီသည် မည်သည့် channel တွင် ရှိသနည်း?
self.bssid_channel = {
    "50:3E:AA:12:34:56": 6,
    "02:00:00:AB:CD:EF": 11
}

# ၄။ Signal သမိုင်းကြောင်း (MAC တစ်ခုအတွက် နောက်ဆုံး အကြိမ် ၂၀ မှတ်တမ်း)
# deque = အများဆုံးအရွယ်အစားရှိသော list တစ်ခု; အဟောင်းများ အလိုအလျောက် ပျောက်သွားသည်
self.bssid_rssi = {
    "50:3E:AA:12:34:56": deque([-45, -44, -46, -43, -45, ...], maxlen=20),
    "02:00:00:AB:CD:EF": deque([-72, -68, -75, -70, -71, ...], maxlen=20)
}

# ၅။ MAC တစ်ခုစီကို ကျွန်ုပ်တို့ ပထမဆုံး ဘယ်အချိန်မှာ တွေ့ခဲ့သလဲ?
self.bssid_first_seen = {
    "50:3E:AA:12:34:56": 1234567890.5,  # Unix timestamp
    "02:00:00:AB:CD:EF": 1234567898.2   # ၈ စက္ကန့် အကြာမှာ!
}

# ၆။ MAC တစ်ခုစီမှ packets ဘယ်လောက် တွေ့ပြီးပြီလဲ?
self.bssid_seen_count = {
    "50:3E:AA:12:34:56": 152,
    "02:00:00:AB:CD:EF": 37
}

# ၇။ Whitelist (ဖိုင်ထဲသို့ သိမ်းဆည်းသည်) — ကျွန်ုပ်တို့ ယုံကြည်သော MACs များ
self.whitelist = {
    "Starbucks_WiFi": {"AA:AA:AA:BB:BB:BB", "CC:CC:CC:DD:DD:DD"}
}

# ၈။ Alert သမိုင်းကြောင်း
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

# ၉။ Thread-safe packet queue (threads ကြားရှိ တံတား)
self.packet_queue = queue.Queue()
```

### ၉.၃ ကိန်းဂဏန်း ကတ်များ (The Stats Cards)

```python
def create_stat_card(self, parent, title, value, col, highlight_color):
    """
    စာရင်းအင်းကိန်းဂဏန်းတစ်ခုကို ပြသသော "ကတ်" တစ်ခုကို ဖန်တီးသည်။
    parent = ၎င်းကိုထည့်မည့် frame
    title = "TOTAL PACKETS"
    value = "0" (အပ်ဒိတ်ဖြစ်လိမ့်မည်)
    col = မည်သည့်ကော်လံ (0, 1, or 2)
    highlight_color = ဂဏန်းအတွက် အရောင် (အစိမ်း၊ လိမ္မော်၊ အနီ)
    """
    card = ctk.CTkFrame(parent, fg_color="#18181b", corner_radius=12, height=110)
    card.grid(row=0, column=col, padx=10, sticky="ew")
    card.grid_propagate(False)  # အကြောင်းအရာက ကတ်ကို အရွယ်အစားမပြောင်းစေရန်
    
    # ခေါင်းစဉ် လေဘယ် (သေးငယ်သည်၊ မီးခိုးရောင်)
    title_lbl = ctk.CTkLabel(card, text=title, 
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color="#a1a1aa")
    title_lbl.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
    
    # တန်ဖိုး လေဘယ် (ကြီးမားသည်၊ အရောင်ပါသော ဂဏန်း)
    val_lbl = ctk.CTkLabel(card, text=value,
                           font=ctk.CTkFont(size=36, weight="bold"),
                           text_color=highlight_color)
    val_lbl.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
    
    return val_lbl  # လေဘယ်ကို return ပြန်ပါ (နောက်မှ update လုပ်ရန်)
```

### ၉.၄ Packet အလုပ်လုပ်မည့် အင်ဂျင်

၎င်းသည် app ၏ နှလုံးသားဖြစ်သည်။ ၎င်းသည် ၂၅၀ မီလီစက္ကန့်တိုင်း အလုပ်လုပ်ပြီး packets များကို အလုပ်လုပ်ပေးသည်။

```python
def process_packet_queue(self):
    """GUI main loop မှ ၂၅၀ မီလီစက္ကန့်တိုင်း ခေါ်သည်။"""
    packets_to_insert = []  # တစ်ပြိုင်တည်း ထည့်ရန် packets များကို စုဆောင်းပါ
    
    try:
        # UI လေးလံမှုမဖြစ်စေရန် တစ်ကြိမ်လျှင် packets ၁၀၀ အထိ လုပ်ဆောင်ပါ
        for _ in range(100):
            packet = self.packet_queue.get_nowait()  # Non-blocking ဖြင့် ယူပါ
            
            # ─── ရေတွက်စက်များကို အပ်ဒိတ်လုပ်ပါ ───
            self.total_packets += 1
            subtype = packet.get('subtype', '')
            
            # ─── DEAUTH ကို ထောက်လှမ်းခြင်း ───
            if subtype == "Deauthentication":
                self.deauth_count += 1
                # deauth ၁၀ ခုတိုင်းတွင် Alert ပြပါ (အများအပြား ဝင်လာမှုကို တားဆီးရန်)
                if self.deauth_count % 10 == 0:
                    self.alert_count += 1
                    self.alerts_list.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Deauth Flood",
                        "severity": "High",
                        "details": f"Target MAC: {packet.get('mac_dst', 'Unknown')}"
                    })
            
            # ─── PACKET FIELDS များကို ထုတ်ယူပါ ───
            bssid = packet.get('bssid', '')
            ssid = packet.get('ssid', '')
            mac_src = packet.get('mac_src', '')
            mac_dst = packet.get('mac_dst', '')
            channel = packet.get('channel', None)
            rssi = packet.get('rssi', None)
            
            # ─── ကွန်ရက်များကို ခြေရာခံပါ ───
            if ssid and bssid:
                self.network_map[bssid] = ssid  # MAC → name
                
                # ဤ MAC ကို ပထမဆုံးအကြိမ် တွေ့ခြင်းလား?
                if bssid not in self.bssid_first_seen:
                    self.bssid_first_seen[bssid] = time.time()
                
                # Channel ကို ခြေရာခံပါ
                if channel:
                    self.bssid_channel[bssid] = int(channel)
                
                # RSSI သမိုင်းကြောင်းကို ခြေရာခံပါ (အကြိမ် ၂၀ မှတ်တမ်း)
                if rssi is not None:
                    try:
                        if bssid not in self.bssid_rssi:
                        self.bssid_rssi[bssid] = collections.deque(maxlen=20)
                        self.bssid_rssi[bssid].append(int(rssi))
                    except (ValueError, TypeError):
                        pass
                
                # မည်သည့် SSID က မည်သည့် BSSIDs ကို သုံးသလဲဆိုတာ ခြေရာခံပါ
                if ssid not in self.ssid_to_bssid:
                    self.ssid_to_bssid[ssid] = set()
                self.ssid_to_bssid[ssid].add(bssid)
                
                # ဤ BSSID အတွက် packet အရေအတွက်ကို တိုးပါ
                self.bssid_seen_count[bssid] = self.bssid_seen_count.get(bssid, 0) + 1
                
                # ─── EVIL TWIN ကို ထောက်လှမ်းခြင်း ───
                # (အပိုင်း ၁၀ တွင် အသေးစိတ် ရှင်းပြထားသည်)
                if self.should_check_evil_twin(ssid, bssid):
                    score, reasons = self._score_evil_twin(ssid, bssid, channel, rssi)
                    if score > 0:
                        self.handle_evil_twin_alert(ssid, bssid, score, reasons)
            
            # ─── ပြသရန်အတွက် အတန်းကို ပြင်ဆင်ပါ ───
            # ပြသရန် ကွန်ရက်အမည်ကို ဆုံးဖြတ်ပါ
            network_name = self.network_map.get(bssid, "")
            
            # သက်ဆိုင်ပါက evil twin လေဘယ်တပ်ပါ
            if packet.get('is_evil_twin'):
                if bssid == packet.get('et_rogue_mac'):
                    network_name = f"🔴 ROGUE AP — {network_name}"
                elif bssid == packet.get('et_legit_mac'):
                    network_name = f"✅ LEGITIMATE — {network_name}"
            
            packet['network_name'] = network_name
            
            # ဤ packet ကို ပြသင့်မပြသင့် စစ်ဆေးပါ (filtering)
            if not self.should_show_packet(packet):
                continue
            
            packets_to_insert.append(packet)
            
    except queue.Empty:
        pass  # queue ထဲတွင် packet မရှိတော့ပါ — ပုံမှန်ပါပဲ
    
    # ─── DISPLAY ကို အပ်ဒိတ်လုပ်ပါ ───
    if packets_to_insert:
        # stat ကတ်များကို အပ်ဒိတ်လုပ်ပါ
        self.stat_packets.configure(text=str(self.total_packets))
        self.stat_deauth.configure(text=str(self.deauth_count))
        self.stat_alerts.configure(text=str(self.alert_count))
        
        # treeview ထဲသို့ အတန်းများ ထည့်သွင်းပါ
        for packet in packets_to_insert:
            self.insert_packet_row(packet)
        
        # treeview ကို အများဆုံး အတန်း ၅၀၀ ထိ ဖြတ်ထုတ်ပါ
        children = self.tree.get_children()
        if len(children) > 500:
            for child in children[500:]:
                self.tree.delete(child)
    
    # နောက်ထပ်အသုတ်ကို စီစဉ်ပါ
    self.after(250, self.process_packet_queue)
```

---

## ၁၀။ Evil Twin ကို ထောက်လှမ်းခြင်း (ဉာဏ်ကောင်းသော အပိုင်း)

၎င်းသည် စနစ်၏ အဆင့်မြင့်ဆုံးအပိုင်းဖြစ်သည်။ BSSID တစ်ခုသည် ကွန်ရက်အစစ်တစ်ခု၏ အတုအယောင်ဗားရှင်း ဟုတ်မဟုတ် ဆုံးဖြတ်ရန် ၎င်းသည် **မတူညီသော လက္ခဏာရပ် ၈ ချက် (signals)** ကို အသုံးပြုသည်။

### ၁၀.၁ အဓိက ပြဿနာ

```
ကွန်ရက်အစစ် (Router):                    မသင်္ကာဖွယ် BSSID (Hacker):
  SSID: "CoffeeShop_Free"                  SSID: "CoffeeShop_Free"
  BSSID: 50:3E:AA:12:34:56                 BSSID: 02:00:00:AB:CD:EF
  OUI: TP-Link ✓                           OUI: Locally Administered ✗
  Channel: 6                               Channel: 11
  Avg RSSI: -45 dBm                        Avg RSSI: -72 dBm
  First seen: 12:00:00                     First seen: 12:05:30 (၅ မိနစ် နောက်ကျသည်)
  RSSI variance: 2.1 (တည်ငြိမ်သည်)            RSSI variance: 35.8 (မတည်ငြိမ်ပါ)
```

**မေးခွန်း -** `02:00:00:AB:CD:EF` သည် `50:3E:AA:12:34:56` ၏ evil twin ဟုတ်ပါသလား?  
**အဖြေ -** ဟုတ်လောက်ပါသည်။ ၎င်းကို အမှတ်ပေး (score) ကြည့်ကြပါစို့!

### ၁၀.၂ Signal ၁: BSSID တိုက်ဆိုင်မှု (+50 Base)

```python
# အကယ်၍ SSID တစ်ခုတွင် BSSID တစ်ခုထက်ပိုရှိနေပါက၊ ၎င်းသည် မသင်္ကာစရာဖြစ်သည်
known_bssids = self.ssid_to_bssid.get(ssid, set()) - {bssid}
if not known_bssids:
    # ဤ SSID အတွက် BSSID တစ်ခုတည်းသာ ရှိသည် — တိုက်ဆိုင်မှုမရှိပါ၊ evil twin မဟုတ်ပါ
    return 0, []

# Base score: တိုက်ဆိုင်မှု (conflict) ရှိသည်
score += 50
reasons.append(f"SSID '{ssid}' ကို MACs များစွာမှ ထုတ်လွှင့်နေသည်")
```

**နှိုင်းယှဉ်ချက် -** လမ်းတစ်ခုတည်းပေါ်မှာ နာမည်တူတဲ့ ဆိုင်နှစ်ဆိုင်ကို သင်တွေ့လိုက်ရတယ်။ တစ်ဆိုင်က အစစ်ဖြစ်ပြီး တစ်ဆိုင်က အတုပါ။ နှစ်ဆိုင် (TWO) ဖြစ်နေတယ်ဆိုတဲ့ အချက်ကကို မသင်္ကာစရာပါ။

### ၁၀.၃ Signal ၂: Channel ကိုက်ညီမှုမရှိခြင်း (+20)

```python
other_channels = {self.bssid_channel[b] for b in known_bssids if b in self.bssid_channel}
if channel and other_channels and int(channel) not in other_channels:
    score += 20
    reasons.append(f"Channel ကိုက်ညီမှုမရှိပါ (this: {channel}, known: {sorted(other_channels)})")
```

**နှိုင်းယှဉ်ချက် -** ဆိုင်အစစ်က ပထမထပ်မှာ ရှိတယ်။ "အတု" ဆိုင်က တတိယထပ်မှာ ရှိတယ်။ ဆိုင်အစစ်က ဘာလို့ အထပ်ပြောင်းရမှာလဲ? မသင်္ကာစရာပါပဲ။

**ဒါက ဘာကြောင့် အလုပ်ဖြစ်တာလဲ -** Router အစစ်တွေက channel တစ်ခုကို ရွေးပြီး အဲဒီမှာပဲ နေပါတယ်။ AP အတုဖွင့်ထားတဲ့ ဟက်ကာရဲ့ လက်ပ်တော့က ဘယ် channel မှာမဆို ရှိနေနိုင်ပါတယ်။

### ၁၀.၄ Signal ၃: RSSI ပုံမှန်မဟုတ်ခြင်း (+20)

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
            if diff >= 15:  # 15 dBm = သိသာထင်ရှားသော ကွာခြားချက်
                score += 20
                reasons.append(f"RSSI ပုံမှန်မဟုတ်ပါ ({rssi_val} dBm vs known avg {avg_known:.0f} dBm, Δ{diff:.0f} dBm)")
    except (ValueError, TypeError):
        pass
```

**နှိုင်းယှဉ်ချက် -** ဆိုင်အစစ်ရဲ့ ငွေရှင်းကောင်တာက ၅ ပေ အကွာမှာ ရှိတယ်။ အတုဆိုင်ရဲ့ ကောင်တာက ပေ ၅၀ အကွာမှာ ရှိနေသလို အသံထွက်နေတယ်။ သူတို့က ရုပ်ပိုင်းဆိုင်ရာအရ တစ်နေရာတည်းမှာ မရှိဘူး။

**ဒါက ဘာကြောင့် အလုပ်ဖြစ်တာလဲ -** ဟက်ကာရဲ့ လက်ပ်တော့နဲ့ router အစစ်ဟာ ရုပ်ပိုင်းဆိုင်ရာ နေရာမတူပါဘူး။ Signal အား ကွာခြားချက်က ၎င်းကို ဖော်ပြနေပါတယ်။

### ၁၀.၅ Signal ၄: OUI အမျိုးအစားခွဲခြားခြင်း (+10 သို့မဟုတ် +5)

```python
# ဤ MAC က ဘယ်လို hardware အမျိုးအစားကနေ လာတာလဲ?
oui_class = self._classify_oui(bssid)
known_oui_classes = [self._classify_oui(b) for b in known_bssids]

if oui_class == "laptop" and "router" in known_oui_classes:
    score += 10
    reasons.append("MAC OUI က laptop/USB NIC တစ်ခုပိုင်ဖြစ်သည် (rogue APs များတွင် တွေ့ရလေ့ရှိသည်)")
elif oui_class == "unknown" and "router" in known_oui_classes:
    score += 5
    reasons.append("MAC OUI ကို အသိအမှတ်မပြုပါ (ကျပန်းဖြစ်နိုင်သည် သို့မဟုတ် custom firmware ဖြစ်နိုင်သည်)")
```

**ဒါက ဘာကြောင့် အလုပ်ဖြစ်တာလဲ -** Router အစစ်တွေမှာ လူသိများတဲ့ (TP-Link, Netgear, ASUS, Cisco) ထုတ်လုပ်သူတွေဆီက MAC addresses တွေ ရှိပါတယ်။ ဟက်ကာတွေက Intel/Realtek Wi-Fi ချစ်ပ်တွေ ဒါမှမဟုတ် USB dongles (Alfa, Atheros) တပ်ထားတဲ့ လက်ပ်တော့တွေကို သုံးပါတယ်။ အကယ်၍ သိထားတဲ့ BSSIDs အားလုံးက "router" အမျိုးအစားဖြစ်ပြီး ၎င်းတစ်ခုတည်းက "laptop" အမျိုးအစားဖြစ်နေရင်၊ ဒါဟာ ဟက်ကာဖြစ်ဖို့ များပါတယ်။

```python
def _classify_oui(self, mac: str) -> str:
    """ပထမ MAC အပိုင်း ၃ ခုပေါ်မူတည်၍ 'router', 'laptop', သို့မဟုတ် 'unknown' ကို return ပြန်သည်။"""
    prefix = mac.lower()[:8]  # e.g., "50:3e:aa"
    if prefix in self.ROUTER_OUIS:
        return "router"
    if prefix in self.LAPTOP_NIC_OUIS:
        return "laptop"
    return "unknown"
```

OUI ဇယားများတွင် သိထားသော vendor prefixes ရာပေါင်းများစွာ ပါဝင်သည်။ ဥပမာ -
```python
# Router OUIs (တစ်စိတ်တစ်ပိုင်းစာရင်း):
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
    "00:c0:ca",  # Alfa Network (နာမည်ကြီး pentest adapter)
    "00:03:7f",  # Atheros
    ...
}
```

### ၁၀.၆ Signal ၅: Locally Administered Address (+40)

```python
def _is_locally_administered(self, mac: str) -> bool:
    """
    MAC ကို ဆော့ဖ်ဝဲလ်မှတစ်ဆင့် လိမ်လည်ထားခြင်း (spoofed) ရှိမရှိ စစ်ဆေးပါ။
    အစစ်အမှန် hardware MAC များသည် ပထမဘိုက်၏ bit 1 ကို မည်သည့်အခါမှ မဖွင့် (set) ထားပါ။
    """
    try:
        first_octet = int(mac.split(':')[0], 16)  # ပထမ ဘိုက်ကို ဂဏန်းအဖြစ်
        return bool(first_octet & 0x02)  # bit 1 ပွင့်နေသလား (set) စစ်ဆေးပါ
    except (ValueError, IndexError):
        return False
```

**MAC addresses အလုပ်လုပ်ပုံ -**
```
MAC:  02:00:00:AB:CD:EF
ပထမ ဘိုက်: 0x02
Binary:     0000 0010
                   ↑
                   Bit 1 = 1 → Locally Administered (ဒေသတွင်း စီမံခန့်ခွဲသည်)!
```

**နှိုင်းယှဉ်ချက် -** အစစ်အမှန်ထုတ်ကုန်တိုင်းမှာ စက်ရုံကလာတဲ့ serial နံပါတ်တစ်ခု ရှိပါတယ်။ ဒါပေမယ့် သင်ကိုယ်တိုင်လည်း မာကာ (marker) နဲ့ ကိုယ်ပိုင် serial နံပါတ် ရေးလို့ရပါတယ်။ Locally Administered MACs ဆိုတာ "မာကာနဲ့ရေးထားတဲ့" ဗားရှင်းပါပဲ။

**ဒါက ဘာကြောင့် အပြင်းထန်ဆုံး အချက် (+40) ဖြစ်တာလဲ -**
- Router အစစ်တွေဟာ locally administered MACs တွေကို ဘယ်တော့မှ မသုံးပါဘူး
- `airbase-ng`, `hostapd`, `macchanger` စတဲ့ ဟက်ကင်း tool တွေက များသောအားဖြင့် ဒါတွေကို ထုတ်လုပ်လေ့ရှိပါတယ်
- အကယ်၍ MAC တစ်ခုဟာ locally administered ဖြစ်နေရင်၊ ၎င်းကို spoof လုပ် (လိမ်လည်ဖန်တီး) ထားတာ သေချာသလောက်ပါပဲ

### ၁၀.၇ Signal ၆: နောက်ကျမှ ဝင်လာသူ (+15)

```python
if bssid in self.bssid_first_seen and other_bssids:
    my_ts = self.bssid_first_seen[bssid]
    other_ts = [self.bssid_first_seen[b] for b in other_bssids if b in self.bssid_first_seen]
    if other_ts and my_ts > min(other_ts) + 5:  # ၅ စက္ကန့်ကျော် နောက်ကျသည်
        score += 15
        reasons.append("အခြား BSSID က ထုတ်လွှင့်နေပြီးသား အချိန်မှ ပေါ်လာသည်")
```

**နှိုင်းယှဉ်ချက် -** ဆိုင်အစစ်က မနက် ၈ နာရီမှာ ဖွင့်တယ်။ ၈:၀၅ မှာ နာမည်တူ နောက်ဆိုင်တစ်ဆိုင်က ရုတ်တရက် ပေါ်လာတယ်။ ဒါဟာ မသင်္ကာစရာပါပဲ — ဆိုင်အစစ်တွေက ၅ မိနစ်အတွင်း ပွားလာလေ့ (duplicate) မရှိပါဘူး။

**ဒါက ဘာကြောင့် အလုပ်ဖြစ်တာလဲ -** ဟက်ကာတွေဟာ ကွန်ရက်အစစ်ကို တွေ့ပြီးမှသာ သူတို့ရဲ့ Evil Twin ကို စတင်လေ့ရှိပါတယ်။ အကယ်၍ BSSIDs နှစ်ခုလုံးက တစ်ချိန်တည်းမှာ အတိအကျ ပေါ်လာရင်၊ သူတို့က တရားဝင် (dual-band, mesh, စသည်) ဖြစ်နိုင်ပါတယ်။

### ၁၀.၈ Signal ၇: Signal ပိုအားနည်းခြင်း (+15)

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
        if my_avg_rssi < avg_other - 10:  # 10 dBm ပိုအားနည်းသည်
            score += 15
            reasons.append(f"Signal ပိုအားနည်းသည် ({my_avg_rssi:.0f} dBm vs {avg_other:.0f} dBm)")
```

**နှိုင်းယှဉ်ချက် -** ရေဒီယိုစတေရှင် အစစ်က ဝပ် ၅၀,၀၀၀ နဲ့ လွှင့်တယ်။ ပင်လယ်ဓားပြ (ခိုးလွှင့်တဲ့) ရေဒီယိုစတေရှင်က လူတစ်ယောက်ရဲ့ မြေအောက်ခန်းကနေ ဝပ် ၁၀၀ နဲ့ လွှင့်တယ်။ သင် နှစ်ခုလုံးကို ကြားရနိုင်ပေမယ့်၊ တစ်ခုက အရမ်းကို အားနည်းနေပါလိမ့်မယ်။

**ဒါက ဘာကြောင့် အလုပ်ဖြစ်တာလဲ -** Router အစစ်တစ်ခုမှာ အများဆုံး လွှမ်းခြုံနိုင်ဖို့ ဒီဇိုင်းထုတ်ထားတဲ့ သင့်လျော်တဲ့ အင်တင်နာ (antennas) တွေ ပါရှိပါတယ်။ ဟက်ကာရဲ့ လက်ပ်တော့မှာက အတွင်းပိုင်းက အင်တင်နာအသေးလေး ဒါမှမဟုတ် USB dongle ပဲ ရှိပါတယ်။ လက်ပ်တော့ကလာတဲ့ လှိုင်းဟာ အမြဲလိုလို ပိုအားနည်းနေပါလိမ့်မယ်။

### ၁၀.၉ Signal ၈: RSSI အတက်အကျ ကြမ်းခြင်း (+10)

```python
if len(my_rssi_list) >= 4:
    mean = my_avg_rssi
    variance = sum((x - mean) ** 2 for x in my_rssi_list) / len(my_rssi_list)
    if variance > 30:  # High variance = မတည်ငြိမ်သော signal
        score += 10
        reasons.append(f"မတည်ငြိမ်သော signal (variance {variance:.1f} dBm²)")
```

**Variance ဆိုတာ ဘာလဲ?** ၎င်းက လှိုင်း (signal) ဘယ်လောက်တောင် ခုန်ပေါက်နေသလဲ (ပြောင်းလဲနေသလဲ) ဆိုတာကို တိုင်းတာပါတယ်။

| RSSI ဖတ်ချက်များ | Variance | အဓိပ္ပါယ် |
|---------------|----------|---------|
| -45, -44, -46, -45, -43 | 0.8 | အလွန်တည်ငြိမ်သည် (နံရံကပ် router) |
| -72, -68, -75, -70, -71 | 5.1 | အနည်းငယ် မတည်ငြိမ်ပါ |
| -55, -45, -70, -60, -50 | **95** | အလွန် မတည်ငြိမ်ပါ (လက်ပ်တော့ ရွေ့နေသည်!) |

**နှိုင်းယှဉ်ချက် -** စားပွဲပေါ်က မီးအိမ်မှာ တည်ငြိမ်တဲ့ အလင်းရောင် ရှိတယ်။ အခန်းထဲမှာ ကိုင်ပြီး လျှောက်သွားနေတဲ့ မီးအိမ်မှာ မှိတ်တုတ်မှိတ်တုတ်နဲ့ ပြောင်းလဲနေတဲ့ အလင်းရောင် ရှိတယ်။ Router က တည်ငြိမ်တဲ့ မီးအိမ်ဖြစ်ပြီး၊ ဟက်ကာရဲ့ လက်ပ်တော့က ရွေ့လျားနေတဲ့ မီးအိမ်ပါ။

**ဒါက ဘာကြောင့် အလုပ်ဖြစ်တာလဲ -** Router တွေက ငြိမ်သက်နေပါတယ်။ သူတို့ရဲ့ လှိုင်းက တသမတ်တည်း ရှိပါတယ်။ လက်ပ်တော့နဲ့ ဟက်ကာတစ်ယောက်က နေရာပြောင်းနိုင်တယ်၊ ဒါမှမဟုတ် USB dongle က လှုပ်နိုင်တယ်၊ အဲဒါက signal အတက်အကျ တွေကို ဖြစ်စေပါတယ်။

### ၁၀.၁၀ အရာအားလုံးကို ပေါင်းစပ်ခြင်း: အမှတ်အပြည့်အစုံ

```
BSSID 02:00:00:AB:CD:EF အတွက် အမှတ်စာရင်း (SCORE CARD)
SSID: "CoffeeShop_Free"

+50  BSSID Conflict (SSID တစ်ခုတည်းအတွက် BSSIDs ၂ ခု)
     → "SSID 'CoffeeShop_Free' ကို MACs များစွာမှ ထုတ်လွှင့်နေသည်"

+20  Channel ကိုက်ညီမှုမရှိခြင်း
     → "Channel ကိုက်ညီမှုမရှိပါ (this: 11, known: [6])"

+20  RSSI ပုံမှန်မဟုတ်ခြင်း
     → "RSSI ပုံမှန်မဟုတ်ပါ (-72 dBm vs known avg -45 dBm, Δ27 dBm)"

+10  OUI = Laptop NIC
     → "MAC OUI က laptop/USB NIC တစ်ခုပိုင်ဖြစ်သည် (rogue APs များတွင် တွေ့ရလေ့ရှိသည်)"

+40  Locally Administered MAC
     → "Locally administered MAC — MAC ကို လိမ်လည်ထားကြောင်း အလွန်ထင်ရှားသည်"

+15  နောက်ကျမှ ဝင်လာသူ
     → "အခြား BSSID က ထုတ်လွှင့်နေပြီးသား အချိန်မှ ပေါ်လာသည်"

+15  Signal ပိုအားနည်းခြင်း
     → "Signal ပိုအားနည်းသည် (-72 dBm vs -45 dBm)"

+10  RSSI အတက်အကျ ကြမ်းခြင်း
     → "မတည်ငြိမ်သော signal (variance 35.8 dBm²)"

═══════════════════════════════════════════════════════════
RAW SCORE: 180 → 100 ဖြင့် ကန့်သတ်ထားသည် → သေချာမှု မြင့်မားသည် (HIGH CONFIDENCE) (Critical)
```

### ၁၀.၁၁ သေချာမှု အဆင့်များ (Confidence Levels)

```python
if score >= 70:
    label = "HIGH"
    severity = "Critical"
    tag = "eviltwin_high"      # treeview တွင် အနီရောင် နောက်ခံ
elif score >= 40:
    label = "MEDIUM"
    severity = "High"
    tag = "eviltwin_medium"    # လိမ္မော်ရောင် နောက်ခံ
else:
    label = "LOW"
    severity = "Low"
    tag = "eviltwin_low"       # အဝါရောင် နောက်ခံ
```

### ၁၀.၁၂ Mesh/Extender များကို ဖယ်ရှားခြင်း

တချို့အချိန်တွေမှာ တရားဝင် (legitimate) ကွန်ရက်တွေမှာ SSID တစ်ခုတည်းအတွက် BSSIDs အများကြီး ရှိတတ်ပါတယ် -
- **Mesh networks** (Google Nest, Eero): Nodes အများကြီးရှိပေမယ့် ကွန်ရက်အမည် တစ်ခုတည်း
- **Wi-Fi extenders**: မတူညီတဲ့ MAC နဲ့ လှိုင်းကို ပြန်လည်ထုတ်လွှင့်သည်
- **Dual-band routers**: Band တစ်ခုချင်းစီအတွက် မတူညီတဲ့ BSSIDs (ဒါပေမယ့် ကျွန်ုပ်တို့ရဲ့ ESP32 က 2.4GHz ကိုပဲ ဖမ်းယူတဲ့အတွက် ဒါက မသက်ဆိုင်ပါဘူး)

မှားယွင်းတဲ့ တွေ့ရှိမှုတွေကို ရှောင်ရှားဖို့ -

```python
# BSSIDs အားလုံးက router ထုတ်လုပ်သူတွေဆီက ဟုတ်သလား?
both_router_oui = all(
    self._classify_oui(b) == "router" for b in all_bssids
)

# မည်သည့်အရာမှ locally administered မဖြစ်ဘူးဆိုတာ သေချာလား?
neither_is_laa = all(
    not self._is_locally_administered(b) for b in all_bssids
)

# အမှတ်ကွာခြားချက် သေးငယ်ပါသလား?
score_diff = top_score - bottom_score

# အကယ်၍ သုံးခုလုံး မှန်ကန်ပါက → mesh/extender ဖြစ်ဖို့များတယ်၊ တိုက်ခိုက်မှု မဟုတ်ပါ
is_likely_mesh = both_router_oui and neither_is_laa and score_diff < 20
```

အကယ်၍ mesh ဖြစ်ဖို့များတယ်ဆိုရင် ကျွန်ုပ်တို့က -
- Score ကို 30 ထိပဲ ကန့်သတ်ပါတယ်
- Severity ကို "Low" အဖြစ် သတ်မှတ်ပါတယ်
- မှတ်စုတစ်ခု ပြသပါတယ်: "၎င်းသည် mesh network သို့မဟုတ် Wi-Fi extender တစ်ခု ဖြစ်နိုင်ပါသည်။ ကိုယ်တိုင် စစ်ဆေးပါ။"

### ၁၀.၁၃ သတိပေးချက်ကို ကန့်သတ်ခြင်း (The Alert Throttle)

evil twin တစ်ခုတည်းအတွက် သတိပေးချက်တွေ အများကြီး ဝင်မလာစေဖို့ (ESP32 က တစ်စက္ကန့်အတွင်းမှာ ကွန်ရက်တစ်ခုတည်းဆီက packets တွေကို အကြိမ်များစွာ တွေ့ရလို့ပါ) -

```python
current_time = time.time()
last_alert = self.last_eviltwin_alert_time.get(bssid, 0)

# MAC တစ်ခုတည်းအတွက် ၁၀ စက္ကန့်မှတစ်ကြိမ်သာ သတိပေးချက်ပြပါ
if current_time - last_alert >= 10:
    # ... alert ဖန်တီးပါ သို့မဟုတ် အပ်ဒိတ်လုပ်ပါ ...
    self.last_eviltwin_alert_time[bssid] = current_time
```

ထို့ပြင်: အကယ်၍ အဆိုပါ သတိပေးချက်က list ထဲမှာ ရှိနေပြီးသားဆိုရင်၊ ကတ်အသစ် ဖန်တီးမယ့်အစား ၎င်းရဲ့ `seen_count` နဲ့ `last_seen` အချိန်ကိုပဲ **အပ်ဒိတ်** လုပ်ပါတယ် -

```python
alert_key = (ssid, rogue_mac)
if alert_key in self.eviltwin_alert_index:
    idx = self.eviltwin_alert_index[alert_key]
    self.alerts_list[idx]["seen_count"] += 1
    self.alerts_list[idx]["last_seen"] = datetime.now()
    self.alerts_list[idx]["score"] = score
```

### ၁၀.၁၄ မည်သည့်အရာက အတုဖြစ်သည်ကို ခွဲခြားခြင်း

SSID တစ်ခုအတွက် BSSIDs အများကြီးရှိနေတဲ့အခါ၊ ဘယ်ဟာက အတု (fake) လဲဆိုတာကို ကျွန်ုပ်တို့ ရှာဖွေဖို့ လိုပါတယ်။ `_identify_rogue` function က BSSID တိုင်းကို အမှတ်ပေးပြီး အမှတ်အများဆုံးရတဲ့သူကို အတု (rogue) အဖြစ် ရွေးချယ်ပါတယ် -

```python
def _identify_rogue(self, ssid: str):
    all_bssids = list(self.ssid_to_bssid.get(ssid, set()))
    if len(all_bssids) < 2:
        return None, None, [], False
    
    # BSSID တိုင်းကို အမှတ်ပေးပါ
    scored = []
    for b in all_bssids:
        s, r = self._rogue_score_bssid(b, ssid)
        scored.append((s, b, r))
    
    # စီပါ: အမြင့်ဆုံး rogue အမှတ်ကို အရင်
    scored.sort(reverse=True)
    suspected_rogue = scored[0][1]   # အမြင့်ဆုံး အမှတ် = rogue ဖြစ်နိုင်ခြေအများဆုံး
    suspected_legit = scored[-1][1]  # အနိမ့်ဆုံး အမှတ် = အစစ်ဖြစ်နိုင်ခြေအများဆုံး
    rogue_reasons = scored[0][2]
    
    return suspected_rogue, suspected_legit, rogue_reasons, is_likely_mesh
```

---

## ၁၁။ Deauth Attack ကို ထောက်လှမ်းခြင်း

```python
if subtype == "Deauthentication":
    self.deauth_count += 1
    
    # deauth ၁၀ ခုတိုင်းတွင် Alert ပြပါ (alert ရေလွှမ်းမိုးခြင်းကို တားဆီးသည်)
    if self.deauth_count % 10 == 0:
        self.alert_count += 1
        self.alerts_list.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Deauth Flood",
            "severity": "High",
            "details": f"Target MAC: {packet.get('mac_dst', 'Unknown')}"
        })
```

**ဘာကြောင့် deauth ၁၀ ခုတိုင်းမှာလဲ?** deauth packet တစ်ခုတည်းက တရားဝင်နိုင်ပါတယ် (ဥပမာ၊ router တစ်ခုက မချိတ်ဆက်ထားတော့တဲ့ စက်ကို ကန်ထုတ်တာမျိုး)။ ဒါပေမယ့် အချိန်တိုအတွင်းမှာ deauth (၁၀ ခုနဲ့အထက်) ရေလွှမ်းမိုးလာရင်တော့ ဒါဟာ သေချာပေါက် တိုက်ခိုက်မှုတစ်ခုပါ။ ဤကန့်သတ်ချက် (threshold) က ရံဖန်ရံခါဖြစ်ပေါ်တတ်တဲ့ တရားဝင် deauth တွေကြောင့် မှားယွင်းတဲ့ သတိပေးချက်တွေ မဖြစ်ပေါ်အောင် တားဆီးပေးပါတယ်။

---

## ၁၂။ Whitelist - မှားယွင်းသော သတိပေးချက်များကို မည်သို့ရပ်တန့်မည်နည်း

### ၁၂.၁ Whitelisting ဆိုတာ ဘာလဲ?

အကယ်၍ ကျွန်ုပ်တို့၏ စနစ်က ကွန်ရက်တစ်ခုကို Evil Twin အဖြစ် အသိပေးထားသော်လည်း ၎င်းသည် တကယ်တမ်းတွင် တရားဝင် mesh network သို့မဟုတ် extender ဖြစ်နေပါက၊ သင် ၎င်းကို **ယုံကြည် (trust)** နိုင်ပါသည်။ whitelist သည် app ကို ပိတ်ပြီး ပြန်ဖွင့်သည့်တိုင်အောင် သင်၏ ဆုံးဖြတ်ချက်ကို မှတ်သားထားပါသည်။

### ၁၂.၂ ကွန်ရက်တစ်ခုကို မည်သို့ ယုံကြည်ရမည်နည်း

၁။ Dashboard တွင် **VIEW ALERTS** ကို နှိပ်ပါ (ဘေးဘက်ဘားရှိ အနီရောင် ခလုတ်)
၂။ ကွန်ရက်အတွက် alert ကတ်ကို ရှာပါ
၃။ **"✅ Trust — Mark as False Positive (Mesh/Extender)"** ကို နှိပ်ပါ

### ၁၂.၃ သင် ယုံကြည်သည့်အခါ ဘာဖြစ်မလဲ

```python
def _trust_ssid_bssids(self, ssid: str, bssids: list):
    # ဤ SSID အတွက် BSSIDs အားလုံးကို whitelist ထဲသို့ ထည့်ပါ
    if ssid not in self.whitelist:
        self.whitelist[ssid] = set()
    self.whitelist[ssid].update(bssids)
    self._save_whitelist()  # ဖိုင်ထဲသို့ သိမ်းပါ!
```

ဤအရာက `ids/whitelist.json` ကို ဖန်တီး (သို့မဟုတ် အပ်ဒိတ်လုပ်) ပါသည်:

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

### ၁၂.၄ Whitelist ကို မည်သို့ အသုံးပြုသနည်း

packet တစ်ခု ရောက်လာတိုင်း၊ Evil Twin detection မလုပ်ဆောင်မီ:

```python
# whitelist ကို အရင်စစ်ဆေးပါ
trusted = self.whitelist.get(ssid, set())
if bssid in trusted:
    pass  # ကျော်သွားပါ — ဒါကို ယုံကြည်ထားပြီးပါပြီ!
elif len(self.ssid_to_bssid[ssid]) > 1 and self.bssid_seen_count.get(bssid, 0) >= 3:
    # ၎င်းပြီးမှသာ evil twin detection ကို လုပ်ဆောင်ပါ
    score, reasons = self._score_evil_twin(ssid, bssid, channel, rssi)
    ...

```

**ဘာကြောင့် အနည်းဆုံး အကြိမ် ၃ ကြိမ် တွေ့ရမလဲ?** စနစ်က BSSID တစ်ခုကို မသင်္ကာဖွယ်အဖြစ် မသတ်မှတ်မီ ထို BSSID မှ packet ၃ ခု ရောက်လာသည်အထိ စောင့်ပါသည်။ ၎င်းက လမ်းပျောက်လာသော packet တစ်ခုတည်းကြောင့် အချက်ပြမှု မှားယွင်းခြင်းကို တားဆီးပေးပါသည်။

---

## ၁၃။ ပြီးပြည့်စုံသော ဝေါဟာရများ (A-Z)

### A
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **AP** | Access Point | Wi-Fi ကွန်ရက်တစ်ခု ဖန်တီးပေးသော စက် | Router, hotspot |
| **Arduino** | — | microcontrollers များကို ပရိုဂရမ်ရေးရန် ပလက်ဖောင်းတစ်ခု | ESP32 ကို ပရိုဂရမ်ရေးရန် ကျွန်ုပ်တို့ ၎င်းကို သုံးသည် |

### B
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **Baud** | — | serial မှတစ်ဆင့် ဒေတာပို့လွှတ်သည့် အမြန်နှုန်း | 115200 baud ≈ တစ်စက္ကန့်လျှင် ဇာတ်ကောင် ၁၁,၅၀၀ |
| **BSSID** | Basic Service Set ID | Wi-Fi access point တစ်ခု၏ MAC address | `50:3E:AA:12:34:56` |

### C
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **Callback** | — | တစ်ခုခုဖြစ်လာသည့်အခါ ခေါ်ဆိုခံရသော function တစ်ခု | Packet ရောက်လာသောအခါ ကျွန်ုပ်တို့၏ callback အလုပ်လုပ်သည် |
| **Channel** | — | 2.4GHz Wi-Fi အတွင်းရှိ တိကျသော ကြိမ်နှုန်း (frequency) အပိုင်းအခြား | Channels 1-13 |
| **COM port** | Communications Port | Windows တွင် serial ဆက်သွယ်မှုအတွက် နာမည် | `COM5`, `COM3` |
| **CustomTkinter** | — | ခေတ်မီသော GUIs များကို ဖန်တီးပေးသည့် Python စာကြည့်တိုက် (library) | ကျွန်ုပ်တို့၏ dashboard ကို ၎င်းဖြင့် တည်ဆောက်ထားသည် |

### D
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **Daemon thread** | — | ပရိုဂရမ်ပိတ်သည့်အခါ အလိုအလျောက်ရပ်သွားသော နောက်ကွယ်ရှိ thread | ကျွန်ုပ်တို့၏ SerialReader thread |
| **dBm** | Decibel-milliwatts | Wi-Fi signal ဘယ်လောက်အားကောင်းသလဲ (အနုတ်ဂဏန်းများဖြင့် တိုင်းတာသည်) | -30 = အားကောင်းသည်, -90 = အားနည်းသည် |
| **Deauth** | Deauthentication | စက်တစ်ခုကို ကွန်ရက်မှထွက်ရန် ပြောသည့် frame တစ်ခု | Attackers များက Wi-Fi ကို အနှောင့်အယှက်ပေးရန် ၎င်းတို့ကို ရေလွှမ်းမိုးပို့လွှတ်သည် |
| **Deque** | Double-ended queue | အများဆုံးအရွယ်အစားရှိသော စာရင်းတစ်ခု (အဟောင်းများကို အလိုအလျောက် ဖယ်ရှားသည်) | ပြီးခဲ့သည့် RSSI ဖတ်ချက် ၂၀ ကို deque တွင် သိမ်းထားသည် |

### E
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **ESP32** | — | Wi-Fi နှင့် Bluetooth ပါဝင်သော $5 တန် microcontroller ချစ်ပ် | ကျွန်ုပ်တို့၏ sniffer ဟာ့ဒ်ဝဲ |
| **Evil Twin** | — | အစစ်အမှန်တစ်ခုလို ဟန်ဆောင်ထားသော အတုအယောင် Wi-Fi ကွန်ရက် | Starbucks အနီးရှိ Hacker ၏ "Starbucks_WiFi" |

### F
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **Frame** | — | Wi-Fi packet အတွက် အခြားနာမည်တစ်ခု | Beacon frame, Deauth frame |
| **FreeRTOS** | Free Real-Time Operating System | အလုပ် (tasks) များစွာကို ကိုင်တွယ်ပေးသည့် microcontrollers များအတွက် အသေးစား OS | ကျွန်ုပ်တို့၏ queue နှင့် timing ကို စီမံသည် |

### I
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **IDE** | Integrated Development Environment | ကုဒ်များရေးရန်နှင့် upload လုပ်ရန် ပရိုဂရမ် | Arduino IDE |
| **ISR** | Interrupt Service Routine | ဟာ့ဒ်ဝဲမှ အာရုံစိုက်မှုလိုအပ်သည့်အခါ ချက်ချင်း အလုပ်လုပ်သော function | Wi-Fi packet တိုင်းအတွက် ခေါ်ဆိုခံရသည် |

### J
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **JSON** | JavaScript Object Notation | ဒေတာများကို key-value တွဲများအဖြစ် သိမ်းဆည်းရန် စာသား (text) ပုံစံ | `{"rssi": -45, "channel": 6}` |

### L
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **LAA** | Locally Administered Address | စက်ရုံမှမဟုတ်ဘဲ ဆော့ဖ်ဝဲလ်ဖြင့် လိမ်လည်ဖန်တီးထားသော MAC address | `02:00:00:XX:XX:XX` |

### M
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **MAC** | Media Access Control | Wi-Fi ချစ်ပ်တိုင်းကို သတ်မှတ်ပေးထားသည့် သီးသန့် hardware လိပ်စာ | `AA:BB:CC:DD:EE:FF` |
| **Management Frame** | — | ချိတ်ဆက်မှုများကို ကိုင်တွယ်သော Wi-Fi packets များ (data များမဟုတ်ပါ) | Beacon, Probe, Deauth, Auth |
| **Mesh Network** | — | ကွန်ရက်အမည် တစ်ခုတည်းကို ဝေမျှသုံးစွဲသော APs အများအပြား (တရားဝင် multi-BSSID) | Google Nest, Eero |

### O
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **OUI** | Organizationally Unique Identifier | ထုတ်လုပ်သူကို သတ်မှတ်ပေးသော MAC ၏ ပထမ ၃ ဘိုက် | `50:3E:AA` = TP-Link |

### P
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **Promiscuous Mode** | — | ကိုယ်ပိုင် packets များကိုသာမက ALL (အားလုံးသော) packets များကို ကြားနိုင်သည့် Wi-Fi mode | ESP32 ၏ "စပိုင် မုဒ် (spy mode)" |
| **pyserial** | — | serial ports များကို ဖတ်/ရေးရန် Python library | ESP32 နှင့် ဆက်သွယ်ရန် သုံးသည် |

### Q
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **Queue** | — | ဖြစ်စဉ် (processes) နှစ်ခုကြားရှိ ပစ္စည်းများကို သိမ်းထားပေးသည့် "buffer" | FreeRTOS queue (packets ၅၀), Python queue (thread-safe) |

### R
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **RSSI** | Received Signal Strength Indicator | signal ဘယ်လောက်အားကောင်းသလဲ ဆိုသည် | -45 dBm (ကောင်းသည်), -80 dBm (အားနည်းသည်) |

### S
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **Serial** | — | USB မှတစ်ဆင့် ဒေတာများကို တစ်ကြိမ်လျှင် တစ်ဘစ် (one bit) ပို့လွှတ်သည့် နည်းလမ်း | ESP32 သည် JSON ကို Serial မှတစ်ဆင့် ပို့သည် |
| **SSID** | Service Set Identifier | လူများဖတ်နိုင်သော Wi-Fi ကွန်ရက်အမည် | "Starbucks_WiFi", "Home_Network" |

### T
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **Thread** | — | ကုဒ်အပိုင်းအစ အများအပြားကို တစ်ချိန်တည်းမှာ အလုပ်လုပ်စေသည့် နည်းလမ်း | SerialReader သည် နောက်ကွယ်မှ thread တစ်ခုတွင် အလုပ်လုပ်သည် |
| **Treeview** | — | ဒေတာများကို အတန်းများနှင့် ကော်လံများဖြင့် ပြသပေးသည့် ဇယား (table) widget | ကျွန်ုပ်တို့၏ packet ပြသသည့် ဇယား |
| **ttyUSB** | — | Linux/Mac ရှိ serial port အမည် | `/dev/ttyUSB0` |

### W
| ဝေါဟာရ (Term) | နာမည်အပြည့်အစုံ (Full Name) | ရိုးရှင်းသော ရှင်းလင်းချက် (Simple Explanation) | ဥပမာ (Example) |
|------|-----------|-------------------|---------|
| **WDT** | Watchdog Timer | ပရိုဂရမ် hang (ရပ်) သွားပါက ESP32 ကို reset လုပ်ပေးသည့် လုံခြုံရေး timer | ESP32 ထာဝရ ရပ်တန့်သွားခြင်းမှ ကာကွယ်ပေးသည် |

---

## ၁၄။ ပြဿနာဖြေရှင်းခြင်း - မှားယွင်းနိုင်သမျှ အရာအားလုံး

### ပြဿနာ ၁ - "Dashboard တွင် packets များ မပေါ်ပါ"

**စစ်ဆေးရန်စာရင်း (အစီအစဉ်အတိုင်း) -**

| # | စစ်ဆေးရန် | မည်သို့ပြင်မည်နည်း |
|---|-------|------------|
| ၁ | ESP32 ကို ပလပ်ထိုးထားပါသလား? | USB ချိတ်ဆက်မှုကို စစ်ဆေးပါ; အခြား USB port တစ်ခုဖြင့် စမ်းကြည့်ပါ |
| ၂ | COM port မှန်ကန်ပါသလား? | Arduino IDE တွင်: **Tools → Port** — ၎င်းသည် သင့် COM port ဖြစ်သည် |
| ၃ | အခြား app တစ်ခုက port ကို သုံးနေပါသလား? | Arduino Serial Monitor, Putty စသည်တို့ကို ပိတ်ပါ |
| ၄ | Baud rate က 115200 ဖြစ်ပါသလား? | မတူညီပါက ပြောင်းပါ (code နှင့် GUI နှစ်ခုလုံး တူညီရမည်) |
| ၅ | Firmware ကို upload လုပ်ပြီးပြီလား? | `esp32_sniffer.ino` ကို ပြန်လည် upload လုပ်ပါ |
| ၆ | USB ကြိုးက ဒေတာပို့နိုင်ပါသလား? | အချို့ကြိုးများက "အားသွင်းရန်သာ" ဖြစ်သည် — အခြားကြိုးကို သုံးကြည့်ပါ |
| ၇ | Wi-Fi အသွားအလာ ရှိပါသလား? | Router အနီးသို့ ရွှေ့ပါ သို့မဟုတ် သင့်ဖုန်း၏ hotspot ကို ဖွင့်ပါ |

### ပြဿနာ ၂ - "ESP32 ခဏခဏ restart ကျနေသည် / serial တွင် အမှိုက် (garbage) များ ပေါ်နေသည်"

```
မက်ဆေ့ချ်: "ets Jun  8 2016 00:22:57"
         "rst:0x1 (POWERON_RESET),boot:0x13..."
```

၎င်းသည် **Watchdog Timer (WDT) reset** ဖြစ်ခြင်း သို့မဟုတ် serial ချိတ်ဆက်မှု မကောင်းခြင်း ဖြစ်သည်။

| အကြောင်းရင်း | ဖြေရှင်းနည်း |
|-------|-----|
| ESP32 အလုပ်လုပ်တာ နှေးလွန်းနေသည် | သင်သည် CPU အမြန်နှုန်းကို ပြောင်းလဲထားမိနိုင်သည် — Arduino IDE တွင် 240MHz သို့ ပြန်ထားပါ |
| ISR အတွင်း Serial.println ရှိနေသည် | ISR function အတွင်း၌ print မထုတ်မိရန် သေချာစေပါ |
| Queue ပြည့်လျှံနေသည် (overflow) | ပုံမှန်ပါပဲ — ကုဒ်က crash ဖြစ်မည့်အစား packet များကို ပစ်ချလိုက်သည် |
| Baud rate မှားနေသည် | ESP32 နှင့် GUI နှစ်ခုလုံးတွင် 115200 သုံးကြောင်း သေချာစေပါ |
| USB ပါဝါ မလုံလောက်ပါ | ပါဝါပါသော USB hub သို့မဟုတ် အခြား USB port ကို သုံးကြည့်ပါ |

### ပြဿနာ ၃ - "Error: No module named 'customtkinter'"

```bash
# ၎င်းကို WIDS folder အတွင်း၌ run ခဲ့ကြောင်း သေချာစေပါ:
pip install -r requirements.txt

# ၎င်းက အလုပ်မလုပ်ပါက၊ ဤသို့စမ်းကြည့်ပါ:
python -m pip install customtkinter pyserial
```

### ပြဿနာ ၄ - "GUI လေးလံ (lag) နေသည်"

ကုဒ်သည် packet များကို batch အလိုက် (၂၅၀ms တိုင်း ၁၀၀ ခုစီ) အလုပ်လုပ်ပြီးဖြစ်သည်။ အကယ်၍ သင် လေးလံမှု (lag) ကို တွေ့နေရဆဲဆိုလျှင် -

၁။ Channel ပြောင်းလဲမှု (hopping) အကြိမ်ရေကို လျှော့ပါ (ESP32 တွင်): `CHANNEL_HOP_INTERVAL` ကို 200 မှ 500ms သို့ ပြောင်းပါ
၂။ Batch အရွယ်အစားကို လျှော့ပါ (Python တွင်): `for _ in range(100)` ကို `for _ in range(50)` သို့ ပြောင်းပါ
၃။ treeview ၏ အများဆုံး အတန်းအရေအတွက်ကို လျှော့ပါ: `self.max_rows = 500` ကို `self.max_rows = 200` သို့ ပြောင်းပါ

### ပြဿနာ ၅ - "Evil Twin ထောက်လှမ်းတွေ့ရှိမှု မရှိပါ"

Evil Twin ကို ထောက်လှမ်းနိုင်ရန် အောက်ပါတို့ လိုအပ်သည် -

၁။ **BSSIDs ၂ ခု (သို့) ၂ ခုထက်ပို၍ တူညီသော SSID လွှင့်နေရမည်** — သင့်ပတ်ဝန်းကျင်တွင် multi-AP ကွန်ရက်များ ရှိရပါမည်
၂။ လျာထားသော BSSID ကို **အနည်းဆုံး ၃ ကြိမ် တွေ့ရှိရမည်** (မှားယွင်းသော သတိပေးချက်များကို တားဆီးရန်)
၃။ **SSID အလွတ် မဖြစ်ရပါ** — Beacons များနှင့် Probe Responses များသာ

ကိုယ်တိုင် စမ်းသပ်ကြည့်ပါ -
- သင့်ဖုန်း၏ hotspot ကို "TestWiFi" ကဲ့သို့သော ရိုးရှင်းသည့် နာမည်ဖြင့် ဖွင့်ပါ
- ၎င်းကို ESP32 မှ တွေ့မြင်သည်အထိ စောင့်ပါ
- ထို့နောက် အခြားစက်တစ်ခုတွင် အဆိုပါ နာမည်အတိုင်း (SAME name) ဒုတိယ hotspot တစ်ခုကို ဖွင့်ပါ

### ပြဿနာ ၆ - "မှားယွင်းသော Evil Twin သတိပေးချက်များ များလွန်းနေသည်"

အချို့သော ကွန်ရက်အစစ်များသည် Evil Twins များနှင့် တူနေတတ်သည် -

| ကွန်ရက် အမျိုးအစား | ဘာကြောင့် မသင်္ကာစရာ ဖြစ်နေရသလဲ | ကျွန်ုပ်တို့၏ ဖြေရှင်းနည်း |
|-------------|------------------------|--------------|
| Mesh network (Google Nest, Eero) | Nodes များစွာ၊ SSID အတူတူ၊ BSSIDs မတူညီပါ | Mesh suppression logic က ၎င်းတို့ကို LOW ဟု အမှတ်အသားပြုသည် |
| Wi-Fi extender | ၎င်း၏ ကိုယ်ပိုင် MAC ဖြင့် ကွန်ရက်ကို ထပ်ဆင့်လွှင့်သည် | mesh နှင့် အတူတူပင် — LOW confidence |
| Dual-band router (2.4+5GHz) | Band တစ်ခုစီအတွက် မတူညီသော BSSIDs | ကျွန်ုပ်တို့၏ ESP32 က 2.4GHz ကိုသာ နားထောင်သဖြင့်၊ BSSID တစ်ခုတည်းကိုသာ တွေ့ရမည် — ပြဿနာ မရှိပါ |

**ဖြေရှင်းနည်း -** Alerts မျက်နှာပြင်ရှိ "Trust — Mark as False Positive" ကို နှိပ်ပါ။ Whitelist သည် app ပြန်ဖွင့်လျှင်လည်း ဆက်လက် မှတ်သားထားပါသည်။

### ပြဿနာ ၇ - "Deauth alerts များစွာကို တွေ့နေရသည်"

Deauth frames အနည်းငယ်စီ တွေ့ရခြင်းမှာ ပုံမှန်ဖြစ်နိုင်သည် -
- ဖုန်းတစ်လုံး ကွန်ရက်မှ ထွက်သွားခြင်း
- Router က မလိုအပ်တော့သော ချိတ်ဆက်မှုများကို ရှင်းလင်းခြင်း
- Channel နှောင့်ယှက်မှု

သို့သော် အချိန်တိုအတွင်း deauth ၁၀ ခုထက်ပို၍ လွှမ်းမိုးလာခြင်း (flood) သည် တိုက်ခိုက်မှုတစ်ခုဖြစ်သည်။ မှားယွင်းသော သတိပေးချက်များကို ရှောင်ရှားရန် ကျွန်ုပ်တို့စနစ်သည် deauth ၁၀ ခုတိုင်းတွင်သာ alert ပြသသည်။

### ပြဿနာ ၈ - "Upload ကျရှုံးသည် / 'Connecting...' တွင် အမြဲတမ်း ရပ်နေသည်"

၎င်းသည် အဖြစ်အများဆုံး ESP32 ပြဿနာဖြစ်သည်။ ဖြေရှင်းရန် -

၁။ ESP32 ပေါ်ရှိ **BOOT ခလုတ်ကို ဖိထားပါ**
၂။ ထိုသို့ဖိထားစဉ် Arduino IDE တွင် **Upload** ကို နှိပ်ပါ
၃။ `Connecting...` ထို့နောက် `...` ဟု တွေ့ရသောအခါ ခလုတ်ကို လွှတ်လိုက်ပါ
၄။ Upload ဆက်လက်လုပ်ဆောင်သွားပါမည်

အကယ်၍ ၎င်းက အလုပ်မလုပ်ပါက -
- USB ကို ဖြုတ်ပြီး ပြန်တပ်ပါ
- အခြား USB ကြိုးတစ်ခုကို သုံးကြည့်ပါ
- အခြား USB port တစ်ခုကို သုံးကြည့်ပါ
- မှန်ကန်သော ဘုတ် (ESP32 Dev Module) ကို ရွေးချယ်ထားကြောင်း သေချာစေပါ

### ပြဿနာ ၉ - "Linux/Mac တွင် Permission denied ပြနေသည်"

```bash
# သင့် user ကို dialout group သို့ ထည့်ပါ (serial port အသုံးပြုခွင့်အတွက်):
sudo usermod -a -G dialout $USER

# ထို့နောက် log out ထွက်ပြီး ပြန်ဝင်ပါ (သို့မဟုတ် restart ချပါ)
```

---

## အမြန်ကိုးကား (Quick Reference): ဖိုင်များ၏ ရည်ရွယ်ချက်များ

| ဖိုင် (File) | ဘာလုပ်သလဲ (What It Does) | စာကြောင်းရေ | ဘာသာစကား (Language) |
|------|-------------|-------|----------|
| `main.py` | အရာအားလုံးကို စတင်သည်၊ အစိတ်အပိုင်းများကို ချိတ်ဆက်သည် | ၂၄ | Python |
| `ids/serial_reader.py` | USB serial ကို နောက်ကွယ်ရှိ thread တွင် ဖတ်သည် | ၄၇ | Python |
| `gui/app.py` | Dashboard + ထောက်လှမ်းမှု အယ်လ်ဂိုရီသမ် | ၈၆၄ | Python |
| `esp32_sniffer/esp32_sniffer.ino` | ESP32 အတွက် Firmware | ၁၄၁ | C++ |
| `requirements.txt` | လိုအပ်သော Python packages များ | ၂ | Text |
| `.gitignore` | git တွင် လျစ်လျူရှုရမည့် ဖိုင်များ | ၄ | Text |
| `README.md` | မူလ အတိုချုံး readme | ၆၆ | Markdown |
| `WIDS_README.md` | ဤစာရွက်စာတမ်း | — | Markdown |

---

## ပရောဂျက် သစ်ပင် (Project Tree)

```
WIDS/
│
├── main.py                    # ဝင်ရောက်ရမည့် နေရာ — ဤသို့ run ပါ: python main.py
├── requirements.txt           # pip install -r requirements.txt
├── .gitignore                 # __pycache__ နှင့် .pyc ဖိုင်များကို လျစ်လျူရှုသည်
├── README.md                  # မူလ အတိုချုံး document
├── WIDS_README.md             # ဤ အစပြုသူအတွက် အပြည့်အစုံ လမ်းညွှန်
│
├── esp32_sniffer/             # ← ESP32 firmware
│   └── esp32_sniffer.ino      #   ၎င်းကို ESP32 သို့ Upload လုပ်ပါ
│
├── ids/                       # ← အလစ်အငိုက်ဝင်ရောက်မှုကို ထောက်လှမ်းသည့်စနစ် (Intrusion Detection System)
│   ├── serial_reader.py       #   နောက်ကွယ်မှ serial ဖတ်ပေးသည့် thread
│   └── whitelist.json         #   ကွန်ရက်များကို trust လုပ်သည့်အခါ အလိုအလျောက် ဖန်တီးပေးသည်
│
└── gui/                       # ← Graphical User Interface
    └── app.py                 #   CustomTkinter dashboard
```

---

## နိဂုံးချုပ် စကား (Final Words)

ယခုဆိုလျှင် သင်သည် Sentinel WIDS ပရောဂျက် တစ်ခုလုံးကို နားလည်သွားပါပြီ -

- **၎င်းက ဘာလုပ်သလဲ -** Wi-Fi အသွားအလာများကို နားထောင်ပြီး တိုက်ခိုက်မှုများကို ထောက်လှမ်းသည်
- **ဟာ့ဒ်ဝဲ အလုပ်လုပ်ပုံ -** FreeRTOS queue ပါဝင်သော promiscuous mode ရှိ ESP32
- **ဆော့ဖ်ဝဲ အလုပ်လုပ်ပုံ -** နောက်ကွယ်မှ thread + thread-safe queue + batch processing
- **Evil Twin ထောက်လှမ်းမှု အလုပ်လုပ်ပုံ -** အတုအယောင် ကွန်ရက်များကို ရှာဖွေရန် အမှတ်ပေးထားသော signals ၈ ချက်
- **ပြဿနာများကို မည်သို့ ဖြေရှင်းမလဲ -** အဖြစ်များသော ပြဿနာတိုင်းအတွက် Troubleshooting (ပြဿနာဖြေရှင်းခြင်း)

အောင်မြင်စွာ ထောက်လှမ်းနိုင်ပါစေ! 🛡️

---

*ဤပရောဂျက်သည် ပညာရေးနှင့် လုံခြုံရေး ကာကွယ်ရန် ရည်ရွယ်ချက်အတွက်သာ ဖြစ်ပါသည်။ သင်ကိုယ်တိုင်ပိုင်ဆိုင်သော (သို့မဟုတ်) ခွဲခြမ်းစိတ်ဖြာရန် တိကျသေချာသော ခွင့်ပြုချက်ရထားသည့် ကွန်ရက်များကိုသာ စစ်ဆေးပါ။*
