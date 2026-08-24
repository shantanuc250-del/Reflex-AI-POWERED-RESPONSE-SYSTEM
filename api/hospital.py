"""
Reflex - Hospital API
Read access to the hospitals table. Swap the seed data in database/db.py
with real hospitals near your venue before the demo.
"""

from flask import Blueprint, jsonify
from database.db import get_db

hospital_bp = Blueprint("hospital", __name__, url_prefix="/api/hospitals")


@hospital_bp.route("", methods=["GET"])
def list_hospitals():
    conn = get_db()
    rows = conn.execute("SELECT * FROM hospitals").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@hospital_bp.route("/<int:hospital_id>", methods=["GET"])
def get_hospital(hospital_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM hospitals WHERE id = ?", (hospital_id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Hospital not found"}), 404
    return jsonify(dict(row))
