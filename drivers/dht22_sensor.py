import time
import machine
import dht

class DHT22Sensor:
    def __init__(self, pin, refresh_rate_ms=2000):
        self._pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self._dht = dht.DHT22(self._pin)
        self._refresh_rate_ms = refresh_rate_ms
        self._t_last = 0
        self._temp_c = None
        self._hum = None

    def read(self, force=False):
        now = time.ticks_ms()
        if (not force) and self._temp_c is not None:
            if time.ticks_diff(now, self._t_last) < self._refresh_rate_ms:
                return (self._temp_c, self._hum)
        self._dht.measure()
        self._temp_c = self._dht.temperature()
        self._hum = self._dht.humidity()
        self._t_last = now
        return (self._temp_c, self._hum)
    
    def temperature(self):
        return self.read()[0]

    def humidity(self):
        return self.read()[1]
    
    def refresh_rate(self):
        return self._refresh_rate_ms