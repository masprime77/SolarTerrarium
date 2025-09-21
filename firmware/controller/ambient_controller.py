from drivers.led_neopixel import LedNeopixel

class AmbientController:
    def __init__(self, led: LedNeopixel, dimmed_if_cached: bool = True, fps: int = 24):
        self._led = led
        self._default_brightness = led.brightness
        self._dimmed_if_cached = dimmed_if_cached
        self._fps = fps
        self._f_duration_ms = int(1000 / fps)

    