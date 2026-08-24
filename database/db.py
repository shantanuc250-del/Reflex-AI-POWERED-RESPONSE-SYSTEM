"""
Reflex - Database helper
Thin wrapper around sqlite3. database.db is created automatically the
first time this runs -- nothing to set up manually.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            beds_available INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS accidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            clip TEXT,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            event_detected INTEGER NOT NULL,
            reason TEXT,
            num_objects INTEGER,
            severity TEXT,
            score INTEGER,
            hospital_id INTEGER,
            distance_km REAL,
            duration_min REAL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals (id)
        )
    """)

    # Seed a couple of mock hospitals only if the table is empty
    cur.execute("SELECT COUNT(*) FROM hospitals")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO hospitals (name, lat, lng, beds_available) VALUES (?, ?, ?, ?)",
            [
                ("Replace with real hospital name #1", 28.4744, 77.5040, 12),
                ("Replace with real hospital name #2", 28.4595, 77.0266, 5),
            ],
        )

    conn.commit()
    conn.close()
