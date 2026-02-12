# Smart Biometric Attendance & Lab Automation System

**Author:** IMPRESEO  
**Project Type:** Personal Development Project  
**Technologies:** Python, Flask, ESP32, Biometric Integration  

![Project Status](https://img.shields.io/badge/status-active--development-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-2.0+-red)
![License](https://img.shields.io/badge/license-MIT-blue)
![ESP32](https://img.shields.io/badge/platform-ESP32-orange)

[![GitHub stars](https://img.shields.io/github/stars/IMPRESEO/Lab-Attendance-System-with-WOL.svg?style=social&label=Star)](https://github.com/IMPRESEO/Lab-Attendance-System-with-WOL)
[![GitHub forks](https://img.shields.io/github/forks/IMPRESEO/Lab-Attendance-System-with-WOL.svg?style=social&label=Fork)](https://github.com/IMPRESEO/Lab-Attendance-System-with-WOL)
[![GitHub issues](https://img.shields.io/github/issues/IMPRESEO/Lab-Attendance-System-with-WOL)](https://github.com/IMPRESEO/Lab-Attendance-System-with-WOL/issues)

**🚀 A complete biometric attendance system with automated lab PC management**

---

## 📋 About This Project

This is a comprehensive biometric attendance system that combines fingerprint recognition with automated PC management. Built as a personal project to demonstrate full-stack development skills, hardware integration, and system architecture.

### What It Does
- **Biometric Authentication**: Uses R307 fingerprint sensor for secure attendance
- **Automated PC Control**: Sends Wake-on-LAN signals to turn on assigned computers
- **Web Dashboard**: Real-time monitoring and management interface
- **Role-Based Access**: Different permission levels for admins, staff, and students
- **Data Export**: Generate attendance reports in Excel format

### Why I Built This
- Learn hardware-software integration
- Practice full-stack web development
- Understand biometric systems
- Implement network automation protocols
- Create a practical, deployable solution

---

## 🏗️ System Architecture

### The Three-Way Link

Every student connects three pieces of information:

1. **Digital Profile** → Name, Register No, Role
2. **Biometric ID** → Fingerprint stored in R307 sensor (ID 1-127)
3. **Hardware ID** → MAC address of their assigned PC

**Example Flow:**
```
Student scans finger → Sensor identifies "Finger ID 11" 
→ Server looks up "ID 11 = Buvanesh" 
→ Server finds MAC "D4-5D-64-A1-B2-C3" 
→ Magic Packet sent → PC turns on!
```

---

## 📋 Prerequisites

### Software Requirements
- Python 3.8 or higher
- Arduino IDE (for ESP32)
- SQLite3 (comes with Python)

### Hardware Requirements
- ESP32 Development Board
- R307 Optical Fingerprint Sensor
- 5V Power Supply for sensor
- Jumper wires

### Python Libraries
```bash
pip install -r requirements.txt
```

The main dependencies include:
- Flask 2.3.3 - Web framework
- pandas 2.0.3 - Data manipulation
- openpyxl 3.1.22 - Excel file handling
- wakeonlan 3.0.0 - Wake-on-LAN functionality
- Werkzeug 2.3.6 - WSGI utilities

### Arduino Libraries
- WiFi (built-in)
- HTTPClient (built-in)
- ArduinoJson
- Adafruit_Fingerprint

---

## 🚀 Quick Start Guide

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Database Setup

```bash
python scripts/setup_db.py
```

This creates a fresh database with sample data:
- **Admin:** admin / admin123
- **HOD:** Dr. Ravi Kumar / hod123
- **Staff:** Prof. Priya Sharma / staff123
- **5 Sample Students** with pre-assigned Finger IDs and MAC addresses

### Step 3: Start Flask Server

```bash
python run.py
```

Server runs on `http://0.0.0.0:5000`

### Step 4: Configure ESP32

1. Open `esp32_firmware.ino` in Arduino IDE
2. Update WiFi credentials:
   ```cpp
   const char* WIFI_SSID = "YourWiFiName";
   const char* WIFI_PASSWORD = "YourPassword";
   ```
3. Update server IP (find with `ipconfig` or `ifconfig`):
   ```cpp
   const char* SERVER_URL = "http://192.168.1.100:5000";
   ```

### Step 5: Wire the Hardware

**CRITICAL - R307 to ESP32 Connections:**

| R307 Wire | Color  | ESP32 Pin |
|-----------|--------|-----------|
| VCC       | Red    | 5V        |
| GND       | Black  | GND       |
| TX        | White  | GPIO 16   |
| RX        | Green  | GPIO 17   |

⚠️ **Important:** R307 requires 5V power. Do NOT use 3.3V!

### Step 6: Upload Firmware

1. Select **ESP32 Dev Module** as board
2. Select correct COM port
3. Click **Upload**
4. Open Serial Monitor (115200 baud) to verify connection

---

## 📖 How to Use the System

### 🔐 Login

1. Go to `http://[SERVER_IP]:5000`
2. Login with admin credentials
3. You'll see the Navy Blue home screen

### ➕ Add a New Student

1. Go to **Dashboard**
2. Fill the "Register New User" form:
   - Name: Student's full name
   - Register No: Unique ID (e.g., A23CS006)
   - Role: Select "Student"
   - Password: Login password for web access
3. Click "Add User"
4. System automatically assigns next Finger ID (e.g., ID 6)

### 🖐️ Enroll Fingerprint

1. In the Users table, find the student
2. Click the yellow **"🔐 Enroll"** button
3. ESP32 will show "ENROLLMENT MODE ACTIVATED"
4. Place student's finger on sensor when prompted
5. Remove finger, then place SAME finger again
6. Success message confirms enrollment

### 💻 Assign PC MAC Address

1. Go to the student's assigned computer
2. Open Command Prompt (Windows) or Terminal (Linux/Mac)
3. Type `getmac` (Windows) or `ifconfig` (Linux/Mac)
4. Copy the MAC address (format: `XX-XX-XX-XX-XX-XX`)
5. In Dashboard, paste into the MAC box next to student's name
6. Click **Save**

### ✅ Test the System

1. Student scans their enrolled finger
2. ESP32 shows "Match found! Finger ID: X"
3. Server logs attendance in database
4. Magic Packet sent to student's PC
5. PC turns on automatically!
6. Home screen shows: "🚀 Wake Signal Sent to [Name]'s PC"

---

## 🗂️ Project Structure

```
lab-attendance-system/
├── run.py                    # Flask server entry point
├── app/                      # Application package
│   ├── __init__.py          # Flask app initialization
│   ├── routes.py            # Web routes and logic
│   ├── models.py            # Database models
│   └── utils.py             # Utility functions
├── scripts/                  # Setup and utility scripts
│   └── setup_db.py          # Database initialization
├── attendance.db             # SQLite database (auto-created)
├── esp32_firmware/           # Arduino code for ESP32
│   └── esp32_firmware.ino   # Main firmware file
├── templates/               # HTML templates
│   ├── login.html           # Login page
│   ├── index.html           # Home screen with banner
│   ├── dashboard.html       # Admin panel
│   └── attendance_report.html # View all logs
├── static/                  # Static assets
│   └── css/                 # Stylesheets
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── LICENSE                  # License file
└── wake_on_lan.py           # Wake-on-LAN utility
```

---

## 🎨 Design Philosophy

### Corporate Professional Theme
- **Primary Color:** Navy Blue (#001f3f)
- **Background:** Light Gray (#f4f6f9)
- **Cards:** Solid White with subtle shadows
- **Text:** High contrast (Dark Grey/Black)
- **NO Glassmorphism** - Clean, solid colors only

### UI Components
- Large "Thiagarajar Polytechnic College" banner
- Welcome card with user stats
- Recent activity table
- Responsive tables for all data views

---

## 🔌 API Endpoints

### Hardware Endpoints (ESP32)

**GET** `/get_mode`  
Returns current operation mode
```json
{
  "action": "enroll",
  "id": 10
}
```

**POST** `/verify`  
Verify fingerprint and log attendance
```json
{
  "finger_id": 10
}
```

### Web Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home screen |
| `/login` | GET/POST | Login page |
| `/logout` | GET | Logout |
| `/dashboard` | GET | Admin panel |
| `/add_user` | POST | Register new user |
| `/delete_user/<id>` | GET | Delete user |
| `/update_mac` | POST | Update MAC address |
| `/activate_enroll/<id>` | GET | Start enrollment |
| `/attendance_report` | GET | View all logs |
| `/download_excel` | GET | Download CSV report |

---

## 🗄️ Database Schema

### `users` Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Full name |
| reg_no | TEXT | Register number (Unique) |
| role | TEXT | admin, hod, staff, student |
| finger_id | INTEGER | R307 sensor ID (Unique) |
| mac_address | TEXT | PC MAC address |
| password | TEXT | Login password |

### `attendance` Table
| Column | Type | Description |
|--------|------|-------------|
| log_id | INTEGER | Primary Key |
| name | TEXT | Student name |
| reg_no | TEXT | Register number |
| timestamp | TEXT | Scan time |
| status | TEXT | Present |

---

## 🔒 Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **Admin** | Full access. Add/delete users, enroll fingerprints, assign MACs, view all logs, download reports |
| **HOD** | View-only access to all logs and reports. Cannot delete users |
| **Staff** | View attendance logs and PC status |
| **Student** | View their own attendance history |

---

## 🛠️ Troubleshooting

### Fingerprint Sensor Not Detected
- Check wiring (Red=5V, Black=GND, White=GPIO16, Green=GPIO17)
- Verify sensor is getting 5V power
- Try different baud rate in code (57600 or 9600)

### WiFi Connection Failed
- Verify SSID and password in code
- Check ESP32 is within WiFi range
- Ensure network allows new device connections

### Wake-on-LAN Not Working
- Enable WOL in PC BIOS settings
- Enable WOL in network adapter properties (Windows)
- Verify MAC address format (XX-XX-XX-XX-XX-XX)
- Ensure PC and ESP32 are on same network

### Database Errors
- Delete `attendance.db` and run `setup_db.py` again
- Check file permissions on database
- Verify SQLite3 is installed

---

## 📊 Excel Export Format

Downloaded CSV contains:
- Name
- Register Number
- Timestamp
- Status

File naming: `attendance_report_YYYYMMDD.csv`

---

## 🔐 Security Considerations

1. **Change default passwords** in production
2. Use HTTPS in production (not HTTP)
3. Implement password hashing (currently plain text)
4. Add session timeout
5. Implement fingerprint template encryption
6. Use environment variables for secrets

---

## 🛠️ Technical Implementation

### Architecture Overview
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   R307 Sensor   │────│   ESP32      │────│   Flask Server  │
│  (Fingerprint)  │    │ (WiFi/HTTP)  │    │   (Database)    │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │   Web Dashboard │
                                            │  (Management)   │
                                            └─────────────────┘
```

### Technology Stack
- **Backend**: Python 3.8+ with Flask framework
- **Database**: SQLite for data persistence
- **Hardware**: ESP32 microcontroller + R307 fingerprint sensor
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Network**: Wake-on-LAN protocol for PC automation
- **Communication**: HTTP REST API between ESP32 and server

### Key Components
1. **Fingerprint Management**: Enrollment, verification, and template storage
2. **User Management**: Role-based access control system
3. **Attendance Tracking**: Real-time logging and reporting
4. **PC Automation**: Wake-on-LAN signal broadcasting
5. **Web Interface**: Responsive dashboard for system management

---

## 👤 About the Author

**IMPRESEO** - Full Stack Developer & IoT Enthusiast

This project was developed to showcase skills in:
- Full-stack web development
- Embedded systems programming
- Hardware-software integration
- Database design and management
- Network protocol implementation

### Connect With Me
- **GitHub**: [github.com/IMPRESEO](https://github.com/IMPRESEO)
- **LinkedIn**: [linkedin.com/in/impreseo]
- **Email**: [contact@impreseo.com]
- **Portfolio**: [impreseo.dev]

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve this project:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow clean code principles
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

---

##  Project Resources

**Repository**: https://github.com/IMPRESEO/Lab-Attendance-System-with-WOL  
**Documentation**: Complete setup and usage guide  
**Hardware List**: All components with purchase links  
**API Reference**: REST API documentation  
**Video Tutorial**: Step-by-step implementation guide

---

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review ESP32 serial monitor output
3. Check Flask server console logs
4. Verify database integrity

---

## 🚀 Future Enhancements

- [ ] SMS/Email notifications
- [ ] Face recognition integration
- [ ] Mobile app for students
- [ ] Real-time dashboard with WebSockets
- [ ] RFID card backup system
- [ ] Attendance analytics and reports
- [ ] Multi-lab support
- [ ] Cloud database integration

---

**Built with ❤️ by Impreseo** 