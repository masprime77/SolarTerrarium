import config
import time
from utils.turn_all_off import turn_all_off
from drivers.led_neopixel import LedNeopixel
from controller.ambient_controller import AmbientController

def mock_weather(wmo, is_day=True, ok=True, age_s=0):
    return {
        "ok": ok,
        "wmo": wmo,
        "label": "",
        "temp": None,
        "humidity": None,
        "is_day": is_day,
        "time": None,
        "source": "MOCK",
        "age_s": age_s,
    }

def demo_sequence():
    time_s = 5
    return [
        # ("Clear day", mock_weather(0, is_day=True), time_s),
        # ("Clear night", mock_weather(0, is_day=False), time_s),
        # ("Cloudy day light", mock_weather(2, is_day=True), time_s),
        # ("Cloudy night light", mock_weather(2, is_day=False), time_s),
        # ("Cloudy day heavy", mock_weather(45, is_day=True), time_s),
        # ("Cloudy night heavy", mock_weather(45, is_day=False), time_s),
        # ("Rainy day light", mock_weather(51, is_day=True), time_s),
        # ("Rainy night light", mock_weather(51, is_day=False), time_s),
        # ("Rainy day heavy", mock_weather(61, is_day=True), time_s),
        # ("Rainy night heavy", mock_weather(61, is_day=False), time_s),
        # ("Snowy day light", mock_weather(71, is_day=True), time_s),
        # ("Snowy night light", mock_weather(71, is_day=False), time_s),
        # ("Snowy day heavy", mock_weather(75, is_day=True), time_s),
        # ("Snowy night heavy", mock_weather(75, is_day=False), time_s),
        # ("Stormy day", mock_weather(95, is_day=True), time_s),
        # ("Stormy night", mock_weather(95, is_day=False), time_s),
        ("Unknown", mock_weather(-1, ok=False), time_s),
    ]

def main():
    overhead = LedNeopixel(pin=config.PIN_OVERHEAD_LED, pixel_count=config.PIXEL_COUNT_OVERHEAD, brightness=config.BRIGHTNESS_OVERHEAD_LED, auto_show=True)
    amb_ctl = AmbientController(led=overhead, fps=24)

    for label, weather, duration_s in demo_sequence():
        print(f"Demo: {label} for {duration_s}s")
        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < duration_s * 1000:
            amb_ctl.render(weather)
            time.sleep_ms(10)

    turn_all_off()

if __name__ == "__main__":
    main()