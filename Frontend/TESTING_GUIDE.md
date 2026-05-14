# AgriCheck Frontend - Testing & Quick Start Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ or Bun
- Backend running at `http://127.0.0.1:8000`
- Firebase credentials configured

### 1. Install & Setup
```bash
# Navigate to frontend directory
cd "d:\uni client projects\frontend"

# Install dependencies
npm install

# Configure environment
# Edit .env with your API and Firebase credentials
```

### 2. Start Development Server
```bash
npm run dev
```
Frontend will be available at `http://localhost:5173`

### 3. Build for Production
```bash
npm run build
```
Output in `dist/` folder

---

## 🧪 Testing Guide

### Test 1: Sensor Dashboard
**Path:** `http://localhost:5173/dashboard` (requires login)

**What to verify:**
1. ✅ Dashboard loads with 7 sensor metric cards
2. ✅ Each metric shows current value and status
3. ✅ Soil health score is calculated (top card)
4. ✅ Data refreshes every 30 seconds
5. ✅ Colors indicate status: optimal (green), good (blue), high/low (orange/red)

**Expected Metrics:**
- Nitrogen: 200-250 is optimal
- Phosphorus: 20-30 is optimal
- Potassium: 150-200 is optimal
- pH: 6.0-7.0 is optimal
- Temperature: 20-30°C is optimal
- Humidity: 40-70% is optimal
- EC: 800-1500 µS/cm is optimal

**Error Cases:**
- If backend down: Should show error alert
- If no sensor data: Should show "no data available" message

---

### Test 2: Public Chat (Landing Page)
**Path:** `http://localhost:5173/` (no login needed)

**What to verify:**
1. ✅ Public chat component appears on page
2. ✅ Can type and send messages
3. ✅ Response comes from `/api/v1/chat/public`
4. ✅ Messages appear with timestamps
5. ✅ "Clear Chat" button works

**Test Queries:**
```
1. "What services does AgriCheck provide?"
   Expected: General info response, no login needed

2. "What is my nitrogen level?"
   Expected: "requires_login: true" response with prompt

3. "Hello"
   Expected: Greeting response from AI
```

---

### Test 3: Authenticated Chat (Floating Widget)
**Path:** After logging in, visible as floating button (bottom-right)

**What to verify:**
1. ✅ Floating chat button appears on all pages
2. ✅ Click opens/closes chat window
3. ✅ Chat persists across page navigation
4. ✅ Messages include timestamps
5. ✅ Advanced options panel works
6. ✅ Land size input accepted
7. ✅ Sensor data checkbox toggles

**Test Workflow:**
1. Click floating chat button
2. Type: "What fertilizer should I use?"
3. AI should respond with recommendations based on sensor data
4. Click "Show Options ▼"
5. Change land size to 5 acres
6. Toggle sensor data off/on
7. Send another message - should see different response
8. Click "Clear Chat" - history should reset

**Expected Features:**
- Session ID is generated and persists
- Includes latest sensor data if enabled
- Responses include agricultural advice
- Error messages if backend unavailable

---

### Test 4: Error Handling

**Scenario 1: Backend Down**
```bash
# Stop the backend server
# Try accessing dashboard or sending chat message
# Expected: Error alert "Failed to fetch sensor data"
```

**Scenario 2: Invalid Firebase Token**
```bash
# Clear localStorage
# Try accessing protected routes
# Expected: Redirect to login page
```

**Scenario 3: Malformed Response**
```bash
# Mock an error response from backend
# Expected: Graceful error message, app doesn't crash
```

---

## 📊 API Endpoints Reference

### Sensor Endpoints
```
GET http://127.0.0.1:8000/readings/latest
├─ Response: Single SensorReading object
├─ Status: 200 (success) | 404 (no data)
└─ Used by: Dashboard.tsx

GET http://127.0.0.1:8000/readings/history?limit=20
├─ Response: Array of SensorReading objects
├─ Status: 200 (success)
└─ Used by: Charts (not yet implemented)

POST http://127.0.0.1:8000/readings
├─ Body: { nitrogen, phosphorus, potassium, ph, temperature, humidity, ec }
├─ Response: SensorReading with id and timestamp
└─ Used by: Sensor upload (ESP32 integration)
```

