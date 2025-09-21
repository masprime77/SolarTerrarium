import config
import time
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

    def set_coordinates(self, lat, lon):
        self.lat, self.lon = float(lat), float(lon)

    def _now_s(self):
        try:
            return int(time.time())
        except:
            return time.ticks_ms() // 1000
        
    def _build_url(self):
        return (
            "https://api.open-meteo.com/v1/forecast?"
            "latitude={lat}&longitude={lon}"
            "&current=weather_code,"
            "&daily=sunrise,sunset"
            "&forecast_days=1"
            "&timezone=auto"
        ).format(lat=self.lat, lon=self.lon)

    def _no_format_weather(self, raw):
        cur = raw.get("current", {})
        daily = raw.get("daily", {})
        code = cur.get("weather_code")

        return {
            "ok": code is not None,
            "wmo": code,
            "sunrise": daily.get("sunrise", [None])[0],
            "sunset": daily.get("sunset", [None])[0],
            "time": cur.get("time"),
            "temp_inside_C": self._th_sensor.temperature(),
            "age_s":0,
        }
    
    def get_now(self, cache_max_age_s=0, timeout=10):
        now = self._now_s()
        
        if self._last and (now - self._last_ts) < int(cache_max_age_s):
            res = dict(self._last)
            res["age_s"] = now - self._last_ts
            return res
        
        try:
            raw = self._http(self._build_url(), timeout=timeout)
            result = self._no_format_weather(raw)
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
                "time": None,
                "temp_inside_C": None,
                "age_s": 0
            }
    
    def last(self):
        return self._last