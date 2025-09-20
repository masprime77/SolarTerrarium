import time
import network
import rp2

class WiFiService:
    def __init__(self, ssid: str, password: str, country: str, host_name: str, power_save: bool, led=None):
        self.ssid = ssid
        self.password = password
        self.country = country
        self.host_name = host_name
        self.power_save = power_save
        self.led = led

        try:
            rp2.country(country)
        except:
            pass

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

        try:
            self.wlan.config(hostname=self.host_name)
        except:
            pass

        try:
            self.wlan.config(pm=0 if not power_save else 2)
        except:
            pass

    def connect(self, timeout_s: int = 20) -> bool:
        if self.is_connected():
            self.led.on() if self.led else None
            return True

        if self.led:
            self.led.off()

        self.wlan.connect(self.ssid, self.password)

        t0 = time.ticks_ms()
        while not self.is_connected():
            if self.led:
                self.led.blink(1, 0.2)
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_s * 1000:
                return False
            
        if self.led:
            self.led.on()
        return True

    def is_connected(self) -> bool:
        try:
            return self.wlan.isconnected()
        except:
            return False

    def ifconfig(self):
        return self.wlan.ifconfig() if self.is_connected() else None

    def disconnect(self):
        try:
            self.wlan.disconnect()
        except:
            pass

    def ensure_connected(self, timeout_s: int = 10) -> bool:
        if self.is_connected():
            return True
        return self.connect(timeout_s=timeout_s)