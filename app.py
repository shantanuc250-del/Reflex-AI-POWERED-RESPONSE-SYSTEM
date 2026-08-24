"""
REFLEX - Main Application

Run:
    python app.py

Then open:
    http://127.0.0.1:8000/dashboard
"""

from flask import (
    Flask,
    render_template,
    send_from_directory
)

from flask_socketio import SocketIO

from database.db import init_db

from api.hospital import hospital_bp

from api.ambulance import ambulance_bp

from api.accidents import (
    accidents_bp,
    init_socketio
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "reflex-hackathon-demo"


# =========================================================
# SOCKET.IO
# =========================================================

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)


# Give Socket.IO instance to accidents API

init_socketio(socketio)


# =========================================================
# BLUEPRINTS
# =========================================================

app.register_blueprint(
    hospital_bp
)

app.register_blueprint(
    ambulance_bp
)

app.register_blueprint(
    accidents_bp
)


# =========================================================
# MAIN PAGES
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html"
    )


@app.route("/hospital")
def hospital_view():

    return render_template(
        "hospital.html"
    )


# =========================================================
# VIDEO SERVING
# =========================================================

@app.route("/videos/<path:filename>")
def serve_video(filename):

    return send_from_directory(
        "videos",
        filename
    )


# =========================================================
# EVIDENCE IMAGE SERVING
# =========================================================

@app.route("/evidence/<path:filename>")
def serve_evidence(filename):
    """Serve captured accident evidence frames."""

    return send_from_directory(
        "evidence",
        filename
    )



# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    init_db()

    print()
    print(
        "=========================================="
    )

    print(
        "          ⚡ REFLEX SERVER"
    )

    print(
        "=========================================="
    )

    print()

    print(
        "Dashboard:"
    )

    print(
        "http://127.0.0.1:8000/dashboard"
    )

    print()

    print(
        "Video directory:"
    )

    print(
        "http://127.0.0.1:8000/videos/"
    )

    print()

    print(
        "=========================================="
    )

    print()

    socketio.run(
        app,
        host="0.0.0.0",
        port=8000,
        debug=True,
        allow_unsafe_werkzeug=True
    )