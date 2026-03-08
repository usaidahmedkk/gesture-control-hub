"""Sign Language Interpreter module — detects ASL hand signs using landmarks."""

import cv2
from .hand_tracker import HandTracker


class SignLanguage:
    """
    Recognises a subset of the ASL alphabet from hand landmark geometry.

    Supported letters: A, B, C, D, E, F, I, L, O, V, W, Y
    """

    def __init__(self):
        self.tracker = HandTracker(max_hands=1)
        self.letter = ""
        self.word = ""
        self.confidence = 0
        self.frame_count = 0
        self.stable_count = 0
        self.last_stable = ""

    # ------------------------------------------------------------------
    # Gesture classification helpers
    # ------------------------------------------------------------------
    def _classify(self, lm, fingers):
        """Return (letter, confidence) based on landmark positions."""
        if not lm:
            return "", 0

        f = fingers  # [thumb, index, middle, ring, pinky]

        # Distances / helpers
        def dist(a, b):
            return ((lm[a][0] - lm[b][0]) ** 2 + (lm[a][1] - lm[b][1]) ** 2) ** 0.5

        # --- A: fist with thumb to side (no fingers up) ---
        if not any(f):
            # Thumb tip roughly beside index knuckle
            if abs(lm[4][0] - lm[5][0]) < 50:
                return "A", 85

        # --- B: all four fingers up, thumb tucked ---
        if f[1] and f[2] and f[3] and f[4] and not f[0]:
            return "B", 90

        # --- C: curved hand — no fingers extended, palm partially open ---
        if not any(f[1:]) and dist(4, 8) < 80 and dist(4, 8) > 30:
            return "C", 75

        # --- D: index up, others curled, thumb touches middle ---
        if f[1] and not f[2] and not f[3] and not f[4]:
            if dist(4, 12) < 50:
                return "D", 80

        # --- E: all fingers bent (tips near palm) ---
        if all(lm[tip][1] > lm[tip - 1][1] for tip in [8, 12, 16, 20]):
            return "E", 80

        # --- F: OK sign — index + thumb pinched, others up ---
        if f[2] and f[3] and f[4] and dist(4, 8) < 40:
            return "F", 82

        # --- I: only pinky up ---
        if f[4] and not f[1] and not f[2] and not f[3]:
            return "I", 88

        # --- L: index up + thumb out ---
        if f[0] and f[1] and not f[2] and not f[3] and not f[4]:
            return "L", 88

        # --- O: all fingers curved, thumb tip near index tip ---
        if dist(4, 8) < 40 and not any(f[1:]):
            return "O", 80

        # --- V: index + middle up (peace sign) ---
        if f[1] and f[2] and not f[3] and not f[4] and not f[0]:
            return "V", 90

        # --- W: index + middle + ring up ---
        if f[1] and f[2] and f[3] and not f[4] and not f[0]:
            return "W", 88

        # --- Y: thumb + pinky out ---
        if f[0] and f[4] and not f[1] and not f[2] and not f[3]:
            return "Y", 88

        return "", 0

    # ------------------------------------------------------------------
    # Frame processing
    # ------------------------------------------------------------------
    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame = self.tracker.process(frame)
        lm = self.tracker.get_landmarks()
        fingers = self.tracker.fingers_up()

        letter, confidence = self._classify(lm, fingers)
        self.letter = letter
        self.confidence = confidence

        # Stable letter accumulation: same letter for ~20 frames → append
        if letter and letter == self.last_stable:
            self.stable_count += 1
            if self.stable_count == 20:
                self.word += letter
                self.stable_count = 0
        else:
            self.last_stable = letter
            self.stable_count = 0

        self._draw_overlay(frame, letter, confidence)
        return frame

    def _draw_overlay(self, frame, letter, confidence):
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), cv2.FILLED)
        if letter:
            cv2.putText(frame, letter, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 128), 3)
            cv2.putText(frame, f"{confidence}%", (75, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
        else:
            cv2.putText(frame, "No sign detected", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150, 150, 150), 2)
        # Word
        cv2.putText(frame, f"Word: {self.word}", (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)

    def add_space(self):
        self.word += " "

    def clear_word(self):
        self.word = ""

    def get_status(self):
        return {
            "letter": self.letter,
            "confidence": self.confidence,
            "word": self.word,
        }

    def release(self):
        self.tracker.release()
