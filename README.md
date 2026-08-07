# Weather Explorer - Weather Data FastAPI Backend & React Dashboard

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.1-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Google Cloud Storage](https://img.shields.io/badge/Google_Cloud_Storage-Storage-4285F4.svg?style=flat&logo=google-cloud&logoColor=white)](https://cloud.google.com/storage)
[![pytest](https://img.shields.io/badge/Pytest-Passed-success.svg?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org/)

Production-ready full-stack application combining a **FastAPI backend** (Open-Meteo API integration + Google Cloud Storage/local storage, `slowapi` rate limiting, structured logging) with a **React + Vite + Tailwind CSS + Recharts** interactive analytics dashboard.

---

## 🌟 Project Overview

**Weather Explorer** empowers developers and analysts to query historical daily weather datasets worldwide via Open-Meteo's API, enforce strict input validation, persist the structured JSON payloads into Google Cloud Storage or local filesystem, and analyze temperature trends using an interactive dashboard.

### Core Capabilities:
- **FastAPI Backend**: Asynchronous HTTP client (`httpx`), modular architecture, Pydantic input/output schemas with 31-day range limit enforcement, and rate-limiting using `slowapi`.
- **Google Cloud Storage Integration**: Flexible storage supporting Google Cloud Storage for production and local filesystem for development.
- **Structured Logging & Tracing**: Every request is assigned a unique `X-Request-ID` UUID, tracking process duration in milliseconds and logging key events.
- **React Analytics Dashboard**: React 19, Vite, Tailwind CSS, Recharts temperature trend lines (°C and °F modes), searchable file browser, paginated data tables with CSV export, and persistent Dark Mode.
- **Comprehensive Unit & Integration Test Suite**: Built with `pytest` and FastAPI `TestClient`, featuring 100% mocked external API calls and storage operations.

---

## 🏗️ Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT / BROWSER                                  |
|                 React 19 + Vite + Tailwind CSS + Recharts Dashboard               |
+-----------------------------------------------------------------------------------+
                                          |
                              Axios HTTP Requests (JSON)
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND                                    |
|                                                                                   |
|  [ Middleware: X-Request-ID Tracing & SlowAPI Rate Limiting ]                    |
|                                                                                   |
|  +---------------------------+       +-----------------------------------------+  |
|  |     Weather APIRouter     | ----> |           WeatherService                |  |
|  |  POST /store-weather-data |       | - Coordinates & Date Range Validation   |  |
|  |  GET  /list-weather-files |       | - Async HTTP Request via httpx          |  |
|  |  GET  /weather-file-content|       +-----------------------------------------+  |
|  +---------------------------+                            |                       |
|                                                           v                       |
|                                      +-----------------------------------------+  |
|                                      |            StorageService               |  |
|                                      | - Google Cloud Storage / Local Storage  |  |
|                                      | - Automatic Fallback Mode               |  |
|                                      +-----------------------------------------+  |
+-----------------------------------------------------------------------------------+
                       |                                         |
                       v                                         v
+-------------------------------------------+   +-----------------------------------+
|      Open-Meteo Historical API            |   |    Google Cloud Storage / Local   |
| (https://archive-api.open-meteo.com/v1)   |   |           Filesystem               |
+-------------------------------------------+   +-----------------------------------+
```

---

## 💻 Tech Stack

### Backend:
- **Framework**: FastAPI (Python 3.12 for deployment)
- **ASGI Server**: Uvicorn
- **Storage**: Google Cloud Storage / Local Filesystem
- **Async HTTP Client**: `httpx`
- **Rate Limiting**: `slowapi`
- **Validation**: Pydantic v2 & `pydantic-settings`
- **Testing**: `pytest`, `pytest-asyncio`, `starlette.testclient`

### Frontend:
- **UI Library**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS, Lucide Icons
- **HTTP Client**: Axios
- **Charts**: Recharts
- **State Management**: Custom React Hooks (`useWeatherData`)

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
# Storage Configuration
STORAGE_TYPE=local
GCS_BUCKET=weather-data-bucket
LOCAL_STORAGE_DIR=./data

# Open-Meteo API Base URL
OPEN_METEO_BASE_URL=https://archive-api.open-meteo.com/v1/archive

# Rate Limiting Configuration (slowapi)
RATE_LIMIT_STORE=10/minute
RATE_LIMIT_LIST=60/minute
RATE_LIMIT_CONTENT=60/minute

# Logging Level
LOG_LEVEL=INFO
```

For the frontend, create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

> **Note on Storage Configuration**: The backend supports both Google Cloud Storage (production) and local filesystem (development). Set `STORAGE_TYPE=gcs` for Google Cloud Storage or `STORAGE_TYPE=local` for local filesystem. If GCS credentials are not configured, the backend seamlessly falls back to local storage.

---

## 🚀 Local Development

### Backend Setup (Python 3.12 for Docker, Python 3.14 local)

**Important**: For local development with Python 3.14, use Docker. The backend is configured for Python 3.12 in Docker for deployment compatibility.

```bash
# Using Docker Compose (Recommended)
docker compose up --build
```

Backend runs on: http://localhost:8000

**Alternative**: If you have Python 3.12, you can run locally:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (Python 3.12)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload
```

### Frontend Setup (Node.js LTS 22+)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: http://localhost:5173

---

## 🐳 Docker Setup

### Using Docker Compose (Recommended)

```bash
# Build and start both backend and frontend
docker compose up --build
```

This will start:
- Backend on http://localhost:8000
- Frontend on http://localhost:5173

### Backend Only (Docker)

```bash
# Build backend image
docker build -t weather-backend ./backend

# Run backend container
docker run -d -p 8000:8000 --env-file .env weather-backend
```

### Frontend Only (Docker)

```bash
# Build frontend image
docker build -t weather-frontend ./frontend

# Run frontend container
docker run -d -p 5173:5173 -e VITE_API_URL=http://localhost:8000 weather-frontend
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description | Rate Limit |
|---|---|---|---|
| `GET` | `/health` | System health status & storage mode | Unlimited |
| `POST` | `/store-weather-data` | Fetch Open-Meteo data & persist to storage | 10/min |
| `GET` | `/list-weather-files` | List all stored JSON weather objects | 60/min |
| `GET` | `/weather-file-content/{filename}` | Download and inspect raw JSON payload | 60/min |

### Example Request Body (`POST /store-weather-data`):
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "start_date": "2024-01-01",
  "end_date": "2024-01-15"
}
```

### Validation Rules:
- `latitude`: Float between `-90.0` and `90.0`
- `longitude`: Float between `-180.0` and `180.0`
- `start_date` & `end_date`: `YYYY-MM-DD`
- `start_date <= end_date`
- Maximum date range: **31 days** (returns `422 Unprocessable Entity` if exceeded)

---

## 🧪 Testing Suite

Execute the automated test suite built with `pytest`:

```bash
# Navigate to backend directory
cd backend

# Run tests
python -m pytest tests/ -v
```

### Coverage:
- **Unit Tests (`tests/test_services.py`)**:
  - `WeatherService` fetching, parameter construction, and Open-Meteo 502/504 error handling.
  - `StorageService` upload, listing, retrieval, and fallback mechanism.
- **Integration Tests (`tests/test_api.py`)**:
  - `POST /store-weather-data` success and validation errors (invalid coordinates, inverted dates, >31 day range).
  - `GET /list-weather-files` listing verification.
  - `GET /weather-file-content/{filename}` 200 payload and 404 missing handling.

---

## ☁️ Deployment

### Backend Deployment

#### Render

**Repository Settings:**
- Repository: https://github.com/Sreevalli20/fullstack
- Branch: main
- Environment: Docker
- Root Directory: backend
- Dockerfile Path: Dockerfile
- Plan: Free
- Health Check: /health

**Environment Variables:**
- STORAGE_TYPE=local
- LOCAL_STORAGE_DIR=data
- OPEN_METEO_BASE_URL=https://archive-api.open-meteo.com/v1/archive
- RATE_LIMIT_STORE=10/minute
- RATE_LIMIT_LIST=60/minute
- RATE_LIMIT_CONTENT=60/minute
- LOG_LEVEL=INFO

The backend will automatically use the `render.yaml` configuration when deployed to Render.

### Frontend Deployment

#### Vercel

**Repository Settings:**
- Repository: https://github.com/Sreevalli20/fullstack
- Root Directory: frontend
- Build Command: npm run build
- Output Directory: dist
- Framework: Vite

**Environment Variables:**
- VITE_API_URL=<your-render-backend-url>

The frontend will automatically use the `vercel.json` configuration when deployed to Vercel.

---

## 📁 Folder Structure

```
.
├── backend/
│   ├── app/
│   │   ├── config.py             # Pydantic settings & env configurations
│   │   ├── main.py               # FastAPI entry point, middlewares, rate limiting
│   │   ├── models/
│   │   │   └── weather.py        # Pydantic request/response schemas & range validators
│   │   ├── routes/
│   │   │   └── weather_routes.py # FastAPI APIRouter endpoints
│   │   ├── services/
│   │   │   └── weather_service.py# Open-Meteo API integration & business logic
│   │   ├── storage/
│   │   │   └── storage_service.py# Google Cloud Storage / local storage integration
│   │   └── utils/
│   │       ├── limiter.py        # slowapi limiter instance
│   │       ├── logger.py         # Structured logging utility
│   │       └── validators.py     # Filename sanitization
│   ├── tests/
│   │   ├── test_api.py           # Endpoint integration tests
│   │   └── test_services.py      # Unit tests with mocks
│   ├── Dockerfile                # Backend production container
│   └── requirements.txt          # Python dependencies (pinned for Python 3.12)
├── frontend/
│   ├── src/
│   │   ├── components/           # React dashboard UI components
│   │   │   ├── EmptyState.tsx
│   │   │   ├── ErrorAlert.tsx
│   │   │   ├── InputForm.tsx
│   │   │   ├── LoadingSkeletons.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── StoredFiles.tsx
│   │   │   ├── WeatherChart.tsx
│   │   │   └── WeatherTable.tsx
│   │   ├── hooks/
│   │   │   └── useWeatherData.ts # Custom React hook for API state management
│   │   ├── services/
│   │   │   └── api.ts            # Axios HTTP client configuration
│   │   ├── types/
│   │   │   └── weather.ts        # TypeScript interfaces
│   │   ├── App.tsx               # Main Dashboard layout & Dark Mode persistence
│   │   └── main.tsx              # React entry point
│   ├── public/                   # Static assets
│   ├── Dockerfile                # Frontend production container
│   ├── package.json              # Node.js dependencies
│   ├── vite.config.ts            # Vite configuration
│   ├── tsconfig.json             # TypeScript configuration
│   └── index.html                # HTML entry point
├── docker-compose.yml            # Local development orchestration
├── render.yaml                   # Render deployment configuration
├── vercel.json                   # Vercel deployment configuration
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
└── README.md                     # Project documentation
```

---

## 📦 Production Build Commands

### Frontend

```bash
# Navigate to frontend directory
cd frontend

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🔧 GitHub Setup

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit"

# Add remote origin
git remote add origin https://github.com/Sreevalli20/fullstack.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## 💡 Key Design Decisions & Interview Notes

1. **Google Cloud Storage Integration**:
   - The backend supports Google Cloud Storage for production deployments and local filesystem for development. Storage type is controlled by the `STORAGE_TYPE` environment variable.

2. **Graceful Storage Fallback**:
   - To avoid developer setup friction, if Google Cloud Storage is unavailable or unconfigured, the app falls back to local file storage (`./data/`) without throwing crashes.

3. **Rate Limiting with `slowapi`**:
   - Implemented IP-based rate limiting on sensitive write and list endpoints to prevent API abuse and respect Open-Meteo rate limits.

4. **Client-Side & Server-Side Dual Validation**:
   - Input fields perform instant client-side date checks, while Pydantic schemas enforce strict bounds (-90 to 90 lat, -180 to 180 lon, 31-day range limit) on the server.

5. **Python 3.12 for Deployment**:
   - The backend uses Python 3.12 in Docker for stable deployment compatibility. Local development with Python 3.14 is supported via Docker.

6. **Docker Strategy**:
   - Backend uses `python:3.12-slim` for stable deployment
   - Frontend uses `node:22-alpine` for Node.js LTS
   - Docker Compose orchestrates both services for local development
