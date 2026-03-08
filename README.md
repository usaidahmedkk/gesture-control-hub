# 🎯 Gesture Control Hub

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-hand%20tracking-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-video%20processing-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **Control your PC with hand gestures — no extra hardware required.**

A complete Flask-based web dashboard with **5 gesture-powered projects**, each using your laptop camera with **MediaPipe** and **OpenCV** for real-time hand tracking.

---

## ✨ Features

| # | Project | What it does |
|---|---------|-------------|
| 1 | 🖐️ Air Mouse | Move the cursor and click with your finger |
| 2 | 🎨 Air Canvas | Draw on the camera feed in real time |
| 3 | 🎵 Media Controller | Play/pause, skip tracks, change volume |
| 4 | 📊 Presentation Controller | Navigate slides hands-free |
| 5 | 🤟 Sign Language | Real-time ASL alphabet recognition |

---

## 📋 Prerequisites

- **Windows 10 / 11** (tested; other OS should work too)
- **Python 3.10+**
- A working **laptop or USB camera**

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/usaidahmedkk/gesture-control-hub.git
cd gesture-control-hub

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

# 4. Open in browser
#    http://localhost:5000
```

---

## 🎮 How to Use

### Dashboard
Navigate to `http://localhost:5000` and click **LAUNCH** on any project card.

### 🖐️ Air Mouse
| Gesture | Action |
|---------|--------|
| Index finger only | Move mouse cursor |
| Thumb + index pinch | Left click |
| Index + middle pinch | Right click |
| Open palm (move up/down) | Scroll |

### 🎨 Air Canvas
| Gesture | Action |
|---------|--------|
| Index finger only | Draw |
| All fingers up | Pause drawing |
| Fist | Clear canvas |
| Peace sign ✌️ | Switch to red |
| Thumbs up 👍 | Switch to blue |
| Ring + pinky up | Switch to green |
| Pinky only 🤙 | Switch to yellow |

### 🎵 Media Controller
| Gesture | Action |
|---------|--------|
| Open palm 🖐️ | Play / Pause |
| Index finger swipe left | Previous track |
| Index finger swipe right | Next track |
| Index + middle (move up) | Volume up |
| Index + middle (move down) | Volume down |
| Fist ✊ | Mute / Unmute |

### 📊 Presentation Controller
| Gesture | Action |
|---------|--------|
| Index finger swipe right | Next slide → |
| Index finger swipe left | ← Previous slide |
| Thumbs up 👍 | Start slideshow (F5) |
| Fist ✊ | End slideshow (Esc) |
| Open palm 🖐️ | Pause |

### 🤟 Sign Language Interpreter
Hold any of the following ASL hand shapes for ~1 second to register the letter:

| Letter | Hand Shape |
|--------|-----------|
| A | Fist, thumb beside index |
| B | Four fingers up, thumb tucked |
| C | Curved open hand |
| D | Index up, others curled, thumb touches middle |
| E | All fingertips bent |
| F | OK sign + other fingers up |
| I | Pinky only |
| L | Index + thumb out (L-shape) |
| O | Rounded O shape |
| V | Peace / V sign |
| W | Three fingers up |
| Y | Thumb + pinky out |

Use the **Space** and **Clear** buttons to manage the word being built.

---

## 🛠 Tech Stack

- **Backend:** Python 3.10 + Flask
- **Hand Tracking:** MediaPipe Hands
- **Video:** OpenCV
- **Mouse / Keyboard:** pyautogui
- **Volume (Windows):** pycaw + comtypes
- **Frontend:** HTML5 / CSS3 / Vanilla JS
- **Streaming:** MJPEG via Flask Response

---

## 📁 Project Structure

```
gesture-control-hub/
├── app.py                          # Flask server & routes
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html                  # Dashboard
│   ├── air_mouse.html
│   ├── air_canvas.html
│   ├── media_controller.html
│   ├── presentation.html
│   └── sign_language.html
├── static/
│   ├── css/style.css               # Dark theme
│   └── js/
│       ├── air_mouse.js
│       ├── air_canvas.js
│       ├── media_controller.js
│       ├── presentation.js
│       └── sign_language.js
└── modules/
    ├── __init__.py
    ├── hand_tracker.py             # Shared MediaPipe wrapper
    ├── air_mouse.py
    ├── air_canvas.py
    ├── media_controller.py
    ├── presentation_controller.py
    └── sign_language.py
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---------|-----|
| **Camera not found** | Make sure no other app has the camera open; try a different camera index in `cv2.VideoCapture(0)` → `(1)` |
| **pip install fails** | Upgrade pip: `python -m pip install --upgrade pip` then retry |
| **pycaw volume control not working** | Only works on Windows. Volume gestures fall back to keyboard simulation on other OS. |
| **MediaPipe import error** | Ensure Python 3.10+ and run `pip install mediapipe` |
| **Slow video feed** | Reduce camera resolution in `app.py` or close other heavy applications |
| **pyautogui.FailSafeException** | Already disabled with `pyautogui.FAILSAFE = False` |