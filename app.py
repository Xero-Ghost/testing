import os
import time
import uuid
from statistics import fmean

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

ALLOWED_ORIGIN = "https://dash-3bg9uz.example.com"
EMAIL = os.getenv("EMAIL", "24f3004321@ds.study.iitm.ac.in")  # replace or set in env

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=600,
)

@app.middleware("http")
async def add_required_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())

    try:
        response = await call_next(request)
    except Exception:
        response = JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    process_time = max(time.perf_counter() - start, 0.0)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    return response

@app.get("/stats")
def stats(values: str = Query(..., description="Comma-separated integers")):
    try:
        nums = [int(x.strip()) for x in values.split(",") if x.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")

    if not nums:
        raise HTTPException(status_code=400, detail="values cannot be empty")

    total = sum(nums)
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": fmean(nums),
    }