### Chat Endpoints
```
POST http://127.0.0.1:8000/api/v1/chat/public
├─ Body: { message: string, language?: "en"|"ur"|"auto" }
├─ Response: { response, intent, requires_login, ... }
├─ Auth: NOT REQUIRED
└─ Used by: PublicChat.tsx

POST http://127.0.0.1:8000/chat
├─ Body: { message, session_id, land_size_acres, include_sensor_data }
├─ Response: { response, session_id, sensor_data_used, ... }
├─ Auth: REQUIRED (Firebase JWT in Authorization header)
└─ Used by: ChatAssistant.tsx
```

---

## 🔍 Troubleshooting

### Issue: "Cannot connect to backend"
**Solution:**
1. Ensure backend is running: `http://127.0.0.1:8000`
2. Check VITE_API_BASE_URL in `.env`
3. Verify CORS is enabled on backend
4. Check browser console for exact error

### Issue: "Firebase authentication failed"
**Solution:**
1. Verify Firebase credentials in `.env`
2. Check Firebase project exists and is active
3. Ensure credentials have correct permissions
4. Check `localStorage` for token: `firebaseToken`

### Issue: "Chat not receiving responses"
**Solution:**
1. Verify session ID is generated correctly
2. Check if user is authenticated (for private chat)
3. Examine network tab in DevTools
4. Check backend logs for errors

### Issue: "Sensor data not updating"
**Solution:**
1. Verify backend has sensor data: `/readings/latest`
2. Check refresh interval: 30 seconds (automatic)
3. Try manual refresh if needed
4. Verify ESP32 is sending data

---

## 📱 Mobile Testing

The frontend is fully responsive:

**Media Breakpoints:**
- Mobile: 320px - 640px
- Tablet: 641px - 1024px
- Desktop: 1025px+

**Test on mobile:**
1. Open `http://localhost:5173` on phone
2. Verify layout adjusts
3. Sensor cards stack vertically
4. Chat widget is accessible
5. Navigation works on smaller screens

---

## 🔧 Environment Variables

Required `.env` file:
```env
# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:8000

# Firebase Configuration
VITE_FIREBASE_API_KEY=your_key
VITE_FIREBASE_AUTH_DOMAIN=your_domain
VITE_FIREBASE_PROJECT_ID=your_project
VITE_FIREBASE_STORAGE_BUCKET=your_bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

---

## 📝 Code Organization

```
src/
├── components/
│   ├── ChatAssistant.tsx         ← Authenticated chat widget
│   ├── PublicChat.tsx            ← Public chat component
│   ├── DashboardLayout.tsx       ← Main app layout
│   └── ui/                       ← shadcn/ui components
├── pages/
│   ├── Dashboard.tsx             ← Sensor dashboard
│   ├── HomePage.tsx              ← Landing page
│   └── ...
├── services/
│   ├── api.ts                    ← Base HTTP client
│   ├── chatService.ts            ← Chat API functions
│   └── sensorService.ts          ← Sensor API functions
├── contexts/
│   ├── AuthContext.tsx           ← Firebase authentication
│   └── LanguageContext.tsx       ← i18n support
└── lib/
    ├── firebase.ts               ← Firebase initialization
    └── utils.ts                  ← Utility functions
```

---

## ✅ Checklist for Deployment

- [ ] All environment variables configured
- [ ] Backend API is accessible and running
- [ ] Firebase project is set up and credentials verified
- [ ] Build completes without errors (`npm run build`)
- [ ] No console errors in DevTools
- [ ] Sensor dashboard loads with real data
- [ ] Chat endpoints respond correctly
- [ ] Mobile view is responsive
- [ ] Error handling works (test with backend down)
- [ ] Performance is acceptable (check build size)

---

## 📞 Support

For issues or questions:
1. Check browser console (F12 → Console)
2. Check network tab (F12 → Network)
3. Check backend logs
4. Verify `.env` configuration
5. Ensure backend is running at correct URL

---

**Last Updated:** March 12, 2026  
**Version:** 1.0  
**Status:** ✅ Ready for Testing
