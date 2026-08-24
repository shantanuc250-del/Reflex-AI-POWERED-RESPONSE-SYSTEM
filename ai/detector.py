"""
REFLEX - YOLO Detector

Detects and tracks:
- Person
- Bicycle
- Car
- Motorcycle
- Bus
- Truck

This file is responsible only for object detection
and tracking. Accident logic is handled separately
in ai/accident.py.
"""

import os

from ultralytics import YOLO


# =========================================================
# COCO CLASS IDs
# =========================================================

PERSON_CLASS = 0

# Vehicle class IDs
#
# 2 = Car
# 3 = Motorcycle
# 5 = Bus
# 7 = Truck

VEHICLE_CLASSES = {2, 3, 5, 7}


# Human-readable names

CLASS_NAMES = {
    0: "Person",
    1: "Bicycle",
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}


# =========================================================
# CLASSES THAT REFLEX WILL TRACK
# =========================================================

TRACK_CLASSES = [
    0,  # Person
    1,  # Bicycle
    2,  # Car
    3,  # Motorcycle
    5,  # Bus
    7   # Truck
]


# =========================================================
# MODEL LOCATION
# =========================================================

MODEL_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)
    ),
    "models"
)


MODEL_PATH = os.path.join(
    MODEL_DIR,
    "yolov8s.pt"
)


# =========================================================
# DETECTOR CLASS
# =========================================================

class Detector:

    def __init__(
        self,
        model_path=None,
        conf=0.15
    ):

        """
        Create YOLO detector.

        conf:
            Minimum detection confidence.

        0.15 is used because motorcycles and
        other small objects can be difficult
        to detect in traffic footage.
        """

        # If a custom model path is provided,
        # use it.

        if model_path:

            path = model_path

        # Otherwise use the model inside models/

        elif os.path.exists(MODEL_PATH):

            path = MODEL_PATH

        # If the model is not there,
        # Ultralytics will download it.

        else:

            path = "yolov8s.pt"


        print(
            f"Loading YOLO model: {path}"
        )


        # Load YOLO

        self.model = YOLO(path)


        # Save confidence threshold

        self.conf = conf


    # =====================================================
    # TRACK ONE FRAME
    # =====================================================

    def track_frame(self, frame):

        """
        Detect and track objects in one frame.

        Returns a list like:

        [
            {
                "id": 1,
                "cls": 2,
                "name": "Car",
                "box": [x1, y1, x2, y2]
            }
        ]
        """


        # -------------------------------------------------
        # Run YOLO tracking
        # -------------------------------------------------

        result = self.model.track(

            frame,

            # Detection confidence

            conf=self.conf,

            # Only track useful classes

            classes=TRACK_CLASSES,

            # Higher resolution helps with
            # small motorcycles/bikes

            imgsz=1280,

            # Keep IDs between frames

            persist=True,

            # Don't print information
            # for every frame

            verbose=False

        )[0]


        # -------------------------------------------------
        # Store detections
        # -------------------------------------------------

        detections = []


        # -------------------------------------------------
        # Check if objects were detected
        # -------------------------------------------------

        if (

            result.boxes is not None

            and

            result.boxes.id is not None

        ):


            # Bounding boxes

            boxes = (
                result.boxes.xyxy
                .cpu()
                .numpy()
            )


            # Class IDs

            classes = (
                result.boxes.cls
                .cpu()
                .numpy()
                .astype(int)
            )


            # Tracking IDs

            ids = (
                result.boxes.id
                .cpu()
                .numpy()
                .astype(int)
            )


            # -------------------------------------------------
            # Process every detection
            # -------------------------------------------------

            for box, cls, track_id in zip(
                boxes,
                classes,
                ids
            ):


                # Convert class ID
                # into a readable name

                name = CLASS_NAMES.get(
                    int(cls),
                    "Unknown"
                )


                # Add detection

                detections.append({

                    "id": int(track_id),

                    "cls": int(cls),

                    "name": name,

                    "box": box.tolist()

                })


        # Return all detections

        return detections


# =========================================================
# IOU FUNCTION
# =========================================================

def iou(box_a, box_b):

    """
    Calculate Intersection over Union.

    IoU tells us how much two bounding
    boxes overlap.

    Used by the accident detection engine.
    """


    # Box A

    xa1, ya1, xa2, ya2 = box_a


    # Box B

    xb1, yb1, xb2, yb2 = box_b


    # -----------------------------------------------------
    # Intersection coordinates
    # -----------------------------------------------------

    inter_x1 = max(
        xa1,
        xb1
    )

    inter_y1 = max(
        ya1,
        yb1
    )

    inter_x2 = min(
        xa2,
        xb2
    )

    inter_y2 = min(
        ya2,
        yb2
    )


    # -----------------------------------------------------
    # No overlap
    # -----------------------------------------------------

    if (

        inter_x2 <= inter_x1

        or

        inter_y2 <= inter_y1

    ):

        return 0.0


    # -----------------------------------------------------
    # Intersection area
    # -----------------------------------------------------

    inter_area = (

        (inter_x2 - inter_x1)

        *

        (inter_y2 - inter_y1)

    )


    # -----------------------------------------------------
    # Area of box A
    # -----------------------------------------------------

    area_a = (

        (xa2 - xa1)

        *

        (ya2 - ya1)

    )


    # -----------------------------------------------------
    # Area of box B
    # -----------------------------------------------------

    area_b = (

        (xb2 - xb1)

        *

        (yb2 - yb1)

    )


    # -----------------------------------------------------
    # IoU formula
    # -----------------------------------------------------

    return inter_area / float(

        area_a

        +

        area_b

        -

        inter_area

        +

        1e-6

    )


# =========================================================
# BOUNDING BOX CENTER
# =========================================================

def box_center(box):

    """
    Find the center of a bounding box.

    Example:

    [100, 200, 300, 400]

    returns:

    (200, 300)
    """


    x1, y1, x2, y2 = box


    return (

        (x1 + x2) / 2.0,

        (y1 + y2) / 2.0

    )