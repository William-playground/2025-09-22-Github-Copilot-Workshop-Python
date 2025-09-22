from flask import Flask, jsonify, render_template, send_from_directory
import time
import threading
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Timer state management
class PomodoroTimer:
    def __init__(self):
        self.state = "stopped"  # stopped, running, paused
        self.start_time = None
        self.pause_time = None
        self.duration = 25 * 60  # 25 minutes in seconds
        self.remaining_time = self.duration
        self.last_update = time.time()
        self.today_completed = 0
        self.today_focus_time = 0  # in seconds
        self.today_date = datetime.now().date()
        
    def start(self):
        if self.state == "stopped":
            self.remaining_time = self.duration
        
        self.state = "running"
        self.start_time = time.time()
        self.last_update = time.time()
        
    def pause(self):
        if self.state == "running":
            self.state = "paused"
            self.pause_time = time.time()
            
    def resume(self):
        if self.state == "paused":
            self.state = "running"
            # Adjust start_time to account for pause duration
            pause_duration = time.time() - self.pause_time
            self.start_time += pause_duration
            self.last_update = time.time()
            
    def reset(self):
        self.state = "stopped"
        self.remaining_time = self.duration
        self.start_time = None
        self.pause_time = None
        self.last_update = time.time()
        
    def update(self):
        current_time = time.time()
        
        # Check if it's a new day
        if datetime.now().date() != self.today_date:
            self.today_completed = 0
            self.today_focus_time = 0
            self.today_date = datetime.now().date()
        
        if self.state == "running":
            elapsed = current_time - self.start_time
            self.remaining_time = max(0, self.duration - elapsed)
            
            # Timer completed
            if self.remaining_time <= 0:
                self.today_completed += 1
                self.today_focus_time += self.duration
                self.reset()
                
        self.last_update = current_time
        
    def get_state(self):
        self.update()
        
        # Format remaining time as mm:ss
        minutes = int(self.remaining_time // 60)
        seconds = int(self.remaining_time % 60)
        time_display = f"{minutes:02d}:{seconds:02d}"
        
        # Calculate progress percentage
        progress = ((self.duration - self.remaining_time) / self.duration) * 100
        if self.state == "stopped":
            progress = 0
            
        return {
            "state": self.state,
            "remaining_time": int(self.remaining_time),
            "time_display": time_display,
            "progress": round(progress, 1),
            "duration": self.duration
        }
        
    def get_today_stats(self):
        self.update()
        
        # Calculate total focus time in minutes
        total_minutes = self.today_focus_time // 60
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        focus_time_display = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        return {
            "completed_sessions": self.today_completed,
            "total_focus_time": self.today_focus_time,
            "focus_time_display": focus_time_display,
            "date": self.today_date.isoformat()
        }

# Global timer instance
timer = PomodoroTimer()

# Static file serving
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# API Routes
@app.route('/api/timer/state')
def get_timer_state():
    return jsonify(timer.get_state())

@app.route('/api/timer/start', methods=['POST'])
def start_timer():
    timer.start()
    return jsonify({"success": True, "message": "Timer started"})

@app.route('/api/timer/pause', methods=['POST'])
def pause_timer():
    timer.pause()
    return jsonify({"success": True, "message": "Timer paused"})

@app.route('/api/timer/resume', methods=['POST'])
def resume_timer():
    timer.resume()
    return jsonify({"success": True, "message": "Timer resumed"})

@app.route('/api/timer/reset', methods=['POST'])
def reset_timer():
    timer.reset()
    return jsonify({"success": True, "message": "Timer reset"})

@app.route('/api/stats/today')
def get_today_stats():
    return jsonify(timer.get_today_stats())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)