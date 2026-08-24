import cv2

from ai.detector import Detector
from ai.detector import VEHICLE_CLASSES
from ai.detector import box_center
from ai.detector import iou


# =========================================================
# SETTINGS
# =========================================================

VIDEO_PATH = "videos/traffic.mp4"

# Your accident happens at approximately 3 seconds
START_TIME = 2.5
END_TIME = 3.5


# =========================================================
# CREATE YOLO DETECTOR
# =========================================================

detector = Detector(conf=0.15)


# =========================================================
# OPEN VIDEO
# =========================================================

cap = cv2.VideoCapture(VIDEO_PATH)


if not cap.isOpened():

    print("ERROR: Could not open video.")

    print(
        "Check that this file exists:"
    )

    print(VIDEO_PATH)

    exit()


# =========================================================
# GET FPS
# =========================================================

fps = cap.get(
    cv2.CAP_PROP_FPS
)

if fps <= 0:

    fps = 30


print()
print("==========================================")
print("       REFLEX ACCIDENT DEBUGGER")
print("==========================================")
print()

print("Video:", VIDEO_PATH)

print("FPS:", fps)

print(
    "Checking from",
    START_TIME,
    "seconds to",
    END_TIME,
    "seconds"
)

print()

print("Accident expected around 3 seconds.")

print()


# =========================================================
# CONVERT TIME TO FRAME NUMBERS
# =========================================================

start_frame = int(
    START_TIME * fps
)

end_frame = int(
    END_TIME * fps
)


# =========================================================
# MOVE VIDEO TO START FRAME
# =========================================================

cap.set(
    cv2.CAP_PROP_POS_FRAMES,
    start_frame
)


frame_number = start_frame


# =========================================================
# PROCESS FRAMES
# =========================================================

while cap.isOpened():

    success, frame = cap.read()


    # Stop if video ends

    if not success:

        break


    # Stop after our debug range

    if frame_number > end_frame:

        break


    # =====================================================
    # RUN YOLO
    # =====================================================

    detections = detector.track_frame(
        frame
    )


    # =====================================================
    # KEEP ONLY VEHICLES
    # =====================================================

    vehicles = [

        detection

        for detection in detections

        if detection["cls"]
        in VEHICLE_CLASSES

    ]


    # =====================================================
    # PRINT FRAME INFORMATION
    # =====================================================

    current_time = (
        frame_number / fps
    )


    print()
    print("------------------------------------------")

    print(
        f"FRAME {frame_number} "
        f"TIME {current_time:.2f}s"
    )

    print(
        "Vehicles detected:",
        len(vehicles)
    )


    # =====================================================
    # PRINT EVERY VEHICLE
    # =====================================================

    for vehicle in vehicles:

        track_id = vehicle["id"]

        name = vehicle["name"]

        box = vehicle["box"]


        # Calculate center

        center = box_center(
            box
        )


        print(

            f"  {name} "
            f"ID={track_id} "
            f"center=("
            f"{center[0]:.1f}, "
            f"{center[1]:.1f}"
            f")"

        )


    # =====================================================
    # CHECK PAIRWISE OVERLAP
    # =====================================================

    if len(vehicles) >= 2:

        print()

        print(
            "Vehicle overlap:"
        )


    for i in range(
        len(vehicles)
    ):

        for j in range(
            i + 1,
            len(vehicles)
        ):


            vehicle_a = vehicles[i]

            vehicle_b = vehicles[j]


            # Calculate IoU

            overlap = iou(

                vehicle_a["box"],

                vehicle_b["box"]

            )


            # Only print actual overlap

            if overlap > 0:

                print(

                    f"  "
                    f"{vehicle_a['name']} "
                    f"#{vehicle_a['id']} "
                    f"<-> "
                    f"{vehicle_b['name']} "
                    f"#{vehicle_b['id']} "
                    f"IOU={overlap:.3f}"

                )


    # =====================================================
    # NEXT FRAME
    # =====================================================

    frame_number += 1


# =========================================================
# CLEANUP
# =========================================================

cap.release()


print()
print("==========================================")
print("            DEBUG COMPLETE")
print("==========================================")
print()

print(
    "The accident area was checked from",
    START_TIME,
    "to",
    END_TIME,
    "seconds."
)

print()