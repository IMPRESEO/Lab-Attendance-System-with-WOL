# Installation Guide
## Thiagarajar Polytechnic - Smart Attendance System

This guide will walk you through the complete installation process from scratch.

---

## 📋 System Requirements

### Hardware:
- Computer (Windows/Linux/Mac) to run the server
- ESP32 Development Board
- R307 Optical Fingerprint Sensor
- USB cable for ESP32
- 4 jumper wires (Female-to-Male)
- Network router (for WiFi)

### Software:
- Python 3.8 or higher
- Arduino IDE 1.8.19 or higher
- Web browser (Chrome, Firefox, Edge)

---

## 🔧 Part 1: Python Server Installation

### Step 1: Install Python

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"
5. Verify: Open Command Prompt and type `python --version`

**Linux/Mac:**
```bash
# Usually pre-installed, verify with:
python3 --version

# If not installed (Ubuntu/Debian):
sudo apt update
sudo apt install python3 python3-pip
```

### Step 2: Download Project Files

Extract all files to a folder, e.g., `C:\thiagarajar-attendance\`

Your folder should contain:
```
thiagarajar-attendance/
├── app.py
├── setup_db.py
├── requirements.txt
├── esp32_firmware.ino
├── templates/
│   ├── login.html
│   ├── index.html
│   ├── dashboard.html
│   └── attendance_report.html
└── static/
    └── (empty, for logo.png)
```

### Step 3: Install Dependencies

Open terminal/command prompt in the project folder:

**Windows:**
```cmd
cd C:\thiagarajar-attendance
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
cd ~/thiagarajar-attendance
pip3 install -r requirements.txt
```

You should see:
```
Successfully installed Flask-2.3.2 wakeonlan-3.0.0 Werkzeug-2.3.6
```

### Step 4: Initialize Database

```bash
python setup_db.py
```

Expected output:
```
✓ Created users table
✓ Created attendance table
✓ Inserted 8 sample users
✓ Inserted 6 sample attendance logs

✅ Database setup complete!

📋 Login Credentials:
   Admin:  admin / admin123
   ...
```

### Step 5: Find Your Computer's IP Address

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

**Linux/Mac:**
```bash
ifconfig
# or
ip addr show
```
Look for "inet" address (e.g., 192.168.1.100)

**Write this down! You'll need it for ESP32 configuration.**

### Step 6: Start the Server

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

**Keep this terminal window open!**

### Step 7: Test Web Interface

1. Open browser
2. Go to `http://localhost:5000`
3. You should see the login page
4. Login with: `admin` / `admin123`
5. You should see the Navy Blue home screen

✅ **Server installation complete!**

---

## 🤖 Part 2: ESP32 Firmware Installation

### Step 1: Install Arduino IDE

1. Download from https://www.arduino.cc/en/software
2. Install on your computer
3. Open Arduino IDE

### Step 2: Install ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Click **OK**
5. Go to **Tools → Board → Boards Manager**
6. Search for "esp32"
7. Install "ESP32 by Espressif Systems"
8. Wait for installation to complete

### Step 3: Install Required Libraries

1. Go to **Sketch → Include Library → Manage Libraries**
2. Install these libraries:

**Library 1: Adafruit Fingerprint Sensor Library**
- Search: "Adafruit Fingerprint"
- Install by Adafruit

**Library 2: ArduinoJson**
- Search: "ArduinoJson"
- Install by Benoit Blanchon
- Choose version 6.x.x

### Step 4: Configure the Code

1. Open `esp32_firmware.ino` in Arduino IDE
2. Find these lines (around line 20-22):

```cpp
const char* WIFI_SSID = "YourWiFiName";
const char* WIFI_PASSWORD = "YourWiFiPassword";
const char* SERVER_URL = "http://192.168.1.100:5000";
```

3. Change them to:
```cpp
const char* WIFI_SSID = "YOUR_ACTUAL_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_ACTUAL_WIFI_PASSWORD";
const char* SERVER_URL = "http://YOUR_COMPUTER_IP:5000";
```

**Example:**
```cpp
const char* WIFI_SSID = "TP-LAB-WIFI";
const char* WIFI_PASSWORD = "Lab@2024";
const char* SERVER_URL = "http://192.168.1.100:5000";
```

### Step 5: Connect ESP32 to Computer

1. Connect ESP32 to computer via USB cable
2. Wait for drivers to install (Windows may take a moment)

### Step 6: Select Board and Port

1. Go to **Tools → Board → ESP32 Arduino**
2. Select **"ESP32 Dev Module"**
3. Go to **Tools → Port**
4. Select the COM port with ESP32 (e.g., COM3, /dev/ttyUSB0)

If you don't see a port:
- Try a different USB cable
- Install CH340 or CP2102 drivers
- Check Device Manager (Windows)

### Step 7: Upload Code

1. Click the **Upload** button (→ icon)
2. Wait for compilation
3. You'll see: "Connecting........"
4. If it hangs, press and hold the "BOOT" button on ESP32
5. Wait for "Hard resetting via RTS pin..."

Upload successful!

### Step 8: Test Communication

1. Open **Serial Monitor** (magnifying glass icon)
2. Set baud rate to **115200**
3. You should see:

