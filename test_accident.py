from ai.accident import analyze_video


VIDEO_PATH = "videos/traffic.mp4"


print()
print("==========================================")
print("        REFLEX ACCIDENT ANALYZER")
print("==========================================")
print()

print("Video:", VIDEO_PATH)
print("Starting video analysis...")
print("Please wait...")
print()


result = analyze_video(VIDEO_PATH)


print()
print("==========================================")
print("             ANALYSIS RESULT")
print("==========================================")
print()

print(
    "Accident detected:",
    result.get("event_detected")
)

print(
    "Accident confidence:",
    result.get("confidence", 0)
)

print(
    "Reason:",
    result.get("reason")
)

print(
    "Vehicles involved:",
    result.get("vehicles_involved", 0)
)

print(
    "Event frame:",
    result.get("event_frame")
)

print(
    "Event time:",
    result.get("event_time_sec"),
    "seconds"
)

print()

if result.get("event_detected"):
    print("🚨 POSSIBLE ACCIDENT DETECTED!")
else:
    print("✅ No accident detected in this video.")

print()
print("==========================================")
print("             TEST COMPLETE")
print("==========================================")