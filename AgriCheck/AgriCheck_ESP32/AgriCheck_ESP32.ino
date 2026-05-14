#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============ WiFi Configuration ============
const char* ssid = "TP-Link_DDBD";
const char* password = "84705594";
const char* serverUrl = "http://192.168.0.109:8000/readings/";  // ← FIXED IP


// ============ RS485 & LCD Pins ============
#define RS485_RX_PIN      16
#define RS485_TX_PIN      17
#define RS485_DE_RE_PIN   4
#define RS485_BAUD        9600
#define LCD_ADDR          0x27
#define LCD_COLS          20
#define LCD_ROWS          4

// ============ Modbus Configuration ============
#define SLAVE_ID          0x01
#define FC_READ_HOLD      0x03
#define REG_START         0x0000
#define REG_COUNT         7
#define MODBUS_TIMEOUT_MS 1000
#define POLL_INTERVAL_MS  10000
#define DE_RE_SETTLE_MS   50

LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);
HardwareSerial npkSerial(2);
bool lcdAvailable = false;
bool wifiConnected = false;

uint16_t crc16Modbus(const uint8_t *buf, uint8_t len) {
    uint16_t crc = 0xFFFF;
    for (uint8_t i = 0; i < len; i++) {
        crc ^= (uint16_t)buf[i];
        for (uint8_t b = 0; b < 8; b++) {
            if (crc & 0x0001) { crc = (crc >> 1) ^ 0xA001; }
            else { crc >>= 1; }
        }
    }
    return crc;
}

void sendModbusRequest(uint8_t slaveID, uint16_t regStart, uint16_t regCount) {
    uint8_t frame[8];
    frame[0] = slaveID;
    frame[1] = FC_READ_HOLD;
    frame[2] = (regStart >> 8) & 0xFF;
    frame[3] =  regStart       & 0xFF;
    frame[4] = (regCount >> 8) & 0xFF;
    frame[5] =  regCount       & 0xFF;
    uint16_t crc = crc16Modbus(frame, 6);
    frame[6] = crc & 0xFF;
    frame[7] = (crc >> 8) & 0xFF;

    Serial.print("[TX] ");
    for (uint8_t i = 0; i < 8; i++) Serial.printf("0x%02X ", frame[i]);
    Serial.println();

    while (npkSerial.available()) npkSerial.read();

    digitalWrite(RS485_DE_RE_PIN, HIGH);
    delayMicroseconds(100);
    npkSerial.write(frame, 8);
    npkSerial.flush();
    digitalWrite(RS485_DE_RE_PIN, LOW);

    delay(DE_RE_SETTLE_MS);
}

bool receiveModbusResponse(uint16_t *humidity,   uint16_t *temperature,
                           uint16_t *ec,         uint16_t *ph,
                           uint16_t *nitrogen,   uint16_t *phosphorus,
                           uint16_t *potassium) {
    const uint8_t EXPECTED = 19;
    uint8_t  buf[64];
    uint8_t  idx          = 0;
    uint32_t deadline     = millis() + MODBUS_TIMEOUT_MS;
    bool     frameStarted = false;

    while (millis() < deadline) {
        while (npkSerial.available() && idx < sizeof(buf)) {
            uint8_t incoming = (uint8_t)npkSerial.read();

            if (!frameStarted) {
                if (incoming == SLAVE_ID) {
                    frameStarted = true;
                    buf[idx++]   = incoming;
                    Serial.printf("[SYNC] 0x%02X found. Frame capture started.\n", incoming);
                } else {
                    Serial.printf("[SKIP] Garbage: 0x%02X\n", incoming);
                }
            } else {
                buf[idx++] = incoming;
            }
        }
        if (idx >= EXPECTED) break;
        delay(1);
    }

    if (idx > 0) {
        Serial.print("[RX] ");
        for (uint8_t i = 0; i < idx; i++) Serial.printf("0x%02X ", buf[i]);
        Serial.println();
    } else {
        Serial.println("[RX] No response (timeout).");
        return false;
    }

    if (idx < EXPECTED) {
        Serial.printf("[ERR] Short frame: got %d, need %d\n", idx, EXPECTED);
        return false;
    }
    if (buf[0] != SLAVE_ID) {
        Serial.printf("[ERR] Slave ID mismatch: got 0x%02X\n", buf[0]);
        return false;
    }
    if (buf[1] & 0x80) {
        Serial.printf("[ERR] Modbus exception: 0x%02X\n", buf[2]);
        return false;
    }
    if (buf[1] != FC_READ_HOLD) {
        Serial.printf("[ERR] Wrong function code: 0x%02X\n", buf[1]);
        return false;
    }
    if (buf[2] != REG_COUNT * 2) {
        Serial.printf("[ERR] Wrong byte count: got %d, expected %d\n", buf[2], REG_COUNT * 2);
        return false;
    }

    uint16_t rxCRC  = (uint16_t)buf[idx - 1] << 8 | buf[idx - 2];
    uint16_t calCRC = crc16Modbus(buf, idx - 2);
    Serial.printf("[CRC] RX=0x%04X  CALC=0x%04X  %s\n",
                  rxCRC, calCRC, rxCRC == calCRC ? "OK" : "FAIL");
    if (rxCRC != calCRC) return false;

    *humidity    = (uint16_t)buf[3]  << 8 | buf[4];
    *temperature = (uint16_t)buf[5]  << 8 | buf[6];
    *ec          = (uint16_t)buf[7]  << 8 | buf[8];
    *ph          = (uint16_t)buf[9]  << 8 | buf[10];
    *nitrogen    = (uint16_t)buf[11] << 8 | buf[12];
    *phosphorus  = (uint16_t)buf[13] << 8 | buf[14];
    *potassium   = (uint16_t)buf[15] << 8 | buf[16];

    return true;
}

