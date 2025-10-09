import config
import time
import utime
from drivers.led_neopixel import LedNeopixel

class SphereController:
    def __init__(self, led:LedNeopixel, fps:int=24):
        self._led = led
        self._f_duration_ms = int(1000 / fps)
        self._last_frame_ms = time.ticks_ms()
        self._is_day = True
        self._current_ts = None
        self._sunrise_ts = None
        self._sunset_ts = None
        self._moonrise_ts = None
        self._moonset_ts = None
        self._moon_phase = 0

    def _within(self, start_iso, end_iso, current_ts):
        if not (start_iso and end_iso and current_ts):
            return False
        return start_iso < current_ts < end_iso
    
    def _iso_to_tuple(self, ts_iso:str):
        date, hm = ts_iso.split("T")
        y, m, d = [int(x) for x in date.split("-")]
        hh, mm = [int(x) for x in hm.split(":")]
        return y, m, d, hh, mm
    
    def _tuple_to_iso(self, tup):
        y, m, d, hh, mm = tup
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}".format(y, m, d, hh, mm)

    
    def _add_minutes(self, ts_iso:str, minutes:int):
        if not ts_iso:
            return None
        y, m, d, hh, mm = self._iso_to_tuple(ts_iso)
        sec = utime.mktime((y, m, d, hh, mm, 0, 0, 0)) + minutes * 60
        tup = utime.localtime(sec)
        return self._tuple_to_iso(tup[:5])
    
    def _moon_phase_name(self, p: float | None) -> str:
        if p is None:
            return "unknown"

        if p < 0:
            p = 0.0

        p = p % 1.0

        if p < 0.0625 or p >= 0.9375:  return "new"
        if p < 0.1875:                 return "waxing_crescent"
        if p < 0.3125:                 return "first_quarter"
        if p < 0.4375:                 return "waxing_gibbous"
        if p <= 0.5625:                return "full"
        if p <= 0.6875:                return "waning_gibbous"
        if p <= 0.8125:                return "last_quarter"
        return "waning_crescent"

    def _transition(self, end_color, duration_ms=5000, step=100):
        if self._led.frame()[0] == end_color:
            return
        self._led.transition(end_color, duration_ms=duration_ms, step=step)

    def _pat_unknown(self):
        self._led.breathe(times=1, colors=[config.COLOR_RED], step=30,
                          breathe_duration_ms=1000, end_on=False)

    def render(self, weather):
        now =time.ticks_ms()
        if time.ticks_diff(now, self._last_frame_ms) < self._f_duration_ms:
            return
        self._last_frame_ms = now

        ok = weather.get("ok", False)
        wmo = weather.get("wmo", None)
        self._is_day = weather.get("is_day", True)
        self._current_ts = weather.get("time", None)
        self._sunrise_ts = weather.get("sunrise", None)
        self._sunset_ts = weather.get("sunset", None)
        self._moonrise_ts = weather.get("moonrise", None)
        self._moonset_ts = weather.get("moonset", None)
        self._moon_phase = weather.get("moon_phase", 0)

        if not ok or wmo is None:
            self._pat_unknown()

        elif self._is_day:
            if self._within(self._sunrise_ts, self._add_minutes(self._sunrise_ts, 60),
                            self._current_ts):
                self._transition(config.COLOR_SUNRISE)
            elif self._within(self._add_minutes(self._sunrise_ts, 60), self._add_minutes(self._sunrise_ts, 120), self._current_ts):
                self._transition(config.COLOR_DAWN)
            elif self._within(self._add_minutes(self._sunrise_ts, 120), self._add_minutes(self._sunset_ts, -120), self._current_ts):
                self._transition(config.COLOR_DAY)
            elif self._within(self._add_minutes(self._sunset_ts, -120), self._add_minutes(self._sunset_ts, -60), self._current_ts):
                self._transition(config.COLOR_DUSK)
            elif self._within(self._add_minutes(self._sunset_ts, -60), self._sunset_ts, self._current_ts):
                self._transition(config.COLOR_SUNSET)
            else:
                self._transition(config.COLOR_DAY)
        
        elif not self._is_day:
            if self._within(self._moonrise_ts, self._moonset_ts, self._current_ts):
                phase_name = self._moon_phase_name(self._moon_phase)
                if phase_name == "new":
                    self._transition(config.COLOR_NEW_MOON)
                elif phase_name == "waxing_crescent":
                    self._transition(config.COLOR_WAXING_CRESCENT)
                elif phase_name == "first_quarter":
                    self._transition(config.COLOR_FIRST_QUARTER)
                elif phase_name == "waxing_gibbous":
                    self._transition(config.COLOR_WAXING_GIBBOUS)
                elif phase_name == "full":
                    self._transition(config.COLOR_FULL_MOON)
                elif phase_name == "waning_gibbous":
                    self._transition(config.COLOR_WANING_GIBBOUS)
                elif phase_name == "last_quarter":
                    self._transition(config.COLOR_LAST_QUARTER)
                elif phase_name == "waning_crescent":
                    self._transition(config.COLOR_WANING_CRESCENT)

        else:
            self._pat_unknown() 