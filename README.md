# Reflex — AI Emergency Response Network

*Faster than the first call.*

## Structure
```
REFLEX/
├── app.py                 # Flask entrypoint — run this
├── ai/
│   ├── detector.py         # YOLOv8 wrapper (raw detection)
│   ├── accident.py         # collision heuristic (uses detector.py)
│   └── severity.py         # rule-based severity scoring
├── api/
│   ├── accidents.py        # orchestrates pipeline, Socket.IO broadcast
│   ├── ambulance.py        # nearest hospital + OpenRouteService routing
│   └── hospital.py         # hospital CRUD (read)
├── database/
│   ├── db.py                # sqlite connection + schema (creates database.db)
│   └── database.db          # created automatically on first run
├── static/
│   ├── css/style.css
│   └── js/dashboard.js, hospital.js
├── templates/
│   ├── index.html           # landing page
│   ├── dashboard.html        # response console (with trigger controls)
│   └── hospital.html         # read-only hospital intake view
├── videos/                  # put your yt-dlp accident clips here
├── models/                  # put yolov8n.pt here (optional, see below)
└── requirements.txt
```

> Note: three empty `__init__.py` files exist in `ai/`, `api/`, `database/`
> so Python imports them as packages — not shown in the tree above but
> required, otherwise identical to your spec.

## Setup

```bash
cd REFLEX
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Get a free OpenRouteService key (no card needed):
https://openrouteservice.org/dev/#/signup

```bash
export ORS_API_KEY="your_key_here"
```

The database, tables, and mock hospitals are created automatically the
first time you run the app — nothing to set up manually. Just edit the
seed data in `database/db.py` (`init_db()`) with real hospitals near your
venue before the demo.

### Model weights (optional but recommended)
`ai/detector.py` looks for `models/yolov8n.pt` first, and falls back to
auto-downloading the standard model if it's not there. To pre-download it
into the right place so your demo doesn't depend on internet access on
stage:
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
# then move the downloaded weights file into models/yolov8n.pt
```

### Test clips
```bash
pip install yt-dlp
yt-dlp -f "best[height<=480]" -o "videos/clip1.mp4" "VIDEO_URL"
```

## Run it
```bash
python app.py
```
Open **http://localhost:8000** — landing page links to:
- `/dashboard` — the response console (map, incident feed, trigger button)
- `/hospital` — read-only incoming-case view (for a "hospital side" screen)

## Demo flow
1. Open `/dashboard` — hospital markers should already be on the map.
2. Enter a clip filename (must exist in `videos/`) and an accident lat/lng.
3. Click **Trigger Accident** — runs detection → severity → dispatch live.
4. Watch the incident card appear, the pulse line spike, and the route
   draw on the map — all pushed over Socket.IO in real time.
5. Optionally open `/hospital` in a second window/tab to show the
   "receiving end" of the same live event.

## What's real vs. simulated (say this in your pitch)
- **Real & live:** object detection, severity logic, nearest-hospital
  calculation, live routing/ETA via OpenRouteService, both dashboards,
  SQLite persistence of every incident.
- **Simulated for demo:** live CCTV feed (using pre-recorded clips from
  `videos/` instead), real hospital system integration (the `/hospital`
  page stands in for that).

## Division of labor
- **Person A (AI):** `ai/detector.py`, `ai/accident.py`, `ai/severity.py`
  — tune thresholds against your clips in `videos/`.
- **Person B (Backend/Frontend):** `api/*.py`, `app.py`, `templates/`,
  `static/` — wiring, dashboard polish, demo rehearsal.
