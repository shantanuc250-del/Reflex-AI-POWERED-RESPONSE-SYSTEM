"""
REFLEX - Accident Detection Engine

Detects possible road accidents using:

1. Vehicle overlap
2. Rapidly decreasing distance
3. Sudden speed change
4. Multiple vehicles
5. Persistent collision evidence across frames

The persistence requirement helps reduce false positives
caused by normal traffic movement.

This is a hackathon prototype, not a production
or medical-grade accident detection system.
"""

import cv2
import math

from ai.detector import (
    Detector,
    iou,
    box_center,
    VEHICLE_CLASSES
)


# =========================================================
# SETTINGS
# =========================================================

# Minimum score needed for a suspicious collision
ACCIDENT_SCORE_THRESHOLD = 55


# IoU values
IOU_THRESHOLD = 0.08
STRONG_IOU_THRESHOLD = 0.20


# Speed change
SPEED_DROP_THRESHOLD = 0.45
MIN_SPEED = 4


# History
MIN_HISTORY = 4
MAX_HISTORY = 15


# Distance change
DISTANCE_DROP_RATIO = 0.25


# IMPORTANT:
# Collision evidence must remain strong for several
# consecutive frames before we declare an accident.

REQUIRED_CONFIRMATION_FRAMES = 3


# =========================================================
# DISTANCE
# =========================================================

def distance(point_a, point_b):

    return math.sqrt(

        (point_a[0] - point_b[0]) ** 2

        +

        (point_a[1] - point_b[1]) ** 2

    )


# =========================================================
# MAIN ACCIDENT ANALYSIS
# =========================================================

