from pathlib import Path
from flask import Blueprint, jsonify, render_template, request, Response
from werkzeug.utils import secure_filename
from . import UPLOAD_DIR
from .storage import get_slots, save_slots, get_settings, save_settings, get_runtime
from .stream import stream_manager

bp = Blueprint("main", __name__)
ALLOWED = {"mp4", "avi", "mov", "mkv", "webm"}

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/video_feed")
def video_feed():
    return Response(stream_manager.mjpeg(), mimetype="multipart/x-mixed-replace; boundary=frame")

@bp.get("/api/slots")
def api_slots():
    return jsonify(get_slots())

@bp.post("/api/slots")
def api_save_slots():
    payload = request.get_json(force=True)
    if "slots" not in payload or not isinstance(payload["slots"], list):
        return jsonify({"error": "slots must be a list"}), 400
    save_slots(payload)
    return jsonify(get_slots())

@bp.post("/api/slots/delete")
def api_delete_slot():
    payload = request.get_json(force=True)
    slot_id = payload.get("id")
    cfg = get_slots()
    cfg["slots"] = [s for s in cfg.get("slots", []) if s.get("id") != slot_id]
    save_slots(cfg)
    return jsonify(cfg)

@bp.post("/api/slots/grid")
def api_grid():
    payload = request.get_json(force=True)
    rows = max(1, int(payload.get("rows", 2)))
    cols = max(1, int(payload.get("cols", 3)))
    x0,y0,x1,y1 = [float(v) for v in payload.get("bounds", [120,120,540,580])]
    gap_x = (x1-x0)/cols
    gap_y = (y1-y0)/rows
    slots=[]
    for r in range(rows):
        for c in range(cols):
            xa, xb = x0+c*gap_x+6, x0+(c+1)*gap_x-6
            ya, yb = y0+r*gap_y+6, y0+(r+1)*gap_y-6
            slots.append({"id": f"Slot_{r*cols+c+1:02d}", "points": [[round(xa),round(ya)],[round(xb),round(ya)],[round(xb),round(yb)],[round(xa),round(yb)]]})
    cfg=get_slots(); cfg["slots"]=slots; save_slots(cfg)
    return jsonify(cfg)

@bp.post("/api/entrance")
def api_entrance():
    payload=request.get_json(force=True)
    cfg=get_slots(); cfg["entrance"]=[int(payload.get("x",80)), int(payload.get("y",590))]; save_slots(cfg)
    return jsonify(cfg)

@bp.get("/api/occupancy")
def api_occupancy():
    runtime=get_runtime(); cfg=get_slots()
    occupancy=runtime.get("occupancy", {})
    return jsonify({
        "slots": [{"id": s["id"], "occupied": bool(occupancy.get(s["id"], False))} for s in cfg.get("slots", [])],
        "nearest_slot": runtime.get("nearest_slot"),
        "distance_px": runtime.get("distance_px"),
        "fps": runtime.get("fps", 0),
        "resolution": runtime.get("resolution", "1280x720"),
        "last_error": runtime.get("last_error")
    })

@bp.get("/api/settings")
def api_settings():
    return jsonify(get_settings())

@bp.post("/api/settings")
def api_update_settings():
    payload=request.get_json(force=True)
    confidence=min(.9,max(.1,float(payload.get("confidence",.25))))
    classes=[int(v) for v in payload.get("classes", [2,5,7,3])]
    model=str(payload.get("model", get_settings().get("model","yolov8n.pt")))
    settings={**get_settings(), "confidence": confidence, "classes": classes, "class_names": payload.get("class_names", get_settings().get("class_names", [])), "model": model}
    save_settings(settings)
    stream_manager.update_settings(confidence, classes, model)
    return jsonify(settings)

@bp.post("/api/set_source")
def api_set_source():
    payload=request.get_json(force=True)
    source=str(payload.get("source", "0"))
    settings=get_settings(); settings["source"]=source; save_settings(settings)
    stream_manager.connect(source)
    return jsonify({"ok": True, "source": source})

@bp.post("/api/upload_video")
def api_upload_video():
    file=request.files.get("video")
    if not file or not file.filename:
        return jsonify({"error":"No video file supplied"}),400
    ext=Path(file.filename).suffix.lower().lstrip('.')
    if ext not in ALLOWED:
        return jsonify({"error":"Unsupported video type"}),400
    filename=secure_filename(file.filename)
    destination=UPLOAD_DIR/filename
    file.save(destination)
    stream_manager.connect(str(destination))
    settings=get_settings(); settings["source"]=str(destination); save_settings(settings)
    return jsonify({"ok":True,"filename":filename,"source":str(destination)})
