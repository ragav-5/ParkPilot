# ParkPilot Web Suite

**ParkPilot - AI-Powered Intelligent Parking Space Detection and Navigation Using Computer Vision**

A browser-based parking management prototype built around Python, Flask, OpenCV and YOLOv8. The supplied project material describes a camera-based pipeline that detects vehicles, maps them to user-defined parking polygons, determines occupancy, selects the nearest vacant slot and exposes a live dashboard. The included implementation turns those documented requirements into a runnable GitHub project.

## Features

- Live MJPEG camera/video dashboard.
- YOLOv8 vehicle detection with adjustable confidence threshold.
- Vehicle-class selection: Car, Truck, Bus and Motorcycle.
- Interactive four-point parking-slot polygon editor.
- Custom slot IDs persisted to `config/slots_config.json`.
- Click-to-place entrance/start point.
- Automatic rectangular slot-grid generator.
- Occupancy matrix with VACANT/OCCUPIED states.
- Nearest vacant slot calculation using Euclidean pixel distance.
- Video upload for `.mp4`, `.avi`, `.mov`, `.mkv` and `.webm`.
- Webcam index or RTSP/source-string connection.
- REST API endpoints for slots, occupancy, source and model settings.
- Screenshots and college project documents included under `docs/`.

## Architecture

```text
Camera / Uploaded Video / RTSP
            |
            v
       OpenCV capture
            |
            v
       YOLOv8 detection
            |
            v
 Vehicle detections + slot polygons
            |
            v
      Occupancy classification
            |
            v
 Entrance -> nearest vacant slot
            |
            v
      Flask REST API + UI
```

## Requirements

- Python 3.10+ recommended
- 8 GB RAM recommended for local development
- Webcam, local video or RTSP camera
- Optional NVIDIA GPU/CUDA environment for faster YOLO inference

## Setup

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Open `http://127.0.0.1:5000`.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open `http://127.0.0.1:5000`.

On the first YOLO run, Ultralytics may download the configured model weights. Model files are ignored by Git to keep the repository lightweight.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/slots` | Read active slot polygons and entrance |
| POST | `/api/slots` | Save slot configuration |
| POST | `/api/slots/delete` | Delete one slot |
| POST | `/api/slots/grid` | Generate a rectangular slot grid |
| POST | `/api/entrance` | Update entrance point |
| GET | `/api/occupancy` | Read occupancy and nearest-slot telemetry |
| GET | `/api/settings` | Read YOLO/source settings |
| POST | `/api/settings` | Update confidence/classes/model |
| POST | `/api/set_source` | Switch camera/video source |
| POST | `/api/upload_video` | Upload and connect a video file |
| GET | `/video_feed` | MJPEG live stream |

## Configuration

Do not commit RTSP usernames/passwords or private camera addresses. Put local-only values in `.env` or configure them from the browser. The repository intentionally uses `0` as the default webcam source and does not contain real camera credentials.

## Project evidence

The supplied working-model screenshots show a six-slot demonstration with four vacant slots, two occupied slots, and Slot_01 displayed as the nearest target at 167 px. The project report also documents a 1280×720, 30 FPS runtime stream and the interactive polygon editor/configuration capabilities.

## Evaluation note

The supplied academic material does **not** contain formal precision, recall, F1, mAP, confusion-matrix or held-out-set results. Do not claim those metrics until they are measured from the actual dataset/model run.

## Repository layout

```text
ParkPilot_GitHub_Project/
├── app/                  # Flask application, detector and stream manager
├── config/               # Persistent parking-slot configuration
├── data/                 # Runtime/settings JSON
├── docs/                 # Project report and supplied screenshots
├── models/               # Local model weights (ignored by Git)
├── templates/            # Web UI
├── static/               # CSS + browser JavaScript
├── uploads/              # Local uploaded videos (ignored by Git)
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## Academic project

Project: **ParkPilot - AI-Powered Intelligent Parking Space Detection and Navigation Using Computer Vision**

Authors: **R. Ragav (2104251040740)** and **Tharun K.S. (2104251041038)**

Mentor / Faculty Guide / Project Coordinator: **Pratham Verma, Machine Learning Faculty**

Institution: **Chennai Institute of Technology, Department of Computer Science and Engineering**

## GitHub publishing

After creating an empty repository named `ParkPilot` under the GitHub account `ragav-5`, run:

```bash
git init
git add .
git commit -m "Initial ParkPilot Web Suite implementation"
git branch -M main
git remote add origin https://github.com/ragav-5/ParkPilot.git
git push -u origin main
```

If you choose a different repository name, replace the remote URL accordingly.
