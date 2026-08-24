import cv2

from ai.detector import Detector
from ai.accident import analyze_video
from ai.severity import score_severity


# =========================================================
# SETTINGS
# =========================================================

VIDEO_PATH = "videos/traffic.mp4"


# =========================================================
# STEP 1
# ANALYZE THE VIDEO
# =========================================================

print()
print("==========================================")
print("       REFLEX AI VIDEO DEMO")
print("==========================================")
print()

print("Step 1: Analyzing video...")
print("Please wait...")
print()


accident_result = analyze_video(
    VIDEO_PATH
)


# =========================================================
# STEP 2
# CALCULATE SEVERITY
# =========================================================

severity_result = score_severity(
    accident_result
)


# =========================================================
# PRINT AI RESULT
# =========================================================

print()
print("AI ANALYSIS COMPLETE")
print("------------------------------------------")

print(
    "Accident:",
    accident_result.get("event_detected")
)

print(
    "Confidence:",
    accident_result.get(
        "confidence",
        0
    )
)

print(
    "Event time:",
    accident_result.get(
        "event_time_sec"
    ),
    "seconds"
)

print(
    "Severity:",
    severity_result.get(
        "severity"
    )
)

print()


# =========================================================
# OPEN VIDEO AGAIN
# =========================================================

video = cv2.VideoCapture(
    VIDEO_PATH
)


if not video.isOpened():

    print("ERROR: Cannot open video.")

    exit()


# =========================================================
# VIDEO INFORMATION
# =========================================================

fps = video.get(
    cv2.CAP_PROP_FPS
) or 30


event_frame = accident_result.get(
    "event_frame"
)


event_detected = accident_result.get(
    "event_detected",
    False
)


severity = severity_result.get(
    "severity",
    "NONE"
)


confidence = accident_result.get(
    "confidence",
    0
)


vehicles_involved = accident_result.get(
    "vehicles_involved",
    0
)


# =========================================================
# CREATE YOLO DETECTOR
# =========================================================

detector = Detector(
    conf=0.15
)


# =========================================================
# DISPLAY VIDEO
# =========================================================

frame_number = 0


while True:

    ret, frame = video.read()


    if not ret:

        break


    frame_number += 1


    # =====================================================
    # RUN YOLO
    # =====================================================

    detections = detector.track_frame(
        frame
    )


    # =====================================================
    # DRAW OBJECTS
    # =====================================================

    for obj in detections:

        x1, y1, x2, y2 = map(
            int,
            obj["box"]
        )


        name = obj["name"]

        object_id = obj["id"]


        # Draw box

        cv2.rectangle(

            frame,

            (x1, y1),

            (x2, y2),

            (0, 255, 0),

            2

        )


        # Label

        label = (
            f"{name} ID:{object_id}"
        )


        cv2.putText(

            frame,

            label,

            (x1, max(y1 - 10, 20)),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            (0, 255, 0),

            2

        )


    # =====================================================
    # TOP BANNER
    # =====================================================

    cv2.rectangle(

        frame,

        (0, 0),

        (frame.shape[1], 75),

        (30, 30, 30),

        -1

    )


    cv2.putText(

        frame,

        "REFLEX - AI EMERGENCY RESPONSE",

        (20, 30),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (255, 255, 255),

        2

    )


    cv2.putText(

        frame,

        "YOLOv8s | LIVE ACCIDENT ANALYSIS",

        (20, 58),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        (200, 200, 200),

        1

    )


    # =====================================================
    # ACCIDENT ALERT
    # =====================================================

    if (

        event_detected

        and

        event_frame is not None

        and

        frame_number >= event_frame

    ):


        # Alert box

        cv2.rectangle(

            frame,

            (20, 95),

            (500, 235),

            (0, 0, 180),

            -1

        )


        cv2.putText(

            frame,

            "ACCIDENT DETECTED!",

            (40, 130),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.9,

            (255, 255, 255),

            2

        )


        cv2.putText(

            frame,

            f"Severity: {severity}",

            (40, 165),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2

        )


        cv2.putText(

            frame,

            f"Confidence: {confidence}%",

            (40, 195),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2

        )


        cv2.putText(

            frame,

            f"Vehicles: {vehicles_involved}",

            (40, 225),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            (255, 255, 255),

            2

        )


    else:


        # Normal status

        cv2.putText(

            frame,

            "STATUS: MONITORING",

            (20, 105),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 255, 0),

            2

        )


    # =====================================================
    # CURRENT TIME
    # =====================================================

    current_time = (
        frame_number / fps
    )


    time_text = (
        f"Time: {current_time:.1f}s"
    )


    cv2.putText(

        frame,

        time_text,

        (
            frame.shape[1] - 160,
            frame.shape[0] - 20
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.6,

        (255, 255, 255),

        2

    )


    # =====================================================
    # SHOW VIDEO
    # =====================================================

    cv2.imshow(

        "REFLEX - Emergency Detection",

        frame

    )


    # =====================================================
    # QUIT
    # =====================================================

    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        break


# =========================================================
# CLEANUP
# =========================================================

video.release()

cv2.destroyAllWindows()


print()
print("REFLEX video demo finished.")