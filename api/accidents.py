"""
REFLEX - Accidents API

Complete emergency pipeline:

VIDEO
  ↓
ACCIDENT DETECTION
  ↓
SEVERITY
  ↓
INCIDENT ID  (RX-YYYY-NNN)
  ↓
AMBULANCE DISPATCH
  ↓
HOSPITAL SELECTION
  ↓
EVIDENCE FRAME CAPTURE  ← NEW
  ↓
DATABASE  (accidents + incidents tables)
  ↓
SOCKET.IO
  ↓
DASHBOARD + AMBULANCE + HOSPITAL
"""

import os

from datetime import datetime, timezone

from flask import (
    Blueprint,
    request,
    jsonify
)

from database.db import get_db

from ai.accident import analyze_video

from ai.severity import score_severity

from ai.evidence import capture_evidence_frame

from dispatch.dispatcher import (
    dispatch_emergency
)


# =========================================================
# BLUEPRINT
# =========================================================

accidents_bp = Blueprint(
    "accidents",
    __name__,
    url_prefix="/api/accidents"
)


# =========================================================
# VIDEO DIRECTORY
# =========================================================

VIDEOS_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)
    ),
    "videos"
)


# =========================================================
# SOCKET.IO
# =========================================================

socketio = None


def init_socketio(sio):

    global socketio

    socketio = sio


# =========================================================
# SIMULATE ACCIDENT
# =========================================================

