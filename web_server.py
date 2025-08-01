from flask import Flask, jsonify
import threading
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "online",
        "service": "Lufthansa Virtual Airlines Discord Bot",
        "timestamp": datetime.now().isoformat(),
        "message": "Bot is running successfully"
    })

@app.route('/health')
def health():
    """Additional health check endpoint"""
    return jsonify({
        "status": "healthy",
        "uptime": "Bot operational"
    })

@app.route('/stats')
def stats():
    """Basic bot statistics endpoint"""
    return jsonify({
        "bot_name": "Lufthansa Virtual Airlines Bot",
        "features": [
            "Flight Logging System",
            "Rank Progression",
            "AI Assistant",
            "Session Tracking",
            "Flight Logbook"
        ],
        "commands": 6,
        "status": "operational"
    })

def run_web_server():
    """Run Flask web server in a separate thread"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

def start_web_server():
    """Start the web server in a background thread"""
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    print(f"Web server started on port {os.environ.get('PORT', 5000)}")

if __name__ == "__main__":
    run_web_server()