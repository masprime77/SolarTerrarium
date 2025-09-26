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

ring.set_all(config.COLOR_OFF, show=True)
overhead.set_all(config.COLOR_OFF, show=True)

# ring.set_all((100, 100, 165))

# for i in range(ring.pixel_count()):
#     ring.set_pixel(i, config.COLOR_ON)
#     time.sleep(1.5)
#     ring.set_pixel(i, config.COLOR_OFF)

# ring.set_all(config.COLOR_OFF)
# ring.set_pixel(0, config.COLOR_NO_MOON)

# time.sleep(2)

# ring.set_all(config.COLOR_OFF)
# ring.set_pixel(0, config.COLOR_NEW_MOON)

# time.sleep(2)

# ring.set_all(config.COLOR_OFF)
# ring.set_pixel(1, config.COLOR_WAXING_CRESCENT)
# ring.set_pixel(2, config.COLOR_WAXING_CRESCENT)

# time.sleep(2)

# ring.set_all(config.COLOR_OFF)
# ring.set_pixel(0, config.COLOR_FIRST_QUARTER)
# ring.set_pixel(1, config.COLOR_FIRST_QUARTER)
# ring.set_pixel(2, config.COLOR_FIRST_QUARTER)

# time.sleep(2)

# ring
# ring.set_pixel(0, config.COLOR_WAXING_GIBBOUS)
# ring.set_pixel(1, config.COLOR_WAXING_GIBBOUS)
# ring.set_pixel(2, config.COLOR_WAXING_GIBBOUS)
# ring.set_pixel(3, config.COLOR_WAXING_GIBBOUS)
# ring.set_pixel(6, config.COLOR_WAXING_GIBBOUS)

# time.sleep(2)

# ring.set_all(config.COLOR_FULL_MOON)

# time.sleep(2)

# ring.set_all(config.COLOR_OFF)
# ring.set_pixel(0, config.COLOR_WANING_GIBBOUS)
# ring.set_pixel(3, config.COLOR_WANING_GIBBOUS)
# ring.set_pixel(4, config.COLOR_WANING_GIBBOUS)
# ring.set_pixel(5, config.COLOR_WANING_GIBBOUS)
# ring.set_pixel(6, config.COLOR_WANING_GIBBOUS)

# time.sleep(2)

# ring.set_all(config.COLOR_OFF)
# ring.set_pixel(0, config.COLOR_LAST_QUARTER)
# ring.set_pixel(4, config.COLOR_LAST_QUARTER)
# ring.set_pixel(5, config.COLOR_LAST_QUARTER)

# time.sleep(2)

# ring.set_all(config.COLOR_OFF)
# ring.set_pixel(4, config.COLOR_WANING_CRESCENT)
# ring.set_pixel(5, config.COLOR_WANING_CRESCENT)

# ring.set_all(config.COLOR_NO_MOON)
# time.sleep(2)
# ring.set_all(config.COLOR_NEW_MOON)
# time.sleep(2)
# ring.set_all(config.COLOR_WAXING_CRESCENT)
# time.sleep(2)
# ring.set_all(config.COLOR_FIRST_QUARTER)
# time.sleep(2)
# ring.set_all(config.COLOR_WAXING_GIBBOUS)
# time.sleep(2)
# ring.set_all(config.COLOR_FULL_MOON)
# time.sleep(2)
# ring.set_all(config.COLOR_WANING_GIBBOUS)
# time.sleep(2)
# ring.set_all(config.COLOR_LAST_QUARTER)
# time.sleep(2)
# ring.set_all(config.COLOR_WANING_CRESCENT)
# time.sleep(2)
# ring.set_all(config.COLOR_NO_MOON)
# time.sleep(2)
# ring.set_all(config.COLOR_OFF, show=True)

ring.set_all(config.COLOR_SUNRISE)
time.sleep(2)
ring.set_all(config.COLOR_DAWN)
time.sleep(2)
ring.set_all(config.COLOR_DAY)
time.sleep(2)
ring.set_all(config.COLOR_DUSK)
time.sleep(2)
ring.set_all(config.COLOR_SUNSET)