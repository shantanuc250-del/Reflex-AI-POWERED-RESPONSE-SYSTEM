"""
REFLEX - Emergency Dispatch Test

Tests:

1. Accident location
2. Nearest available ambulance
3. Nearest suitable hospital
4. Ambulance ETA
5. Hospital ETA
"""

from dispatch.dispatcher import (
    dispatch_emergency
)


# =========================================================
# DEMO ACCIDENT LOCATION
# =========================================================

ACCIDENT_LATITUDE = 28.4755

ACCIDENT_LONGITUDE = 77.5050


# =========================================================
# START
# =========================================================

print()

print(
    "=========================================="
)

print(
    "       REFLEX EMERGENCY DISPATCH"
)

print(
    "=========================================="
)

print()


# =========================================================
# ACCIDENT LOCATION
# =========================================================

print(
    "📍 ACCIDENT LOCATION"
)

print(
    "Latitude:",
    ACCIDENT_LATITUDE
)

print(
    "Longitude:",
    ACCIDENT_LONGITUDE
)

print()


# =========================================================
# RUN DISPATCH
# =========================================================

print(
    "Finding nearest emergency resources..."
)

print()


result = dispatch_emergency(

    ACCIDENT_LATITUDE,

    ACCIDENT_LONGITUDE

)


# =========================================================
# AMBULANCE RESULT
# =========================================================

ambulance = result.get(
    "ambulance"
)


print(
    "=========================================="
)

print(
    "             🚑 AMBULANCE"
)

print(
    "=========================================="
)

print()


if ambulance:

    print(
        "Status: DISPATCHED"
    )

    print(
        "Ambulance:",
        ambulance["name"]
    )

    print(
        "ID:",
        ambulance["id"]
    )

    print(
        "Status:",
        ambulance["status"]
    )

    print(
        "Distance:",
        ambulance["distance_km"],
        "km"
    )

    print(
        "ETA:",
        ambulance["eta_minutes"],
        "minutes"
    )

else:

    print(
        "❌ No available ambulance."
    )


print()


# =========================================================
# HOSPITAL RESULT
# =========================================================

hospital = result.get(
    "hospital"
)


print(
    "=========================================="
)

print(
    "             🏥 HOSPITAL"
)

print(
    "=========================================="
)

print()


if hospital:

    print(
        "Status: SELECTED"
    )

    print(
        "Hospital:",
        hospital["name"]
    )

    print(
        "ID:",
        hospital["id"]
    )

    print(
        "Hospital status:",
        hospital["status"]
    )

    print(
        "Distance:",
        hospital["distance_km"],
        "km"
    )

    print(
        "ETA:",
        hospital["eta_minutes"],
        "minutes"
    )

    print(
        "Emergency capacity:",
        hospital["emergency_capacity"]
    )

else:

    print(
        "❌ No suitable hospital available."
    )


print()


# =========================================================
# FINAL DISPATCH STATUS
# =========================================================

print(
    "=========================================="
)

print(
    "          🚨 DISPATCH STATUS"
)

print(
    "=========================================="
)

print()


if ambulance and hospital:

    print(
        "✅ EMERGENCY DISPATCH SUCCESSFUL"
    )

    print()

    print(
        "🚑 Ambulance:",
        ambulance["id"]
    )

    print(
        "⏱️ Ambulance ETA:",
        ambulance["eta_minutes"],
        "minutes"
    )

    print()

    print(
        "🏥 Hospital:",
        hospital["name"]
    )

    print(
        "⏱️ Hospital ETA:",
        hospital["eta_minutes"],
        "minutes"
    )

else:

    print(
        "⚠️ DISPATCH INCOMPLETE"
    )


print()

print(
    "=========================================="
)

print(
    "          DISPATCH TEST COMPLETE"
)

print(
    "=========================================="
)

print()