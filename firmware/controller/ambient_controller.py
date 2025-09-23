import time
from drivers.led_neopixel import LedNeopixel

class AmbientController:
    def __init__(self, led: LedNeopixel, fps: int = 24):
        self._led = led
        self._default_brightness = led.brightness
        if self._dimm_scale < 0 or self._dimm_scale > 1:
            raise ValueError("dimm_scale must be between 0 and 1")
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
        is_day = weather.get("is_day", True)
        age_s = weather.get("age_s", 0)

        if not ok or wmo is None:
            self._pat_unwnown()
        elif is_day:
            if wmo in (0, 1):
                self._pat_clear_day()
            elif wmo in (2, 3):
                self._pat_cloudy_day()
            elif wmo in (45, 48):
                self._pat_cloudy(14, visibility=0.5)
            elif wmo in (51, 53, 55, 56, 57):
                self._pat_rain(rain_speed_ms=300, drops=2)
            elif wmo in (61, 63, 66):
                self._pat_rain(rain_speed_ms=200, drops=4)
            elif wmo in (65, 67):
                self._pat_rain(rain_speed_ms=100, drops=6)
            elif wmo in (71, 73):
                self._pat_snow(snow_speed_ms=500, snow_flakes=4)
            elif wmo in (75, 77):
                self._pat_snow(snow_speed_ms=350, snow_flakes=8)
            elif wmo in (80, 81):
                self._pat_rain(rain_speed_ms=150, drops=6)
            elif wmo in (82, 85, 86):
                self._pat_rain(rain_speed_ms=100, drops=10)
            elif wmo in (95, 96, 99):
                self._pat_storm()
            else:
                self._pat_unknown()