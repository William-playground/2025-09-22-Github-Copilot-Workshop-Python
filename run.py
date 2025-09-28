from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    env = os.environ.get("APP_ENV", "development")
    # デバッグモードは明示的に有効化された場合のみ使用
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    if env == "production":
        # 本番環境では常にデバッグモードを無効化
        app.run(host="127.0.0.1", port=5000, debug=False)
    else:
        # 開発環境でもデバッグモードは環境変数で制御
        host = os.environ.get("FLASK_HOST", "127.0.0.1")
        app.run(host=host, port=5000, debug=debug_mode)