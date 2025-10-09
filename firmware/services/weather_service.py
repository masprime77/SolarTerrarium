import config
import time
import api_openweather
import utime
import ntptime

from services.http import http_get_json
from drivers.dht22_sensor import DHT22Sensor

class WeatherService:
    def __init__(self, coordinates, cache_grace_sec=60*60, http=http_get_json):
        self.lat, self.lon = float(coordinates[0]), float(coordinates[1])
        self._http = http
        self._grace = int(cache_grace_sec)
        self._last = None
        self._last_ts = 0
        self.source = "open-meteo"
        self._th_sensor = DHT22Sensor(pin=config.PIN_DHT22_SENSOR)
        self._offset = self._get_offset(self.lat, self.lon)

        ntptime.host = "time.google.com"
        ntptime.settime()

    def set_coordinates(self, lat, lon):
        self.lat, self.lon = float(lat), float(lon)

    def _now_s(self):
        try:
            return int(time.time())
        except:
            return time.ticks_ms() // 1000
        
    def _build_url(self):
        return (
            "http://api.open-meteo.com/v1/forecast?"
            "latitude={lat}&longitude={lon}"
            "&current=weather_code"
            "&daily=sunrise,sunset"
            "&forecast_days=1"
            "&timezone=auto"
        ).format(lat=self.lat, lon=self.lon)
    
    def _build_url_moon(self):
        return (
            "https://api.openweathermap.org/data/3.0/onecall?"
            "lat={lat}&lon={lon}&appid={api_key}"
        ).format(lat=self.lat, lon=self.lon, api_key=api_openweather.KEY)
    
    def _local_now_iso(self, offset_s=0):
        t = utime.localtime(utime.time() + offset_s)  # add local offset
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4])

    def _get_offset(self, lat, lon):
        url = (
            f"http://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m&timezone=auto"
        )

        data = http_get_json(url)

        return data.get("utc_offset_seconds", 0)
    
    def ts_to_iso(self, unix_ts, offset=0):
        if unix_ts is None:
            return None
        tm = utime.localtime(unix_ts + offset)
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}".format(tm[0], tm[1], tm[2], tm[3], tm[4])

    def _no_format_weather(self, raw):
        cur = raw.get("current", {})
        daily = raw.get("daily", {})
        code = cur.get("weather_code")
        time = self._local_now_iso(self._offset)
        time_rtc = utime.localtime(utime.time() + self._offset)
        sunrise = daily.get("sunrise", [None])[0]
        sunset = daily.get("sunset", [None])[0]

        return {
            "ok": code is not None,
            "wmo": code,
            "time": time,
            "time_rtc": time_rtc,
            "sunrise": sunrise,
            "sunset": sunset,
            "is_day": sunrise is not None and sunset is not None and time is not None and sunrise <= time <= sunset,
            "temp_inside_C": self._th_sensor.temperature(),
            "age_s":0,
        }
    
    def _no_format_moon(self, raw):
        today = raw["daily"][0]

        return {
            "moonrise": self.ts_to_iso(today.get("moonrise"), self._offset),
            "moonset": self.ts_to_iso(today.get("moonset"), self._offset),
            "moon_phase": today.get("moon_phase")
        }
    
    def get_now(self, cache_max_age_s=0, timeout=10):
        now = self._now_s()
        
        if self._last and (now - self._last_ts) < int(cache_max_age_s):
            res = dict(self._last)
            res["age_s"] = now - self._last_ts
            return res
        
        try:
            weather_data_raw = self._http(self._build_url(), timeout=timeout)
            result = self._no_format_weather(weather_data_raw)

            try:
                moon_data_raw = self._http(self._build_url_moon(), timeout=timeout)
            except Exception as e:
                print(f"Warning: cannot get moon data: {e}")
                moon_data_raw = None

            if moon_data_raw is not None:
                moon_data = self._no_format_moon(moon_data_raw)
                result.update(moon_data)            
            
            self._last = result
            self._last_ts = now
            return result
        except Exception as e:
            print(f"Error: {e}!")
            if self._last and (now - self._last_ts) <= self._grace:
                res = dict(self._last)
                res["age_s"] = now - self._last_ts
                return res
            
            return {
                "ok": False,
                "wmo": None,
                "sunrise": None,
                "sunset": None,
                "is_day": None,
                "time": None,
                "temp_inside_C": None,
                "age_s": 0
            }
    
    def last(self):
        return self._last