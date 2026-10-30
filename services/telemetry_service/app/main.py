"""
ChangeGuard Connected-Vehicle Telemetry Microservice.
Provides real-time telemetry streaming, Prometheus metrics, and chaos injection.
"""
import os
import time
import random
import asyncio
import logging
import psutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.metrics import (
    metrics_app,
    REQUESTS_TOTAL,
    REQUEST_LATENCY,
    ACTIVE_VEHICLES,
    BATTERY_HEALTH,
    MEMORY_USAGE,
    ERRORS_TOTAL,
)
from app.chaos import chaos_controller
from app.telemetry import VehicleTelemetry, telemetry_store

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "telemetry-service", "message": "%(message)s"}'
)
logger = logging.getLogger("changeguard.telemetry")

# Simulator flag
simulator_running = True

async def background_telemetry_simulator():
    """Simulates active connected vehicles publishing telemetry every 2 seconds."""
    idx = 0
    while simulator_running:
        try:
            # Update memory metric
            process = psutil.Process()
            mem_bytes = process.memory_info().rss
            extra_leak = sum(len(c) for c in chaos_controller.memory_buffer)
            MEMORY_USAGE.set(mem_bytes + extra_leak)

            # Ingest simulated telemetry
            sample = telemetry_store.generate_sample(idx)
            telemetry_store.ingest(sample)
            ACTIVE_VEHICLES.set(telemetry_store.get_vehicle_count())
            BATTERY_HEALTH.labels(fleet_id=sample.fleet_id).set(sample.battery_pct)

            # Record baseline metrics
            status_code = "200"
            latency = 0.05 + random.uniform(0.01, 0.04)

            # Apply chaos if active
            if chaos_controller.latency_ms > 0:
                latency += (chaos_controller.latency_ms / 1000.0)

            if chaos_controller.error_rate > 0 and random.random() < chaos_controller.error_rate:
                status_code = "500"
                ERRORS_TOTAL.labels(error_type="simulated_chaos_500").inc()

            REQUESTS_TOTAL.labels(endpoint="/telemetry", status=status_code, method="POST").inc()
            REQUEST_LATENCY.labels(endpoint="/telemetry").observe(latency)

            idx += 1
        except Exception as e:
            logger.error(f"Simulator error: {e}")
        await asyncio.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background simulator
    sim_task = asyncio.create_task(background_telemetry_simulator())
    logger.info("Connected-Vehicle Telemetry Service started with background simulator")
    yield
    global simulator_running
    simulator_running = False
    sim_task.cancel()

app = FastAPI(
    title="ChangeGuard - Connected-Vehicle Telemetry Service",
    description="High-frequency telemetry ingestion backend with chaos engineering hooks",
    version="2.4.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    # Skip chaos for health, metrics, and chaos management endpoints
    if request.url.path.startswith(("/health", "/metrics", "/chaos")):
        return await call_next(request)

    # 1. Latency injection
    if chaos_controller.latency_ms > 0:
        await asyncio.sleep(chaos_controller.latency_ms / 1000.0)

    # 2. Error rate injection
    if chaos_controller.error_rate > 0 and random.random() < chaos_controller.error_rate:
        REQUESTS_TOTAL.labels(endpoint=request.url.path, status="500", method=request.method).inc()
        ERRORS_TOTAL.labels(error_type="chaos_injected_fault").inc()
        logger.error(f"[CHAOS FAULT] Injected 500 Internal Error on {request.url.path}")
        raise HTTPException(status_code=500, detail="Internal Service Error [Simulated Incident]")

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUESTS_TOTAL.labels(endpoint=request.url.path, status=str(response.status_code), method=request.method).inc()
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(duration)
    return response

@app.get("/health")
def health():
    return {
        "status": "healthy" if not chaos_controller.get_status()["is_degraded"] else "degraded",
        "service": "connected-vehicle-telemetry",
        "version": "v2.4.1-rc3",
        "chaos_state": chaos_controller.get_status()
    }

@app.post("/telemetry")
def ingest_telemetry(payload: VehicleTelemetry):
    result = telemetry_store.ingest(payload)
    ACTIVE_VEHICLES.set(telemetry_store.get_vehicle_count())
    BATTERY_HEALTH.labels(fleet_id=payload.fleet_id).set(payload.battery_pct)
    return result

@app.get("/telemetry/latest")
def get_latest_telemetry(limit: int = 20):
    return {
        "count": len(telemetry_store.records),
        "active_vehicles": telemetry_store.get_vehicle_count(),
        "records": telemetry_store.get_latest(limit)
    }

# ----------------- CHAOS ENGINEERING ENDPOINTS -----------------

@app.post("/chaos/latency")
def inject_latency(ms: float = 2500.0):
    incident = chaos_controller.inject_latency(ms)
    return {"message": f"Latency injected: {ms}ms", "incident": incident}

@app.post("/chaos/error-rate")
def inject_error_rate(rate: float = 0.5):
    incident = chaos_controller.inject_error_rate(rate)
    return {"message": f"Error rate set to {rate * 100}%", "incident": incident}

@app.post("/chaos/memory-leak")
def inject_memory_leak(mb: int = 150):
    incident = chaos_controller.inject_memory_leak(mb)
    return {"message": f"Allocated {mb}MB memory chunk", "incident": incident}

@app.post("/chaos/reset")
def reset_chaos():
    res = chaos_controller.reset()
    return res

@app.get("/chaos/status")
def chaos_status():
    return chaos_controller.get_status()
