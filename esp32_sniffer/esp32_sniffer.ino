#include "esp_wifi.h"
#include <WiFi.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>

// Configuration
const int CHANNEL_HOP_INTERVAL = 200; // ms
const int MIN_RSSI_THRESHOLD = -80; // Filter out packets weaker than -80 dBm (reduces sniffing area to ~medium room)
unsigned long lastHopTime = 0;
int currentChannel = 1;

// Define a struct to hold only the essential data (saves memory)
typedef struct {
    uint32_t timestamp;
    int8_t rssi;
    uint8_t channel;
    uint8_t macSrc[6];
    uint8_t macDst[6];
    uint8_t bssid[6];
    uint8_t frameSubtype;
    char ssid[33];
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
    
    // Range Limiter: Drop packets that are too weak (outside our intended sniffing zone)
    if (pkt->rx_ctrl.rssi < MIN_RSSI_THRESHOLD) return;

    // Safety: ensure packet is large enough for a management frame header (24 bytes minimum)
    if (pkt->rx_ctrl.sig_len < 24) return;

    SniffPacket p;
    p.timestamp = millis();
    p.rssi = pkt->rx_ctrl.rssi;
    p.channel = pkt->rx_ctrl.channel;
    p.frameSubtype = frameSubtype;
    
    // Extract Source and Destination MACs
    memcpy(p.macDst, &payload[4], 6);
    memcpy(p.macSrc, &payload[10], 6);

    // Extract BSSID (Address 3)
    memcpy(p.bssid, &payload[16], 6);

    // Clear SSID initially
    p.ssid[0] = '\0';

    // If Beacon (8) or Probe Response (5), extract SSID
    if (frameSubtype == 8 || frameSubtype == 5) {
        int offset = 36;
        if (offset + 1 < pkt->rx_ctrl.sig_len) {
            if (payload[offset] == 0) { // Tag 0 is SSID
                int ssid_len = payload[offset + 1];
                if (ssid_len > 0 && ssid_len <= 32 && (offset + 2 + ssid_len <= pkt->rx_ctrl.sig_len)) {
                    memcpy(p.ssid, &payload[offset + 2], ssid_len);
                    p.ssid[ssid_len] = '\0';
                }
            }
        }
    }

    // Send the packet to the queue (non-blocking)
    // If the queue is full, we just drop the packet to prevent crashing
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xQueueSendFromISR(packetQueue, &p, &xHigherPriorityTaskWoken);
    if (xHigherPriorityTaskWoken) {
        portYIELD_FROM_ISR();
    }
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

// Helper to escape double quotes and backslashes in JSON strings
void escape_json_string(const char* src, char* dst, size_t max_len) {
    size_t j = 0;
    for (size_t i = 0; src[i] != '\0' && j < max_len - 2; i++) {
        if (src[i] == '"' || src[i] == '\\') {
            dst[j++] = '\\';
        }
        dst[j++] = src[i];
    }
    dst[j] = '\0';
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
            case 1: subtypeStr = "Association Response"; break;
            case 2: subtypeStr = "Reassociation Request"; break;
            case 3: subtypeStr = "Reassociation Response"; break;
            case 4: subtypeStr = "Probe Request"; break;
            case 5: subtypeStr = "Probe Response"; break;
            case 6: subtypeStr = "Timing Advertisement"; break;
            case 7: subtypeStr = "Reserved (7)"; break;
            case 8: subtypeStr = "Beacon"; break;
            case 9: subtypeStr = "ATIM"; break;
            case 10: subtypeStr = "Disassociation"; break;
            case 11: subtypeStr = "Authentication"; break;
            case 12: subtypeStr = "Deauthentication"; break;
            case 13: subtypeStr = "Action"; break;
            case 14: subtypeStr = "Action No Ack"; break;
            case 15: subtypeStr = "Reserved (15)"; break;
        }

        char escapedSsid[65];
        escape_json_string(p.ssid, escapedSsid, sizeof(escapedSsid));

        // Print JSON to Serial (This is safe to do in the main loop)
        Serial.printf("{\"timestamp\": %lu, \"rssi\": %d, \"channel\": %d, \"mac_src\": \"%02X:%02X:%02X:%02X:%02X:%02X\", \"mac_dst\": \"%02X:%02X:%02X:%02X:%02X:%02X\", \"bssid\": \"%02X:%02X:%02X:%02X:%02X:%02X\", \"type\": \"Management\", \"subtype\": \"%s\", \"ssid\": \"%s\"}\n",
                      p.timestamp, p.rssi, p.channel, 
                      p.macSrc[0], p.macSrc[1], p.macSrc[2], p.macSrc[3], p.macSrc[4], p.macSrc[5],
                      p.macDst[0], p.macDst[1], p.macDst[2], p.macDst[3], p.macDst[4], p.macDst[5],
                      p.bssid[0], p.bssid[1], p.bssid[2], p.bssid[3], p.bssid[4], p.bssid[5],
                      subtypeStr, escapedSsid);
                      
        packetsProcessed++;
    }
    
    // Yield to FreeRTOS idle task without blocking
    vTaskDelay(1);
}
