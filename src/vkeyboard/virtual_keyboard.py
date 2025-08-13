import cv2
from .key_mapping import KEY_LAYOUT
import time


class VirtualKeyboard:
    def __init__(self, key_size=(80, 80), start_pos=(50, 100), gap=10):
        self.key_size = key_size
        self.start_pos = start_pos
        self.gap = gap
        self.keys = []  # List of key position dicts
        self.text_buffer = ""  # Stores typed text
        self.hover_start_time = None
        self.hover_key = None

    def _generate_key_positions(self, start_pos):
        """Generate key positions based on starting coordinates."""
        keys = []
        x_start, y_start = start_pos
        for row_index, row in enumerate(KEY_LAYOUT):
            row_keys = []
            for col_index, key in enumerate(row):
                x = x_start + col_index * (self.key_size[0] + self.gap)
                y = y_start + row_index * (self.key_size[1] + self.gap)
                row_keys.append({"key": key, "pos": (x, y)})
            keys.append(row_keys)
        return keys

    def draw(self, frame, hover_key=None, pressed_key=None, position="topleft"):
        """Draws the keyboard with hover & pressed highlights."""
        frame_h, frame_w = frame.shape[:2]

        # Calculate starting position
        if position == "center":
            total_width = len(KEY_LAYOUT[0]) * (self.key_size[0] + self.gap) - self.gap
            total_height = len(KEY_LAYOUT) * (self.key_size[1] + self.gap) - self.gap
            start_x = (frame_w - total_width) // 2
            start_y = (frame_h - total_height) // 2
        else:
            start_x, start_y = self.start_pos

        # Generate keys
        self.keys = self._generate_key_positions((start_x, start_y))

        for row in self.keys:
            for k in row:
                x, y = k["pos"]
                w, h = self.key_size
                key_label = k["key"].upper()

                # Handle Space and Backspace display width
                if k["key"] == "Space":
                    w = w * 5  # Make space bar wider
                elif k["key"] == "Backspace":
                    w = int(w * 1.5)

                # State-based coloring
                if pressed_key == k["key"]:
                    color = (0, 0, 255)       # 🔴 Red for pressed
                    text_color = (255, 255, 255)
                    thickness = -1
                elif hover_key == k["key"]:
                    color = (0, 255, 0)       # 🟢 Green for hover
                    text_color = (0, 0, 0)
                    thickness = -1
                else:
                    color = (255, 0, 0)       # 🔵 Blue border for normal
                    text_color = (255, 0, 0)
                    thickness = 2

                cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
                cv2.putText(frame, key_label, (x + 20, y + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)

        # Show typed text above keyboard
        cv2.putText(frame, self.text_buffer, (start_x, start_y - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

        return frame

    def get_key_at_pos(self, x, y):
        """Returns the key under given coordinates, or None."""
        for row in self.keys:
            for k in row:
                key_x, key_y = k["pos"]
                w, h = self.key_size
                if k["key"] == "Space":
                    w = w * 5
                elif k["key"] == "Backspace":
                    w = int(w * 1.5)
                if key_x <= x <= key_x + w and key_y <= y <= key_y + h:
                    return k["key"]
        return None

    def press_key(self, key):
        """Update text buffer for special keys."""
        if key == "Space":
            self.text_buffer += " "
        elif key == "Backspace":
            self.text_buffer = self.text_buffer[:-1]
        else:
            self.text_buffer += key
