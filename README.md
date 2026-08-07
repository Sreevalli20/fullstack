# WeatherS3 Pro - Weather Data FastAPI Backend & React Dashboard

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.1-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![boto3](https://img.shields.io/badge/AWS_boto3-S3_Storage-FF9900.svg?style=flat&logo=amazon-aws&logoColor=white)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
[![pytest](https://img.shields.io/badge/Pytest-Passed-success.svg?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org/)

Production-ready full-stack application combining a **FastAPI backend** (Open-Meteo API integration + AWS S3 persistence via `boto3`, `slowapi` rate limiting, structured logging) with a **React + Vite + Tailwind CSS + Recharts** interactive analytics dashboard.

---

## 🌟 Project Overview

**WeatherS3 Pro** empowers developers and analysts to query historical daily weather datasets worldwide via Open-Meteo's API, enforce strict input validation, persist the structured JSON payloads into AWS S3 buckets (or local S3 mock fallback), and analyze temperature trends using an interactive dashboard.

### Core Capabilities:
- **FastAPI Backend**: Asynchronous HTTP client (`httpx`), modular architecture, Pydantic input/output schemas with 31-day range limit enforcement, and rate-limiting using `slowapi`.
- **AWS S3 Integration**: Flexible credentials handling via `boto3` supporting both explicit keys and the default AWS credential provider chain (IAM Roles, EC2/ECS metadata, AWS CLI credentials).
- **Structured Logging & Tracing**: Every request is assigned a unique `X-Request-ID` UUID, tracking process duration in milliseconds and logging key events.
- **React Analytics Dashboard**: React 19, Vite, Tailwind CSS, Recharts temperature trend lines (°C and °F modes), searchable S3 object browser, paginated data tables with CSV export, and persistent Dark Mode.
- **Comprehensive Unit & Integration Test Suite**: Built with `pytest` and FastAPI `TestClient`, featuring 100% mocked external API calls and S3 operations.

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
|                                      |            S3StorageService             |  |
|                                      | - boto3 AWS Credential Chain            |  |
|                                      | - Local Fallback Mode for Dev           |  |
|                                      +-----------------------------------------+  |
+-----------------------------------------------------------------------------------+
                       |                                         |
                       v                                         v
+-------------------------------------------+   +-----------------------------------+
|      Open-Meteo Historical API            |   |           AWS S3 Bucket           |
| (https://archive-api.open-meteo.com/v1)   |   |     (boto3 put/list/get_object)   |
+-------------------------------------------+   +-----------------------------------+
```

---

## 💻 Tech Stack

### Backend:
- **Framework**: FastAPI (Python 3.12/3.14)
- **ASGI Server**: Uvicorn
- **AWS SDK**: `boto3` (AWS S3)
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
# AWS Configuration (Placeholder or Actual Credentials)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET=weather-data-bucket

# Open-Meteo API Base URL
OPEN_METEO_BASE_URL=https://archive-api.open-meteo.com/v1/archive

# Rate Limiting Configuration (slowapi)
RATE_LIMIT_STORE=10/minute
RATE_LIMIT_LIST=60/minute
RATE_LIMIT_CONTENT=60/minute

# Logging Level
LOG_LEVEL=INFO

# Frontend API Base URL (For React Vite build)
VITE_API_BASE_URL=http://localhost:3000
```

> **Note on AWS Configuration**: You do **NOT** need to hardcode `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY`. `boto3` will automatically look for credentials via the default credential provider chain (IAM Roles, AWS CLI credentials, environment variables). If no AWS environment is reachable, the backend seamlessly operates in **Local Storage Fallback Mode** so all endpoints remain fully functional during development.

---

## 🚀 Local Development

### Backend Setup (Python 3.14 - Docker Required)

**Important**: pydantic-core does not yet support Python 3.14. Use Docker for running the backend.

```bash
# Using Docker Compose (Recommended)
docker compose up --build
```

Backend runs on: http://localhost:3000

**Alternative**: If you have Python 3.12, you can run locally:

```bash
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
- Backend on http://localhost:3000
- Frontend on http://localhost:5173

### Backend Only (Docker)

```bash
# Build backend image
docker build -t weather-backend .

# Run backend container
docker run -d -p 3000:3000 --env-file .env weather-backend
```

### Frontend Only (Docker)

```bash
# Build frontend image
docker build -f Dockerfile.frontend -t weather-frontend .

# Run frontend container
docker run -d -p 5173:5173 -e VITE_API_BASE_URL=http://localhost:3000 weather-frontend
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description | Rate Limit |
|---|---|---|---|
| `GET` | `/health` | System health status & storage mode | Unlimited |
| `POST` | `/store-weather-data` | Fetch Open-Meteo data & persist to S3 | 10/min |
| `GET` | `/list-weather-files` | List all stored S3 JSON weather objects | 60/min |
| `GET` | `/weather-file-content/{filename}` | Download and inspect raw S3 JSON payload | 60/min |

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
# Run tests
python -m pytest tests/ -v
```

### Coverage:
- **Unit Tests (`tests/test_services.py`)**:
  - `WeatherService` fetching, parameter construction, and Open-Meteo 502/504 error handling.
  - `S3StorageService` upload, listing, retrieval, and fallback mechanism.
- **Integration Tests (`tests/test_api.py`)**:
  - `POST /store-weather-data` success and validation errors (invalid coordinates, inverted dates, >31 day range).
  - `GET /list-weather-files` listing verification.
  - `GET /weather-file-content/{filename}` 200 payload and 404 missing handling.

---

## ☁️ Deployment

### Backend Deployment

#### Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/weather-backend

# Deploy to Cloud Run
gcloud run deploy weather-backend \
  --image gcr.io/PROJECT_ID/weather-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000
```

Or use the provided `cloudbuild.yaml`:

```bash
gcloud builds submit --config cloudbuild.yaml
```

#### Render

1. Connect your GitHub repository to Render
2. Select "Web Service"
3. Use the provided `render.yaml` configuration
4. Set environment variables in the Render dashboard

### Frontend Deployment

#### Vercel

1. Push code to GitHub repository
2. Import project in Vercel dashboard
3. Framework preset: **Vite**
4. Build command: `npm run build`
5. Output directory: `dist`
6. Set environment variable: `VITE_API_BASE_URL` (your deployed backend URL)

Or use the provided `vercel.json` configuration.

---

## 📁 Folder Structure

```
.
├── app/
│   ├── config.py             # Pydantic settings & env configurations
│   ├── main.py               # FastAPI entry point, middlewares, rate limiting
│   ├── models/
│   │   └── weather.py        # Pydantic request/response schemas & range validators
│   ├── routes/
│   │   └── weather_routes.py # FastAPI APIRouter endpoints
│   ├── services/
│   │   └── weather_service.py# Open-Meteo API integration & business logic
│   ├── storage/
│   │   └── s3_service.py     # boto3 S3 integration with local fallback
│   └── utils/
│       ├── limiter.py        # slowapi limiter instance
│       ├── logger.py         # Structured logging utility
│       └── validators.py     # Filename sanitization
├── src/
│   ├── components/           # React dashboard UI components
│   │   ├── EmptyState.tsx
│   │   ├── ErrorAlert.tsx
│   │   ├── InputForm.tsx
│   │   ├── LoadingSkeletons.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── Navbar.tsx
│   │   ├── StoredFiles.tsx
│   │   ├── WeatherChart.tsx
│   │   └── WeatherTable.tsx
│   ├── hooks/
│   │   └── useWeatherData.ts # Custom React hook for API state management
│   ├── services/
│   │   └── api.ts            # Axios HTTP client configuration
│   ├── types/
│   │   └── weather.ts        # TypeScript interfaces
│   ├── App.tsx               # Main Dashboard layout & Dark Mode persistence
│   └── main.tsx              # React entry point
├── tests/
│   ├── test_api.py           # Endpoint integration tests
│   └── test_services.py      # Unit tests with mocks
├── Dockerfile                # Backend production container
├── Dockerfile.frontend       # Frontend production container
├── docker-compose.yml        # Local development orchestration
├── cloudbuild.yaml           # Google Cloud Run deployment
├── render.yaml               # Render deployment
├── vercel.json               # Vercel deployment
├── requirements.txt          # Python dependencies (pinned for Python 3.14)
├── package.json              # Node.js dependencies
└── README.md                 # Project documentation
```

---

## 📦 Production Build Commands

### Frontend

```bash
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

1. **boto3 Default Credential Provider Chain**:
   - Rather than forcing static `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` strings in source code, `boto3` relies on the standard AWS credential chain. This makes the container cloud-native and ready for AWS IAM Roles (ECS/EKS/EC2 Task Roles).

2. **Graceful Storage Fallback**:
   - To avoid developer setup friction, if S3 is unavailable or unconfigured, the app falls back to local file storage (`./data/s3_local_mock/`) without throwing crashes.

3. **Rate Limiting with `slowapi`**:
   - Implemented IP-based rate limiting on sensitive write and list endpoints to prevent API abuse and respect Open-Meteo rate limits.

4. **Client-Side & Server-Side Dual Validation**:
   - Input fields perform instant client-side date checks, while Pydantic schemas enforce strict bounds (-90 to 90 lat, -180 to 180 lon, 31-day range limit) on the server.

5. **Python 3.14 Compatibility**:
   - All dependencies are pinned to versions tested with Python 3.14. If any package doesn't support Python 3.14, use Docker for running the backend with Python 3.12-slim.

6. **Docker Strategy**:
   - Backend uses `python:3.12-slim` for stable deployment
   - Frontend uses `node:22-alpine` for Node.js LTS
   - Docker Compose orchestrates both services for local development
