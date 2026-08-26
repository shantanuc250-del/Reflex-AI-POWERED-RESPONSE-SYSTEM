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
    Seek to before, event, and after frames in video_path, annotate them,
    and save the stitched image as evidence/<incident_id>.jpg.

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
    # Open video and determine FPS / frame counts
    # ----------------------------------------------------------
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"[evidence] Could not open video: {video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    offset_frames = int(2.0 * fps)
    before_idx = max(0, event_frame - offset_frames)
    during_idx = event_frame
    after_idx = min(total_frames - 1, event_frame + offset_frames)

    # Read BEFORE frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, before_idx - 1))
    ok, before_frame = cap.read()
    if not ok or before_frame is None:
        print(f"[evidence] Could not read before frame at {before_idx}")
        before_frame = None

    # Read DURING frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, during_idx - 1))
    ok, during_frame = cap.read()
    if not ok or during_frame is None:
        print(f"[evidence] Could not read during frame at {during_idx}")
        cap.release()
        return None

    # Read AFTER frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, after_idx - 1))
    ok, after_frame = cap.read()
    if not ok or after_frame is None:
        print(f"[evidence] Could not read after frame at {after_idx}")
        after_frame = None

    cap.release()

    # Fallbacks in case seek/read fails on edges
    if before_frame is None:
        before_frame = during_frame.copy()
    if after_frame is None:
        after_frame = during_frame.copy()

    # ----------------------------------------------------------
    # Resize frames to 640 width (maintaining aspect ratio)
    # ----------------------------------------------------------
    h, w = during_frame.shape[:2]
    target_w = 640
    target_h = int(h * (target_w / w))

    before_resized = cv2.resize(before_frame, (target_w, target_h))
    during_resized = cv2.resize(during_frame, (target_w, target_h))
    after_resized = cv2.resize(after_frame, (target_w, target_h))

    # ----------------------------------------------------------
    # Timestamp label
    # ----------------------------------------------------------
    ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    # ----------------------------------------------------------
    # Severity colour
    # ----------------------------------------------------------
    sev_colour = COLOURS.get(severity, COLOURS["UNKNOWN"])

    # ==============================================================
    # BEFORE PANEL ANNOTATIONS
    # ==============================================================
    before_txt = "BEFORE (-2.0s)"
    (btw, bth), _ = cv2.getTextSize(before_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.50, 2)
    bbx1, bby1 = 12, 12
    bbx2, bby2 = bbx1 + btw + 16, bby1 + bth + 16
    _filled_rect(before_resized, bbx1, bby1, bbx2, bby2, (20, 20, 20), alpha=0.78)
    cv2.rectangle(before_resized, (bbx1, bby1), (bbx2, bby2), (122, 212, 34), 1)  # Green border
    _text(before_resized, before_txt, bbx1 + 8, bby1 + bth + 8 - 2,
          font_scale=0.50, colour=(122, 212, 34), thickness=2)

    # ==============================================================
    # AFTER PANEL ANNOTATIONS
    # ==============================================================
    after_txt = "AFTER (+2.0s)"
    (atw, ath), _ = cv2.getTextSize(after_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.50, 2)
    abx1, aby1 = 12, 12
    abx2, aby2 = abx1 + atw + 16, aby1 + ath + 16
    _filled_rect(after_resized, abx1, aby1, abx2, aby2, (20, 20, 20), alpha=0.78)
    cv2.rectangle(after_resized, (abx1, aby1), (abx2, aby2), (71, 61, 255), 1)  # Red border
    _text(after_resized, after_txt, abx1 + 8, aby1 + ath + 8 - 2,
          font_scale=0.50, colour=(71, 61, 255), thickness=2)

    # ==============================================================
    # DURING PANEL ANNOTATIONS (original overlays scaled)
    # ==============================================================
    
    # "DURING (IMPACT)" label (top-center)
    during_txt = "DURING (IMPACT)"
    (dtw, dth), _ = cv2.getTextSize(during_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.50, 2)
    dbx1 = int((target_w - dtw) / 2) - 8
    dby1 = 12
    dbx2 = dbx1 + dtw + 16
    dby2 = dby1 + dth + 16
    _filled_rect(during_resized, dbx1, dby1, dbx2, dby2, (20, 20, 20), alpha=0.78)
    cv2.rectangle(during_resized, (dbx1, dby1), (dbx2, dby2), (11, 158, 245), 1)  # Amber border
    _text(during_resized, during_txt, dbx1 + 8, dby1 + dth + 8 - 2,
          font_scale=0.50, colour=(11, 158, 245), thickness=2)

    # TOP-LEFT BADGE  —  INCIDENT ID
    badge_pad = 8
    badge_text = f"  {incident_id}  "
    (tw, th), _ = cv2.getTextSize(
        badge_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1
    )
    bx1, by1 = 12, 12
    bx2, by2 = bx1 + tw + badge_pad * 2, by1 + th + badge_pad * 2
    _filled_rect(during_resized, bx1, by1, bx2, by2, (20, 20, 20), alpha=0.78)
    cv2.rectangle(during_resized, (bx1, by1), (bx2, by2), ACCENT, 1)
    _text(during_resized, badge_text, bx1 + badge_pad, by1 + th + badge_pad - 2,
          font_scale=0.55, colour=ACCENT, thickness=1)

    # TOP-RIGHT BADGE  —  TIMESTAMP
    (tsw, tsh), _ = cv2.getTextSize(
        ts, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1
    )
    tx1 = target_w - tsw - badge_pad * 2 - 12
    ty1 = 12
    tx2 = target_w - 12
    ty2 = ty1 + tsh + badge_pad * 2
    _filled_rect(during_resized, tx1, ty1, tx2, ty2, (20, 20, 20), alpha=0.78)
    cv2.rectangle(during_resized, (tx1, ty1), (tx2, ty2), (80, 80, 80), 1)
    _text(during_resized, ts, tx1 + badge_pad, ty1 + tsh + badge_pad - 2,
          font_scale=0.40, colour=(200, 200, 200), thickness=1)

    # BOTTOM-LEFT  —  SEVERITY STRIP
    sev_label = f"  SEVERITY: {severity}  "
    (slw, slh), _ = cv2.getTextSize(
        sev_label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1
    )
    sl_y1 = target_h - slh - badge_pad * 2 - 12
    sl_y2 = target_h - 12
    _filled_rect(during_resized, 12, sl_y1, 12 + slw + badge_pad * 2, sl_y2,
                 sev_colour, alpha=0.72)
    _text(during_resized, sev_label, 12 + badge_pad, sl_y2 - badge_pad,
          font_scale=0.55, colour=WHITE, thickness=1)

    # BOTTOM-RIGHT  —  REFLEX WATERMARK
    wm_text = "⚡ REFLEX EVIDENCE"
    (wmw, wmh), _ = cv2.getTextSize(
        wm_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1
    )
    wm_x = target_w - wmw - badge_pad * 2 - 12
    wm_y1 = target_h - wmh - badge_pad * 2 - 12
    wm_y2 = target_h - 12
    _filled_rect(during_resized, wm_x - badge_pad, wm_y1, target_w - 12, wm_y2,
                 (20, 20, 20), alpha=0.72)
    _text(during_resized, wm_text, wm_x, wm_y2 - badge_pad,
          font_scale=0.45, colour=ACCENT, thickness=1)

    # ==============================================================
    # HORIZONTAL CONCATENATION & SAVE
    # ==============================================================
    stitched_frame = cv2.hconcat([before_resized, during_resized, after_resized])

    filename    = f"{incident_id}.jpg"
    output_path = os.path.join(EVIDENCE_DIR, filename)

    success = cv2.imwrite(
        output_path,
        stitched_frame,
        [cv2.IMWRITE_JPEG_QUALITY, 92]
    )

    if not success:
        print(f"[evidence] Failed to write {output_path}")
        return None

    relative_path = f"evidence/{filename}"
    print(f"[evidence] Saved: {relative_path}")
    return relative_path
