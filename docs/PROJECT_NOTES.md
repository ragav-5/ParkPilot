# ParkPilot implementation notes

This repository was assembled from the supplied ParkPilot project report, PBL report and working-model screenshots.

The academic material explicitly describes:
- Python + OpenCV + YOLOv8.
- Polygon-defined parking slots and an entrance point.
- Occupancy classification and nearest-slot navigation.
- A browser dashboard with live occupancy cards.
- Video upload and source switching.
- Adjustable YOLOv8 confidence and vehicle classes.
- API endpoints for slots, occupancy, video upload, source switching and settings.

The supplied runtime evidence shows six slots, four vacant and two occupied, Slot_01 as the nearest target at 167 px, and a 1280×720 / 30 FPS stream.

Where the source material leaves implementation details unspecified (for example exact trained YOLO checkpoint, training split, hyperparameters and formal evaluation metrics), this repository uses sensible runtime defaults rather than presenting them as measured academic results.
