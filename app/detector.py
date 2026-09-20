import os
import time
from dataclasses import dataclass
from typing import List, Dict, Any

import cv2
import numpy as np

@dataclass
class Detection:
    cls: int
    name: str
    confidence: float
    box: tuple

class YOLODetector:
    """Thin wrapper around Ultralytics YOLO with a safe no-model fallback."""
    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.25, classes=None):
        self.model_path = model_path
        self.confidence = confidence
        self.classes = classes
        self.model = None
        self.names = {}
        self.error = None
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            self.names = self.model.names
        except Exception as exc:
            self.error = str(exc)

    def update(self, confidence=None, classes=None):
        if confidence is not None:
            self.confidence = float(confidence)
        if classes is not None:
            self.classes = classes

    def infer(self, frame) -> List[Detection]:
        if self.model is None:
            return []
        try:
            result = self.model.predict(frame, conf=self.confidence, classes=self.classes, verbose=False)[0]
            detections = []
            boxes = result.boxes
            if boxes is None:
                return detections
            for box in boxes:
                cls = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                xyxy = tuple(int(v) for v in box.xyxy[0].tolist())
                name = self.names.get(cls, str(cls)) if isinstance(self.names, dict) else str(cls)
                detections.append(Detection(cls, name, conf, xyxy))
            return detections
        except Exception as exc:
            self.error = str(exc)
            return []

def point_in_polygon(point, polygon):
    contour = np.array(polygon, dtype=np.int32)
    return cv2.pointPolygonTest(contour, point, False) >= 0

def occupancy_from_detections(slots: List[Dict[str, Any]], detections: List[Detection]):
    result = {slot["id"]: False for slot in slots}
    for det in detections:
        x1, y1, x2, y2 = det.box
        center = ((x1 + x2) // 2, (y1 + y2) // 2)
        for slot in slots:
            if point_in_polygon(center, slot["points"]):
                result[slot["id"]] = True
                break
    return result

def slot_distance(a, b):
    return float(np.linalg.norm(np.array(a, dtype=float) - np.array(b, dtype=float)))

def nearest_vacant(slots, occupancy, entrance):
    candidates = []
    for slot in slots:
        if not occupancy.get(slot["id"], False):
            pts = np.array(slot["points"], dtype=float)
            center = pts.mean(axis=0)
            candidates.append((slot_distance(entrance, center), slot["id"]))
    if not candidates:
        return None, None
    distance, slot_id = min(candidates)
    return slot_id, round(distance, 1)

def draw_overlay(frame, slots, occupancy, entrance, nearest):
    canvas = frame.copy()
    for slot in slots:
        pts = np.array(slot["points"], dtype=np.int32).reshape((-1, 1, 2))
        occupied = occupancy.get(slot["id"], False)
        color = (70, 70, 255) if occupied else (0, 190, 145)
        if slot["id"] == nearest:
            color = (0, 165, 255)
        cv2.polylines(canvas, [pts], True, color, 3)
        center = tuple(np.mean(np.array(slot["points"]), axis=0).astype(int))
        cv2.putText(canvas, slot["id"], center, cv2.FONT_HERSHEY_SIMPLEX, 0.65, (245,245,245), 2, cv2.LINE_AA)
    if entrance:
        ex, ey = map(int, entrance)
        cv2.circle(canvas, (ex, ey), 9, (255, 220, 0), -1)
        cv2.putText(canvas, "ENTRANCE", (ex + 12, ey + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 2, cv2.LINE_AA)
        if nearest:
            slot = next((s for s in slots if s["id"] == nearest), None)
            if slot:
                center = tuple(np.mean(np.array(slot["points"]), axis=0).astype(int))
                cv2.arrowedLine(canvas, (ex, ey), center, (0, 165, 255), 3, tipLength=0.04)
    return canvas
