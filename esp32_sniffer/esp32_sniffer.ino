#include "esp_wifi.h"
#include <WiFi.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>

// Configuration
const int CHANNEL_HOP_INTERVAL = 200; // ms
unsigned long lastHopTime = 0;
int currentChannel = 1;

// Define a struct to hold only the essential data (saves memory)
typedef struct {
    uint32_t timestamp;
    int8_t rssi;
    uint8_t channel;
    uint8_t macSrc[6];
    uint8_t macDst[6];
    uint8_t frameSubtype;
} SniffPacket;

// FreeRTOS queue to safely pass data from the callback to the main loop
QueueHandle_t packetQueue;
const int QUEUE_SIZE = 50; // Buffer up to 50 packets

// The callback runs in a high-priority context. 
// DO NOT use Serial.print or heavy String operations here!
void wifi_promiscuous_cb(void *buf, wifi_promiscuous_pkt_type_t type) {
    if (type != WIFI_PKT_MGMT) return; // Only process Management frames for now
    
    wifi_promiscuous_pkt_t *pkt = (wifi_promiscuous_pkt_t *)buf;
    uint8_t *payload = pkt->payload;
    
    // Frame Control
    uint16_t fc = payload[0] | (payload[1] << 8);
    uint8_t frameType = (fc & 0x0C) >> 2;
    uint8_t frameSubtype = (fc & 0xF0) >> 4;
    
    // Safety check: ensure it's a management frame (Type 0)
    if (frameType != 0) return; 

    SniffPacket p;
    p.timestamp = millis();
    p.rssi = pkt->rx_ctrl.rssi;
    p.channel = pkt->rx_ctrl.channel;
    p.frameSubtype = frameSubtype;
    
    // Extract Source and Destination MACs
    memcpy(p.macDst, &payload[4], 6);
    memcpy(p.macSrc, &payload[10], 6);

    // Send the packet to the queue (non-blocking)
    // If the queue is full, we just drop the packet to prevent crashing
    xQueueSendFromISR(packetQueue, &p, NULL);
}

void setup() {
    Serial.begin(115200);
    
    // Initialize the queue
    packetQueue = xQueueCreate(QUEUE_SIZE, sizeof(SniffPacket));
    
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_promiscuous_rx_cb(&wifi_promiscuous_cb);
    
    Serial.println("{\"log\": \"ESP32 Sniffer initialized. Waiting for packets...\"}");
}

void loop() {
    // 1. Check if we need to hop channels
    if (millis() - lastHopTime > CHANNEL_HOP_INTERVAL) {
        lastHopTime = millis();
        currentChannel++;
        if (currentChannel > 13) currentChannel = 1;
        esp_wifi_set_channel(currentChannel, WIFI_SECOND_CHAN_NONE);
    }
    
    // 2. Process packets from the queue
    SniffPacket p;
    // Process up to 10 packets per loop to avoid blocking channel hopping
    int packetsProcessed = 0; 
    while (xQueueReceive(packetQueue, &p, 0) == pdTRUE && packetsProcessed < 10) {
        
        const char* subtypeStr = "Unknown";
        switch(p.frameSubtype) {
            case 0: subtypeStr = "Association Request"; break;
            case 4: subtypeStr = "Probe Request"; break;
            case 5: subtypeStr = "Probe Response"; break;
            case 8: subtypeStr = "Beacon"; break;
            case 10: subtypeStr = "Disassociation"; break;
            case 11: subtypeStr = "Authentication"; break;
            case 12: subtypeStr = "Deauthentication"; break;
        }

        // Print JSON to Serial (This is safe to do in the main loop)
        Serial.printf("{\"timestamp\": %lu, \"rssi\": %d, \"channel\": %d, \"mac_src\": \"%02X:%02X:%02X:%02X:%02X:%02X\", \"mac_dst\": \"%02X:%02X:%02X:%02X:%02X:%02X\", \"type\": \"Management\", \"subtype\": \"%s\"}\n",
                      p.timestamp, p.rssi, p.channel, 
                      p.macSrc[0], p.macSrc[1], p.macSrc[2], p.macSrc[3], p.macSrc[4], p.macSrc[5],
                      p.macDst[0], p.macDst[1], p.macDst[2], p.macDst[3], p.macDst[4], p.macDst[5],
                      subtypeStr);
                      
        packetsProcessed++;
    }
    
    // Small delay to yield to the FreeRTOS idle task
    delay(1);
}
