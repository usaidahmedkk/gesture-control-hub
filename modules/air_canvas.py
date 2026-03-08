"""Air Canvas module — draws on the camera feed with hand gestures."""

import cv2
import numpy as np
from .hand_tracker import HandTracker

COLORS = {
    "white": (255, 255, 255),
    "red": (0, 0, 255),
    "blue": (255, 0, 0),
    "green": (0, 255, 0),
    "yellow": (0, 255, 255),
}

BRUSH_THICKNESS = 8
ERASER_THICKNESS = 50


class AirCanvas:
    def __init__(self):
        self.tracker = HandTracker(max_hands=1)
        self.canvas = None
        self.prev_x, self.prev_y = 0, 0
        self.color = COLORS["white"]
        self.color_name = "white"
        self.gesture = "No Hand"
        self.drawing = False

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Initialise canvas on first frame
        if self.canvas is None:
            self.canvas = np.zeros((h, w, 3), np.uint8)

        frame = self.tracker.process(frame)
        lm = self.tracker.get_landmarks()
        fingers = self.tracker.fingers_up()

        gesture = "No Hand"

        if lm:
            ix, iy = lm[8]  # index fingertip

            # --- Color selection gestures ---
            # Peace sign (index + middle) → red
            if fingers == [False, True, True, False, False]:
                gesture = "Color: Red"
                self.color = COLORS["red"]
                self.color_name = "red"
                self.prev_x, self.prev_y = 0, 0

            # Thumbs up → blue
            elif fingers == [True, False, False, False, False]:
                gesture = "Color: Blue"
                self.color = COLORS["blue"]
                self.color_name = "blue"
                self.prev_x, self.prev_y = 0, 0

            # OK-like (ring + pinky up) → green
            elif fingers == [False, False, False, True, True]:
                gesture = "Color: Green"
                self.color = COLORS["green"]
                self.color_name = "green"
                self.prev_x, self.prev_y = 0, 0

            # Pinky only → yellow
            elif fingers == [False, False, False, False, True]:
                gesture = "Color: Yellow"
                self.color = COLORS["yellow"]
                self.color_name = "yellow"
                self.prev_x, self.prev_y = 0, 0

            # --- Fist → clear canvas ---
            elif not any(fingers[1:]):  # no fingers except possibly thumb
                gesture = "Clear Canvas"
                self.canvas = np.zeros((h, w, 3), np.uint8)
                self.prev_x, self.prev_y = 0, 0

            # --- All fingers up → stop drawing ---
            elif all(fingers[1:]):
                gesture = "Pause Drawing"
                self.drawing = False
                self.prev_x, self.prev_y = 0, 0

            # --- Index only → draw ---
            elif fingers == [False, True, False, False, False]:
                gesture = f"Drawing ({self.color_name})"
                self.drawing = True
                if self.prev_x == 0 and self.prev_y == 0:
                    self.prev_x, self.prev_y = ix, iy
                cv2.line(self.canvas, (self.prev_x, self.prev_y), (ix, iy),
                         self.color, BRUSH_THICKNESS)
                self.prev_x, self.prev_y = ix, iy
            else:
                self.prev_x, self.prev_y = 0, 0

        self.gesture = gesture

        # Blend canvas onto frame
        canvas_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, canvas_inv = cv2.threshold(canvas_gray, 20, 255, cv2.THRESH_BINARY_INV)
        canvas_inv = cv2.cvtColor(canvas_inv, cv2.COLOR_GRAY2BGR)
        frame = cv2.bitwise_and(frame, canvas_inv)
        frame = cv2.bitwise_or(frame, self.canvas)

        self._draw_overlay(frame, gesture)
        return frame

    def _draw_overlay(self, frame, gesture):
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 0), cv2.FILLED)
        color_preview = self.color
        cv2.circle(frame, (20, 20), 14, color_preview, cv2.FILLED)
        cv2.putText(frame, f"Gesture: {gesture}", (45, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 128), 2)

    def get_status(self):
        return {"gesture": self.gesture, "color": self.color_name}

    def release(self):
        self.tracker.release()
