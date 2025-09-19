import machine
from utils.blink import Blink

class LedBar10(Blink):
    def __init__(self, pins):
        assert len(pins) == 10, "need 10 pins"
        self._pins = [machine.Pin(p, machine.Pin.OUT) for p in pins]
        self.off()

    def on(self):
        for p in self._pins:
            p.value(1)

    def off(self):
        for p in self._pins:
            p.value(0)

    def set_level(self, level):
        n = 0 if level < 0 else 10 if level > 10 else int(level)
        for i, p in enumerate(self._pins):
            p.value(1 if i < n else 0)

    def set_mask(self, mask):
        for i, p in enumerate(self._pins):
            p.value(1 if (mask >> i) & 1 else 0)

    def set_led(self, pixel, state:str="on"):
        state_map = {"on": 1, "off": 0}
        if state not in state_map:
            raise ValueError("state must be 'on' or 'off'")
        state_i = state_map[state]
        
        self._pins[pixel].value(state_i)