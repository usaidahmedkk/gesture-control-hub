"""Gesture Control Hub — Main Flask application."""

import threading
import cv2
from flask import Flask, Response, render_template, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
_lock = threading.Lock()
_active_project = None   # name of the currently running project
_processor = None        # module instance (AirMouse, AirCanvas, …)
_cap = None              # cv2.VideoCapture

# ---------------------------------------------------------------------------
# Lazy imports to avoid loading heavy libs unless a project is started
# ---------------------------------------------------------------------------

def _load_processor(project_name):
    """Instantiate and return the processor for *project_name*."""
    if project_name == "air_mouse":
        from modules.air_mouse import AirMouse
        return AirMouse()
    elif project_name == "air_canvas":
        from modules.air_canvas import AirCanvas
        return AirCanvas()
    elif project_name == "media_controller":
        from modules.media_controller import MediaController
        return MediaController()
    elif project_name == "presentation":
        from modules.presentation_controller import PresentationController
        return PresentationController()
    elif project_name == "sign_language":
        from modules.sign_language import SignLanguage
        return SignLanguage()
    else:
        return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _stop_current():
    """Stop & release whatever project is currently running (call with lock)."""
    global _active_project, _processor, _cap
    if _cap is not None:
        _cap.release()
        _cap = None
    if _processor is not None:
        try:
            _processor.release()
        except Exception:
            pass
        _processor = None
    _active_project = None


def _generate_frames(project_name):
    """Generator that yields MJPEG frames for *project_name*."""
    while True:
        with _lock:
            if _active_project != project_name or _cap is None:
                break
            ret, frame = _cap.read()
            if not ret:
                break
            try:
                frame = _processor.process_frame(frame)
            except Exception as exc:
                # Draw error on frame rather than crashing
                cv2.putText(frame, str(exc)[:60], (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/project/air_mouse")
def air_mouse_page():
    return render_template("air_mouse.html")


@app.route("/project/air_canvas")
def air_canvas_page():
    return render_template("air_canvas.html")


@app.route("/project/media_controller")
def media_controller_page():
    return render_template("media_controller.html")


@app.route("/project/presentation")
def presentation_page():
    return render_template("presentation.html")


@app.route("/project/sign_language")
def sign_language_page():
    return render_template("sign_language.html")


# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------

@app.route("/start/<project_name>", methods=["POST"])
def start_project(project_name):
    """Start a project's camera & processing."""
    global _active_project, _processor, _cap

    with _lock:
        # Stop any running project first
        _stop_current()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return jsonify({"status": "error", "message": "Camera not found"}), 500

        processor = _load_processor(project_name)
        if processor is None:
            cap.release()
            return jsonify({"status": "error", "message": "Unknown project"}), 400

        _cap = cap
        _processor = processor
        _active_project = project_name

    return jsonify({"status": "ok", "project": project_name})


@app.route("/stop/<project_name>", methods=["POST"])
def stop_project(project_name):
    """Stop the camera for the given project."""
    with _lock:
        if _active_project == project_name:
            _stop_current()
    return jsonify({"status": "ok"})


@app.route("/stop_all", methods=["POST"])
def stop_all():
    """Stop any active project (used when navigating back to dashboard)."""
    with _lock:
        _stop_current()
    return jsonify({"status": "ok"})


@app.route("/status/<project_name>")
def get_status(project_name):
    """Return current gesture status as JSON."""
    with _lock:
        if _active_project != project_name or _processor is None:
            return jsonify({"status": "inactive"})
        try:
            data = _processor.get_status()
        except Exception as exc:
            data = {"error": str(exc)}
    data["status"] = "active"
    return jsonify(data)


@app.route("/sign_language/action", methods=["POST"])
def sign_language_action():
    """Handle clear/space actions for the sign language interpreter."""
    action = request.json.get("action", "")
    with _lock:
        if _active_project == "sign_language" and _processor is not None:
            if action == "clear":
                _processor.clear_word()
            elif action == "space":
                _processor.add_space()
    return jsonify({"status": "ok"})


@app.route("/video_feed/<project_name>")
def video_feed(project_name):
    """MJPEG streaming endpoint."""
    return Response(
        _generate_frames(project_name),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
