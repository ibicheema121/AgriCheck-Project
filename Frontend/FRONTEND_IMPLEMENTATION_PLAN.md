# AgriCheck React Frontend - Implementation Plan

## 📋 Backend Overview

Your FastAPI backend is a sophisticated agricultural AI system with these core features:

### Server Status
- **URL**: `http://127.0.0.1:8000`
- **Framework**: FastAPI with CORS enabled (allows localhost:3000, 5173, 8080, and *)
- **Database**: SQLite (agricheck.db)
- **AI Model**: Azure OpenAI (gpt-4)
- **Speech Services**: Azure Cognitive Services (Speech-to-Text & Text-to-Speech)

---

## 🌱 Core Features & Endpoints

### 1️⃣ **Sensor Data Management** (`/readings`)

#### POST `/readings/`
**Upload ESP32 Sensor Data**
```json
{
  "nitrogen": 250,
  "phosphorus": 25,
  "potassium": 180,
  "ph": 6.8,
  "temperature": 28.5,
  "humidity": 65,
  "ec": 1200
}
```
**Response:**
```json
{
  "id": 1,
  "nitrogen": 250,
  "phosphorus": 25,
  "potassium": 180,
  "ph": 6.8,
  "temperature": 28.5,
  "humidity": 65,
  "ec": 1200,
  "timestamp": "2026-03-12T10:30:00"
}
```

#### GET `/readings/latest`
**Get Most Recent Sensor Reading**
- No parameters needed
- Returns latest single reading (same schema as above)
- Use Case: Dashboard display

#### GET `/readings/history?limit=20`
**Get Historical Readings**
- `limit`: Number of readings (default: 20, max recommended: 100)
- Returns array of sensor readings
- Use Case: Charts/graphs over time

---

### 2️⃣ **AI Agricultural Advisor - Authenticated Chat** (`/chat`)

#### POST `/chat/`
**Chat with Dr. AgriBot (Requires Latest Sensor Data)**

**Request:**
```json
{
  "message": "What fertilizer should I use?",
  "session_id": "uuid-here",           // Optional, auto-generated if not provided
  "land_size_acres": 2.5,              // Optional, default: 1.0
  "include_sensor_data": true          // Optional, default: true
}
```

**Response:**
```json
{
  "response": "📊 SOIL STATUS:\n• Nitrogen: 250 mg/kg - Good...",
  "session_id": "uuid-here",
  "sensor_data_used": {
    "nitrogen": 250,
    "phosphorus": 25,
    "potassium": 180,
    "ph": 6.8,
    "temperature": 28.5,
    "humidity": 65,
    "ec": 1200
  },
  "timestamp": "2026-03-12T10:30:00",
  "recommendations": null
}
```

**Key Features:**
- ✅ Bilingual: English & Urdu
- ✅ Persistent session memory (LangGraph)
- ✅ Sensor data integration
- ✅ Land size consideration
- ✅ Auto-generated session IDs
- ✅ Formatted recommendations with emojis

**AI Capabilities:**
- Fertilizer recommendations (type + dosage)
- Watering schedules
- pH management advice
- Crop-specific nutrients
- Sensor error detection
- Greeting/farewell handling

---

### 3️⃣ **Public Chat - Dashboard LLM Button** (`/api/v1/chat`)

#### POST `/api/v1/chat/public`
**No Auth Required - Dashboard Button**

**Request:**
```json
{
  "message": "What services does AgriCheck provide?",
  "language": "en"  // or "ur" for Urdu, default: "auto"
}
```

**Response:**
```json
{
  "response": "AgriCheck helps you monitor soil health...",
  "intent": "GENERAL_INFO",           // or "DETAIL_REQUIRED" or "OFF_TOPIC"
  "requires_login": false,
  "show_features": true,
  "agricheck_features": "🌱 AgriCheck helps you monitor soil health...",
  "endpoint_info": {
    "public_endpoint": "POST /api/v1/chat/public",
    "private_endpoint": "POST /api/v1/chat/private",
    "auth_required_for_private": true,
    "auth_type": "Firebase JWT Token"
  }
}
```

**Intent Classification:**
| Intent | Example | Response | Action |
|--------|---------|----------|--------|
| `GENERAL_INFO` | "How does AgriCheck work?" | Feature explanation | Show features |
| `DETAIL_REQUIRED` | "What's my soil's N level?" | Login required message | Redirect to auth |
| `OFF_TOPIC` | "Tell me a joke" | Not our domain | Redirect to auth |

