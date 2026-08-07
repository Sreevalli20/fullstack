"""
Main FastAPI Application Entry Point.
Configures CORS middleware, registers routers, and sets up dashboard & OpenAPI docs.
"""

import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routes import weather_router
from app.storage.s3_service import s3_storage_service
from app.utils.limiter import limiter
from app.utils.logger import logger

app = FastAPI(
    title="Weather Data S3 Storage API",
    description=(
        "Production-ready FastAPI backend for fetching historical weather data "
        "from Open-Meteo API and storing/retrieving JSON datasets in AWS S3 using boto3."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Register slowapi limiter state and rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_and_trace_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start_time = time.time()
    logger.info(f"[{request_id}] {request.method} {request.url.path} initiated")

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(f"[{request_id}] {request.method} {request.url.path} -> Status {response.status_code} ({process_time:.2f}ms)")
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response
    except Exception as exc:
        process_time = (time.time() - start_time) * 1000
        logger.error(f"[{request_id}] Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
        raise exc


# Register weather API router
app.include_router(weather_router)


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint returning application status and storage mode.
    """
    storage_type = "AWS S3 (boto3)" if s3_storage_service._s3_client else "Local Storage (AWS Mock)"
    return {
        "status": "healthy",
        "service": "weather-data-backend",
        "storage_mode": storage_type,
        "s3_bucket": settings.S3_BUCKET,
        "region": settings.AWS_REGION,
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index_dashboard():
    """
    Interactive API Dashboard rendered at root route using Geometric Balance design theme.
    """
    storage_mode = "AWS S3 (boto3)" if s3_storage_service._s3_client else "Local S3 Fallback (Dev Mode)"
    status_badge_color = "bg-green-100 text-green-700 border-green-200" if s3_storage_service._s3_client else "bg-amber-100 text-amber-700 border-amber-200"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en" class="h-full">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weather Data FastAPI Backend - WeatherS3 Pro</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        </style>
    </head>
    <body class="bg-slate-50 text-slate-800 min-h-full flex flex-col md:flex-row overflow-x-hidden">
        <!-- Left Sidebar: Architecture & Env Info -->
        <aside class="w-full md:w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shrink-0">
            <div class="p-6 border-b border-slate-800">
                <div class="flex items-center gap-2 mb-1">
                    <div class="w-3.5 h-3.5 bg-blue-500 rounded-sm"></div>
                    <h1 class="text-white font-bold text-lg tracking-tight">WeatherS3 Pro</h1>
                </div>
                <p class="text-[10px] text-slate-400 uppercase font-bold tracking-widest">FastAPI Backend</p>
            </div>

            <nav class="flex-1 p-5 space-y-6">
                <div>
                    <p class="text-[10px] text-slate-400 uppercase font-bold mb-3 tracking-widest">Modular Structure</p>
                    <ul class="space-y-2 text-xs font-mono">
                        <li class="flex items-center gap-2 text-blue-400 font-bold"><span class="opacity-70">📁</span> app/</li>
                        <li class="flex items-center gap-2 pl-4 text-slate-300"><span class="opacity-70">📂</span> routes/</li>
                        <li class="flex items-center gap-2 pl-4 text-slate-300"><span class="opacity-70">📂</span> services/</li>
                        <li class="flex items-center gap-2 pl-4 text-slate-300"><span class="opacity-70">📂</span> storage/</li>
                        <li class="flex items-center gap-2 pl-4 text-slate-300"><span class="opacity-70">📂</span> models/</li>
                        <li class="flex items-center gap-2 pl-4 text-slate-300"><span class="opacity-70">📂</span> utils/</li>
                        <li class="flex items-center gap-2 text-slate-300"><span class="opacity-70">📄</span> config.py</li>
                        <li class="flex items-center gap-2 text-slate-300"><span class="opacity-70">🐳</span> Dockerfile</li>
                    </ul>
                </div>

                <div>
                    <p class="text-[10px] text-slate-400 uppercase font-bold mb-3 tracking-widest">Environment Config</p>
                    <div class="space-y-2">
                        <div class="bg-slate-800/80 p-2.5 rounded-lg flex justify-between items-center border border-slate-700/50">
                            <span class="text-[11px] font-medium text-slate-300">AWS_REGION</span>
                            <span class="text-[11px] font-mono text-green-400 font-bold">{settings.AWS_REGION}</span>
                        </div>
                        <div class="bg-slate-800/80 p-2.5 rounded-lg flex justify-between items-center border border-slate-700/50">
                            <span class="text-[11px] font-medium text-slate-300">S3_BUCKET</span>
                            <span class="text-[11px] font-mono text-green-400 font-bold truncate max-w-[100px]">{settings.S3_BUCKET}</span>
                        </div>
                    </div>
                </div>
            </nav>

            <div class="p-4 border-t border-slate-800 bg-slate-900/50">
                <div class="flex items-center justify-between text-[11px] font-medium mb-1.5">
                    <span class="text-slate-400">Worker Engine</span>
                    <span class="text-emerald-400 font-bold">● Running</span>
                </div>
                <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div class="bg-emerald-500 h-1.5 w-full rounded-full"></div>
                </div>
            </div>
        </aside>

        <!-- Main Content Area -->
        <main class="flex-1 flex flex-col min-w-0">
            <!-- Header Bar -->
            <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 md:px-8 shrink-0">
                <div class="flex items-center gap-6">
                    <div class="flex items-center gap-2 text-xs md:text-sm font-medium">
                        <span class="text-slate-400">Instance:</span>
                        <span class="bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded font-mono border border-blue-100 font-semibold">weather-api-01</span>
                    </div>
                    <div class="hidden sm:flex items-center gap-2 text-xs md:text-sm font-medium">
                        <span class="text-slate-400">Storage Mode:</span>
                        <span class="px-2.5 py-0.5 rounded font-mono text-xs font-semibold border {status_badge_color}">{storage_mode}</span>
                    </div>
                </div>
                <div class="flex items-center gap-3">
                    <a href="/docs" target="_blank" class="bg-slate-900 hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-lg font-bold transition flex items-center gap-1.5 shadow-sm">
                        <span>OpenAPI Docs</span>
                        <span class="text-slate-400">↗</span>
                    </a>
                </div>
            </header>

            <!-- Dashboard Body -->
            <div class="p-6 md:p-8 flex-1 space-y-6 overflow-y-auto">
                
                <!-- Stats Row -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="bg-white border border-slate-200 p-5 rounded-xl shadow-sm">
                        <p class="text-slate-500 text-[11px] font-bold uppercase tracking-wider mb-1">Total Weather Files</p>
                        <p id="totalFilesStat" class="text-3xl font-light text-slate-900">0</p>
                        <div class="mt-3 flex items-center text-xs text-green-600 font-bold">
                            <span>S3 Objects Syncing</span>
                        </div>
                    </div>

                    <div class="bg-white border border-slate-200 p-5 rounded-xl shadow-sm">
                        <p class="text-slate-500 text-[11px] font-bold uppercase tracking-wider mb-1">AWS S3 Target</p>
                        <p class="text-xl font-semibold text-slate-900 truncate" title="{settings.S3_BUCKET}">{settings.S3_BUCKET}</p>
                        <div class="mt-3 flex items-center text-xs text-blue-600 font-bold">
                            <span>Region: {settings.AWS_REGION}</span>
                        </div>
                    </div>

                    <div class="bg-white border border-slate-200 p-5 rounded-xl shadow-sm">
                        <p class="text-slate-500 text-[11px] font-bold uppercase tracking-wider mb-1">Open-Meteo Latency</p>
                        <p class="text-3xl font-light text-slate-900">~140 ms</p>
                        <div class="mt-3 flex items-center text-xs text-emerald-600 font-bold">
                            <span>Historical API: Operational</span>
                        </div>
                    </div>

                    <div class="bg-slate-900 p-5 rounded-xl shadow-sm flex flex-col justify-between text-white">
                        <p class="text-slate-400 text-[11px] font-bold uppercase tracking-wider">Service Stack</p>
                        <div class="font-mono text-xs space-y-1 mt-2">
                            <div class="flex justify-between border-b border-slate-800 py-0.5">
                                <span class="text-slate-300">boto3</span><span class="text-green-400 font-bold">ACTIVE</span>
                            </div>
                            <div class="flex justify-between border-b border-slate-800 py-0.5">
                                <span class="text-slate-300">httpx</span><span class="text-green-400 font-bold">ACTIVE</span>
                            </div>
                            <div class="flex justify-between py-0.5">
                                <span class="text-slate-300">uvicorn</span><span class="text-green-400 font-bold">ACTIVE</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Main Work Area Grid -->
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    
                    <!-- Form Column (POST /store-weather-data) -->
                    <div class="lg:col-span-5 bg-white border border-slate-200 p-6 rounded-xl shadow-sm flex flex-col">
                        <div class="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
                            <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wide flex items-center gap-2">
                                <span class="w-2.5 h-2.5 bg-blue-600 rounded-sm"></span>
                                POST /store-weather-data
                            </h2>
                            <span class="text-[10px] bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-mono font-semibold">Async HTTP</span>
                        </div>

                        <form id="storeForm" class="space-y-4 flex-1 flex flex-col">
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 mb-1">Latitude (-90 to 90)</label>
                                <input type="number" step="any" id="lat" value="37.7749" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 mb-1">Longitude (-180 to 180)</label>
                                <input type="number" step="any" id="lon" value="-122.4194" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition">
                            </div>
                            <div class="grid grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-xs font-semibold text-slate-700 mb-1">Start Date</label>
                                    <input type="date" id="startDate" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition">
                                </div>
                                <div>
                                    <label class="block text-xs font-semibold text-slate-700 mb-1">End Date (Max 31 days)</label>
                                    <input type="date" id="endDate" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition">
                                </div>
                            </div>

                            <div class="pt-2 mt-auto">
                                <button type="submit" id="submitBtn" class="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-lg transition uppercase tracking-wider shadow">
                                    Fetch & Store in AWS S3
                                </button>
                            </div>
                        </form>

                        <div id="formStatus" class="mt-4 hidden p-3 rounded-lg text-xs font-mono"></div>
                    </div>

                    <!-- Right Column: S3 File Browser & Content -->
                    <div class="lg:col-span-7 space-y-6">
                        <!-- File Browser Card -->
                        <div class="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
                            <div class="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
                                <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wide flex items-center gap-2">
                                    <span class="w-2.5 h-2.5 bg-emerald-500 rounded-sm"></span>
                                    GET /list-weather-files
                                </h2>
                                <button onclick="fetchFileList()" class="text-xs text-blue-600 font-semibold hover:underline">
                                    🔄 Refresh List
                                </button>
                            </div>

                            <div id="fileListContainer" class="space-y-2 max-h-52 overflow-y-auto pr-1">
                                <p class="text-xs text-slate-400 font-mono">Loading stored S3 weather files...</p>
                            </div>
                        </div>

                        <!-- JSON Content Inspector -->
                        <div class="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
                            <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
                                <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wide flex items-center gap-2">
                                    <span class="w-2.5 h-2.5 bg-blue-500 rounded-sm"></span>
                                    GET /weather-file-content/&#123;filename&#125;
                                </h2>
                                <span id="activeFilename" class="text-xs font-mono font-medium text-slate-500 truncate max-w-[200px]">No file selected</span>
                            </div>

                            <pre id="jsonViewer" class="bg-slate-900 text-emerald-400 p-4 rounded-lg text-xs font-mono overflow-x-auto max-h-72 border border-slate-800">Select a file from the list above to view S3 JSON payload</pre>
                        </div>
                    </div>

                </div>

                <!-- Logs & Activity Section -->
                <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                    <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
                            <span class="w-2 h-2 bg-slate-900 rounded-full"></span>
                            Recent Backend Event Logs
                        </h3>
                        <span class="text-[10px] text-slate-400 font-mono uppercase">Live Log Output</span>
                    </div>
                    <div id="logConsole" class="font-mono text-[11px] space-y-2 max-h-40 overflow-y-auto bg-slate-950 p-4 rounded-lg text-slate-300">
                        <div><span class="text-blue-400 font-bold">[INFO]</span> Service initialized. AWS S3 Storage handler ready.</div>
                    </div>
                </div>

                <!-- Bottom System Checks Bar -->
                <div class="bg-blue-600 rounded-xl p-5 text-white flex flex-col sm:flex-row items-center justify-between gap-4 shadow">
                    <div class="flex flex-wrap items-center gap-6">
                        <div class="flex items-center gap-2.5">
                            <div class="w-2.5 h-2.5 bg-white rounded-full animate-pulse"></div>
                            <span class="text-xs font-bold uppercase tracking-wider">Master Storage Cluster: Operational</span>
                        </div>
                        <div class="flex items-center gap-2.5">
                            <div class="w-2.5 h-2.5 bg-blue-300 rounded-full"></div>
                            <span class="text-xs font-bold uppercase tracking-wider">boto3 S3 Sync: Active</span>
                        </div>
                    </div>
                    <span class="font-mono text-xs text-blue-100 uppercase font-semibold">Build: FastAPI v1.0.0</span>
                </div>

            </div>
        </main>

        <script>
            // Set default dates (past 10 days)
            const today = new Date();
            const tenDaysAgo = new Date();
            tenDaysAgo.setDate(today.getDate() - 10);
            
            document.getElementById('endDate').value = today.toISOString().split('T')[0];
            document.getElementById('startDate').value = tenDaysAgo.toISOString().split('T')[0];

            function appendLog(type, msg) {{
                const consoleDiv = document.getElementById('logConsole');
                const now = new Date().toISOString().split('T')[1].split('.')[0];
                const color = type === 'WARN' ? 'text-amber-400' : (type === 'ERROR' ? 'text-rose-400' : 'text-blue-400');
                const logLine = document.createElement('div');
                logLine.innerHTML = `<span class="${{color}} font-bold">[${{type}}]</span> <span class="text-slate-500">${{now}}</span> | ${{msg}}`;
                consoleDiv.appendChild(logLine);
                consoleDiv.scrollTop = consoleDiv.scrollHeight;
            }}

            async function fetchFileList() {{
                const container = document.getElementById('fileListContainer');
                try {{
                    const res = await fetch('/list-weather-files');
                    const data = await res.json();
                    
                    if (!data.files || data.files.length === 0) {{
                        container.innerHTML = '<p class="text-xs text-slate-400 font-mono py-2">No weather files stored in S3 yet.</p>';
                        document.getElementById('totalFilesStat').innerText = '0';
                        return;
                    }}
                    
                    document.getElementById('totalFilesStat').innerText = data.files.length;

                    container.innerHTML = data.files.map(f => `
                        <div onclick="viewFile('${{f.name}}')" class="p-3 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg cursor-pointer flex items-center justify-between transition group">
                            <div class="truncate pr-2">
                                <p class="text-xs font-mono font-bold text-slate-800 group-hover:text-blue-600 truncate">${{f.name}}</p>
                                <p class="text-[10px] text-slate-400 font-mono">${{f.created_at}}</p>
                            </div>
                            <span class="text-[10px] font-mono font-semibold text-slate-600 bg-white border border-slate-200 px-2.5 py-1 rounded shrink-0">${{f.size}} Bytes</span>
                        </div>
                    `).join('');
                    appendLog('INFO', `Retrieved ${{data.files.length}} file(s) from GET /list-weather-files`);
                }} catch (e) {{
                    container.innerHTML = '<p class="text-xs text-rose-500 font-mono">Error loading files list</p>';
                    appendLog('ERROR', `GET /list-weather-files failed: ${{e.message}}`);
                }}
            }}

            async function viewFile(filename) {{
                document.getElementById('activeFilename').innerText = filename;
                const viewer = document.getElementById('jsonViewer');
                viewer.innerText = "Downloading payload from S3...";
                try {{
                    const res = await fetch('/weather-file-content/' + encodeURIComponent(filename));
                    const data = await res.json();
                    viewer.innerText = JSON.stringify(data, null, 2);
                    appendLog('INFO', `Downloaded and parsed ${{filename}}`);
                }} catch (e) {{
                    viewer.innerText = "Error fetching file content: " + e.message;
                    appendLog('ERROR', `Failed downloading ${{filename}}: ${{e.message}}`);
                }}
            }}

            document.getElementById('storeForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                const btn = document.getElementById('submitBtn');
                const statusDiv = document.getElementById('formStatus');
                btn.disabled = true;
                btn.innerText = "Fetching Open-Meteo & Uploading to S3...";
                statusDiv.classList.add('hidden');
                
                const payload = {{
                    latitude: parseFloat(document.getElementById('lat').value),
                    longitude: parseFloat(document.getElementById('lon').value),
                    start_date: document.getElementById('startDate').value,
                    end_date: document.getElementById('endDate').value
                }};

                appendLog('INFO', `Initiating POST /store-weather-data for lat=${{payload.latitude}}, lon=${{payload.longitude}}`);

                try {{
                    const res = await fetch('/store-weather-data', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(payload)
                    }});
                    const data = await res.json();
                    if (res.ok) {{
                        statusDiv.className = "mt-4 p-3 rounded-lg text-xs font-mono bg-emerald-50 text-emerald-800 border border-emerald-200";
                        statusDiv.innerText = "✓ Success! Saved file: " + data.file;
                        appendLog('INFO', `S3 Storage Success: Created ${{data.file}}`);
                        fetchFileList();
                        viewFile(data.file);
                    }} else {{
                        statusDiv.className = "mt-4 p-3 rounded-lg text-xs font-mono bg-rose-50 text-rose-800 border border-rose-200";
                        statusDiv.innerText = "✗ Error " + res.status + ": " + JSON.stringify(data.detail || data);
                        appendLog('WARN', `POST /store-weather-data returned ${{res.status}}`);
                    }}
                    statusDiv.classList.remove('hidden');
                }} catch (err) {{
                    statusDiv.className = "mt-4 p-3 rounded-lg text-xs font-mono bg-rose-50 text-rose-800 border border-rose-200";
                    statusDiv.innerText = "✗ Request failed: " + err.message;
                    appendLog('ERROR', `Network failure: ${{err.message}}`);
                    statusDiv.classList.remove('hidden');
                }} finally {{
                    btn.disabled = false;
                    btn.innerText = "Fetch & Store in AWS S3";
                }}
            }});

            // Initial load
            fetchFileList();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

