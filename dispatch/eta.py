"""
REFLEX - ETA Calculator

Estimates ambulance and hospital travel time.

This is a prototype calculation using distance
and estimated average speed.

A real deployment would use live routing and
traffic data.
"""


# =========================================================
# CALCULATE ETA
# =========================================================

def calculate_eta(
    distance_km,
    average_speed_kmh=40
):

    """
    Calculate estimated travel time.

    Parameters:
        distance_km:
            Distance in kilometers.

        average_speed_kmh:
            Estimated average road speed.

    Returns:
        ETA in minutes.
    """

    if distance_km <= 0:

        return 0


    if average_speed_kmh <= 0:

        average_speed_kmh = 40


    # Hours

    travel_hours = (
        distance_km
        /
        average_speed_kmh
    )


    # Minutes

    travel_minutes = (
        travel_hours
        *
        60
    )


    return round(
        travel_minutes,
        1
    )


# =========================================================
# AMBULANCE ETA
# =========================================================

def ambulance_eta(
    distance_km
):

    """
    Ambulances get a higher estimated
    average speed.
    """

    return calculate_eta(
        distance_km,
        average_speed_kmh=45
    )


# =========================================================
# HOSPITAL ETA
# =========================================================

def hospital_eta(
    distance_km
):

    return calculate_eta(
        distance_km,
        average_speed_kmh=35
    )