---

### 4️⃣ **Voice-to-Voice AI Advisor** (WebSocket - Currently Commented)
Located in `/voice` router - Features real-time speech recognition and synthesis via Azure.
**Protocol:**
- Client sends: Raw audio chunks (16kHz, 16-bit, mono PCM)
- Server responds: Transcription + AI response + Audio chunks
- Auto-muting during playback

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend App                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Dashboard   │  │ Chat Widget  │  │ Sensor Panel │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  API Service    │
                    │ (Axios/Fetch)   │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │ /readings   │ │ /chat       │ │ /api/v1/chat│
    │ Sensor Data │ │ Advisor     │ │ Public Chat │
    └─────────────┘ └─────────────┘ └─────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                    ┌────────▼────────┐
                    │  FastAPI Backend│
                    │  + Azure OpenAI │
                    │  + Azure Speech │
                    └─────────────────┘
```

---

## 📦 Implementation Phases

### Phase 1: Core Sensor Dashboard (Week 1)
**Components to build:**
- [ ] Sensor data display (latest readings)
- [ ] Real-time gauge charts (NPK, pH, EC, Temp, Humidity)
- [ ] Historical chart (7-day, 30-day views)
- [ ] API integration for `/readings/latest` and `/readings/history`

**Dependencies:**
- `axios` or `fetch` API
- Chart library: `recharts`, `chart.js`, or `plotly.js`
- State management: `useState`, `useEffect`

**Key Metrics to Display:**
```
Nitrogen (N):     0-300 mg/kg   (🟢 Good: 200-250)
Phosphorus (P):   0-50 mg/kg    (🟢 Good: 20-30)
Potassium (K):    0-300 mg/kg   (🟢 Good: 150-200)
pH Level:         4.0-8.5       (🟢 Good: 6.0-7.0)
Temperature:      0-50°C        (🟢 Good: 20-30°C)
Humidity:         0-100%        (🟢 Good: 40-70%)
EC (Salinity):    0-2000 µS/cm  (🟢 Good: 800-1500)
```

---

### Phase 2: Public Chat (Week 2)
**Components to build:**
- [ ] Chat interface (message bubble UI)
- [ ] Public chat endpoint integration (`/api/v1/chat/public`)
- [ ] Intent-based routing (show features or redirect to login)
- [ ] Message history UI
- [ ] Loading states

**User Flow:**
1. User types message on landing page
2. Frontend calls `/api/v1/chat/public`
3. Check `requires_login` flag
4. If true: Show "You need to login" + Redirect to Auth
5. If false: Show AI response + Features

---

### Phase 3: Authenticated Chat (Week 3)
**Components to build:**
- [ ] Authentication system (Firebase or custom JWT)
- [ ] Persistent session management
- [ ] Chat window (persisting across page reloads)
- [ ] ChatRequest form with advanced options
- [ ] Sensor data selector (which sensors to include)
- [ ] Land size input field
- [ ] Session history

**State to Manage:**
```javascript
{
  sessionId: "uuid",
  messages: [
    { id: 1, role: "user", text: "What fertilizer?", timestamp },
    { id: 2, role: "assistant", text: "📊 Soil status...", timestamp }
  ],
  landSize: 2.5,
  includeSensorData: true,
  isLoading: false,
  sensorDataUsed: { n, p, k, ph, ... }
}
```

---

### Phase 4: Voice Chat (Week 4) - *Optional/Advanced*
**Components to build:**
- [ ] WebSocket connection handler
- [ ] Microphone permission handler
- [ ] Real-time audio recording
- [ ] Audio chunks streaming
- [ ] Playback control
- [ ] Visual feedback (listening/speaking/processing states)

**WebSocket Protocol:**
```
Client → Server: Raw PCM audio chunks
Server → Client: {type: "transcription", text: "..."}
Server → Client: {type: "ai_response", text: "..."}
Server → Client: {type: "audio_chunk", data: "base64..."}
Server → Client: {type: "mute_mic"}
Server → Client: {type: "completed"}
```

---

## 🔧 Frontend API Service Layer

### Recommended Structure

```typescript
// api/sensorService.ts
export const sensorService = {
  getLatest: () => GET('/readings/latest'),
  getHistory: (limit = 20) => GET(`/readings/history?limit=${limit}`),
  uploadReading: (data) => POST('/readings', data)
};

