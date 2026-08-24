"""
REFLEX - Accident Severity Engine

Converts the accident detection result into:

LOW
MEDIUM
CRITICAL

The scoring is rule-based and explainable, making it
easy to demonstrate and defend during a hackathon.

IMPORTANT:
This is a prototype severity estimate, NOT a medical
diagnosis or clinical triage system.
"""


# =========================================================
# MAIN SEVERITY FUNCTION
# =========================================================

def score_severity(
    detection_result: dict,
    person_down: bool = False
) -> dict:

    """
    Calculate accident severity.

    Parameters
    ----------
    detection_result : dict
        Output from ai.accident.analyze_video()

    person_down : bool
        Optional signal indicating a person appears
        stationary/down near the accident.

    Returns
    -------
    dict

    Example:

    {
        "severity": "CRITICAL",
        "score": 82,
        "explanation": "...",
    }
    """


    # =====================================================
    # NO ACCIDENT
    # =====================================================

    if not detection_result.get(
        "event_detected",
        False
    ):

        return {

            "severity": "NONE",

            "score": 0,

            "explanation":
                "No accident detected."

        }


    # =====================================================
    # INITIAL SCORE
    # =====================================================

    score = 0

    reasons = []


    # =====================================================
    # ACCIDENT CONFIDENCE
    # =====================================================

    confidence = detection_result.get(
        "confidence",
        0
    )


    # Strong AI collision confidence

    if confidence >= 80:

        score += 30

        reasons.append(
            "Very strong collision evidence"
        )


    elif confidence >= 65:

        score += 20

        reasons.append(
            "Strong collision evidence"
        )


    elif confidence >= 55:

        score += 10

        reasons.append(
            "Moderate collision evidence"
        )


    # =====================================================
    # NUMBER OF VEHICLES
    # =====================================================

    vehicles_involved = detection_result.get(
        "vehicles_involved",
        0
    )


    if vehicles_involved >= 4:

        score += 30

        reasons.append(
            f"{vehicles_involved} vehicles involved"
        )


    elif vehicles_involved == 3:

        score += 25

        reasons.append(
            "3 vehicles involved"
        )


    elif vehicles_involved == 2:

        score += 15

        reasons.append(
            "2 vehicles involved"
        )


    elif vehicles_involved == 1:

        score += 5

        reasons.append(
            "1 vehicle involved"
        )


    # =====================================================
    # COLLISION REASONS
    # =====================================================

    reason = detection_result.get(
        "reason",
        ""
    )


    # Make sure reason is a string

    reason = str(reason).lower()


    # -----------------------------------------------------
    # Strong vehicle overlap
    # -----------------------------------------------------

    if (
        "strong_vehicle_overlap"
        in reason
    ):

        score += 20

        reasons.append(
            "Strong vehicle overlap detected"
        )


    # -----------------------------------------------------
    # Normal vehicle overlap
    # -----------------------------------------------------

    elif (
        "vehicle_overlap"
        in reason
    ):

        score += 10

        reasons.append(
            "Vehicle collision overlap detected"
        )


    # -----------------------------------------------------
    # Rapid approach
    # -----------------------------------------------------

    if (
        "rapid_vehicle_approach"
        in reason
    ):

        score += 15

        reasons.append(
            "Vehicles rapidly approached each other"
        )


    # -----------------------------------------------------
    # Sudden speed change
    # -----------------------------------------------------

    if (
        "sudden_speed_change"
        in reason
    ):

        score += 20

        reasons.append(
            "Sudden vehicle speed change detected"
        )


    # =====================================================
    # PERSON DOWN SIGNAL
    # =====================================================

    if person_down:

        score += 30

        reasons.append(
            "Possible person down/stationary near accident"
        )


    # =====================================================
    # LIMIT SCORE
    # =====================================================

    score = min(
        score,
        100
    )


    # =====================================================
    # DETERMINE SEVERITY
    # =====================================================

    if score >= 70:

        severity = "CRITICAL"


    elif score >= 40:

        severity = "MEDIUM"


    else:

        severity = "LOW"


    # =====================================================
    # EXPLANATION
    # =====================================================

    explanation = "; ".join(
        reasons
    )


    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "severity": severity,

        "score": score,

        "explanation": explanation

    }