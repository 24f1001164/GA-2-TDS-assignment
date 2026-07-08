import time
import uuid
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

EMAIL = "24f1001164@ds.study.iitm.ac.in"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

# Prometheus counter
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests"
)

# Keep recent logs in memory
LOGS = deque(maxlen=1000)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())

    # Increment counter for EVERY request
    HTTP_REQUESTS.inc()

    response = await call_next(request)

    LOGS.append({
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id
    })

    return response


@app.get("/work")
def work(n: int = 1):
    # Simulate K units of work
    total = 0
    for i in range(n):
        total += i

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return list(LOGS)[-limit:]