// api/chatService.ts
export const chatService = {
  publicChat: (message, language = 'auto') => 
    POST('/api/v1/chat/public', { message, language }),
  
  advisorChat: (message, sessionId, landSize, includeSensor) =>
    POST('/chat', { message, session_id: sessionId, land_size_acres: landSize, include_sensor_data: includeSensor })
};

// api/voiceService.ts (for WebSocket)
export const voiceService = {
  connectVoice: () => WebSocket('ws://localhost:8000/voice/ws/voice-advisor')
};
```

### Error Handling
```typescript
const handleApiError = (error) => {
  if (error.response?.status === 404) {
    // No sensor data available
    return "Please upload sensor data first";
  }
  if (error.response?.status === 500) {
    // Server error (likely Azure OpenAI issue)
    return "AI service temporarily unavailable";
  }
  return error.message;
};
```

---

## 🎨 UI Components Checklist

### Dashboard Page
- [ ] Header (Logo, Navigation, User Profile)
- [ ] Sensor Status Cards (7 cards for NPK, pH, EC, Temp, Humidity)
- [ ] Sensor Gauge Charts (Real-time visual feedback)
- [ ] Historical Chart (Line graph over time)
- [ ] Refresh button
- [ ] Date range selector

### Chat Page
- [ ] Chat message container
- [ ] Message input form
- [ ] Advanced options (Land size, Include sensor data)
- [ ] Session switch dropdown
- [ ] Clear history button
- [ ] Session metadata display

### Landing/Public Page
- [ ] Public chat widget
- [ ] Features showcase
- [ ] Login/Signup CTA
- [ ] Testimonials

### Settings Page
- [ ] Sensor configuration
- [ ] Default land size
- [ ] Language preference
- [ ] Session management

---

## 🔐 Authentication Flow (Assuming Firebase)

```
1. User lands on app
│
├─ Already logged in? → Go to Dashboard
│
└─ Not logged in? → Landing page with public chat
    │
    ├─ Clicks "Ask AI" → /api/v1/chat/public (no auth)
    │   └─ Response says "requires_login: true"
    │   └─ Show login modal
    │
    └─ Clicks "Login/Signup"
        └─ Firebase Auth UI
        └─ Get JWT token
        └─ Store in localStorage or sessionStorage
        └─ Redirect to Dashboard
        └─ Now can use /chat endpoint with sensor data
```

---

## 📝 Environmental Variables (Frontend)

```env
# .env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
REACT_APP_FIREBASE_API_KEY=xxx
REACT_APP_FIREBASE_AUTH_DOMAIN=xxx.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=xxx
```

---

## 🚀 Implementation Priority

**P1 - Must Have (MVP):**
- ✅ Sensor dashboard with latest reading
- ✅ Historical sensor data chart
- ✅ Public chat on landing page
- ✅ Authenticated chat interface
- ✅ Session management

**P2 - Should Have (v1.1):**
- ⚠️ Advanced chat options (land size, sensor selection)
- ⚠️ Session history persistence
- ⚠️ Multi-language support
- ⚠️ Real-time sensor updates (polling or WebSocket)

**P3 - Nice to Have (v2.0):**
- ⚠️ Voice chat WebSocket
- ⚠️ Sensor data export (CSV, PDF)
- ⚠️ Crop calendar/guides
- ⚠️ Community forum
- ⚠️ Mobile app

---

## 📊 Data Flow Examples

### Example 1: Check Soil & Get Advice
```
Frontend                          Backend
   │                               │
   ├─ GET /readings/latest ────────┤
   │                    ┌──────────┘
   │                    │ Latest: N=250, P=25, K=180, pH=6.8
   │         Response ──┤
   │         ◄──────────┤
   │                    │
   │ User clicks "Ask AI": "My plants look weak"
   │                    │
   ├─ POST /chat ──────┤
   │   (session_id, message, include_sensor_data=true)
   │                    │
   │         ┌─────────→│
   │         │ Calls Azure OpenAI with sensor data
   │         │ "N=250 (Good), but P=25 (Low). Use DAP fertilizer"
   │         │
   │  Response ◄────────┤
   │         │ "📦 FERTILIZER: DAP: 10kg for 1 acre"
   │         │
   │         └─ Display message in chat UI
