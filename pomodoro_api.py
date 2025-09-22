from flask import Flask, jsonify, request
from datetime import datetime
from pomodoro_session import get_pomodoro_db, get_pomodoro_timer, PomodoroSession


app = Flask(__name__)


@app.route('/api/stats/today', methods=['GET'])
def get_today_stats():
    """Get today's Pomodoro session statistics"""
    try:
        db = get_pomodoro_db()
        stats = db.get_today_stats()
        return jsonify({
            "success": True,
            "data": stats
        }), 200
    except Exception as e:
        # Log the actual error for debugging, but don't expose details to user
        print(f"Error in get_today_stats: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new Pomodoro session"""
    try:
        timer = get_pomodoro_timer()
        
        # Get parameters from request
        data = request.get_json() or {}
        duration_minutes = data.get('duration_minutes', 25)
        task_description = data.get('task_description', '')
        
        # Validate duration
        if not isinstance(duration_minutes, int) or duration_minutes <= 0 or duration_minutes > 240:
            return jsonify({
                "success": False,
                "error": "Duration must be between 1 and 240 minutes"
            }), 400
        
        session = timer.start_session(duration_minutes, task_description)
        
        return jsonify({
            "success": True,
            "data": {
                "session_id": session.id,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "duration_minutes": session.duration_minutes,
                "task_description": session.task_description
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        # Log the actual error for debugging, but don't expose details to user
        print(f"Error in start_session: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/session/complete', methods=['POST'])
def complete_session():
    """Complete the current Pomodoro session"""
    try:
        timer = get_pomodoro_timer()
        completed_session = timer.complete_session()
        
        if completed_session is None:
            return jsonify({
                "success": False,
                "error": "No active session to complete"
            }), 400
        
        return jsonify({
            "success": True,
            "data": {
                "session_id": completed_session.id,
                "start_time": completed_session.start_time.isoformat() if completed_session.start_time else None,
                "end_time": completed_session.end_time.isoformat() if completed_session.end_time else None,
                "duration_minutes": completed_session.duration_minutes,
                "completed": completed_session.completed,
                "task_description": completed_session.task_description
            }
        }), 200
        
    except Exception as e:
        # Log the actual error for debugging, but don't expose details to user
        print(f"Error in complete_session: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/session/cancel', methods=['POST'])
def cancel_session():
    """Cancel the current Pomodoro session"""
    try:
        timer = get_pomodoro_timer()
        cancelled_session = timer.cancel_session()
        
        if cancelled_session is None:
            return jsonify({
                "success": False,
                "error": "No active session to cancel"
            }), 400
        
        return jsonify({
            "success": True,
            "data": {
                "session_id": cancelled_session.id,
                "start_time": cancelled_session.start_time.isoformat() if cancelled_session.start_time else None,
                "end_time": cancelled_session.end_time.isoformat() if cancelled_session.end_time else None,
                "duration_minutes": cancelled_session.duration_minutes,
                "completed": cancelled_session.completed,
                "task_description": cancelled_session.task_description
            }
        }), 200
        
    except Exception as e:
        # Log the actual error for debugging, but don't expose details to user
        print(f"Error in cancel_session: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/session/status', methods=['GET'])
def get_session_status():
    """Get current session status"""
    try:
        timer = get_pomodoro_timer()
        current_session = timer.get_current_session()
        
        if current_session is None:
            return jsonify({
                "success": True,
                "data": {
                    "is_running": False,
                    "session": None
                }
            }), 200
        
        return jsonify({
            "success": True,
            "data": {
                "is_running": timer.is_running,
                "session": {
                    "start_time": current_session.start_time.isoformat() if current_session.start_time else None,
                    "duration_minutes": current_session.duration_minutes,
                    "task_description": current_session.task_description,
                    "elapsed_minutes": round(timer.get_elapsed_time(), 2),
                    "remaining_minutes": round(timer.get_remaining_time(), 2),
                    "is_complete": timer.is_session_complete()
                }
            }
        }), 200
        
    except Exception as e:
        # Log the actual error for debugging, but don't expose details to user
        print(f"Error in get_session_status: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "message": "Pomodoro API is running",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("Starting Pomodoro API server...")
    print("Available endpoints:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/stats/today - Today's statistics")
    print("  GET  /api/session/status - Current session status")
    print("  POST /api/session/start - Start new session")
    print("  POST /api/session/complete - Complete current session")
    print("  POST /api/session/cancel - Cancel current session")
    print()
    
    # In production, set debug=False for security
    debug_mode = False  # Change to True only for development
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)