bool checkLCD() {
    Wire.beginTransmission(LCD_ADDR);
    return (Wire.endTransmission() == 0);
}

void lcdWrite(uint8_t col, uint8_t row, const char *text, uint8_t width = 20) {
    if (!lcdAvailable) return;
    lcd.setCursor(col, row);
    uint8_t i = 0;
    while (text[i] && i < width) { lcd.print(text[i++]); }
    while (i++ < width)          { lcd.print(' ');        }
}

void showWelcome() {
    if (!lcdAvailable) return;
    lcd.clear();
    lcdWrite(0, 0, "====================");
    lcdWrite(0, 1, "   AgriCheck v3.0   ");
    lcdWrite(0, 2, " WiFi + Cloud Ready ");
    lcdWrite(0, 3, "====================");
    delay(2500);
}

void showPage1(uint16_t hum, uint16_t temp, uint16_t ec, uint16_t ph) {
    if (!lcdAvailable) return;
    char row[21];
    lcdWrite(0, 0, "-- AgriCheck 1/2  --");
    snprintf(row, sizeof(row), "Humidity   : %4d.%d%%", hum  / 10, hum  % 10); lcdWrite(0, 1, row);
    snprintf(row, sizeof(row), "Temp (C)   : %4d.%d ", temp / 10, temp % 10); lcdWrite(0, 2, row);
    snprintf(row, sizeof(row), "pH         :  %2d.%d  ", ph   / 10, ph   % 10); lcdWrite(0, 3, row);
}

void showPage2(uint16_t ec, uint16_t n, uint16_t p, uint16_t k) {
    if (!lcdAvailable) return;
    char row[21];
    lcdWrite(0, 0, "-- AgriCheck 2/2  --");
    snprintf(row, sizeof(row), "EC  (us/cm): %6d ", ec);          lcdWrite(0, 1, row);
    snprintf(row, sizeof(row), "N (Nitrog) : %4d    ", n);         lcdWrite(0, 2, row);
    snprintf(row, sizeof(row), "P:%4d  K:%4d mg/kg", p, k);       lcdWrite(0, 3, row);
}

void showError() {
    if (!lcdAvailable) return;
    lcdWrite(0, 0, "-- AgriCheck v3.0 --");
    lcdWrite(0, 1, "                    ");
    lcdWrite(0, 2, "  !! Sensor Error!! ");
    lcdWrite(0, 3, "  Check 12V & GND   ");
}

void showWiFiStatus() {
    if (!lcdAvailable) return;
    char row[21];
    lcdWrite(0, 0, "-- WiFi Status    --");
    if (wifiConnected) {
        lcdWrite(0, 1, "Status: Connected   ");
        snprintf(row, sizeof(row), "IP: %s", WiFi.localIP().toString().c_str());
        lcdWrite(0, 2, row);
    } else {
        lcdWrite(0, 1, "Status: Disconnected");
        lcdWrite(0, 2, "Retrying...         ");
    }
    lcdWrite(0, 3, "                    ");
    delay(2000);
}

void connectToWiFi() {
    Serial.print("[WiFi] Connecting to: ");
    Serial.println(ssid);
    
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        wifiConnected = true;
        Serial.println("\n[WiFi] Connected!");
        Serial.print("[WiFi] IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        wifiConnected = false;
        Serial.println("\n[WiFi] Connection Failed!");
    }
    
    showWiFiStatus();
}