```

### Example 2: Public Chat Flow
```
Landing Page User (Not Logged In)
   │
   ├─ Types: "How does AgriCheck work?"
   │
   ├─ POST /api/v1/chat/public
   │   (message="How does AgriCheck work?")
   │
   ├─ Response:
   │   {
   │     intent: "GENERAL_INFO",
   │     requires_login: false,
   │     response: "🌱 AgriCheck monitors your soil's NPK, pH, EC..."
   │   }
   │
   ├─ Shows AI response + Features list
   └─ No login required

Different User Types:
   ├─ Types: "What's my NPK level?"
   │  └─ Response has requires_login=true → Show login CTA
   │
   ├─ Types: "Tell me a joke"
   │  └─ Response has intent="OFF_TOPIC" → Show features + login CTA
```

---

## 🐛 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| CORS error | Backend not allowing frontend origin | Check CORS_ORIGINS in config.py (already set to allow localhost) |
| 404 on `/readings/latest` | No sensor data in DB | POST to `/readings` first with test data |
| AI response is slow | Azure OpenAI API latency | Show loading spinner for 5-10 seconds |
| WebSocket fails | Browser security | Ensure wss:// for production (use secure WebSocket) |
| Session data lost | Using new session each time | Store sessionId in localStorage |
| Language mixing in response | Urdu text detected as English | AI handles this, but test with pure Urdu text |

---

## 📱 Sample Component Usage

### React Hook for Sensor Data
```typescript
function useSensorData() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const lat = await sensorService.getLatest();
        const hist = await sensorService.getHistory(20);
        setLatest(lat);
        setHistory(hist);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    })();
  }, []);

  return { latest, history, loading };
}
```

### Chat Component
```typescript
function ChatAdvisor({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const handleSend = async () => {
    const res = await chatService.advisorChat(
      input, 
      sessionId, 
      2.5, 
      true
    );
    setMessages([...messages, 
      { role: 'user', text: input },
      { role: 'assistant', text: res.response }
    ]);
    setInput('');
  };

  return (
    <div>
      {messages.map(m => <Message role={m.role} text={m.text} />)}
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}
```

---

## ✅ Testing Checklist

**Manual Testing:**
- [ ] POST sensor data via Postman/curl
- [ ] GET `/readings/latest` returns correct data
- [ ] GET `/readings/history?limit=5` returns array
- [ ] POST `/chat` with message returns AI response
- [ ] POST `/api/v1/chat/public` returns intent correctly
- [ ] Session ID persists across multiple requests
- [ ] Urdu responses are pure Urdu (not Hinglish)
- [ ] CORS headers present in responses

**Frontend Testing:**
- [ ] Charts render correctly with sample data
- [ ] Chat messages display in correct format
- [ ] Loading states show while API calls pending
- [ ] Error messages display on API failure
- [ ] Session switching works
- [ ] Responsive design on mobile

---

## 📞 Backend Endpoints Summary

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/` | ✅ | Health check |
| POST | `/readings/` | ✅ | Submit sensor data |
| GET | `/readings/latest` | ✅ | Latest reading |
| GET | `/readings/history` | ✅ | Historical readings |
| POST | `/chat/` | ✅ | Chat with AI advisor |
| POST | `/api/v1/chat/public` | ❌ | Public chat (no login) |
| WS | `/voice/ws/voice-advisor` | ✅ | Voice chat (WebSocket) |

---

## 🎯 Next Steps

1. **Set up base API service** with axios/fetch
2. **Create sensor dashboard component** with charts
3. **Implement public chat** on landing page
4. **Add Firebase authentication**
5. **Build authenticated chat** interface
6. **Test entire flow** with real sensor data
7. **Deploy frontend** to Vercel/Netlify
8. **Connect to production backend** (update API_URL)

---

## 📚 Useful Libraries

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0",
    "firebase": "^10.0.0",
    "zustand": "^4.4.0",
    "react-router-dom": "^6.0.0",
    "tailwindcss": "^3.3.0",
    "react-icons": "^4.12.0"
  }
}
```

---

**Last Updated:** March 12, 2026  
**Backend Version:** 2.0.0  
**Status:** Running on http://127.0.0.1:8000 ✅
