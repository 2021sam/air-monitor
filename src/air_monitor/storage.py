import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "air_monitor.db"


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature_c REAL NOT NULL,
                humidity_percent REAL NOT NULL,
                pressure_hpa REAL NOT NULL,
                gas_resistance_ohms REAL NOT NULL
            )
            """
        )


def insert_reading(reading):
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO readings (
                timestamp,
                temperature_c,
                humidity_percent,
                pressure_hpa,
                gas_resistance_ohms
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                reading.timestamp.isoformat(),
                reading.temperature_c,
                reading.humidity_percent,
                reading.pressure_hpa,
                reading.gas_resistance_ohms,
            ),
        )


def recent_readings(limit=1000):
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM readings
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]
