/*
 * Thiagarajar Polytechnic - ESP32 Fingerprint Attendance System
 *
 * Hardware: ESP32 + R307 Fingerprint Sensor
 *
 * UPDATED WIRING:
 * ============================
 * R307 VCC (Red)    → ESP32 3.3V
 * R307 GND (Black)  → ESP32 GND
 * R307 TX (Yellow)  → ESP32 GPIO 4 (D4)
 * R307 RX (Green)   → ESP32 GPIO 5 (D5)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_Fingerprint.h>
#include <ArduinoJson.h>

// ========================================
// WIFI CONFIGURATION - YOUR SETTINGS
// ========================================
const char* WIFI_SSID = "ProjectWiFi";
const char* WIFI_PASSWORD = "12345678";
const char* SERVER_URL = "http://192.168.137.1:5000";

// ========================================
// HARDWARE SETUP
// ========================================
HardwareSerial mySerial(2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

// ========================================
// GLOBAL VARIABLES
// ========================================
String currentMode = "attendance";
int enrollID = -1;
int lastFingerID = -1;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n========================================");
  Serial.println("Thiagarajar Polytechnic College");
  Serial.println("AI & ML Lab - Smart Attendance");
  Serial.println("========================================\n");

  // 🔹 UPDATED UART PINS (RX=4, TX=5)
  mySerial.begin(57600, SERIAL_8N1, 4, 5);

  if (finger.verifyPassword()) {
    Serial.println("✓ Fingerprint sensor detected!");
  } else {
    Serial.println("✗ Sensor not found! Check wiring.");
    while (1) { delay(1); }
  }

  // WiFi connection
  Serial.print("Connecting to: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ WiFi failed!");
  }

  Serial.println("\n✅ System Ready!\n");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    checkServerMode();
  }

  if (currentMode == "enroll") {
    enrollFingerprint(enrollID);
    currentMode = "attendance";
  } else {
    checkFingerprint();
  }

  delay(500);
}

void checkServerMode() {
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck < 500) return;
  lastCheck = millis();

  HTTPClient http;
  http.begin(String(SERVER_URL) + "/get_mode");
  int httpCode = http.GET();

  if (httpCode == 200) {
    StaticJsonDocument<200> doc;
    deserializeJson(doc, http.getString());

    const char* action = doc["action"];
    if (strcmp(action, "enroll") == 0) {
      currentMode = "enroll";
      enrollID = doc["id"];
      Serial.println("\n📝 ENROLLMENT MODE - ID: " + String(enrollID));
    } else {
      currentMode = "attendance";
    }
  }
  http.end();
}

void enrollFingerprint(int id) {
  Serial.println("\n🔵 Starting enrollment for ID: " + String(id));
  reportEnrollmentStatus("started", id);
  
  // Step 1: Get first fingerprint image
  Serial.println("🔵 Place finger...");
  reportEnrollmentStatus("waiting_finger_1", id);
  
  int p = -1;
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    delay(100);
  }
  Serial.println("✓ Image 1 captured");
  reportEnrollmentStatus("got_finger_1", id);

  finger.image2Tz(1);
  
  Serial.println("🔵 Remove finger");
  reportEnrollmentStatus("remove_finger", id);
  delay(2000);

  while (finger.getImage() != FINGERPRINT_NOFINGER) delay(100);

  // Step 2: Get second fingerprint image
  Serial.println("🔵 Place SAME finger again...");
  reportEnrollmentStatus("waiting_finger_2", id);
  
  p = -1;
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    delay(100);
  }
  Serial.println("✓ Image 2 captured");
  reportEnrollmentStatus("got_finger_2", id);

  finger.image2Tz(2);

  // Step 3: Create and store model
  Serial.println("🔄 Processing...");
  reportEnrollmentStatus("processing", id);
  
  if (finger.createModel() == FINGERPRINT_OK) {
    if (finger.storeModel(id) == FINGERPRINT_OK) {
      Serial.println("\n✅ ENROLLED! ID: " + String(id) + "\n");
      reportEnrollmentStatus("success", id);
    } else {
      Serial.println("✗ Storage failed!");
      reportEnrollmentStatus("failed", id);
    }
  } else {
    Serial.println("✗ Mismatch! Try again");
    reportEnrollmentStatus("failed", id);
  }
}

void checkFingerprint() {
  if (finger.getImage() != FINGERPRINT_OK) return;

  Serial.println("\n🔍 Scanning...");
  finger.image2Tz();

  if (finger.fingerSearch() == FINGERPRINT_OK) {
    int fingerID = finger.fingerID;

    if (fingerID == lastFingerID) return;
    lastFingerID = fingerID;

    Serial.println("✅ MATCH! ID: " + String(fingerID));

    if (WiFi.status() == WL_CONNECTED) {
      sendToServer(fingerID);
    }

    delay(3000);
    lastFingerID = -1;
  } else {
    Serial.println("✗ No match\n");
    delay(2000);
  }
}

void sendToServer(int fingerID) {
  HTTPClient http;
  http.begin(String(SERVER_URL) + "/verify");
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["finger_id"] = fingerID;
  String json;
  serializeJson(doc, json);

  int httpCode = http.POST(json);
  if (httpCode == 200) {
    Serial.println("✓ Attendance marked!\n");
  }
  http.end();
}

void reportEnrollmentStatus(String status, int fingerID) {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  http.begin(String(SERVER_URL) + "/enrollment_status");
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["finger_id"] = fingerID;
  doc["status"] = status;
  String json;
  serializeJson(doc, json);

  int httpCode = http.POST(json);
  if (httpCode == 200) {
    Serial.println("✓ Status sent: " + status);
  }
  http.end();
}
