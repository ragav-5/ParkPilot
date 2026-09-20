import os
from flask import Flask
from dotenv import load_dotenv
from .routes import bp

def create_app():
    load_dotenv()
    app=Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024
    app.register_blueprint(bp)
    return app

app=create_app()

if __name__ == "__main__":
    host=os.getenv("PARKPILOT_HOST","0.0.0.0")
    port=int(os.getenv("PARKPILOT_PORT","5000"))
    debug=os.getenv("PARKPILOT_DEBUG","false").lower()=="true"
    app.run(host=host, port=port, debug=debug, threaded=True)
