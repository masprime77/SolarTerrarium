import config
from drivers.led_neopixel import LedNeopixel

overhead = LedNeopixel(pin=config.PIN_OVERHEAD_LED,
                       pixel_count=config.PIXEL_COUNT_OVERHEAD,
                       brightness=config.BRIGHTNESS_OVERHEAD_LED,
                       auto_show=True)

overhead.set_all((255, 200, 50))