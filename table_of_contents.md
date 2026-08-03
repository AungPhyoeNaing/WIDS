# TABLE OF CONTENTS

| | Page |
|---|---:|
| ACKNOWLEDGEMENT | i |
| ABSTRACT | ii |
| TABLE OF CONTENTS | iii |
| LIST OF FIGURES | v |

**CHAPTER 1: INTRODUCTION**
1.1. Introduction to the System .............................................................. 1
1.2. Aim and Objectives .......................................................................... 2
1.3. Scopes of the Project ....................................................................... 2
1.4. Outlines of the Project ..................................................................... 3

**CHAPTER 2: BACKGROUND THEORY**
2.1. Background Theory ......................................................................... 4
2.2. Wireless Networks (IEEE 802.11) ..................................................... 4
2.3. Wireless Intrusion Detection Systems (WIDS) ................................. 5
2.4. Network Attacks and Vulnerabilities ................................................ 6
&nbsp;&nbsp;&nbsp;&nbsp;2.4.1. ARP Spoofing Attacks ........................................................... 6
&nbsp;&nbsp;&nbsp;&nbsp;2.4.2. Deauthentication Attacks ...................................................... 7
2.5. Microcontrollers in Network Security ................................................ 8
&nbsp;&nbsp;&nbsp;&nbsp;2.5.1. ESP32 Architecture .............................................................. 8
&nbsp;&nbsp;&nbsp;&nbsp;2.5.2. Serial Communication (UART) ............................................. 9
2.6. Summary .......................................................................................... 10

**CHAPTER 3: DESIGN AND IMPLEMENTATION**
3.1. Project Plan ..................................................................................... 11
3.2. System Architecture Design ............................................................. 12
3.3. Hardware Implementation ................................................................ 13
&nbsp;&nbsp;&nbsp;&nbsp;3.3.1. ESP32 Promiscuous Mode Setup ........................................ 13
&nbsp;&nbsp;&nbsp;&nbsp;3.3.2. Firmware Programming (C++/Arduino) ............................... 14
3.4. Software Implementation .................................................................. 15
&nbsp;&nbsp;&nbsp;&nbsp;3.4.1. Application Flow and Entry Point (`main.py`) ..................... 15
&nbsp;&nbsp;&nbsp;&nbsp;3.4.2. Intrusion Detection Engine (`ids/`) ...................................... 16
&nbsp;&nbsp;&nbsp;&nbsp;3.4.3. Graphical User Interface (`gui/`) .......................................... 18
3.5. Equipment and Software List ........................................................... 20
&nbsp;&nbsp;&nbsp;&nbsp;3.5.1. Hardware Requirements (ESP32, Cabling) ......................... 20
&nbsp;&nbsp;&nbsp;&nbsp;3.5.2. Python Libraries (CustomTkinter, Scapy) ........................... 21
3.6. System Integration and Testing ........................................................ 23
&nbsp;&nbsp;&nbsp;&nbsp;3.6.1. Hardware-Software Integration ............................................ 23
&nbsp;&nbsp;&nbsp;&nbsp;3.6.2. Simulated Attack Testing ...................................................... 24
3.7. Summary .......................................................................................... 26

**CHAPTER 4: CONCLUSION AND FURTHER EXTENSIONS**
4.1. Conclusion ........................................................................................ 27
4.2. Further Extensions ............................................................................ 28

REFERENCES ....................................................................................... 29
