from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
MODEL_DIR = BASE_DIR / "models"
SLOTS_FILE = CONFIG_DIR / "slots_config.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
RUNTIME_FILE = DATA_DIR / "runtime_state.json"

for path in (CONFIG_DIR, DATA_DIR, UPLOAD_DIR, MODEL_DIR):
    path.mkdir(parents=True, exist_ok=True)
