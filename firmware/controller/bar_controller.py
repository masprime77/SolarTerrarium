import config

from drivers.led_bar10 import LedBar10

class BarController:
    def __init__(self, min_temp_c=0, max_temp_c=36):
        self._led = LedBar10(pins=config.PIN_LED_BAR10)
        self._min_temp_c = min_temp_c
        self._max_temp_c = max_temp_c

    def render(self, weather):
        temperature_c = weather.get("temp_inside_C", -100)
        if temperature_c == None:
            self._bar.set_mask(0b1010110101)
            return
        
        def _as_five_bits(temp):
            try:
                value = int(round(float(temp)))
            except (TypeError, ValueError):
                return None
            value = 0 if value < 0 else 31 if value > 31 else value
            return value

        outside_temp = weather.get("temp_outside_C")
        inside_temp = weather.get("temp_inside_C")

        outside_bits = _as_five_bits(outside_temp)
        inside_bits = _as_five_bits(inside_temp)

        if outside_bits is None and inside_bits is None:
            self._led.set_mask(self._ERROR_MASK)
            return

        mask = 0
        if outside_bits is not None:
            mask |= outside_bits & 0b11111  # first 5 LEDs -> outside temp
        if inside_bits is not None:
            mask |= (inside_bits & 0b11111) << 5  # last 5 LEDs -> inside temp

        self._led.set_mask(mask)