void sendDataToServer(uint16_t hum, uint16_t temp, uint16_t ec, uint16_t ph,
                      uint16_t n, uint16_t p, uint16_t k) {
    if (!wifiConnected) {
        Serial.println("[HTTP] WiFi not connected. Skipping upload.");
        return;
    }
    
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<256> doc;
    doc["humidity"]    = hum  / 10.0;
    doc["temperature"] = temp / 10.0;
    doc["ec"]          = (float)ec;
    doc["ph"]          = ph   / 10.0;
    doc["nitrogen"]    = (float)n;
    doc["phosphorus"]  = (float)p;
    doc["potassium"]   = (float)k;
    
    String jsonPayload;
    serializeJson(doc, jsonPayload);
    
    Serial.println("\n[HTTP] Sending to server...");
    Serial.print("[HTTP] URL: ");
    Serial.println(serverUrl);
    Serial.print("[HTTP] Payload: ");
    Serial.println(jsonPayload);
    
    int httpCode = http.POST(jsonPayload);
    
    if (httpCode > 0) {
        Serial.printf("[HTTP] Response Code: %d\n", httpCode);
        String response = http.getString();
        Serial.print("[HTTP] Response: ");
        Serial.println(response);
        
        if (httpCode == 201) {
            Serial.println("[HTTP] ✓ Data uploaded successfully!");
        }
    } else {
        Serial.printf("[HTTP] ✗ Failed. Error: %s\n", http.errorToString(httpCode).c_str());
    }
    
    http.end();
}

void setup() {
    Serial.begin(115200);
    while (!Serial) delay(10);

    pinMode(RS485_DE_RE_PIN, OUTPUT);
    digitalWrite(RS485_DE_RE_PIN, LOW);

    npkSerial.begin(RS485_BAUD, SERIAL_8N1, RS485_RX_PIN, RS485_TX_PIN);
    Serial.printf("[INIT] Serial2 RX=GPIO%d TX=GPIO%d DE/RE=GPIO%d @ %d baud\n",
                  RS485_RX_PIN, RS485_TX_PIN, RS485_DE_RE_PIN, RS485_BAUD);

    Wire.begin();
    lcdAvailable = checkLCD();

    if (lcdAvailable) {
        lcd.init();
        lcd.backlight();
        Serial.printf("[INIT] LCD found at 0x%02X\n", LCD_ADDR);
        showWelcome();
    } else {
        Serial.printf("[WARN] LCD not found at 0x%02X. Running without LCD.\n", LCD_ADDR);
    }

    // Connect to WiFi
    connectToWiFi();

    Serial.println("[INIT] AgriCheck ready. Polling every 10 seconds.");
    Serial.println("--------------------------------------------");
}

void loop() {
    static uint32_t lastPoll     = 0;
    static bool     showingPage1 = true;

    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED && wifiConnected) {
        Serial.println("[WiFi] Connection lost. Reconnecting...");
        wifiConnected = false;
        connectToWiFi();
    }

    if (millis() - lastPoll < POLL_INTERVAL_MS) return;
    lastPoll = millis();

    bool lcdWasAvailable = lcdAvailable;
    lcdAvailable = checkLCD();
    if (lcdAvailable && !lcdWasAvailable) {
        Serial.println("[LCD] Reconnected. Reinitializing...");
        lcd.init();
        lcd.backlight();
    }

    Serial.println("\n[POLL] Querying 7-in-1 soil sensor...");
    sendModbusRequest(SLAVE_ID, REG_START, REG_COUNT);

    uint16_t humidity = 0, temperature = 0, ec = 0, ph = 0;
    uint16_t nitrogen = 0, phosphorus  = 0, potassium = 0;

    bool ok = receiveModbusResponse(&humidity, &temperature, &ec, &ph,
                                    &nitrogen, &phosphorus, &potassium);
    if (ok) {
        Serial.println("[OK] Sensor data decoded:");
        Serial.printf("     Humidity    : %d.%d %%\n",   humidity    / 10, humidity    % 10);
        Serial.printf("     Temperature : %d.%d C\n",    temperature / 10, temperature % 10);
        Serial.printf("     EC          : %d us/cm\n",   ec);
        Serial.printf("     pH          : %d.%d\n",      ph          / 10, ph          % 10);
        Serial.printf("     Nitrogen    : %d mg/kg\n",   nitrogen);
        Serial.printf("     Phosphorus  : %d mg/kg\n",   phosphorus);
        Serial.printf("     Potassium   : %d mg/kg\n",   potassium);

        // Show on LCD
        if (showingPage1) {
            showPage1(humidity, temperature, ec, ph);
        } else {
            showPage2(ec, nitrogen, phosphorus, potassium);
        }
        showingPage1 = !showingPage1;

        // Send to server
        sendDataToServer(humidity, temperature, ec, ph, nitrogen, phosphorus, potassium);

    } else {
        Serial.println("[FAIL] No valid response.");
        showError();
    }

    Serial.println("--------------------------------------------");
}