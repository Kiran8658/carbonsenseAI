# 🌿 CarbonSense AI

> AI-powered carbon footprint tracker for MSMEs — built for hackathons, production-ready architecture.

![Tech Stack](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-38bdf8?style=flat-square&logo=tailwindcss)
![Recharts](https://img.shields.io/badge/Recharts-2.12-22c55e?style=flat-square)

---

## 📋 Features

| Feature | Description |
|---|---|
| 🧮 Carbon Calculator | Electricity (0.82 kg/kWh) + Fuel (2.3 kg/litre) emissions |
| 📊 Emission Breakdown | Interactive pie chart by source |
| 📈 Trend Chart | 6-month historical area chart |
| 🤖 AI Recommendations | Mock suggestions (or real OpenAI/Gemini) |
| 🎛️ Emission Simulator | Before/after sliders for reduction planning |
| 🏆 Carbon Score | 0–100 score with animated ring |
| ⚡ Quick Presets | Small Shop / Mid Factory / Large MSME |

---

## 🗂️ Project Structure

```
carbonsense/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # App entry point + CORS
│   ├── routes/
│   │   ├── calculator.py       # POST /api/calculate, /api/simulate, GET /api/history
│   │   └── suggestions.py      # POST /api/ai-suggestions
│   ├── services/
│   │   ├── carbon_service.py   # Emission calculation logic
│   │   └── ai_service.py       # Mock + OpenAI/Gemini suggestions
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   ├── requirements.txt
│   ├── render.yaml             # Render deployment config
│   └── .env.example
│
└── frontend/                   # Next.js + TypeScript frontend
    ├── pages/
    │   ├── _app.tsx
    │   └── index.tsx           # Main dashboard page
    ├── components/
    │   ├── ui/
    │   │   ├── Navbar.tsx
    │   │   ├── MetricCard.tsx
    │   │   └── ScoreRing.tsx
    │   ├── charts/
    │   │   ├── PieBreakdown.tsx
    │   │   └── TrendChart.tsx
    │   └── dashboard/
    │       ├── InputForm.tsx
    │       ├── AISuggestions.tsx
    │       └── Simulator.tsx
    ├── lib/
    │   ├── api.ts              # Axios API calls
    │   └── types.ts            # TypeScript interfaces
    ├── styles/
    │   └── globals.css         # Dark theme + custom CSS
    ├── package.json
    ├── tailwind.config.js
    ├── vercel.json
    └── .env.local.example
```

---

## 🚀 Quick Start (Local Dev)

### Prerequisites
- Python 3.10+
- Node.js 18+

---

### 1. Backend Setup

```bash
cd carbonsense/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment (optional — works without API keys using mock AI)
cp .env.example .env
# Edit .env if you have OpenAI or Gemini keys

# Start the server
uvicorn main:app --reload --port 8000
```

Backend runs at: **http://localhost:8000**
API Docs (Swagger): **http://localhost:8000/docs**

---

### 2. Frontend Setup

```bash
cd carbonsense/frontend

# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local
# Default points to http://localhost:8000 — no changes needed for local dev

# Start development server
npm run dev
```

Frontend runs at: **http://localhost:3000**

---

## 🔌 API Reference

### `POST /api/calculate`
Calculate carbon emissions.

**Request:**
```json
{
  "electricity_kwh": 500,
  "fuel_litres": 100
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "electricity_co2": 410.0,
    "fuel_co2": 230.0,
    "total_co2": 640.0,
    "carbon_score": "Average",
    "carbon_score_value": 50,
    "breakdown_percentage": {
      "electricity": 64.1,
      "fuel": 35.9
    }
  },
  "message": "Carbon footprint calculated: 640.0 kg CO₂"
}
```

---

### `POST /api/ai-suggestions`
Get AI reduction recommendations.

**Request:**
```json
{
  "electricity_kwh": 500,
  "fuel_litres": 100,
  "total_co2": 640.0,
  "business_type": "MSME"
}
```

**Response:**
```json
{
  "success": true,
  "suggestions": [...],
  "summary": "Based on your 640 kg CO₂...",
  "estimated_reduction": 45.0
}
```

---

### `POST /api/simulate`
Simulate reduction impact.

**Request:**
```json
{
  "electricity_kwh": 500,
  "fuel_litres": 100,
  "electricity_reduction_pct": 20,
  "fuel_reduction_pct": 30
}
```

**Response:**
```json
{
  "before_co2": 640.0,
  "after_co2": 489.4,
  "savings_co2": 150.6,
  "savings_percentage": 23.5,
  ...
}
```

---

### `GET /api/history`
Returns 6 months of mock historical data for trend charts.

---

## 🤖 AI Integration

The project works **out of the box with mock AI** — no API key needed.

To use real AI:

**OpenAI:**
```env
OPENAI_API_KEY=sk-...
```

**Gemini:**
```env
GEMINI_API_KEY=AIza...
```

The service automatically detects which key is set and falls back to mock if the API call fails.

---

## 📦 Deployment

### Backend → Render

1. Push `backend/` to a GitHub repo
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your repo
4. Render auto-detects `render.yaml`
5. Set env vars `OPENAI_API_KEY` / `GEMINI_API_KEY` in Render dashboard (optional)

### Frontend → Vercel

1. Push `frontend/` to a GitHub repo
2. Import on [vercel.com](https://vercel.com)
3. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL = https://your-carbonsense-api.onrender.com
   ```
4. Deploy!

---

## 🧮 Emission Factors

| Source | Factor | Reference |
|---|---|---|
| Electricity | 0.82 kg CO₂/kWh | India grid average (CEA 2023) |
| Diesel fuel | 2.3 kg CO₂/litre | IPCC / MoEFCC India |

---

## 🏆 Carbon Score Logic

| Score | Range | Value |
|---|---|---|
| Excellent | ≤ 100 kg/mo | 90/100 |
| Good | 101–300 kg/mo | 70/100 |
| Average | 301–600 kg/mo | 50/100 |
| Poor | 601–1000 kg/mo | 30/100 |
| Critical | > 1000 kg/mo | 10/100 |

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Pydantic v2, Uvicorn, httpx |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Charts | Recharts (AreaChart, PieChart) |
| Fonts | Syne (display) + DM Sans (body) + DM Mono |
| AI | Mock suggestions / OpenAI GPT-3.5 / Gemini Pro |
| Deploy | Render (API) + Vercel (UI) |

---

## 📄 License

MIT — free to use for hackathons and commercial projects.

---

*Built with 💚 for a greener planet*
