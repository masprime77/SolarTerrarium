import config
from drivers.led_builtin import LedBuiltin
from drivers.led_neopixel import LedNeopixel
from drivers.led_bar10 import LedBar10

def turn_all_off():
    builtin = LedBuiltin()
    ring = LedNeopixel(config.PIN_LED_RING, config.PIXEL_COUNT_RING, config.BRIGHTNESS_LED_RING, auto_show=True)
    overhead = LedNeopixel(config.PIN_OVERHEAD_LED, config.PIXEL_COUNT_OVERHEAD, config.BRIGHTNESS_OVERHEAD_LED, auto_show=True)
    bar = LedBar10(config.PIN_LED_BAR10)
    
    try:
        builtin.off()
    except:
        pass

    try:
        ring.off()
    except:
        pass

    try:
        overhead.off()
    except:
        pass

    try:
        bar.off()
    except:
        pass

    try:
        builtin.blink(times=3, duration_s=0.3)
    except:
        pass

if __name__ == "__main__":
    turn_all_off()