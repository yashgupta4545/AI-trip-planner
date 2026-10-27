"""Local SQLite database persistence service for saving, loading, editing, and deleting trips.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.config import DATABASE_FILE


def get_db_connection() -> sqlite3.Connection:
    """Create and return a connection to trips.db."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize trips SQLite database schema."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                trip_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                destination_id TEXT NOT NULL,
                destination_name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                travelers_count INTEGER NOT NULL,
                total_cost_inr REAL DEFAULT 0.0,
                itinerary_json TEXT NOT NULL,
                budget_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        conn.commit()


def save_trip(
    destination_id: str,
    destination_name: str,
    start_date: str,
    duration_days: int,
    travelers_count: int,
    itinerary_data: Dict[str, Any],
    budget_data: Optional[Dict[str, Any]] = None,
    custom_title: Optional[str] = None
) -> str:
    """Persist a new trip to SQLite."""
    init_db()
    trip_id = f"TRIP_{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.now().isoformat()
    title = custom_title or f"Trip to {destination_name} ({duration_days} Days)"

    total_cost = 0.0
    if budget_data and "total_estimated_cost_inr" in budget_data:
        total_cost = float(budget_data["total_estimated_cost_inr"])
    elif "total_activity_cost_inr" in itinerary_data:
        total_cost = float(itinerary_data["total_activity_cost_inr"])

    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO trips (
                trip_id, title, destination_id, destination_name, start_date,
                duration_days, travelers_count, total_cost_inr,
                itinerary_json, budget_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            trip_id,
            title,
            destination_id,
            destination_name,
            start_date,
            duration_days,
            travelers_count,
            total_cost,
            json.dumps(itinerary_data),
            json.dumps(budget_data) if budget_data else "{}",
            now_iso,
            now_iso
        ))
        conn.commit()

    return trip_id


def get_all_trips() -> List[Dict[str, Any]]:
    """Retrieve all saved itineraries ordered by creation date descending."""
    init_db()
    trips = []
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM trips ORDER BY created_at DESC;")
        for row in cursor.fetchall():
            trips.append({
                "trip_id": row["trip_id"],
                "title": row["title"],
                "destination_id": row["destination_id"],
                "destination_name": row["destination_name"],
                "start_date": row["start_date"],
                "duration_days": row["duration_days"],
                "travelers_count": row["travelers_count"],
                "total_cost_inr": row["total_cost_inr"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            })
    return trips


def get_trip_by_id(trip_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full details of a saved trip including parsed itinerary and budget."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM trips WHERE trip_id = ?;", (trip_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "trip_id": row["trip_id"],
            "title": row["title"],
            "destination_id": row["destination_id"],
            "destination_name": row["destination_name"],
            "start_date": row["start_date"],
            "duration_days": row["duration_days"],
            "travelers_count": row["travelers_count"],
            "total_cost_inr": row["total_cost_inr"],
            "itinerary": json.loads(row["itinerary_json"]),
            "budget": json.loads(row["budget_json"]) if row["budget_json"] else {},
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


def update_trip_title(trip_id: str, new_title: str) -> bool:
    """Update title of an existing trip."""
    init_db()
    now_iso = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.execute(
            "UPDATE trips SET title = ?, updated_at = ? WHERE trip_id = ?;",
            (new_title, now_iso, trip_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_trip(trip_id: str) -> bool:
    """Remove a saved trip by ID."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM trips WHERE trip_id = ?;", (trip_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_all_trips():
    """Delete all saved trips (useful for testing)."""
    init_db()
    with get_db_connection() as conn:
        conn.execute("DELETE FROM trips;")
        conn.commit()
