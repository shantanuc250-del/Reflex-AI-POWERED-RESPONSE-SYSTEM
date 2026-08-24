import cv2
from collections import Counter

from ai.detector import Detector


# ==========================================
# CREATE YOLO DETECTOR
# ==========================================

detector = Detector(conf=0.15)


# ==========================================
# OPEN VIDEO
# ==========================================

video_path = "videos/traffic.mp4"

video = cv2.VideoCapture(video_path)


if not video.isOpened():
    print("ERROR: Could not open video.")
    print("Check that this file exists:")
    print(video_path)
    exit()


print()
print("========================================")
print("       REFLEX YOLO VIDEO TEST")
print("========================================")
print()
print("Video opened successfully.")
print("Tracking vehicles and people...")
print()
print("Press Q to stop.")
print()


# ==========================================
# PROCESS VIDEO
# ==========================================

while True:

    ret, frame = video.read()

    # End of video
    if not ret:
        print("Video finished.")
        break


    # ======================================
    # RUN YOLO
    # ======================================

    detections = detector.track_frame(frame)


    # ======================================
    # COUNT OBJECTS
    # ======================================

    counts = Counter(
        obj["name"]
        for obj in detections
    )


    # ======================================
    # DRAW DETECTIONS
    # ======================================

    for obj in detections:

        x1, y1, x2, y2 = map(
            int,
            obj["box"]
        )

        object_name = obj["name"]
        object_id = obj["id"]


        # Draw bounding box

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )


        # Object label

        label = f"{object_name} ID:{object_id}"


        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )


    # ======================================
    # SHOW COUNTERS
    # ======================================

    y = 30

    for name, count in counts.items():

        text = f"{name}: {count}"

        cv2.putText(
            frame,
            text,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        y += 30


    # ======================================
    # DISPLAY VIDEO
    # ======================================

    cv2.imshow(
        "REFLEX - YOLO Tracking",
        frame
    )


    # ======================================
    # PRESS Q TO EXIT
    # ======================================

    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("Stopping...")
        break


# ==========================================
# CLEANUP
# ==========================================

video.release()

cv2.destroyAllWindows()

print()
print("REFLEX video test finished.")