def analyze_video(
    video_path,
    detector=None,
    sample_every_n=1
):

    # -----------------------------------------------------
    # Create detector
    # -----------------------------------------------------

    detector = detector or Detector(
        conf=0.15
    )


    # -----------------------------------------------------
    # Open video
    # -----------------------------------------------------

    cap = cv2.VideoCapture(
        video_path
    )


    if not cap.isOpened():

        return {
            "event_detected": False,
            "event_frame": None,
            "event_time_sec": None,
            "reason": "video_open_failed",
            "confidence": 0,
            "vehicles_involved": 0
        }


    # -----------------------------------------------------
    # FPS
    # -----------------------------------------------------

    fps = cap.get(
        cv2.CAP_PROP_FPS
    ) or 30


    # -----------------------------------------------------
    # Vehicle movement history
    #
    # track_id:
    #
    # [
    #   (frame, x, y),
    #   ...
    # ]
    # -----------------------------------------------------

    track_history = {}


    # -----------------------------------------------------
    # Distance history between vehicle pairs
    # -----------------------------------------------------

    pair_distances = {}


    # -----------------------------------------------------
    # Confirmation counter
    #
    # pair -> number of consecutive suspicious frames
    # -----------------------------------------------------

    pair_confirmation = {}


    frame_idx = 0


    # -----------------------------------------------------
    # Default result
    # -----------------------------------------------------

    result = {

        "event_detected": False,

        "event_frame": None,

        "event_time_sec": None,

        "reason": None,

        "confidence": 0,

        "vehicles_involved": 0

    }


    # =====================================================
    # VIDEO LOOP
    # =====================================================

    while cap.isOpened():


        # -------------------------------------------------
        # Read frame
        # -------------------------------------------------

        ok, frame = cap.read()


        if not ok:

            break


        frame_idx += 1


        # -------------------------------------------------
        # Frame sampling
        # -------------------------------------------------

        if frame_idx % sample_every_n != 0:

            continue


        # -------------------------------------------------
        # YOLO detection
        # -------------------------------------------------

        detections = detector.track_frame(
            frame
        )


        # -------------------------------------------------
        # Keep vehicles only
        # -------------------------------------------------

        vehicles = [

            d

            for d in detections

            if d["cls"] in VEHICLE_CLASSES

        ]


        # =================================================
        # UPDATE TRACK HISTORY
        # =================================================

        for vehicle in vehicles:


            track_id = vehicle["id"]


            center = box_center(
                vehicle["box"]
            )


            history = track_history.setdefault(
                track_id,
                []
            )


            history.append(

                (
                    frame_idx,
                    center[0],
                    center[1]
                )

            )


            if len(history) > MAX_HISTORY:

                history.pop(0)


        # =================================================
        # FIND BEST COLLISION CANDIDATE
        # =================================================

        best_score = 0

        best_reasons = []

        best_involved = set()

        best_pair = None


        # =================================================
        # CHECK VEHICLE PAIRS
        # =================================================

        for i in range(
            len(vehicles)
        ):


            for j in range(
                i + 1,
                len(vehicles)
            ):


                vehicle_a = vehicles[i]

                vehicle_b = vehicles[j]


                id_a = vehicle_a["id"]

                id_b = vehicle_b["id"]


                pair_key = tuple(
                    sorted(
                        [id_a, id_b]
                    )
                )


                # -------------------------------------------------
                # Centers
                # -------------------------------------------------

                center_a = box_center(
                    vehicle_a["box"]
                )

                center_b = box_center(
                    vehicle_b["box"]
                )


                # -------------------------------------------------
                # Current distance
                # -------------------------------------------------

                current_distance = distance(
                    center_a,
                    center_b
                )


                # -------------------------------------------------
                # Previous distance
                # -------------------------------------------------

                previous_distance = pair_distances.get(
                    pair_key
                )


                # Save current distance

                pair_distances[
                    pair_key
                ] = current_distance


                # -------------------------------------------------
                # IoU
                # -------------------------------------------------

                overlap = iou(

                    vehicle_a["box"],

                    vehicle_b["box"]

                )


                score = 0

                reasons = []


                # =================================================
                # SIGNAL 1
                # OVERLAP
                # =================================================

                if overlap >= STRONG_IOU_THRESHOLD:

                    score += 40

                    reasons.append(
                        "strong_vehicle_overlap"
                    )

                elif overlap >= IOU_THRESHOLD:

                    score += 25

                    reasons.append(
                        "vehicle_overlap"
                    )


                # =================================================
                # SIGNAL 2
                # RAPID APPROACH
                # =================================================

                if previous_distance is not None:

                    distance_change = (

                        previous_distance
                        -
                        current_distance

                    )


                    if (

                        previous_distance > 0

                        and

                        distance_change
                        >
                        previous_distance
                        *
                        DISTANCE_DROP_RATIO

                    ):

                        score += 30

                        reasons.append(
                            "rapid_vehicle_approach"
                        )


                # =================================================
                # SIGNAL 3
                # SUDDEN SPEED CHANGE
                # =================================================

                speed_change_detected = False


                for vehicle in (
                    vehicle_a,
                    vehicle_b
                ):


                    track_id = vehicle["id"]


                    history = track_history.get(
                        track_id,
                        []
                    )


                    if len(history) < MIN_HISTORY:

                        continue


                    # Older movement

                    _, x0, y0 = history[-4]

                    _, x1, y1 = history[-3]


                    # Recent movement

                    _, x2, y2 = history[-2]

                    _, x3, y3 = history[-1]


                    # Previous speed

                    previous_speed = math.sqrt(

                        (x1 - x0) ** 2

                        +

                        (y1 - y0) ** 2

                    )


                    # Current speed

                    current_speed = math.sqrt(

                        (x3 - x2) ** 2

                        +

                        (y3 - y2) ** 2

                    )


                    # Check sudden slowdown

                    if (

                        previous_speed > MIN_SPEED

                        and

                        current_speed
                        <
                        previous_speed
                        *
                        (
                            1
                            -
                            SPEED_DROP_THRESHOLD
                        )

                    ):

                        speed_change_detected = True

                        break


                if speed_change_detected:

                    score += 30

                    reasons.append(
                        "sudden_speed_change"
                    )


                # =================================================
                # SIGNAL 4
                # MULTIPLE VEHICLES
                # =================================================

                if score > 0:

                    score += 10

                    reasons.append(
                        "multiple_vehicles_involved"
                    )


                # =================================================
                # CONFIRMATION SYSTEM
                # =================================================

                # A pair is suspicious only if it has
                # meaningful collision evidence.

                suspicious = (

                    score
                    >=
                    ACCIDENT_SCORE_THRESHOLD

                )


                if suspicious:

                    pair_confirmation[pair_key] = (

                        pair_confirmation.get(
                            pair_key,
                            0
                        )

                        + 1

                    )

                else:

                    # Reset if evidence disappears

                    pair_confirmation[pair_key] = 0


                # =================================================
                # REQUIRE MULTIPLE CONSECUTIVE FRAMES
                # =================================================

                confirmed_frames = pair_confirmation.get(
                    pair_key,
                    0
                )


                if (

                    confirmed_frames
                    >=
                    REQUIRED_CONFIRMATION_FRAMES

                ):


                    # This is now a confirmed
                    # collision candidate.

                    if score > best_score:

                        best_score = score

                        best_reasons = reasons

                        best_involved = {
                            id_a,
                            id_b
                        }

                        best_pair = pair_key


        # =====================================================
        # ACCIDENT CONFIRMED
        # =====================================================

        if best_pair is not None:


            cap.release()


            unique_reasons = list(
                dict.fromkeys(
                    best_reasons
                )
            )


            return {

                "event_detected": True,

                "event_frame": frame_idx,

                "event_time_sec": round(
                    frame_idx / fps,
                    2
                ),

                "reason": ", ".join(
                    unique_reasons
                ),

                "confidence": min(
                    best_score,
                    100
                ),

                "vehicles_involved": len(
                    best_involved
                )

            }


    # =====================================================
    # NO ACCIDENT
    # =====================================================

    cap.release()


    return result