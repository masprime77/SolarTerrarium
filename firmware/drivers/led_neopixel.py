import machine
import neopixel
import time
import config
from utils.blink import Blink
from utils.scale_rgb import scale_rgb

class LedNeopixel(Blink):
    def __init__(self, pin, pixel_count, brightness=1, auto_show=True):
        self._led = neopixel.NeoPixel(machine.Pin(pin), pixel_count)
        self._pixel_count = pixel_count
        self._brightness = brightness
        self._auto_show = auto_show
        self._frame = [(0, 0, 0)] * self._pixel_count
        self.off()

    def pixel_count(self):
        return self._pixel_count
    
    def frame(self):
        return self._frame
    
    def getitem(self, index):
        return self._led[index]
    
    @property
    def brightness(self):
        return self._brightness
    
    @brightness.setter
    def brightness(self, value):
        if value < 0 or value > 1:
            raise ValueError("Brightness must be between 0 and 1")
        self._brightness = value

    def show(self):
        for pixel, color in enumerate(self._frame):
            self._led[pixel] = scale_rgb(color, self._brightness)
        self._led.write()

    def clear_buffer(self, show=None):
        self.set_all(config.COLOR_OFF, show=show)

    def on(self):
        self.set_all(config.COLOR_ON, show=True)

    def off(self):
        self.clear_buffer(show=True)

    def toggle(self):
        for _, color in enumerate(self._frame):
            if color != (0, 0, 0):
                self.off()
                return
        self.on()

    def set_pixel(self, pixel, color, show=None):
        if pixel < 0 or pixel >= self._pixel_count:
            raise ValueError("Pixel index out of range")
        self._frame[pixel] = color
        show_it = self._auto_show if show is None else bool(show)
        if show_it:
            self.show()

    def set_all(self, color, show=None):
        for pixel in range(self._pixel_count):
            self._frame[pixel] = color
        show_it = self._auto_show if show is None else bool(show)
        if show_it:
            self.show()

    def breathe(self, times, colors, step=24, breathe_duration_ms=500, end_on=False):
        for _ in range(times):
            for color in colors:
                for i in range(2, step + 2):
                    c = scale_rgb(color, i * (1.0 / step))
                    self.set_all(c, show=True)
                    time.sleep_ms(breathe_duration_ms // step)
                
                if color == colors[len(colors) - 1] and end_on:
                    break

                for i in range(step + 1, 1, -1):
                    c = scale_rgb(color, i * (1.0 / step))
                    self.set_all(c, show=True)
                    time.sleep_ms(breathe_duration_ms // step)

        if not end_on:
            self.off()

    def breathe_pixel(self, pixel, times, colors, step=24, breathe_duration_ms=500, end_on=False):
        for _ in range(times):
            for color in colors:
                for i in range(2, step + 2):
                    c = scale_rgb(color, i * (1.0 / step))
                    self.set_pixel(pixel, c, show=True)
                    time.sleep_ms(breathe_duration_ms // step)
                
                if color == colors[len(colors) - 1] and end_on:
                    break

                for i in range(step + 1, 1, -1):
                    c = scale_rgb(color, i * (1.0 / step))
                    self.set_pixel(pixel, c, show=True)
                    time.sleep_ms(breathe_duration_ms // step)
        self.off()

    def transition(self, end_color, duration_ms=2000, step=48):
        current_color = self._frame.copy()
        for i in range(step + 1, 1, -1):
            c = scale_rgb(current_color, i * (1.0 / step))
            self.set_all(color=c, show=True)
            time.sleep_ms((duration_ms // 2) // step)

        for i in range(2, step + 2):
            c = scale_rgb(end_color, i * (1.0 / step))
            self.set_all(color=c, show=True)
            time.sleep_ms((duration_ms // 2) // step)


