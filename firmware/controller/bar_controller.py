import config

from drivers.led_bar10 import LedBar10

class BarController:
    def __init__(self, min_temp_c=0, max_temp_c=36):
        self._led = LedBar10(pins=config.PIN_LED_BAR10)
        self._min_temp_c = min_temp_c
        self._max_temp_c = max_temp_c

    def render(self, weather):
        temperature_c = weather.get("temp_inside_C", -100)
        if temperature_c == -100:
            self._bar.set_mask(0b1010110101)
            return
        step = (self._max_temp_c - self._min_temp_c) / (len(self._led._pins) - 1)
        for i in range(len(self._led._pins)):
            threshold = self._min_temp_c + i * step
            if temperature_c >= threshold:
                self._led.set_led(i, "on")
            else:
                self._led.set_led(i, "off")