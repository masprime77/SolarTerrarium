import time
from drivers.led_neopixel import LedNeopixel

class AmbientController:
    def __init__(self, led: LedNeopixel, dimmed_if_cached: bool = True, fps: int = 24):
        self._led = led
        self._default_brightness = led.brightness
        self._dimmed_if_cached = dimmed_if_cached
        self._fps = fps
        self._f_duration_ms = int(1000 / fps)

        now = time.ticks_ms()
        self._last_frame_ms = now

    def _pat_clear_day():
        pass

    def _pat_clear_night():
        pass

    def _pat_cloudy_day():
        pass

    def _pat_cloudy_night():
        pass

    def _pat_rain_day():
        pass

    def _pat_rain_night():
        pass

    def _pat_snow_day():
        pass

    def _pat_snow_night():
        pass

    def _pat_storm_day():
        pass

    def _pat_storm_night():
        pass

    def _pat_unwnown():
        pass

    def render(self, weather):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_frame_ms) < self._f_duration_ms:
            return
        self._last_frame_ms = now

        ok = weather.get("ok", False)
        wmo = weather.get("wmo", None)
        time_str = weather.get("time", None)
        age_s = weather.get("age_s", 0)