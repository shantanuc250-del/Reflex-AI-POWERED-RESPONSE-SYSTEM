"""
Reflex - Ambulance Dispatch API
Finds the nearest hospital (Haversine) and calls OpenRouteService for a
real route + ETA. This layer is 100% live/real in your demo -- no faking
needed, so lean on it in your pitch.

Set your ORS key before running:
    export ORS_API_KEY="your_key_here"
Free key, no card required: https://openrouteservice.org/dev/#/signup
"""

import os
import math
import requests
from flask import Blueprint, request, jsonify
from database.db import get_db

ambulance_bp = Blueprint("ambulance", __name__, url_prefix="/api/ambulance")

ORS_API_KEY = os.environ.get("ORS_API_KEY", "")
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def find_nearest_hospital(lat, lng):
    conn = get_db()
    hospitals = conn.execute("SELECT * FROM hospitals").fetchall()
    conn.close()

    best, best_dist = None, float("inf")
    for h in hospitals:
        d = haversine_km(lat, lng, h["lat"], h["lng"])
        if d < best_dist:
            best, best_dist = dict(h), d
    return best, best_dist


def get_route(lat, lng, hospital_lat, hospital_lng):
    if not ORS_API_KEY:
        raise RuntimeError("ORS_API_KEY not set. export ORS_API_KEY=your_key")

    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {"coordinates": [[lng, lat], [hospital_lng, hospital_lat]]}  # ORS wants [lng, lat]
    resp = requests.post(ORS_URL, headers=headers, json=body, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    summary = data["features"][0]["properties"]["summary"]
    geometry = data["features"][0]["geometry"]
    return {
        "distance_km": round(summary["distance"] / 1000, 2),
        "duration_min": round(summary["duration"] / 60, 1),
        "geometry": geometry,  # GeoJSON LineString -- feed straight to Leaflet
    }


def dispatch(lat, lng):
    """Used internally by api/accidents.py. Also callable via the endpoint below."""
    hospital, straight_line_km = find_nearest_hospital(lat, lng)
    if hospital is None:
        return {"error": "No hospitals in database yet"}
    route = get_route(lat, lng, hospital["lat"], hospital["lng"])
    return {"hospital": hospital, "straight_line_km": round(straight_line_km, 2), "route": route}


@ambulance_bp.route("/dispatch", methods=["POST"])
def dispatch_endpoint():
    """
    POST /api/ambulance/dispatch  { "lat": 28.47, "lng": 77.50 }
    Standalone endpoint for testing dispatch logic without running detection.
    """
    payload = request.get_json(force=True)
    lat, lng = payload.get("lat"), payload.get("lng")
    if lat is None or lng is None:
        return jsonify({"error": "lat and lng are required"}), 400
    try:
        return jsonify(dispatch(lat, lng))
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
