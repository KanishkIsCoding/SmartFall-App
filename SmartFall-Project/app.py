from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from flask import render_template 



app = Flask(__name__)
CORS(app)

alertData = {
    "fall": False,
    "bpm": 75,
    "gforce": 1.0,
    "accX": 0.0,
    "gyroX": 0.0,
    "timestamp": ""
}

reset_timer = None

@app.route("/")
def index():
    return render_template("index.html")

def reset_fall_status():
    global alertData
    alertData["fall"] = False
    print("🔄 Fall status reset to Normal")

@app.route("/fall-alert", methods=["POST"])
def update():
    """
    Endpoint for ESP32 to send multi-sensor data.
    Expected JSON: {"fall": bool, "bpm": int, "gforce": float, "accX": float, "gyroX": float}
    """
    global alertData, reset_timer
    
    data = request.json or {}
    
    # Update global state with all sensor parameters
    alertData["fall"] = data.get("fall", False)
    alertData["bpm"] = data.get("bpm", alertData["bpm"]) # Fallback to last known BPM
    alertData["gforce"] = data.get("gforce", 1.0)
    alertData["accX"] = data.get("accX", 0.0)
    alertData["gyroX"] = data.get("gyroX", 0.0)
    alertData["timestamp"] = data.get("timestamp", "N/A")

    print(f"🔥 Telemetry Received | BPM: {alertData['bpm']} | G: {alertData['gforce']} | Fall: {alertData['fall']}")

    # Handle the emergency timer
    if alertData["fall"]:
        if reset_timer is not None:
            reset_timer.cancel()
        reset_timer = threading.Timer(10, reset_fall_status)
        reset_timer.start()

    return jsonify({"status": "success"}), 200

@app.route("/fall-update", methods=["GET"])
def alert():
    """Endpoint for the Frontend Dashboard to pull the latest data."""
    return jsonify(alertData)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)