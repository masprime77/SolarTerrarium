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
    
    def _tuple_to_iso(tup):
        y, m, d, hh, mm = tup
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}".format(y, m, d, hh, mm)

    
    def _add_minutes(self, ts_iso:str, minutes:int):
        if not ts_iso:
            return None
        y, m, d, hh, mm = self._iso_to_tuple(ts_iso)
        sec = utime.mktime((y, m, d, hh, mm, 0, 0, 0)) + minutes * 60
        tup = utime.localtime(sec)
        return self._tuple_to_iso(tup[:5])


    def _pat_sunrise(self):
        """
        Conditions:
          - is_day == True
          - time in [sunrise, sunrise + ~60 min]
        Visual:
          - Warm orange/yellow gradient “rising” from lower edge, slow brighten.
        """
        

    def _pat_dawn(self):
        """
        Conditions:
          - is_day == True
          - time in (sunrise + 60 min, sunrise + 120 min]  (optional “late sunrise” vibe)
        Visual:
          - Soft yellow/white; slightly less warm than sunrise; gentle pulsing.
        """
        pass

    def _pat_day(self):
        """
        Conditions:
          - is_day == True
          - time well between sunrise and sunset (outside dusk/dawn windows)
        Visual:
          - Bright sun core (warm white) with halo; higher brightness cap.
        """
        pass

    def _pat_dusk(self):
        """
        Conditions:
          - is_day == True
          - time in [sunset - 120 min, sunset - 60 min]
        Visual:
          - Cooler yellow → orange; slight dimming; horizon tint.
        """
        pass

    def _pat_sunset(self):
        """
        Conditions:
          - is_day == True
          - time in [sunset - 60 min, sunset] (or until is_day flips to False)
        Visual:
          - Orange → red fade, decreasing brightness; “setting” directionality.
        """
        pass

    def _pat_moon_new(self): pass
    def _pat_moon_waxing_crescent(self): pass
    def _pat_moon_first_quarter(self): pass
    def _pat_moon_waxing_gibbous(self): pass
    def _pat_moon_full(self): pass
    def _pat_moon_waning_gibbous(self): pass
    def _pat_moon_last_quarter(self): pass
    def _pat_moon_waning_crescent(self): pass

    def _transition(self, end_color, duration_ms=5000, steps=100):
        self._led.transition(end_color, duration_ms=duration_ms, steps=steps)

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

        if self._is_day:
            if self._within(self._sunrise_ts, self._add_minutes(self._sunrise_ts, 60),
                            self._current_ts):
                self._pat_sunrise(dt_ms=0)
            elif self._within(self._add_minutes(self._sunrise_ts, 60), self._add_minutes(self._sunrise_ts, 120), self._current_ts):
                self._pat_dawn(dt_ms=0)
            elif self._within(self._add_minutes(self._sunrise_ts, 120), self._add_minutes(self._sunset_ts, -120), self._current_ts):
                self._pat_day(dt_ms=0)
            elif self._within(self._add_minutes(self._sunset_ts, -120), self._add_minutes(self._sunset_ts, -60), self._current_ts):
                self._pat_dusk(dt_ms=0)
            elif self._within(self._add_minutes(self._sunset_ts, -60), self._sunset_ts, self._current_ts):
                self._pat_sunset(dt_ms=0)
            else:
                self._pat_day(dt_ms=0)