"""
REFLEX - Accidents API

Complete emergency pipeline:

VIDEO
  ↓
ACCIDENT DETECTION
  ↓
SEVERITY
  ↓
INCIDENT ID
  ↓
AMBULANCE DISPATCH
  ↓
HOSPITAL SELECTION
  ↓
DATABASE
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

    payload = {

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),


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

    hospital_id = None

    distance_km = None

    duration_min = None


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
    # STEP 4
    # DATABASE
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


    conn.commit()

    conn.close()


    # =====================================================
    # STEP 5
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
# LIST PREVIOUS ACCIDENTS
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