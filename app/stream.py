import time
from threading import Lock
import cv2
from .detector import YOLODetector, occupancy_from_detections, nearest_vacant, draw_overlay
from .storage import get_slots, get_settings, save_runtime

class StreamManager:
    def __init__(self):
        self.lock = Lock()
        self.capture = None
        self.source = None
        self.detector = None
        self.last_frame = None
        self.running = False
        self.last_error = None
        self._last_time = time.perf_counter()
        self._fps = 0.0
        self.connect(get_settings().get("source", "0"))

    def _parse_source(self, source):
        source = str(source).strip()
        return int(source) if source.isdigit() else source

    def connect(self, source):
        with self.lock:
            if self.capture is not None:
                self.capture.release()
            self.source = str(source)
            self.capture = cv2.VideoCapture(self._parse_source(source))
            self.running = bool(self.capture.isOpened())
            self.last_error = None if self.running else f"Unable to open video source: {source}"
            settings = get_settings()
            self.detector = YOLODetector(settings.get("model", "yolov8n.pt"), settings.get("confidence", 0.25), settings.get("classes", [2,5,7,3]))

    def update_settings(self, confidence, classes, model=None):
        with self.lock:
            settings = get_settings()
            if model:
                settings["model"] = model
            if self.detector is None or settings["model"] != self.detector.model_path:
                self.detector = YOLODetector(settings["model"], confidence, classes)
            else:
                self.detector.update(confidence, classes)

    def _placeholder(self, width=1280, height=720):
        img = cv2.imread("docs/screenshots/01_live_monitor.png")
        if img is None:
            img = 255 * __import__('numpy').ones((height, width, 3), dtype='uint8')
        return cv2.resize(img, (width, height))

    def read(self):
        with self.lock:
            if self.capture is None or not self.capture.isOpened():
                return self._placeholder()
            ok, frame = self.capture.read()
            if not ok:
                # Loop uploaded/local files, but don't loop RTSP/webcam endlessly on failure.
                if isinstance(self._parse_source(self.source), str):
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, frame = self.capture.read()
                if not ok:
                    self.running = False
                    self.last_error = f"No frame received from {self.source}"
                    return self._placeholder()

            slots_cfg = get_slots()
            settings = get_settings()
            detections = self.detector.infer(frame) if self.detector else []
            occupancy = occupancy_from_detections(slots_cfg.get("slots", []), detections)
            nearest, distance = nearest_vacant(slots_cfg.get("slots", []), occupancy, slots_cfg.get("entrance", [80,590]))
            annotated = draw_overlay(frame, slots_cfg.get("slots", []), occupancy, slots_cfg.get("entrance"), nearest)
            for det in detections:
                x1,y1,x2,y2 = det.box
                cv2.rectangle(annotated, (x1,y1), (x2,y2), (70,140,255), 2)
                cv2.putText(annotated, f"{det.name} {det.confidence:.2f}", (x1, max(18,y1-6)), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 2, cv2.LINE_AA)

            now = time.perf_counter()
            dt = now - self._last_time
            self._last_time = now
            if dt > 0:
                self._fps = 0.9 * self._fps + 0.1 * (1.0 / dt)
            h,w = annotated.shape[:2]
            save_runtime({
                "occupancy": occupancy,
                "nearest_slot": nearest,
                "distance_px": distance,
                "fps": round(self._fps, 1),
                "resolution": f"{w}x{h}",
                "last_error": self.detector.error if self.detector else self.last_error
            })
            self.last_frame = annotated
            return annotated

    def mjpeg(self):
        while True:
            frame = self.read()
            ok, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if ok:
                yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + encoded.tobytes() + b'\r\n'
            time.sleep(0.03)

stream_manager = StreamManager()
