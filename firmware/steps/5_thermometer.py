import config
import time

from controller.bar_controller import BarController
from utils.turn_all_off import turn_all_off

bar = BarController()

def mock_temp():
    return [
        {"temp_inside_C": -10},   # all off
        {"temp_inside_C": 0},     # 1 on
        {"temp_inside_C": 4},     # 2 on
        {"temp_inside_C": 8},     # 3 on
        {"temp_inside_C": 12},    # 4 on
        {"temp_inside_C": 16},    # 5 on
        {"temp_inside_C": 20},    # 6 on
        {"temp_inside_C": 24},    # 7 on
        {"temp_inside_C": 28},    # 8 on
        {"temp_inside_C": 32},    # 9 on
        {"temp_inside_C": 36},    # 10 on
    ]

def render():
    for weather in mock_temp():
        bar.render(weather)
        print(f"temp_inside_C={weather['temp_inside_C']}")
        time.sleep(3)

    turn_all_off()

if __name__ == "__main__":
    render()