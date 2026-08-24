from ai.accident import analyze_video
from ai.severity import score_severity


# =========================================================
# VIDEO
# =========================================================

VIDEO_PATH = "videos/traffic.mp4"


print()
print("==========================================")
print("       REFLEX SEVERITY ANALYSIS")
print("==========================================")
print()

print("Analyzing accident...")

print()


# =========================================================
# RUN ACCIDENT DETECTION
# =========================================================

accident_result = analyze_video(
    VIDEO_PATH
)


# =========================================================
# PRINT ACCIDENT RESULT
# =========================================================

print("Accident detected:",
      accident_result.get(
          "event_detected"
      ))

print(
    "Accident confidence:",
    accident_result.get(
        "confidence",
        0
    )
)

print(
    "Vehicles involved:",
    accident_result.get(
        "vehicles_involved",
        0
    )
)

print(
    "Reason:",
    accident_result.get(
        "reason"
    )
)

print(
    "Event time:",
    accident_result.get(
        "event_time_sec"
    ),
    "seconds"
)


print()


# =========================================================
# CALCULATE SEVERITY
# =========================================================

severity_result = score_severity(
    accident_result
)


# =========================================================
# PRINT SEVERITY
# =========================================================

print("==========================================")
print("          SEVERITY RESULT")
print("==========================================")
print()

print(
    "Severity:",
    severity_result["severity"]
)

print(
    "Severity score:",
    severity_result["score"]
)

print(
    "Explanation:",
    severity_result["explanation"]
)

print()


# =========================================================
# FINAL RESULT
# =========================================================

if severity_result["severity"] == "CRITICAL":

    print("🔴 CRITICAL ACCIDENT")

elif severity_result["severity"] == "MEDIUM":

    print("🟡 MEDIUM ACCIDENT")

elif severity_result["severity"] == "LOW":

    print("🟢 LOW ACCIDENT")

else:

    print("✅ NO ACCIDENT")


print()
print("==========================================")
print("             TEST COMPLETE")
print("==========================================")