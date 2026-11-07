# 🌾 Kisaan Mitra — React Web Application

Welcome to the frontend web application for **Kisaan Mitra** (Smart Farmer Assistant), migrated from a mobile React Native Expo app to a high-performance, beautifully styled React + TypeScript web application built on top of **Vite**.

---

## 🛠️ Technology Stack
* **Framework**: React 19 + TypeScript
* **Build System**: Vite 8 (extremely fast Hot Module Replacement)
* **Routing**: React Router DOM (protected & public routes)
* **API Handler**: Axios (pre-configured with JWT interceptors)
* **Styling**: Earthy & rich custom CSS design system tailored for farmers
* **Icons**: Lucide React

---

## 📁 Directory Structure
```text
frontend/
├── public/                 # Static assets
└── src/
    ├── components/         # Reusable layouts and visual components
    │   └── Layout.tsx      # Sidebar and responsive hamburger navigation
    ├── context/            # Global React Contexts
    │   └── AuthContext.tsx # Persistent login/session handling using localStorage
    ├── pages/              # Router Page views
    │   ├── LoginPage.tsx   # Secured login page
    │   ├── RegisterPage.tsx# Farmer registration page (with state/district selection)
    │   ├── DashboardPage.tsx# High-level stats, current weather, and movers
    │   ├── PricesPage.tsx  # Interactive Government Mandi prices search
    │   ├── WeatherPage.tsx # Location-based weather & personalized farming tips
    │   ├── NotificationsPage.tsx # Historical alert center
    │   ├── CropRecommendationPage.tsx # AI Crop Advisor input & recommendation results
    │   └── ProfilePage.tsx # Farmer account details and preference settings
    ├── services/           # Backend API connectors
    │   └── api.ts          # Central Axios configuration and endpoints
    ├── App.tsx             # Protected routing table
    ├── index.css           # Premium responsive grid & color system
    └── main.tsx            # App entry point
```

---

## 🚀 Running the Web Client

### 1. Install Dependencies
Run the following command in the `frontend` folder to download all required node modules:
```bash
npm install
```

### 2. Configure Backend Endpoint
By default, the web client communicates with the backend API running at:
`http://localhost:8000/api/v1`

If your backend is hosted elsewhere, you can configure the `BASE_URL` in [src/services/api.ts](file:///d:/clone%20projects/kisaan-mitra-final/frontend/src/services/api.ts).

### 3. Start Development Server
Spin up the hot-reloading development server locally:
```bash
npm run dev
```
The app will immediately be available at: **`http://localhost:5173/`**

---

## ✨ Key Features Implemented

1. **Responsive Dashboard**: Quick stats on tracked mandi items, current weather cards, and top market price movers today.
2. **Real-time Mandi Search**: Search and filter government crop prices by commodity, state, or market instantly.
3. **AI Crop Recommendation**: Input soil, water, state, district, and farming type to receive structured advice on best-matching commodities.
4. **Smart Weather & Tips**: Immediate warning updates if high rains or extreme temperatures threaten your district.
5. **Secure Authentication**: Fully encapsulated router preventing unauthorized access to farmer dashboards.
