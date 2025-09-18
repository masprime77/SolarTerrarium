import machine
from utils.blink import Blink

class LedBuiltin(Blink):
    def __init__(self, pin="LED"):
        self._led = machine.Pin(pin, machine.Pin.OUT)
        self.off()

    def on(self):
        self._led.value(1)
    
    def off(self):
        self._led.value(0)

    def toggle(self):
        self._led.value(not self._led.value())