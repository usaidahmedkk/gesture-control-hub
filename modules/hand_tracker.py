"""Shared MediaPipe hand tracking utility."""

import cv2
import mediapipe as mp
import math


class HandTracker:
    """Wrapper around MediaPipe Hands for detecting and drawing hand landmarks."""

    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.results = None
        self.landmark_list = []

    def process(self, frame):
        """Process a BGR frame and return the frame with landmarks drawn."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)
        self.landmark_list = []

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style(),
                )

            # Build landmark list for first hand
            h, w, _ = frame.shape
            first_hand = self.results.multi_hand_landmarks[0]
            for lm in first_hand.landmark:
                self.landmark_list.append((int(lm.x * w), int(lm.y * h)))

        return frame

    def get_landmarks(self):
        """Return list of (x, y) landmark tuples for the first detected hand."""
        return self.landmark_list

    def fingers_up(self):
        """Return a list of 5 booleans indicating which fingers are extended."""
        lm = self.landmark_list
        if len(lm) < 21:
            return [False, False, False, False, False]

        fingers = []
        # Thumb — compare tip (4) to IP joint (3) on x-axis (mirrored)
        fingers.append(lm[4][0] < lm[3][0])
        # Index, Middle, Ring, Pinky — tip above PIP joint on y-axis
        for tip_id in [8, 12, 16, 20]:
            fingers.append(lm[tip_id][1] < lm[tip_id - 2][1])
        return fingers

    def count_fingers(self):
        """Return the number of fingers currently extended."""
        return sum(self.fingers_up())

    def distance(self, p1_idx, p2_idx):
        """Return pixel distance between two landmark indices."""
        lm = self.landmark_list
        if len(lm) <= max(p1_idx, p2_idx):
            return 0
        x1, y1 = lm[p1_idx]
        x2, y2 = lm[p2_idx]
        return math.hypot(x2 - x1, y2 - y1)

    def hand_detected(self):
        """Return True if at least one hand was detected."""
        return bool(self.landmark_list)

    def release(self):
        """Release MediaPipe resources."""
        self.hands.close()
