# 🌾 Kisaan Mitra — Smart Farmer Assistant

> A production-ready mobile application that helps Indian farmers get **real-time mandi prices** and **instant price alerts** when crop prices change significantly.

![Platform](https://img.shields.io/badge/Platform-Android-green)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Database](https://img.shields.io/badge/Database-MongoDB-47A248)
![Language](https://img.shields.io/badge/Language-English%20%7C%20ಕನ್ನಡ-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## 📱 App Features

- 🌾 **Real-time Mandi Prices** — Live crop prices from Government of India's AgMarket API (data.gov.in)
- 🔔 **Smart Price Alerts** — Push notifications when prices change
- 📊 **Intelligent Alert System**:
  - Normal update → Push notification only
  - ≥10% price change → Push + SMS alert
  - ≥15% price change OR 7-day high → Critical alert
- 🗣️ **Bilingual Support** — English and Kannada (ಕನ್ನಡ)
- 👨‍🌾 **Farmer-friendly UI** — Large text, high contrast, simple navigation
- 📜 **Notification History** — View all past price alerts
- 🌱 **Crop Management** — Select and manage crops to track

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React Native (Expo) + TypeScript |
| Backend | FastAPI (Python) |
| Database | MongoDB Atlas |
| Push Notifications | Expo Push API + Firebase |
| SMS Alerts | Fast2SMS API |
| Price Data | AgMarket API (data.gov.in) |
| Scheduler | APScheduler (every 30 mins) |
| Authentication | JWT tokens |

---

## 📁 Project Structure

```
kisaan-mitra/
├── backend/                         # FastAPI Python backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py              # Register & Login
│   │   │   ├── prices.py            # Mandi price endpoints
│   │   │   ├── notifications.py     # Alert history
│   │   │   └── users.py             # User preferences
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic models
│   │   ├── services/
│   │   │   ├── agmarket_service.py  # data.gov.in API
│   │   │   ├── alert_engine.py      # Price alert logic
│   │   │   ├── firebase_service.py  # Push notifications
│   │   │   └── sms_service.py       # SMS integration
│   │   ├── scheduler/
│   │   │   └── price_scheduler.py   # Background price fetcher
│   │   ├── utils/
│   │   │   └── database.py          # MongoDB connection
│   │   ├── config.py                # Environment settings
│   │   └── main.py                  # App entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── test_pipeline.py             # System test script
│
└── frontend/                        # React Native Expo app
    ├── src/
    │   ├── screens/
    │   │   ├── SplashScreen.tsx
    │   │   ├── LoginScreen.tsx
    │   │   ├── RegisterScreen.tsx
    │   │   ├── HomeScreen.tsx
    │   │   ├── CropSelectionScreen.tsx
    │   │   ├── NotificationsScreen.tsx
    │   │   └── ProfileScreen.tsx
    │   ├── services/
    │   │   ├── api.ts               # Axios API calls
    │   │   └── AuthContext.tsx      # Auth state
    │   └── utils/
    │       ├── theme.ts             # Design system
    │       └── translations.ts      # EN + KN strings
    ├── assets/                      # Icons & splash screen
    ├── app.json                     # Expo config
    └── eas.json                     # EAS Build config
```

---

## 🚀 Setup Guide

### Prerequisites

- [Node.js](https://nodejs.org) v18+
- [Python](https://python.org) v3.10+
- [MongoDB Atlas](https://cloud.mongodb.com) account (free)
- [Expo CLI](https://docs.expo.dev)
- [Git](https://git-scm.com)

---

### Step 1 — Clone Repository

```bash
git clone https://github.com/your-username/kisaan-mitra.git
cd kisaan-mitra
```

---

### Step 2 — Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3 — Environment Variables

Create `.env` file inside `backend/` folder:

```env
# App
DEBUG=false
SECRET_KEY=your-secret-key-here

# MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/kisaan_mitra
MONGODB_DB_NAME=kisaan_mitra

# Firebase (Push Notifications)
FIREBASE_CREDENTIALS_PATH=firebase.json

# Fast2SMS (SMS Alerts)
FAST2SMS_API_KEY=your-fast2sms-api-key
FAST2SMS_SENDER_ID=FSTSMS

# AgMarket API (data.gov.in)
AGMARKET_API_KEY=your-agmarket-api-key
AGMARKET_BASE_URL=https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070

# Alert Thresholds
BIG_JUMP_THRESHOLD=0.10
CRITICAL_THRESHOLD=0.15
INACTIVE_DAYS_THRESHOLD=3

# Scheduler
PRICE_FETCH_INTERVAL_MINUTES=30
```

---

### Step 4 — Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Save the downloaded file as `firebase.json` inside `backend/` folder

---

### Step 5 — AgMarket API Key

1. Go to [data.gov.in](https://data.gov.in/user/register)
2. Register free account
3. Go to **My Account** → **API Keys**
4. Copy your API key
5. Add it to `.env` as `AGMARKET_API_KEY`

---

### Step 6 — Start Backend

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

---

# npx ngrok http 8000

### Step 7 — Frontend Setup

```bash
cd frontend
npm install
npx expo install expo-notifications
```

---

### Step 8 — Update API URL

Open `frontend/src/services/api.ts` and update:

```typescript
// For local development
const BASE_URL = 'http://YOUR_PC_IP:8000/api/v1';

// Find your IP by running: ipconfig (Windows) or ifconfig (Mac/Linux)
// Example: http://192.168.1.105:8000/api/v1
```

> ⚠️ Your phone and PC must be on the **same WiFi network**

---

### Step 9 — Start Frontend

```bash
cd frontend
npx expo start
```

Scan the QR code with Expo Go app on your phone.

---

### Step 10 — Test the System

```bash
cd backend
python test_pipeline.py
```

Expected output:
```
✅ MongoDB connected
✅ AgMarket API working
✅ Prices stored in DB
✅ FCM token set
✅ Push notification sent
✅ Notification saved
```

---

## 📱 Build APK (Android)

To build a real APK for Android:

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
npx eas login

# Initialize project
npx eas init

# Build APK
npx eas build --platform android --profile preview
```

Download and install the APK on your Android phone.

---

## 🔑 API Keys Required

| Service | Purpose | Get it at |
|---------|---------|-----------|
| MongoDB Atlas | Database | [cloud.mongodb.com](https://cloud.mongodb.com) |
| data.gov.in | Mandi prices | [data.gov.in](https://data.gov.in/user/register) |
| Firebase | Push notifications | [console.firebase.google.com](https://console.firebase.google.com) |
| Fast2SMS | SMS alerts | [fast2sms.com](https://fast2sms.com) |
| Expo | App build | [expo.dev](https://expo.dev) |

---

## 🌾 How It Works

```
┌─────────────────────────────────────────────────────┐
│                    SYSTEM FLOW                       │
│                                                      │
│  data.gov.in API                                     │
│       ↓ (every 30 mins)                              │
│  Price Scheduler ──→ MongoDB (prices collection)     │
│       ↓                                              │
│  Alert Engine                                        │
│       ↓ checks price change %                        │
│  ┌────────────────────────────┐                      │
│  │ < 10%  → Push notification │                      │
│  │ ≥ 10%  → Push + SMS        │                      │
│  │ ≥ 15%  → Critical Push+SMS │                      │
│  └────────────────────────────┘                      │
│       ↓                                              │
│  Firebase (Push) + Fast2SMS (SMS)                    │
│       ↓                                              │
│  Farmer's Phone 📱                                   │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Troubleshooting

**App can't connect to backend:**
- Check your PC IP with `ipconfig`
- Update `BASE_URL` in `api.ts`
- Make sure phone and PC are on same WiFi
- Run backend with `--host 0.0.0.0`

**No prices showing:**
- Check `AGMARKET_API_KEY` in `.env`
- Test API: `python test_pipeline.py`
- AgMarket API may be slow — try again

**Push notifications not working:**
- Make sure FCM token is set (check test_pipeline output)
- Re-login in app to refresh FCM token
- Check Firebase credentials file exists

**SMS not working:**
- Fast2SMS requires DLT registration for India
- DLT registration takes 3-7 days
- Push notifications work without SMS

---

## 👨‍🌾 Developer & Team

**Kisaan Mitra Development Team**
- Project: Kisaan Mitra — Smart Farmer Assistant with AI Advisory & Email OTP Auth

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

- [data.gov.in](https://data.gov.in) — Government of India Open Data Platform
- [Expo](https://expo.dev) — React Native development platform
- [FastAPI](https://fastapi.tiangolo.com) — Modern Python web framework
- [MongoDB Atlas](https://cloud.mongodb.com) — Cloud database
- [Firebase](https://firebase.google.com) — Push notification service

---

> Built with ❤️ for Indian Farmers 🇮🇳🌾