import config
from drivers.led_neopixel import LedNeopixel

def loading_animation():
    led_ring = LedNeopixel(config.PIN_LED_RING, config.PIXEL_COUNT_RING, config.BRIGHTNESS_LED_RING, auto_show=True)

    led_ring.breathe(breathe_duration_ms=750, times=3, colors=[config.COLOR_BOOT])

if __name__ == "__main__":
    loading_animation()