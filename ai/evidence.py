"""
REFLEX - Evidence Capture Module

When the AI confirms an accident, this module:

1. Re-opens the video at the exact event frame
2. Burns a professional overlay onto the frame:
   - Incident ID badge (top-left)
   - Timestamp (top-right)
   - Severity label (bottom-left)
   - REFLEX watermark (bottom-right)
3. Saves the annotated JPEG to the evidence/ folder
4. Returns the relative file path for DB storage

This is intentionally separate from accident.py so that
the detection logic remains clean and testable on its own.
"""

import os
import cv2
from datetime import datetime


# =========================================================
# EVIDENCE DIRECTORY
# =========================================================

EVIDENCE_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)
    ),
    "evidence"
)


# =========================================================
# COLOUR PALETTE  (BGR for OpenCV)
# =========================================================

COLOURS = {
    "LOW":      (122, 212, 34),   # green
    "MEDIUM":   (11, 158, 245),   # amber
    "CRITICAL": (71, 61, 255),    # red
    "UNKNOWN":  (158, 122, 59),   # blue-grey
}

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
ACCENT = (255, 158, 59)          # electric blue


# =========================================================
# DRAW FILLED RECTANGLE  (helper)
# =========================================================

def _filled_rect(img, x1, y1, x2, y2, colour, alpha=0.65):
    """Draw a semi-transparent filled rectangle on img in-place."""
    overlay = img.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), colour, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)


# =========================================================
# DRAW TEXT WITH SHADOW  (helper)
# =========================================================

def _text(img, text, x, y, font_scale=0.5, colour=WHITE, thickness=1):
    """Draw text with a 1-px shadow for legibility on any background."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Shadow
    cv2.putText(img, text, (x + 1, y + 1), font,
                font_scale, BLACK, thickness + 1, cv2.LINE_AA)
    # Text
    cv2.putText(img, text, (x, y), font,
                font_scale, colour, thickness, cv2.LINE_AA)


# =========================================================
# MAIN — CAPTURE EVIDENCE FRAME
# =========================================================

def capture_evidence_frame(
    video_path,
    event_frame,
    incident_id,
    severity="UNKNOWN",
    timestamp=None
):
    """
    Seek to event_frame in video_path, annotate the frame,
    and save it as evidence/<incident_id>.jpg.

    Args:
        video_path  : absolute path to the source video
        event_frame : integer frame index where accident was detected
        incident_id : e.g. "RX-2026-001"
        severity    : "LOW" | "MEDIUM" | "CRITICAL" | "UNKNOWN"
        timestamp   : ISO-8601 string; defaults to now

    Returns:
        Relative path string "evidence/<incident_id>.jpg"
        or None if frame capture fails.
    """

    # ----------------------------------------------------------
    # Guard — nothing to capture if no frame index
    # ----------------------------------------------------------
    if event_frame is None:
        return None

    # ----------------------------------------------------------
    # Ensure evidence directory exists
    # ----------------------------------------------------------
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    # ----------------------------------------------------------
    # Open video and seek to the event frame
    # ----------------------------------------------------------
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"[evidence] Could not open video: {video_path}")
        return None

    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, event_frame - 1))
    ok, frame = cap.read()
    cap.release()

    if not ok or frame is None:
        print(f"[evidence] Could not read frame {event_frame}")
        return None

    # ----------------------------------------------------------
    # Frame dimensions
    # ----------------------------------------------------------
    h, w = frame.shape[:2]

    # ----------------------------------------------------------
    # Timestamp label
    # ----------------------------------------------------------
    ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    # ----------------------------------------------------------
    # Severity colour
    # ----------------------------------------------------------
    sev_colour = COLOURS.get(severity, COLOURS["UNKNOWN"])

    # ==============================================================
    # TOP-LEFT BADGE  —  INCIDENT ID
    # ==============================================================
    badge_pad = 8
    badge_text = f"  {incident_id}  "
    (tw, th), _ = cv2.getTextSize(
        badge_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1
    )
    bx1, by1 = 12, 12
    bx2, by2 = bx1 + tw + badge_pad * 2, by1 + th + badge_pad * 2
    _filled_rect(frame, bx1, by1, bx2, by2, (20, 20, 20), alpha=0.78)
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), ACCENT, 1)
    _text(frame, badge_text, bx1 + badge_pad, by1 + th + badge_pad - 2,
          font_scale=0.55, colour=ACCENT, thickness=1)

    # ==============================================================
    # TOP-RIGHT BADGE  —  TIMESTAMP
    # ==============================================================
    (tsw, tsh), _ = cv2.getTextSize(
        ts, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1
    )
    tx1 = w - tsw - badge_pad * 2 - 12
    ty1 = 12
    tx2 = w - 12
    ty2 = ty1 + tsh + badge_pad * 2
    _filled_rect(frame, tx1, ty1, tx2, ty2, (20, 20, 20), alpha=0.78)
    cv2.rectangle(frame, (tx1, ty1), (tx2, ty2), (80, 80, 80), 1)
    _text(frame, ts, tx1 + badge_pad, ty1 + tsh + badge_pad - 2,
          font_scale=0.40, colour=(200, 200, 200), thickness=1)

    # ==============================================================
    # BOTTOM-LEFT  —  SEVERITY STRIP
    # ==============================================================
    sev_label = f"  SEVERITY: {severity}  "
    (slw, slh), _ = cv2.getTextSize(
        sev_label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1
    )
    sl_y1 = h - slh - badge_pad * 2 - 12
    sl_y2 = h - 12
    _filled_rect(frame, 12, sl_y1, 12 + slw + badge_pad * 2, sl_y2,
                 sev_colour, alpha=0.72)
    _text(frame, sev_label, 12 + badge_pad, sl_y2 - badge_pad,
          font_scale=0.55, colour=WHITE, thickness=1)

    # ==============================================================
    # BOTTOM-RIGHT  —  REFLEX WATERMARK
    # ==============================================================
    wm_text = "⚡ REFLEX EVIDENCE"
    (wmw, wmh), _ = cv2.getTextSize(
        wm_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1
    )
    wm_x = w - wmw - badge_pad * 2 - 12
    wm_y1 = h - wmh - badge_pad * 2 - 12
    wm_y2 = h - 12
    _filled_rect(frame, wm_x - badge_pad, wm_y1, w - 12, wm_y2,
                 (20, 20, 20), alpha=0.72)
    _text(frame, wm_text, wm_x, wm_y2 - badge_pad,
          font_scale=0.45, colour=ACCENT, thickness=1)

    # ==============================================================
    # SAVE JPEG
    # ==============================================================
    filename    = f"{incident_id}.jpg"
    output_path = os.path.join(EVIDENCE_DIR, filename)

    success = cv2.imwrite(
        output_path,
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, 92]
    )

    if not success:
        print(f"[evidence] Failed to write {output_path}")
        return None

    relative_path = f"evidence/{filename}"
    print(f"[evidence] Saved: {relative_path}")
    return relative_path
