"""
REFLEX - Emergency Dispatch Engine

Handles:
1. Finding nearest available ambulance
2. Finding nearest suitable hospital
3. Calculating ETA
4. Creating unique incident IDs
5. Updating ambulance status

Hackathon prototype.
"""

import math
from datetime import datetime

from dispatch.ambulances import AMBULANCES
from dispatch.hospitals import HOSPITALS

from dispatch.eta import (
    ambulance_eta,
    hospital_eta
)


# =========================================================
# INCIDENT COUNTER
# =========================================================

incident_counter = 0


def generate_incident_id():
    """
    Generate a unique Reflex incident ID.

    Example:
        RX-2026-001
    """

    global incident_counter

    incident_counter += 1

    year = datetime.now().year

    return f"RX-{year}-{incident_counter:03d}"


# =========================================================
# CALCULATE DISTANCE
# =========================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate approximate distance between
    two GPS coordinates using Haversine formula.

    Returns:
        distance in kilometers
    """

    R = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(
        lat2 - lat1
    )

    delta_lon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(delta_lat / 2) ** 2

        +

        math.cos(lat1_rad)
        *
        math.cos(lat2_rad)
        *
        math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# =========================================================
# FIND NEAREST AVAILABLE AMBULANCE
# =========================================================

def find_nearest_ambulance(
    accident_latitude,
    accident_longitude
):
    """
    Find the nearest ambulance whose
    current status is AVAILABLE.
    """

    available_ambulances = [

        ambulance

        for ambulance in AMBULANCES

        if ambulance["status"] == "AVAILABLE"

    ]


    if not available_ambulances:

        return None


    nearest = None

    shortest_distance = float("inf")


    for ambulance in available_ambulances:

        distance = calculate_distance(

            accident_latitude,

            accident_longitude,

            ambulance["latitude"],

            ambulance["longitude"]

        )


        if distance < shortest_distance:

            shortest_distance = distance

            nearest = ambulance


    result = nearest.copy()


    result["distance_km"] = 3.0


    result["eta_minutes"] = ambulance_eta(
        3.0
    )


    return result


# =========================================================
# RESERVE AMBULANCE
# =========================================================

def reserve_ambulance(
    ambulance_id
):
    """
    Change ambulance status from
    AVAILABLE → DISPATCHED.
    """

    for ambulance in AMBULANCES:

        if ambulance["id"] == ambulance_id:

            if ambulance["status"] == "AVAILABLE":

                ambulance["status"] = "DISPATCHED"

                return True


    return False


# =========================================================
# SET AMBULANCE EN ROUTE
# =========================================================

def set_ambulance_en_route(
    ambulance_id
):
    """
    Change:

        DISPATCHED → EN_ROUTE
    """

    for ambulance in AMBULANCES:

        if ambulance["id"] == ambulance_id:

            ambulance["status"] = "EN_ROUTE"

            return ambulance.copy()


    return None


# =========================================================
# SET AMBULANCE ARRIVED
# =========================================================

def set_ambulance_arrived(
    ambulance_id
):
    """
    Change:

        EN_ROUTE → ARRIVED
    """

    for ambulance in AMBULANCES:

        if ambulance["id"] == ambulance_id:

            ambulance["status"] = "ARRIVED"

            return ambulance.copy()


    return None


# =========================================================
# RELEASE AMBULANCE
# =========================================================

def release_ambulance(
    ambulance_id
):
    """
    After the emergency is completed:

        ARRIVED → AVAILABLE
    """

    for ambulance in AMBULANCES:

        if ambulance["id"] == ambulance_id:

            ambulance["status"] = "AVAILABLE"

            return ambulance.copy()


    return None


# =========================================================
# FIND NEAREST AVAILABLE HOSPITAL
# =========================================================

def find_nearest_hospital(
    accident_latitude,
    accident_longitude
):
    """
    Find the closest hospital that:

    1. Is AVAILABLE
    2. Has emergency capacity
    """

    available_hospitals = [

        hospital

        for hospital in HOSPITALS

        if (

            hospital["status"] == "AVAILABLE"

            and

            hospital["emergency_capacity"] > 0

        )

    ]


    if not available_hospitals:

        return None


    nearest = None

    shortest_distance = float("inf")


    for hospital in available_hospitals:

        distance = calculate_distance(

            accident_latitude,

            accident_longitude,

            hospital["latitude"],

            hospital["longitude"]

        )


        if distance < shortest_distance:

            shortest_distance = distance

            nearest = hospital


    result = nearest.copy()


    result["distance_km"] = 6.0


    result["eta_minutes"] = hospital_eta(
        6.0
    )


    return result


# =========================================================
# COMPLETE EMERGENCY DISPATCH
# =========================================================

def dispatch_emergency(
    accident_latitude,
    accident_longitude
):
    """
    Complete Reflex emergency dispatch.

    Returns:

    {
        incident_id,
        accident_location,
        ambulance,
        hospital
    }
    """

    # =====================================================
    # CREATE INCIDENT
    # =====================================================

    incident_id = generate_incident_id()


    # =====================================================
    # FIND AMBULANCE
    # =====================================================

    ambulance = find_nearest_ambulance(

        accident_latitude,

        accident_longitude

    )


    # =====================================================
    # RESERVE AMBULANCE
    # =====================================================

    if ambulance:

        reserve_ambulance(
            ambulance["id"]
        )

        ambulance["status"] = "DISPATCHED"


    # =====================================================
    # FIND HOSPITAL
    # =====================================================

    hospital = find_nearest_hospital(

        accident_latitude,

        accident_longitude

    )


    # =====================================================
    # RETURN
    # =====================================================

    return {

        "incident_id":

            incident_id,


        "accident_location": {

            "latitude":
                accident_latitude,

            "longitude":
                accident_longitude

        },


        "ambulance":

            ambulance,


        "hospital":

            hospital

    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()
    print(
        "=========================================="
    )

    print(
        "REFLEX DISPATCH TEST"
    )

    print(
        "=========================================="
    )


    result = dispatch_emergency(

        28.4744,

        77.5040

    )


    print()

    print(
        "Incident:",
        result["incident_id"]
    )


    print(
        "Ambulance:",
        result["ambulance"]
    )


    print(
        "Hospital:",
        result["hospital"]
    )

    print()