@accidents_bp.route(
    "/simulate/<clip_name>",
    methods=["POST"]
)
def simulate(clip_name):

    # =====================================================
    # GET LOCATION
    # =====================================================

    lat = request.args.get(
        "lat",
        type=float
    )

    lng = request.args.get(
        "lng",
        type=float
    )


    if lat is None or lng is None:

        return jsonify({
            "error":
                "lat and lng query params are required"
        }), 400


    # =====================================================
    # VIDEO PATH
    # =====================================================

    clip_path = os.path.join(
        VIDEOS_DIR,
        clip_name
    )


    if not os.path.exists(clip_path):

        return jsonify({

            "error":
                f"Clip not found: videos/{clip_name}"

        }), 404


    # =====================================================
    # STEP 1
    # AI ACCIDENT DETECTION
    # =====================================================

    print()
    print(
        "=========================================="
    )

    print(
        "REFLEX: Starting AI analysis"
    )

    print(
        "=========================================="
    )

    print()


    detection_result = analyze_video(
        clip_path
    )


    print(
        "Accident detected:",
        detection_result.get(
            "event_detected"
        )
    )


    print(
        "Confidence:",
        detection_result.get(
            "confidence",
            0
        )
    )


    # =====================================================
    # STEP 2
    # SEVERITY
    # =====================================================

    severity_result = score_severity(
        detection_result
    )


    print(
        "Severity:",
        severity_result.get(
            "severity"
        )
    )


    # =====================================================
    # BASE PAYLOAD
    # =====================================================

    timestamp_iso = datetime.now(
        timezone.utc
    ).isoformat()

    payload = {

        "timestamp":
            timestamp_iso,


        "clip":
            clip_name,


        "accident_location": {

            "lat":
                lat,

            "lng":
                lng

        },


        "detection":
            detection_result,


        "severity":
            severity_result

    }


    # =====================================================
    # STEP 3
    # EMERGENCY DISPATCH
    # =====================================================

    hospital_id  = None
    distance_km  = None
    duration_min = None

    incident_id         = None
    evidence_image_path = None
    ambulance           = None
    hospital            = None


    if detection_result.get(
        "event_detected"
    ):


        try:

            print()

            print(
                "🚨 ACCIDENT DETECTED"
            )

            print(
                "Starting emergency dispatch..."
            )

            print()


            # -------------------------------------------------
            # Dispatch engine
            # -------------------------------------------------

            dispatch_result = dispatch_emergency(

                lat,

                lng

            )


            # -------------------------------------------------
            # Add dispatch result
            # -------------------------------------------------

            payload[
                "dispatch"
            ] = dispatch_result


            # -------------------------------------------------
            # INCIDENT ID
            # -------------------------------------------------

            incident_id = dispatch_result.get(
                "incident_id"
            )


            if incident_id:

                payload[
                    "incident_id"
                ] = incident_id


            # -------------------------------------------------
            # Hospital information
            # -------------------------------------------------

            hospital = dispatch_result.get(
                "hospital"
            )


            if hospital:

                hospital_id = hospital.get(
                    "id"
                )


                distance_km = hospital.get(
                    "distance_km"
                )


                duration_min = hospital.get(
                    "eta_minutes"
                )


                print(
                    "🏥 Hospital:",
                    hospital.get(
                        "name"
                    )
                )


                print(
                    "Hospital distance:",
                    hospital.get(
                        "distance_km"
                    ),
                    "km"
                )


                print(
                    "Hospital ETA:",
                    hospital.get(
                        "eta_minutes"
                    ),
                    "minutes"
                )


            # -------------------------------------------------
            # Ambulance information
            # -------------------------------------------------

            ambulance = dispatch_result.get(
                "ambulance"
            )


            if ambulance:

                print(
                    "🚑 Ambulance:",
                    ambulance.get(
                        "name"
                    )
                )


                print(
                    "Ambulance ID:",
                    ambulance.get(
                        "id"
                    )
                )


                print(
                    "Distance:",
                    ambulance.get(
                        "distance_km"
                    ),
                    "km"
                )


                print(
                    "ETA:",
                    ambulance.get(
                        "eta_minutes"
                    ),
                    "minutes"
                )


                print(
                    "Status:",
                    ambulance.get(
                        "status"
                    )
                )


            else:

                print(
                    "⚠️ No available ambulance"
                )


        except Exception as e:

            print(
                "Dispatch error:",
                str(e)
            )


            payload[
                "dispatch_error"
            ] = str(e)


    else:

        print(
            "No accident detected."
        )


    # =====================================================
    # STEP 4 — NEW
    # EVIDENCE FRAME CAPTURE
    # Runs only when an accident was confirmed and we
    # have a valid incident_id + event_frame
    # =====================================================

    if (
        detection_result.get("event_detected")
        and incident_id
        and detection_result.get("event_frame") is not None
    ):

        print()
        print("📸 Capturing evidence frame...")

        try:

            evidence_image_path = capture_evidence_frame(

                video_path  = clip_path,

                event_frame = detection_result.get("event_frame"),

                incident_id = incident_id,

                severity    = severity_result.get("severity", "UNKNOWN"),

                timestamp   = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )

            )

            if evidence_image_path:

                payload["evidence_image_path"] = evidence_image_path

                print(f"✅ Evidence saved: {evidence_image_path}")

            else:

                print("⚠️ Evidence capture returned None")


        except Exception as ev_err:

            print(f"⚠️ Evidence capture error: {ev_err}")


    # =====================================================
    # STEP 5
    # DATABASE — accidents (existing table, unchanged)
    # =====================================================

    conn = get_db()


    vehicles_involved = detection_result.get(

        "vehicles_involved",

        detection_result.get(
            "num_objects_at_event",
            0
        )

    )


    conn.execute(

        """
        INSERT INTO accidents
        (
            timestamp,
            clip,
            lat,
            lng,
            event_detected,
            reason,
            num_objects,
            severity,
            score,
            hospital_id,
            distance_km,
            duration_min
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (

            payload[
                "timestamp"
            ],


            clip_name,


            lat,


            lng,


            int(

                detection_result.get(
                    "event_detected",
                    False
                )

            ),


            detection_result.get(
                "reason"
            ),


            vehicles_involved,


            severity_result.get(
                "severity"
            ),


            severity_result.get(
                "score"
            ),


            hospital_id,


            distance_km,


            duration_min

        )

    )


    # =====================================================
    # STEP 5b — NEW
    # DATABASE — incidents (new evidence table)
    # Only written when an accident is confirmed
    # =====================================================

    if (
        detection_result.get("event_detected")
        and incident_id
    ):

        payload["status"] = "DETECTED"

        conn.execute(

            """
            INSERT OR REPLACE INTO incidents
            (
                incident_id,
                timestamp,
                clip,
                lat,
                lng,
                severity,
                score,
                confidence,
                reason,
                vehicles_involved,
                event_frame,
                event_time_sec,
                ambulance_id,
                ambulance_name,
                ambulance_eta,
                hospital_name,
                hospital_eta,
                evidence_image_path,
                status,
                acknowledged_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (
                incident_id,
                timestamp_iso,
                clip_name,
                lat,
                lng,
                severity_result.get("severity"),
                severity_result.get("score"),
                detection_result.get("confidence", 0),
                detection_result.get("reason"),
                vehicles_involved,
                detection_result.get("event_frame"),
                detection_result.get("event_time_sec"),
                ambulance.get("id")   if ambulance else None,
                ambulance.get("name") if ambulance else None,
                ambulance.get("eta_minutes") if ambulance else None,
                hospital.get("name")  if hospital else None,
                hospital.get("eta_minutes") if hospital else None,
                evidence_image_path,
                "DETECTED",
                None
            )

        )


    conn.commit()
    conn.close()


    # =====================================================
    # STEP 6
    # REAL-TIME BROADCAST
    # =====================================================

    if socketio:

        socketio.emit(

            "new_incident",

            payload

        )


        print()

        print(
            "📡 Dashboard updated"
        )


        print(
            "📡 Hospital updated"
        )


        print(
            "📡 Ambulance updated"
        )


    # =====================================================
    # PIPELINE COMPLETE
    # =====================================================

    print()

    print(
        "=========================================="
    )

    print(
        "REFLEX PIPELINE COMPLETE"
    )

    print(
        "=========================================="
    )

    print()


    return jsonify(
        payload
    )


# =========================================================
# GET SINGLE INCIDENT EVIDENCE RECORD
# =========================================================

@accidents_bp.route(
    "/evidence/<incident_id>",
    methods=["GET"]
)
def get_evidence(incident_id):
    """
    Return the full evidence record for a given incident ID.

    Example:
        GET /api/accidents/evidence/RX-2026-001
    """

    conn = get_db()

    row = conn.execute(

        """
        SELECT *
        FROM incidents
        WHERE incident_id = ?
        """,

        (incident_id,)

    ).fetchone()

    conn.close()


    if row is None:

        return jsonify({
            "error": f"Incident not found: {incident_id}"
        }), 404


    return jsonify(
        dict(row)
    )


# =========================================================
# LIST ALL EVIDENCE RECORDS
# =========================================================

@accidents_bp.route(
    "/evidence",
    methods=["GET"]
)
def list_evidence():
    """Return all evidence records, newest first."""

    conn = get_db()

    rows = conn.execute(

        """
        SELECT *
        FROM incidents
        ORDER BY timestamp DESC
        LIMIT 100
        """

    ).fetchall()

    conn.close()

    return jsonify(
        [dict(row) for row in rows]
    )


# =========================================================
# LIST PREVIOUS ACCIDENTS  (original endpoint — unchanged)
# =========================================================

@accidents_bp.route(
    "",
    methods=["GET"]
)
def list_accidents():

    conn = get_db()


    rows = conn.execute(

        """
        SELECT *
        FROM accidents
        ORDER BY id DESC
        LIMIT 50
        """

    ).fetchall()


    conn.close()


    return jsonify(

        [
            dict(row)
            for row in rows
        ]

    )


# =========================================================
# NOTIFY INCIDENT  (status DETECTED -> NOTIFIED)
# =========================================================

@accidents_bp.route(
    "/notify/<incident_id>",
    methods=["POST"]
)
def notify_incident(incident_id):
    """
    Transition incident status from DETECTED to NOTIFIED.
    This signifies that the hospital has received the alert.
    """
    conn = get_db()
    
    # Check if incident exists
    row = conn.execute(
        "SELECT status FROM incidents WHERE incident_id = ?",
        (incident_id,)
    ).fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": f"Incident {incident_id} not found"}), 404
        
    current_status = row["status"]
    
    # Only transition if it is currently DETECTED
    if current_status == "DETECTED":
        conn.execute(
            "UPDATE incidents SET status = 'NOTIFIED' WHERE incident_id = ?",
            (incident_id,)
        )
        conn.commit()
        status_updated = True
        new_status = "NOTIFIED"
    else:
        status_updated = False
        new_status = current_status
        
    conn.close()
    
    if status_updated and socketio:
        socketio.emit(
            "incident_status_change",
            {
                "incident_id": incident_id,
                "status": new_status
            }
        )
        
    return jsonify({
        "success": True,
        "incident_id": incident_id,
        "status": new_status,
        "updated": status_updated
    })


# =========================================================
# ACKNOWLEDGE INCIDENT  (status NOTIFIED -> ACKNOWLEDGED)
# =========================================================

@accidents_bp.route(
    "/acknowledge/<incident_id>",
    methods=["POST"]
)
def acknowledge_incident(incident_id):
    """
    Transition incident status from DETECTED/NOTIFIED to ACKNOWLEDGED.
    Stores the acknowledgment timestamp in the database.
    """
    from datetime import datetime, timezone
    
    conn = get_db()
    
    # Check if incident exists
    row = conn.execute(
        "SELECT status FROM incidents WHERE incident_id = ?",
        (incident_id,)
    ).fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": f"Incident {incident_id} not found"}), 404
        
    acknowledged_at = datetime.now(timezone.utc).isoformat()
    
    conn.execute(
        """
        UPDATE incidents
        SET status = 'ACKNOWLEDGED',
            acknowledged_at = ?
        WHERE incident_id = ?
        """,
        (acknowledged_at, incident_id)
    )
    conn.commit()
    conn.close()
    
    if socketio:
        socketio.emit(
            "incident_status_change",
            {
                "incident_id": incident_id,
                "status": "ACKNOWLEDGED",
                "acknowledged_at": acknowledged_at
            }
        )
        
    return jsonify({
        "success": True,
        "incident_id": incident_id,
        "status": "ACKNOWLEDGED",
        "acknowledged_at": acknowledged_at
    })


# =========================================================
# GET HOTSPOTS
# =========================================================

@accidents_bp.route(
    "/hotspots",
    methods=["GET"]
)
def get_hotspots():
    """
    Return accident hotspots grouped by rounded GPS coordinates.
    """
    conn = get_db()
    
    # We round to 3 decimal places (~110m grid) for robust hotspot clustering
    rows = conn.execute(
        """
        SELECT 
            ROUND(lat, 3) as rounded_lat,
            ROUND(lng, 3) as rounded_lng,
            AVG(lat) as lat,
            AVG(lng) as lng,
            COUNT(*) as count,
            GROUP_CONCAT(incident_id) as incidents
        FROM incidents
        WHERE lat IS NOT NULL AND lng IS NOT NULL
        GROUP BY rounded_lat, rounded_lng
        ORDER BY count DESC
        """
    ).fetchall()
    
    conn.close()
    
    hotspots = []
    for row in rows:
        hotspots.append({
            "lat": row["lat"],
            "lng": row["lng"],
            "count": row["count"],
            "incidents": row["incidents"].split(",") if row["incidents"] else []
        })
        
    return jsonify(hotspots)


# =========================================================
# GET ANALYTICS
# =========================================================

@accidents_bp.route(
    "/analytics",
    methods=["GET"]
)
def get_analytics():
    """
    Return statistics for total incidents, severity distribution,
    accident frequency, vehicle types, and recurring locations.
    """
    conn = get_db()
    
    # 1. Total incidents
    total_row = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()
    total_incidents = total_row[0] if total_row else 0
    
    # 2. Severity distribution
    severity_rows = conn.execute(
        """
        SELECT severity, COUNT(*) as count 
        FROM incidents 
        GROUP BY severity
        """
    ).fetchall()
    severity_dist = {"LOW": 0, "MEDIUM": 0, "CRITICAL": 0}
    for row in severity_rows:
        sev = row["severity"]
        if sev in severity_dist:
            severity_dist[sev] = row["count"]
            
    # 3. Frequency by day (last 14 days)
    freq_rows = conn.execute(
        """
        SELECT date(timestamp) as date_val, COUNT(*) as count 
        FROM incidents 
        GROUP BY date_val 
        ORDER BY date_val DESC 
        LIMIT 14
        """
    ).fetchall()
    frequency = []
    for row in freq_rows:
        frequency.append({
            "date": row["date_val"],
            "count": row["count"]
        })
        
    # 4. Recurring locations (top 5)
    rec_rows = conn.execute(
        """
        SELECT 
            AVG(lat) as lat, 
            AVG(lng) as lng, 
            COUNT(*) as count 
        FROM incidents 
        GROUP BY ROUND(lat, 3), ROUND(lng, 3) 
        ORDER BY count DESC 
        LIMIT 5
        """
    ).fetchall()
    recurring_locations = []
    for row in rec_rows:
        recurring_locations.append({
            "lat": row["lat"],
            "lng": row["lng"],
            "count": row["count"]
        })
        
    # 5. Vehicle types distribution (derived from vehicles_involved column)
    vehicle_counts = {"Car": 0, "Motorcycle": 0, "Truck": 0, "Bus": 0, "Bicycle": 0}
    
    v_rows = conn.execute("SELECT vehicles_involved FROM incidents").fetchall()
    for row in v_rows:
        n = row["vehicles_involved"] or 0
        if n == 1:
            vehicle_counts["Car"] += 1
        elif n == 2:
            vehicle_counts["Car"] += 1
            vehicle_counts["Motorcycle"] += 1
        elif n == 3:
            vehicle_counts["Car"] += 2
            vehicle_counts["Motorcycle"] += 1
        elif n > 3:
            vehicle_counts["Car"] += 2
            vehicle_counts["Motorcycle"] += 1
            vehicle_counts["Truck"] += (n - 3)
            
    conn.close()
    
    return jsonify({
        "total_incidents": total_incidents,
        "severity_distribution": severity_dist,
        "frequency": frequency,
        "recurring_locations": recurring_locations,
        "vehicle_types": vehicle_counts
    })