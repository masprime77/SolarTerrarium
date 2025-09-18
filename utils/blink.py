import time

class Blink:
    def blink(self, times:int=1, duration_s:float=0.5) -> None:
        for _ in range(times):
            self.on()
            time.sleep(duration_s)
            self.off()
            time.sleep(duration_s)
