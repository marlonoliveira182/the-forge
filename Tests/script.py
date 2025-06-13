import pyautogui
import time
import math
import random

def simulate_activity(radius=20, move_interval=10, click_interval=60):
    start_time = time.time()
    initial_position = pyautogui.position()

    print("Script is running indefinitely to keep Teams active.")
    print("Logging activity in real time:")

    while True:
        # Randomized small movement to simulate mouse activity
        angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
        x_offset = radius * math.cos(angle)
        y_offset = radius * math.sin(angle)
        new_position = (initial_position[0] + x_offset, initial_position[1] + y_offset)
        
        pyautogui.moveTo(*new_position, duration=0.5)
        print(f"Moved mouse to position: {new_position}")

        # Simulate a periodic mouse click
        if int(time.time() - start_time) % click_interval == 0:
            pyautogui.click()
            print("Performed a mouse click")

        # Simulate occasional keystroke (pressing Shift key)
        if int(time.time() - start_time) % move_interval == 0:
            pyautogui.press("shift")
            print("Pressed 'Shift' key")

        time.sleep(5)  # Wait before next cycle

if __name__ == "__main__":
    simulate_activity()
