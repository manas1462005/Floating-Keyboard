import cv2
import time
from detection.hand_tracking import HandTracker
from vkeyboard.virtual_keyboard import VirtualKeyboard

def main():
    cap = cv2.VideoCapture(0)

    # High resolution for fullscreen
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    tracker = HandTracker()
    vkb = VirtualKeyboard()

    window_name = "Air Typing Keyboard"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    pressed_key = None
    hover_key = None
    hover_start_time = None
    hover_delay = 0.75  # seconds before key turns red
    last_pressed_key = None  # Prevent continuous spam of same key

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Mirror view for natural feel
        frame = tracker.find_hands(frame)
        landmarks = tracker.find_position(frame)  # Returns list of (id, x, y)

        pressed_key = None

        if landmarks:
            index_tip = landmarks[8]  # (id, x, y)
            tip_xy = (index_tip[1], index_tip[2])

            # Hover detection
            current_hover_key = vkb.get_key_at_pos(*tip_xy)

            if current_hover_key:
                if current_hover_key == hover_key:
                    # Same key still being hovered
                    if hover_start_time and (time.time() - hover_start_time >= hover_delay):
                        pressed_key = current_hover_key
                        # Only trigger once per key press
                        if pressed_key != last_pressed_key:
                            vkb.press_key(pressed_key)  # Update text buffer
                            last_pressed_key = pressed_key
                else:
                    # Started hovering a new key
                    hover_key = current_hover_key
                    hover_start_time = time.time()
            else:
                hover_key = None
                hover_start_time = None
                last_pressed_key = None  # Reset when finger leaves key

            # Draw fingertip
            cv2.circle(frame, tip_xy, 10, (0, 0, 255), cv2.FILLED)

        # Draw keyboard with hover & pressed key
        frame = vkb.draw(frame, hover_key=hover_key, pressed_key=pressed_key, position="center")

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
