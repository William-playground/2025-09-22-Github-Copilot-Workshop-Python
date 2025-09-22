"""
Pomodoro Timer REST API Server
Provides REST endpoints for timer state management
"""

from flask import Flask, jsonify, request
import logging
from timer_state import TimerManager, TimerStateError, TimerConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global timer manager instance
timer_manager = TimerManager()


@app.errorhandler(TimerStateError)
def handle_timer_state_error(e):
    """Handle timer state errors with appropriate HTTP status codes"""
    logger.error(f"Timer state error: {str(e)}")
    return jsonify({"error": str(e), "type": "invalid_transition"}), 409


@app.errorhandler(400)
def handle_bad_request(e):
    """Handle bad request errors"""
    logger.error(f"Bad request: {str(e)}")
    return jsonify({"error": "Bad request", "type": "validation_error"}), 400


@app.errorhandler(422)
def handle_unprocessable_entity(e):
    """Handle unprocessable entity errors"""
    logger.error(f"Unprocessable entity: {str(e)}")
    return jsonify({"error": "Unprocessable entity", "type": "validation_error"}), 422


@app.errorhandler(500)
def handle_internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({"error": "Internal server error", "type": "server_error"}), 500


@app.route('/api/timer/state', methods=['GET'])
def get_timer_state():
    """Get current timer state"""
    try:
        # Check for auto-transitions before returning state
        auto_transition = timer_manager.check_auto_transitions()
        if auto_transition:
            logger.info("Auto-transition occurred")
        
        state = timer_manager.get_state()
        logger.info(f"Timer state requested: {state['state']}")
        return jsonify(state), 200
    except Exception as e:
        logger.error(f"Error getting timer state: {str(e)}")
        return jsonify({"error": "Failed to get timer state"}), 500


@app.route('/api/timer/start', methods=['POST'])
def start_timer():
    """Start a focus session"""
    try:
        # Check for auto-transitions first
        auto_transition = timer_manager.check_auto_transitions()
        
        state = timer_manager.start_focus()
        logger.info(f"Timer started: {state}")
        return jsonify(state), 200
    except TimerStateError as e:
        raise e
    except Exception as e:
        logger.error(f"Error starting timer: {str(e)}")
        return jsonify({"error": "Failed to start timer"}), 500


@app.route('/api/timer/pause', methods=['POST'])
def pause_timer():
    """Pause current session"""
    try:
        state = timer_manager.pause()
        logger.info(f"Timer paused: {state}")
        return jsonify(state), 200
    except TimerStateError as e:
        raise e
    except Exception as e:
        logger.error(f"Error pausing timer: {str(e)}")
        return jsonify({"error": "Failed to pause timer"}), 500


@app.route('/api/timer/resume', methods=['POST'])
def resume_timer():
    """Resume paused session"""
    try:
        state = timer_manager.resume()
        logger.info(f"Timer resumed: {state}")
        return jsonify(state), 200
    except TimerStateError as e:
        raise e
    except Exception as e:
        logger.error(f"Error resuming timer: {str(e)}")
        return jsonify({"error": "Failed to resume timer"}), 500


@app.route('/api/timer/reset', methods=['POST'])
def reset_timer():
    """Reset timer to idle state"""
    try:
        state = timer_manager.reset()
        logger.info(f"Timer reset: {state}")
        return jsonify(state), 200
    except Exception as e:
        logger.error(f"Error resetting timer: {str(e)}")
        return jsonify({"error": "Failed to reset timer"}), 500


@app.route('/api/timer/config', methods=['GET'])
def get_timer_config():
    """Get timer configuration"""
    try:
        config = {
            "focus_duration": timer_manager.config.focus_duration,
            "short_break_duration": timer_manager.config.short_break_duration,
            "long_break_duration": timer_manager.config.long_break_duration,
            "cycles_before_long_break": timer_manager.config.cycles_before_long_break
        }
        return jsonify(config), 200
    except Exception as e:
        logger.error(f"Error getting timer config: {str(e)}")
        return jsonify({"error": "Failed to get timer config"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "pomodoro-timer"}), 200


if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    logger.info("Starting Pomodoro Timer API server...")
    logger.info(f"Debug mode: {debug_mode}")
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)