#include "esp_wifi.h"
#include <WiFi.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/semphr.h>
#include "driver/i2s.h"
#include "audio_data.h"

// Configuration
const int CHANNEL_HOP_INTERVAL = 200; // ms
const int MIN_RSSI_THRESHOLD = -80; // Filter out packets weaker than -80 dBm
unsigned long lastHopTime = 0;
int currentChannel = 1;

// I2S Configuration for MAX98357A
#define I2S_BCK_PIN 26
#define I2S_LRC_PIN 25
#define I2S_DOUT_PIN 27
#define I2S_NUM I2S_NUM_0

// Audio State
volatile bool isPlayingAudio = false;
const uint8_t* currentAudioData = NULL;
uint32_t currentAudioLen = 0;
volatile uint32_t currentAudioPos = 0;
SemaphoreHandle_t audioMutex;

// Define a struct to hold only essential packet data
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
const int QUEUE_SIZE = 50; 

// Initialize I2S peripheral
void initI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = AUDIO_SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_STAND_I2S),
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 64,
        .use_apll = false,
        .tx_desc_auto_clear = true,
        .fixed_mclk = 0
    };
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCK_PIN,
        .ws_io_num = I2S_LRC_PIN,
        .data_out_num = I2S_DOUT_PIN,
        .data_in_num = I2S_PIN_NO_CHANGE
    };
    i2s_driver_install(I2S_NUM, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM, &pin_config);
    i2s_set_clk(I2S_NUM, AUDIO_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_MONO);
}

// Trigger audio track playback
void playTrack(const char* track) {
    if (audioMutex == NULL) return;
    if (xSemaphoreTake(audioMutex, portMAX_DELAY) == pdTRUE) {
        if (strcmp(track, "deauth") == 0) {
            currentAudioData = audio_deauth;
            currentAudioLen = audio_deauth_len;
        } else if (strcmp(track, "evil_twin") == 0) {
            currentAudioData = audio_evil_twin;
            currentAudioLen = audio_evil_twin_len;
        } else if (strcmp(track, "mac_spoof") == 0) {
            currentAudioData = audio_mac_spoof;
            currentAudioLen = audio_mac_spoof_len;
        } else if (strcmp(track, "greeting") == 0) {
            currentAudioData = audio_greeting;
            currentAudioLen = audio_greeting_len;
        } else if (strcmp(track, "history") == 0) {
            currentAudioData = audio_history;
            currentAudioLen = audio_history_len;
        } else {
            xSemaphoreGive(audioMutex);
            return;
        }
        currentAudioPos = 0;
        isPlayingAudio = true;
        xSemaphoreGive(audioMutex);
    }
}

// Dedicated FreeRTOS background task running on Core 1 for DMA audio output
void audioTask(void *pvParameters) {
    uint8_t rawBuf[256];
    int16_t i2sBuf[256];
    size_t bytesWritten;

    while (true) {
        bool playing = false;
        const uint8_t* dataPtr = NULL;
        uint32_t len = 0;
        uint32_t pos = 0;

        if (xSemaphoreTake(audioMutex, 10 / portTICK_PERIOD_MS) == pdTRUE) {
            playing = isPlayingAudio;
            dataPtr = currentAudioData;
            len = currentAudioLen;
            pos = currentAudioPos;
            xSemaphoreGive(audioMutex);
        }

        if (playing && dataPtr != NULL && pos < len) {
            uint32_t remaining = len - pos;
            uint32_t chunkSize = (remaining > sizeof(rawBuf)) ? sizeof(rawBuf) : remaining;
            memcpy_P(rawBuf, dataPtr + pos, chunkSize);

            // Convert 8-bit unsigned PCM (0..255) to 16-bit signed PCM with 1.5x Gain Boost for Max Volume
            for (uint32_t i = 0; i < chunkSize; i++) {
                int32_t sample = ((int32_t)rawBuf[i] - 128) * 384; // 1.5x maximum volume gain scaling
                if (sample > 32767) sample = 32767;
                if (sample < -32768) sample = -32768;
                i2sBuf[i] = (int16_t)sample;
            }

            i2s_write(I2S_NUM, i2sBuf, chunkSize * sizeof(int16_t), &bytesWritten, portMAX_DELAY);

            if (xSemaphoreTake(audioMutex, portMAX_DELAY) == pdTRUE) {
                currentAudioPos += chunkSize;
                if (currentAudioPos >= currentAudioLen) {
                    isPlayingAudio = false;
                    currentAudioData = NULL;
                }
                xSemaphoreGive(audioMutex);
            }
        } else {
            vTaskDelay(10 / portTICK_PERIOD_MS);
        }
    }
}

