"""Presentation Controller module — controls slides with hand gestures."""

import time
import cv2
import pyautogui
from .hand_tracker import HandTracker

pyautogui.FAILSAFE = False

COOLDOWN = 0.8
SWIPE_THRESHOLD = 70


class PresentationController:
    def __init__(self):
        self.tracker = HandTracker(max_hands=1)
        self.gesture = "No Hand"
        self.last_action_time = 0
        self.prev_x = None

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame = self.tracker.process(frame)
        lm = self.tracker.get_landmarks()
        fingers = self.tracker.fingers_up()
        now = time.time()

        gesture = "No Hand"

        if lm:
            hand_cx = lm[9][0]

            # --- Swipe right → Next Slide ---
            # --- Swipe left → Previous Slide ---
            if fingers == [False, True, False, False, False]:
                if self.prev_x is not None:
                    delta = hand_cx - self.prev_x
                    if abs(delta) > SWIPE_THRESHOLD and now - self.last_action_time > COOLDOWN:
                        if delta > 0:
                            gesture = "Next Slide →"
                            pyautogui.press("right")
                        else:
                            gesture = "← Prev Slide"
                            pyautogui.press("left")
                        self.last_action_time = now
                        self.prev_x = hand_cx
                    else:
                        gesture = "Swipe..."
                self.prev_x = hand_cx

            # --- Thumbs up → Start Slideshow (F5) ---
            elif fingers == [True, False, False, False, False]:
                if now - self.last_action_time > COOLDOWN:
                    gesture = "Start Slideshow"
                    pyautogui.press("f5")
                    self.last_action_time = now

            # --- Fist → End Slideshow (Escape) ---
            elif not any(fingers):
                if now - self.last_action_time > COOLDOWN:
                    gesture = "End Slideshow"
                    pyautogui.press("escape")
                    self.last_action_time = now

            # --- Open palm → Pause ---
            elif all(fingers[1:]):
                gesture = "Paused"
                self.prev_x = None

            else:
                self.prev_x = None

        else:
            self.prev_x = None

        self.gesture = gesture
        self._draw_overlay(frame, gesture)
        return frame

    def _draw_overlay(self, frame, gesture):
        cv2.rectangle(frame, (0, 0), (300, 40), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, f"Gesture: {gesture}", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 128), 2)

    def get_status(self):
        return {"gesture": self.gesture}

    def release(self):
        self.tracker.release()
