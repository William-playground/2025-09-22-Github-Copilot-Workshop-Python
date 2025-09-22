from flask import Flask

def create_app():
    app = Flask(__name__)
    # Blueprint登録
    from app.blueprints.health.routes import bp as health_bp
    app.register_blueprint(health_bp)
    return app
