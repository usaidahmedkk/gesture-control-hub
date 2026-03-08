"""Air Mouse module — controls the system mouse with hand gestures."""

import time
import cv2
import pyautogui
import numpy as np
from .hand_tracker import HandTracker

pyautogui.FAILSAFE = False

# Screen dimensions
SCREEN_W, SCREEN_H = pyautogui.size()

# Frame region used for mouse mapping (inner portion to reduce edge jitter)
FRAME_MARGIN = 80

CLICK_DISTANCE_THRESHOLD = 40
SCROLL_THRESHOLD = 30
COOLDOWN = 0.4


class AirMouse:
    def __init__(self):
        self.tracker = HandTracker(max_hands=1)
        self.prev_x, self.prev_y = 0, 0
        self.smooth = 5
        self.curr_x, self.curr_y = 0, 0
        self.gesture = "No Hand"
        self.last_action_time = 0
        self.prev_hand_y = None

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        frame = self.tracker.process(frame)
        lm = self.tracker.get_landmarks()
        fingers = self.tracker.fingers_up()

        gesture = "No Hand"

        if lm:
            # Index fingertip position
            ix, iy = lm[8]

            # --- Mouse Move: only index finger up ---
            if fingers == [False, True, False, False, False]:
                gesture = "Move Mouse"
                # Map from frame region to screen
                mx = np.interp(ix, [FRAME_MARGIN, w - FRAME_MARGIN], [0, SCREEN_W])
                my = np.interp(iy, [FRAME_MARGIN, h - FRAME_MARGIN], [0, SCREEN_H])
                # Smoothing
                self.curr_x = self.prev_x + (mx - self.prev_x) / self.smooth
                self.curr_y = self.prev_y + (my - self.prev_y) / self.smooth
                pyautogui.moveTo(int(self.curr_x), int(self.curr_y))
                self.prev_x, self.prev_y = self.curr_x, self.curr_y
                self._draw_move_indicator(frame, ix, iy)

            # --- Left Click: pinch thumb + index ---
            elif self.tracker.distance(4, 8) < CLICK_DISTANCE_THRESHOLD:
                now = time.time()
                if now - self.last_action_time > COOLDOWN:
                    gesture = "Left Click"
                    pyautogui.click()
                    self.last_action_time = now

            # --- Right Click: two-finger pinch (index + middle) ---
            elif (fingers[1] and fingers[2] and not fingers[3] and not fingers[4]
                  and self.tracker.distance(8, 12) < CLICK_DISTANCE_THRESHOLD):
                now = time.time()
                if now - self.last_action_time > COOLDOWN:
                    gesture = "Right Click"
                    pyautogui.rightClick()
                    self.last_action_time = now

            # --- Scroll: all fingers up, track hand vertical motion ---
            elif fingers == [True, True, True, True, True]:
                hand_y = lm[9][1]  # middle of palm
                if self.prev_hand_y is not None:
                    delta = self.prev_hand_y - hand_y
                    if abs(delta) > SCROLL_THRESHOLD:
                        now = time.time()
                        if now - self.last_action_time > COOLDOWN:
                            scroll_amount = int(delta / 20)
                            pyautogui.scroll(scroll_amount)
                            gesture = "Scroll Up" if delta > 0 else "Scroll Down"
                            self.last_action_time = now
                self.prev_hand_y = hand_y
            else:
                self.prev_hand_y = None
        else:
            self.prev_hand_y = None

        self.gesture = gesture
        self._draw_overlay(frame, gesture)
        return frame

    def _draw_move_indicator(self, frame, x, y):
        cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)

    def _draw_overlay(self, frame, gesture):
        cv2.rectangle(frame, (0, 0), (300, 40), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, f"Gesture: {gesture}", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 128), 2)

    def get_status(self):
        return {"gesture": self.gesture}

    def release(self):
        self.tracker.release()
