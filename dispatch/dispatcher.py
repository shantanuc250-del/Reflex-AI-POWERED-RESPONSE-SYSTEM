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
    two GPS coordinates using the Haversine formula.

    Returns:
        distance in kilometers
    """

    R = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
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

    Returns:
        Ambulance information including
        real distance and ETA.
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

    if nearest is None:
        return None

    result = nearest.copy()

    # Use the REAL calculated distance
    result["distance_km"] = round(
        shortest_distance,
        2
    )

    # Calculate ETA from REAL distance
    result["eta_minutes"] = ambulance_eta(
        shortest_distance
    )

    return result


# =========================================================
# RESERVE AMBULANCE
# =========================================================

def reserve_ambulance(
    ambulance_id
):
    """
    Change ambulance status:

        AVAILABLE → DISPATCHED
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
    Release ambulance back to the network.

        DISPATCHED / EN_ROUTE / ARRIVED
        → AVAILABLE
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

    if nearest is None:
        return None

    result = nearest.copy()

    # Use the REAL calculated distance
    result["distance_km"] = round(
        shortest_distance,
        2
    )

    # Calculate ETA from REAL distance
    result["eta_minutes"] = hospital_eta(
        shortest_distance
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

    For the hackathon simulation, the ambulance is
    automatically released after the dispatch result
    is created so repeated simulations can continue.
    """

    # =====================================================
    # CREATE INCIDENT
    # =====================================================

    incident_id = generate_incident_id()


    # =====================================================
    # FIND NEAREST AMBULANCE
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

        # The returned object should show DISPATCHED
        ambulance["status"] = "DISPATCHED"


    # =====================================================
    # FIND NEAREST HOSPITAL
    # =====================================================

    hospital = find_nearest_hospital(
        accident_latitude,
        accident_longitude
    )


    # =====================================================
    # CREATE RESULT
    # =====================================================

    result = {

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


    # =====================================================
    # DEMO MODE - RELEASE AMBULANCE
    # =====================================================
    #
    # The dashboard already received the ambulance
    # as DISPATCHED in the result above.
    #
    # We release it internally so another simulated
    # accident can use an ambulance again.
    #
    # This prevents:
    #
    # Accident 1 → DISPATCHED
    # Accident 2 → DISPATCHED
    # Accident 3 → DISPATCHED
    # Accident 4 → DISPATCHED
    # Accident 5 → NO AMBULANCE
    #
    # Instead, every demo simulation can dispatch again.

    if ambulance:

        release_ambulance(
            ambulance["id"]
        )


    # =====================================================
    # RETURN RESULT
    # =====================================================

    return result


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