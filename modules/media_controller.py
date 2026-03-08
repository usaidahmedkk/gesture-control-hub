"""Media Controller module — controls media playback with hand gestures."""

import time
import cv2
import pyautogui
from .hand_tracker import HandTracker

pyautogui.FAILSAFE = False

COOLDOWN = 0.8
SWIPE_THRESHOLD = 60
VOLUME_STEP = 2


def _get_volume_interface():
    """Attempt to get Windows pycaw volume interface; return None on non-Windows."""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except Exception:
        return None


class MediaController:
    def __init__(self):
        self.tracker = HandTracker(max_hands=1)
        self.gesture = "No Hand"
        self.last_action_time = 0
        self.prev_x = None
        self.prev_y = None
        self.muted = False
        self.volume_iface = _get_volume_interface()
        self.volume_level = self._get_volume()

    # ------------------------------------------------------------------
    # Volume helpers
    # ------------------------------------------------------------------
    def _get_volume(self):
        if self.volume_iface:
            try:
                vol = self.volume_iface.GetMasterVolumeLevelScalar()
                return int(vol * 100)
            except Exception:
                pass
        return 50

    def _set_volume(self, level):
        level = max(0, min(100, level))
        self.volume_level = level
        if self.volume_iface:
            try:
                self.volume_iface.SetMasterVolumeLevelScalar(level / 100.0, None)
                return
            except Exception:
                pass
        # Fallback via pyautogui key simulation
        if level > self.volume_level:
            for _ in range(VOLUME_STEP):
                pyautogui.press("volumeup")
        else:
            for _ in range(VOLUME_STEP):
                pyautogui.press("volumedown")

    # ------------------------------------------------------------------
    # Frame processing
    # ------------------------------------------------------------------
    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame = self.tracker.process(frame)
        lm = self.tracker.get_landmarks()
        fingers = self.tracker.fingers_up()
        now = time.time()

        gesture = "No Hand"

        if lm:
            hand_cx = lm[9][0]  # palm centre x
            hand_cy = lm[9][1]  # palm centre y

            # --- Open palm → Play/Pause ---
            if all(fingers[1:]):
                if now - self.last_action_time > COOLDOWN:
                    gesture = "Play / Pause"
                    pyautogui.press("playpause")
                    self.last_action_time = now

            # --- Fist → Mute/Unmute ---
            elif not any(fingers[1:]):
                if now - self.last_action_time > COOLDOWN:
                    self.muted = not self.muted
                    gesture = "Muted" if self.muted else "Unmuted"
                    pyautogui.press("volumemute")
                    self.last_action_time = now

            # --- Swipe left/right (index only — track horizontal motion) ---
            elif fingers == [False, True, False, False, False]:
                if self.prev_x is not None:
                    delta_x = hand_cx - self.prev_x
                    if abs(delta_x) > SWIPE_THRESHOLD:
                        if now - self.last_action_time > COOLDOWN:
                            if delta_x > 0:
                                gesture = "Next Track →"
                                pyautogui.press("nexttrack")
                            else:
                                gesture = "← Prev Track"
                                pyautogui.press("prevtrack")
                            self.last_action_time = now
                            self.prev_x = hand_cx
                        else:
                            gesture = "Swipe..."
                    else:
                        gesture = "Swipe..."
                self.prev_x = hand_cx

            # --- Hand up → Volume Up (index+middle up, others down) ---
            elif fingers == [False, True, True, False, False]:
                if self.prev_y is not None:
                    delta_y = self.prev_y - hand_cy  # positive = moved up
                    if delta_y > 20 and now - self.last_action_time > COOLDOWN:
                        gesture = "Volume Up ↑"
                        self._set_volume(self.volume_level + 5)
                        self.last_action_time = now
                    elif delta_y < -20 and now - self.last_action_time > COOLDOWN:
                        gesture = "Volume Down ↓"
                        self._set_volume(self.volume_level - 5)
                        self.last_action_time = now
                    else:
                        gesture = "Volume Control"
                else:
                    gesture = "Volume Control"
                self.prev_y = hand_cy
            else:
                self.prev_x = None
                self.prev_y = None

        else:
            self.prev_x = None
            self.prev_y = None

        self.gesture = gesture
        self._draw_overlay(frame, gesture)
        return frame

    def _draw_overlay(self, frame, gesture):
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, 50), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, f"Gesture: {gesture}", (10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 128), 2)
        vol_bar_w = int((self.volume_level / 100) * 200)
        cv2.rectangle(frame, (10, 32), (210, 44), (50, 50, 50), cv2.FILLED)
        cv2.rectangle(frame, (10, 32), (10 + vol_bar_w, 44), (0, 200, 255), cv2.FILLED)
        cv2.putText(frame, f"Vol: {self.volume_level}%", (220, 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    def get_status(self):
        return {
            "gesture": self.gesture,
            "volume": self.volume_level,
            "muted": self.muted,
        }

    def release(self):
        self.tracker.release()
