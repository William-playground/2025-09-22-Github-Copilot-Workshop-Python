"""
Health check endpoint blueprint.
"""
from flask import Blueprint, jsonify
from time_provider import default_time_provider

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify service status.
    
    Returns:
        JSON response with service status and timestamp
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Flask Application',
        'timestamp': default_time_provider.current_time(),
        'version': '1.0.0'
    })
