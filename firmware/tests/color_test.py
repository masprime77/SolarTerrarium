import config
import time
from drivers.led_neopixel import LedNeopixel

overhead = LedNeopixel(pin=config.PIN_OVERHEAD_LED,
                       pixel_count=config.PIXEL_COUNT_OVERHEAD,
                       brightness=config.BRIGHTNESS_OVERHEAD_LED,
                       auto_show=True)

ring = LedNeopixel(pin=config.PIN_LED_RING,
                   pixel_count=config.PIXEL_COUNT_RING,
                   brightness=config.BRIGHTNESS_LED_RING,
                   auto_show=True)

for i in range(ring.pixel_count()):
    ring.set_pixel(i, config.COLOR_ON)
    time.sleep(1.5)
    ring.set_pixel(i, config.COLOR_OFF)