```
========================================
Thiagarajar Polytechnic
Smart Attendance System - ESP32
========================================

Connecting to WiFi....
✓ WiFi connected!
IP Address: 192.168.1.XXX

System Ready. Waiting for commands...
```

✅ **ESP32 installation complete!**

---

## 🔌 Part 3: Hardware Assembly

Follow the **WIRING_GUIDE.md** for detailed instructions.

### Quick Reference:

```
R307 → ESP32
Red (VCC) → 5V
Black (GND) → GND
White (TX) → GPIO 16
Green (RX) → GPIO 17
```

---

## ✅ Part 4: System Testing

### Test 1: Web Access

1. Ensure Flask server is running
2. Open browser: `http://YOUR_IP:5000`
3. Login: admin / admin123
4. Navigate to Dashboard
5. You should see the sample users

### Test 2: Fingerprint Sensor

1. Check Serial Monitor on ESP32
2. Place finger on sensor
3. LED should light up
4. Serial monitor may show "No match found" (normal - not enrolled yet)

### Test 3: Add New User

1. In Dashboard, fill "Register New User" form:
   - Name: Test Student
   - Reg No: TEST001
   - Role: Student
   - Password: test123
2. Click "Add User"
3. System assigns Finger ID automatically

### Test 4: Enroll Fingerprint

1. Click yellow "Enroll" button next to the new user
2. ESP32 Serial Monitor shows: "ENROLLMENT MODE ACTIVATED"
3. Place finger when prompted
4. Remove and place again
5. Success message appears

### Test 5: Verify Attendance

1. Cancel enrollment mode (return to Dashboard)
2. Place enrolled finger on sensor
3. ESP32 should show: "Match found! Finger ID: X"
4. Check Dashboard - attendance should be logged
5. Home screen shows recent activity

### Test 6: Wake-on-LAN (Optional)

1. Find a PC's MAC address: `getmac`
2. In Dashboard, add MAC to a user
3. Enroll that user's fingerprint
4. Scan finger
5. PC should turn on (requires BIOS WOL enabled)

---

## 🎯 Part 5: Production Deployment

### Security Hardening:

1. **Change Default Passwords**
   ```python
   # In setup_db.py, change all passwords
   ('System Admin', 'ADMIN001', 'admin', None, None, 'STRONG_PASSWORD_HERE'),
   ```

2. **Secure the Network**
   - Use WPA2/WPA3 WiFi encryption
   - Don't expose port 5000 to internet
   - Use firewall rules

3. **Regular Backups**
   ```bash
   # Backup database daily
   cp attendance.db attendance_backup_$(date +%Y%m%d).db
   ```

### Auto-Start on Boot:

**Windows (Task Scheduler):**
1. Create batch file `start_server.bat`:
   ```batch
   cd C:\thiagarajar-attendance
   python app.py
   ```
2. Add to Task Scheduler to run at startup

**Linux (systemd):**
1. Create service file `/etc/systemd/system/attendance.service`:
   ```ini
   [Unit]
   Description=Thiagarajar Attendance System
   
   [Service]
   ExecStart=/usr/bin/python3 /home/user/thiagarajar-attendance/app.py
   WorkingDirectory=/home/user/thiagarajar-attendance
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
2. Enable: `sudo systemctl enable attendance`

---

## 🐛 Common Installation Issues

### Issue: "pip: command not found"
**Solution:** Install pip:
```bash
# Windows
python -m ensurepip --upgrade

# Linux
sudo apt install python3-pip
```

### Issue: "Port already in use"
**Solution:** Change port in app.py:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Issue: ESP32 not recognized
**Solution:** Install drivers:
- CH340: https://sparks.gogo.co.nz/ch340.html
- CP2102: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

### Issue: "Module 'flask' not found"
**Solution:** Use full path:
```bash
python -m pip install -r requirements.txt
```

### Issue: WiFi connection timeout
**Solution:**
- Check SSID and password
- Try 2.4GHz network (not 5GHz)
- Move ESP32 closer to router

---

## 📞 Getting Help

If you encounter issues:

1. **Check Logs:**
   - Flask server terminal
   - ESP32 Serial Monitor (115200 baud)

2. **Verify Configuration:**
   - WiFi credentials correct
   - Server IP correct
   - Hardware wiring correct

3. **Test Components:**
   - Test server alone (web browser)
   - Test ESP32 alone (Serial Monitor)
   - Test sensor alone (LED lights up)

4. **Review Documentation:**
   - README.md
   - WIRING_GUIDE.md
   - This INSTALLATION_GUIDE.md

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed and verified
- [ ] Project files extracted
- [ ] Python dependencies installed
- [ ] Database initialized successfully
- [ ] Flask server runs and accessible via browser
- [ ] Arduino IDE installed
- [ ] ESP32 board support added
- [ ] Required libraries installed
- [ ] Firmware configured with WiFi and IP
- [ ] ESP32 connected and recognized
- [ ] Firmware uploaded successfully
- [ ] Serial Monitor shows connection
- [ ] Hardware wired correctly
- [ ] Fingerprint sensor detected
- [ ] Test user enrolled
- [ ] Attendance logging works
- [ ] (Optional) Wake-on-LAN tested

---

**Congratulations! Your system is fully operational! 🎉**

Next steps:
1. Add all students to the system
2. Enroll their fingerprints
3. Assign PC MAC addresses
4. Start tracking attendance!
