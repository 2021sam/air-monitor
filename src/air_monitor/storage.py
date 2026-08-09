import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "air_monitor.db"

RESOLUTIONS = {
    "1s": 1,
    "10s": 10,
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "6h": 21600,
    "1d": 86400,
}


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
                gas_resistance_ohms REAL NOT NULL,
                is_warmup INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(readings)").fetchall()
        }

        if "is_warmup" not in columns:
            conn.execute(
                """
                ALTER TABLE readings
                ADD COLUMN is_warmup INTEGER NOT NULL DEFAULT 0
                """
            )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_readings_timestamp
            ON readings(timestamp)
            """
        )


def insert_reading(reading, is_warmup=False):
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO readings (
                timestamp,
                temperature_c,
                humidity_percent,
                pressure_hpa,
                gas_resistance_ohms,
                is_warmup
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                reading.timestamp.isoformat(),
                reading.temperature_c,
                reading.humidity_percent,
                reading.pressure_hpa,
                reading.gas_resistance_ohms,
                1 if is_warmup else 0,
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


def readings_by_range(start, end, resolution="1m"):
    bucket_seconds = RESOLUTIONS.get(resolution)

    if bucket_seconds is None:
        raise ValueError(f"Unsupported resolution: {resolution}")

    with connect() as conn:
        if bucket_seconds == 1:
            rows = conn.execute(
                """
                SELECT
                    timestamp,
                    temperature_c,
                    humidity_percent,
                    pressure_hpa,
                    gas_resistance_ohms,
                    is_warmup,
                    1 AS sample_count
                FROM readings
                WHERE timestamp >= ?
                  AND timestamp < ?
                ORDER BY timestamp
                """,
                (start, end),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT
                    datetime(
                        (
                            CAST(strftime('%s', timestamp) AS INTEGER)
                            / ?
                        ) * ?,
                        'unixepoch'
                    ) || 'Z' AS timestamp,

                    AVG(temperature_c) AS temperature_c,
                    AVG(humidity_percent) AS humidity_percent,
                    AVG(pressure_hpa) AS pressure_hpa,
                    AVG(gas_resistance_ohms) AS gas_resistance_ohms,

                    CASE
                        WHEN SUM(is_warmup) > 0 THEN 1
                        ELSE 0
                    END AS is_warmup,

                    COUNT(*) AS sample_count

                FROM readings
                WHERE timestamp >= ?
                  AND timestamp < ?

                GROUP BY
                    CAST(strftime('%s', timestamp) AS INTEGER) / ?

                ORDER BY timestamp
                """,
                (
                    bucket_seconds,
                    bucket_seconds,
                    start,
                    end,
                    bucket_seconds,
                ),
            ).fetchall()

    return [dict(row) for row in rows]
