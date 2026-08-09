import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from air_monitor.collector import Collector
from air_monitor.settings import load_settings, save_settings
from air_monitor.storage import (
    RESOLUTIONS,
    init_db,
    readings_by_range,
    recent_readings,
)

app = FastAPI(title="Air Monitor")

TEMPLATE_DIR = Path(__file__).resolve().parent / "web" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

collector = Collector()


@app.on_event("startup")
async def startup():
    init_db()
    asyncio.create_task(collector.run())


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request},
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "settings": load_settings(),
        },
    )


@app.get("/api/status")
async def status():
    reading = collector.latest

    if reading is None:
        return {"online": False}

    settings = load_settings()

    warmup_seconds = max(
        float(settings["warmup_seconds"]),
        0,
    )

    elapsed = collector.elapsed_seconds

    warming_up = elapsed < warmup_seconds

    return {
        "online": True,
        "timestamp": reading.timestamp.isoformat(),
        "temperature_c": reading.temperature_c,
        "humidity_percent": reading.humidity_percent,
        "pressure_hpa": reading.pressure_hpa,
        "gas_resistance_kohms": reading.gas_resistance_kohms,
        "warming_up": warming_up,
        "warmup_seconds": warmup_seconds,
        "warmup_elapsed_seconds": elapsed,
        "warmup_remaining_seconds": max(
            warmup_seconds - elapsed,
            0,
        ),
    }


@app.get("/api/readings")
async def readings(
    limit: int = Query(default=1000, ge=1, le=10000),
    start: str = None,
    end: str = None,
    resolution: str = "1m",
):
    if start is None or end is None:
        rows = recent_readings(limit)
    else:
        if resolution not in RESOLUTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported resolution: {resolution}",
            )

        rows = readings_by_range(
            start=start,
            end=end,
            resolution=resolution,
        )

    for row in rows:
        row["gas_resistance_kohms"] = (
            row["gas_resistance_ohms"] / 1000.0
        )

    return rows


@app.get("/api/settings")
async def get_settings():
    return load_settings()


@app.put("/api/settings")
async def update_settings(payload: dict):
    current = load_settings()

    if "poll_seconds" in payload:
        current["poll_seconds"] = max(
            float(payload["poll_seconds"]),
            0.5,
        )

    if "warmup_seconds" in payload:
        current["warmup_seconds"] = max(
            float(payload["warmup_seconds"]),
            0,
        )

    if "chart_hours" in payload:
        current["chart_hours"] = max(
            float(payload["chart_hours"]),
            0.1,
        )

    save_settings(current)

    return current
