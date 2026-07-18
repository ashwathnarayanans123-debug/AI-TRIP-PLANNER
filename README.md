# AI Trip Planner Agent

Premium AI-powered travel planning SaaS — React + FastAPI.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19, Vite, Tailwind, Framer Motion, Recharts, React Router, Axios |
| Backend | FastAPI, SQLAlchemy, SQLite, Pydantic, Uvicorn |
| AI | Groq (preferred) / OpenAI |
| Maps | Leaflet + OSM (Nominatim / Overpass) |
| Weather | OpenWeather |
| PDF | ReportLab |
| Deploy | Vercel (frontend) · Render (backend) |

## Project structure

```
backend/
  main.py
  database.py
  models.py
  schemas.py
  routers/
  services/
  utils/
  requirements.txt
frontend/
  src/
    components/
    pages/
    hooks/
    services/
  App.jsx / main.jsx (under src/)
  tailwind.config.js
```

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # or: cp .env.example .env
# Edit .env with your API keys (optional — app has demo fallbacks)

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env   # set VITE_API_URL=http://127.0.0.1:8000
npm run dev
```

App: http://localhost:5173

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/plan-trip` | Generate AI itinerary |
| POST | `/save-trip` | Persist trip |
| GET | `/history` | List / search trips |
| GET | `/trip/{id}` | Trip detail |
| PUT | `/trip/{id}` | Edit trip |
| DELETE | `/trip/{id}` | Delete trip |
| POST | `/trip/{id}/duplicate` | Clone trip |
| POST | `/trip/{id}/reuse` | Re-run AI planner |
| GET | `/trip/{id}/pdf` | Download PDF |
| GET | `/weather?city=` | Current + 5-day forecast |
| GET | `/places?destination=` | Hotels, restaurants, attractions |

## Environment variables

**Backend (`.env`)**

- `GROQ_API_KEY` — Groq LLM planning (preferred, free tier)
- `GROQ_MODEL` — default `llama-3.3-70b-versatile`
- `OPENAI_API_KEY` — optional OpenAI fallback (demo template if both missing)
- `OPENWEATHER_API_KEY` — optional; if invalid/missing, uses free Open-Meteo
- `CORS_ORIGINS` — comma-separated frontend URLs

Weather priority: OpenWeather (if key works) → Open-Meteo + Nominatim → demo fallback.

Maps: Leaflet + OSM tiles; places via Nominatim + Overpass (no Google key required).

## Deploy

### Frontend → Vercel

1. Import the `frontend` folder (or monorepo with root `frontend`).
2. Set `VITE_API_URL` to your Render API URL.
3. Set `VITE_GOOGLE_MAPS_API_KEY` if using Maps Embed.

### Backend → Render

1. Use `render.yaml` or create a Web Service with root `backend`.
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Set env vars from `.env.example` and add your Vercel origin to `CORS_ORIGINS`.

## Features

- Landing page with hero, features, testimonials
- Full trip planner form (budget, transport, hotel, interests)
- AI day-by-day itinerary (morning / afternoon / evening)
- Weather, Google Maps places, budget charts
- Trip history (search, edit, delete, duplicate, reuse)
- PDF export, dark mode, glassmorphism UI, toasts, skeletons
