from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    env = os.environ.get("APP_ENV", "development")
    if env == "production":
        app.run(host="127.0.0.1", port=5000, debug=False)
    else:
        app.run(host="0.0.0.0", port=5000, debug=True)