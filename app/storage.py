import json
from pathlib import Path
from threading import Lock
from . import SLOTS_FILE, SETTINGS_FILE, RUNTIME_FILE

_LOCK = Lock()

def read_json(path: Path, default):
    with _LOCK:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            write_json(path, default)
            return default

def write_json(path: Path, value):
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(value, indent=2), encoding="utf-8")
        tmp.replace(path)

def get_slots():
    return read_json(SLOTS_FILE, {"frame_size": [1280, 720], "entrance": [80, 590], "slots": []})

def save_slots(value):
    write_json(SLOTS_FILE, value)

def get_settings():
    return read_json(SETTINGS_FILE, {"confidence": 0.25, "classes": [2,5,7,3], "class_names": ["Car","Truck","Bus","Motorcycle"], "source": "0", "model": "yolov8n.pt"})

def save_settings(value):
    write_json(SETTINGS_FILE, value)

def get_runtime():
    return read_json(RUNTIME_FILE, {})

def save_runtime(value):
    write_json(RUNTIME_FILE, value)
