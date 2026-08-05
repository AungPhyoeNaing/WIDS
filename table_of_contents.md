# TABLE OF CONTENTS

| SECTION | TITLE | PAGE |
| :--- | :--- | :---: |
| | **ACKNOWLEDGEMENT** | i |
| | **ABSTRACT** | ii |
| | **TABLE OF CONTENTS** | iii |
| | **LIST OF FIGURES** | v |
| | | |
| **CHAPTER 1** | **INTRODUCTION** | |
| 1.1 | Introduction to the WIDS System | 1 |
| 1.2 | Aim and Objectives | 2 |
| 1.3 | Scopes of the Project | 2 |
| 1.4 | Outlines of the Project | 3 |
| | | |
| **CHAPTER 2** | **BACKGROUND THEORY** | |
| 2.1 | Background Theory | 4 |
| 2.2 | Wireless Networks (IEEE 802.11) and Protocols | 4 |
| 2.2.1 | Wireless Network | 4 |
| 2.2.2 | WPA2 | 5 |
| 2.2.3 | 802.11 Frames | 5 |
| 2.2.4 | ARP Protocol | 6 |
| 2.2.5 | MAC Address and IP Address | 6 |
| 2.2.6 | SSID and BSSID | 7 |
| 2.3 | Network Attacks and Vulnerabilities | 7 |
| 2.3.1 | Evil Twin Attack | 7 |
| 2.3.2 | Deauthentication Attack | 8 |
| 2.3.3 | ARP Spoofing (MAC Spoofing) | 9 |
| 2.4 | Microcontroller in Network Security (ESP32) | 10 |
| 2.5 | Summary | 11 |
| | | |
| **CHAPTER 3** | **DESIGN AND IMPLEMENTATION** | |
| 3.1 | Project Design Plan | 12 |
| 3.1.1 | Overview of System Components | 12 |
| 3.1.2 | Software Architecture (MVC Pattern) | 13 |
| 3.1.3 | Threat Whitelisting and Network Resolution | 14 |
| 3.2 | Hardware Setup | 15 |
| 3.2.1 | ESP32 Sniffer Circuit and Connection | 15 |
| 3.2.2 | Enabling Promiscuous Mode | 16 |
| 3.2.3 | Serial Transmission and JSON Serialization | 17 |
| 3.3 | Software Implementation | 18 |
| 3.3.1 | Multithreaded Serial Reader | 18 |
| 3.3.2 | ARP Sniffer and Gateway Resolution | 19 |
| 3.3.3 | OUI Lookup and MAC Identification | 20 |
| 3.3.4 | Graphical User Interface | 21 |
| 3.3.5 | User (Non-technician) vs. Technician Views | 22 |
| 3.3.6 | Notification Alerts and JARVIS Audio Alarm | 23 |
| 3.4 | Summary | 24 |
| | | |
| **CHAPTER 4** | **CONCLUSION AND FURTHER EXTENSIONS** | |
| 4.1 | Conclusion | 25 |
| 4.2 | Further Extensions | 26 |
| | | |
| | **REFERENCES** | 27 |