// Wi-Fi Promiscuous Callback (runs in high-priority context on Core 0)
void wifi_promiscuous_cb(void *buf, wifi_promiscuous_pkt_type_t type) {
    if (type != WIFI_PKT_MGMT) return;
    
    wifi_promiscuous_pkt_t *pkt = (wifi_promiscuous_pkt_t *)buf;
    uint8_t *payload = pkt->payload;
    
    uint16_t fc = payload[0] | (payload[1] << 8);
    uint8_t frameType = (fc & 0x0C) >> 2;
    uint8_t frameSubtype = (fc & 0xF0) >> 4;
    
    if (frameType != 0) return; 
    if (pkt->rx_ctrl.rssi < MIN_RSSI_THRESHOLD) return;
    if (pkt->rx_ctrl.sig_len < 24) return;

    SniffPacket p;
    p.timestamp = millis();
    p.rssi = pkt->rx_ctrl.rssi;
    p.channel = pkt->rx_ctrl.channel;
    p.frameSubtype = frameSubtype;
    
    memcpy(p.macDst, &payload[4], 6);
    memcpy(p.macSrc, &payload[10], 6);
    memcpy(p.bssid, &payload[16], 6);

    p.ssid[0] = '\0';

    if (frameSubtype == 8 || frameSubtype == 5) {
        int offset = 36;
        if (offset + 1 < pkt->rx_ctrl.sig_len) {
            if (payload[offset] == 0) {
                int ssid_len = payload[offset + 1];
                if (ssid_len > 0 && ssid_len <= 32 && (offset + 2 + ssid_len <= pkt->rx_ctrl.sig_len)) {
                    memcpy(p.ssid, &payload[offset + 2], ssid_len);
                    p.ssid[ssid_len] = '\0';
                }
            }
        }
    }

    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xQueueSendFromISR(packetQueue, &p, &xHigherPriorityTaskWoken);
    if (xHigherPriorityTaskWoken) {
        portYIELD_FROM_ISR();
    }
}

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(10); // Prevent Serial.readStringUntil from blocking
    
    audioMutex = xSemaphoreCreateMutex();
    initI2S();

    // Create Audio Task on Core 1
    xTaskCreatePinnedToCore(audioTask, "AudioTask", 4096, NULL, 1, NULL, 1);

    packetQueue = xQueueCreate(QUEUE_SIZE, sizeof(SniffPacket));
    
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_promiscuous_rx_cb(&wifi_promiscuous_cb);
    
    Serial.println("{\"log\": \"ESP32 Sniffer + I2S Audio initialized. Waiting for packets...\"}");
}

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
    // 1. Process Incoming Serial Commands for Audio Playback
    if (Serial.available()) {
        String line = Serial.readStringUntil('\n');
        line.trim();
        if (line.startsWith("{")) {
            if (line.indexOf("\"deauth\"") != -1) playTrack("deauth");
            else if (line.indexOf("\"evil_twin\"") != -1) playTrack("evil_twin");
            else if (line.indexOf("\"mac_spoof\"") != -1) playTrack("mac_spoof");
            else if (line.indexOf("\"greeting\"") != -1) playTrack("greeting");
            else if (line.indexOf("\"history\"") != -1) playTrack("history");
        }
    }

    // 2. Hop channels
    if (millis() - lastHopTime > CHANNEL_HOP_INTERVAL) {
        lastHopTime = millis();
        currentChannel++;
        if (currentChannel > 13) currentChannel = 1;
        esp_wifi_set_channel(currentChannel, WIFI_SECOND_CHAN_NONE);
    }
    
    // 3. Process packets from queue
    SniffPacket p;
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

        Serial.printf("{\"timestamp\": %lu, \"rssi\": %d, \"channel\": %d, \"mac_src\": \"%02X:%02X:%02X:%02X:%02X:%02X\", \"mac_dst\": \"%02X:%02X:%02X:%02X:%02X:%02X\", \"bssid\": \"%02X:%02X:%02X:%02X:%02X:%02X\", \"type\": \"Management\", \"subtype\": \"%s\", \"ssid\": \"%s\"}\n",
                      p.timestamp, p.rssi, p.channel, 
                      p.macSrc[0], p.macSrc[1], p.macSrc[2], p.macSrc[3], p.macSrc[4], p.macSrc[5],
                      p.macDst[0], p.macDst[1], p.macDst[2], p.macDst[3], p.macDst[4], p.macDst[5],
                      p.bssid[0], p.bssid[1], p.bssid[2], p.bssid[3], p.bssid[4], p.bssid[5],
                      subtypeStr, escapedSsid);
                      
        packetsProcessed++;
    }
    
    vTaskDelay(1);
}
