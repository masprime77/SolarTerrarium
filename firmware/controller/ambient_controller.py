import random
import config
import time
from drivers.led_neopixel import LedNeopixel
from utils.scale_rgb import scale_rgb

class AmbientController:
    def __init__(self, led: LedNeopixel, fps: int = 24):
        self._led = led
        self._default_brightness = led.brightness
        self._fps = fps
        self._f_duration_ms = int(1000 / fps)

        now = time.ticks_ms()
        self._last_frame_ms = now

    def _pat_clear_day(self):
        self._led.set_all(config.COLOR_CLEAR_DAY, show=True)

    def _pat_clear_night(self, step=48, breathe_duration_ms=2000, stars_prob=3):
        stars_map = []
        for _ in range(self._led._pixel_count):
            stars_map.append(True if random.random() < (stars_prob / config.PIXEL_COUNT_OVERHEAD) else False)

        for i in range(2, step + 2):
            c = scale_rgb(config.COLOR_ON, i * (1.0 / step))
            for j in range(self._led._pixel_count):
                if stars_map[j]:
                    self._led.set_pixel(pixel=j, color=c, show=False)
                else:
                    self._led.set_pixel(pixel=j, color=config.COLOR_OFF, show=False)
            self._led.show()
            time.sleep_ms(breathe_duration_ms // step)

        for i in range(step + 1, 1, -1):
            c = scale_rgb(config.COLOR_ON, i * (1.0 / step))
            for j in range(self._led._pixel_count):
                if stars_map[j]:
                    self._led.set_pixel(pixel=j, color=c, show=False)
                else:
                    self._led.set_pixel(pixel=j, color=config.COLOR_OFF, show=False)
            self._led.show()
            time.sleep_ms(breathe_duration_ms // step)
        
        self._led.off()

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
                self._pat_cloudy_day()
            elif wmo in (51, 53, 55, 56, 57):
                self._pat_rain_day()
            elif wmo in (61, 63, 66):
                self._pat_rain_day()
            elif wmo in (65, 67):
                self._pat_rain_day()
            elif wmo in (71, 73):
                self._pat_snow_day()
            elif wmo in (75, 77):
                self._pat_snow_day()
            elif wmo in (80, 81):
                self._pat_rain_day()
            elif wmo in (82, 85, 86):
                self._pat_rain_day()
            elif wmo in (95, 96, 99):
                self._pat_storm_day()
            else:
                self._pat_unknown()
        
        elif not is_day:
            if wmo in (0, 1):
                self._pat_clear_night()
            elif wmo in (2, 3):
                self._pat_cloudy_night()
            elif wmo in (45, 48):
                self._pat_cloudy_night()
            elif wmo in (51, 53, 55, 56, 57):
                self._pat_rain_night()
            elif wmo in (61, 63, 66):
                self._pat_rain_night()
            elif wmo in (65, 67):
                self._pat_rain_night()
            elif wmo in (71, 73):
                self._pat_snow_night()
            elif wmo in (75, 77):
                self._pat_snow_night()
            elif wmo in (80, 81):
                self._pat_rain_night()
            elif wmo in (82, 85, 86):
                self._pat_rain_night()
            elif wmo in (95, 96, 99):
                self._pat_storm_night()
            else:
                self._pat_unknown()
        
        else:
            self._pat_unknown()