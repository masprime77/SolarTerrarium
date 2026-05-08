import json
import config

_FILE = "config_override.json"

def load():
    try:
        with open(_FILE) as f:
            _apply(json.load(f))
    except:
        pass

def save(data):
    with open(_FILE, "w") as f:
        json.dump(data, f)

def _apply(data):
    if "sleep_start" in data:
        config.SLEEP_START = tuple(data["sleep_start"])
    if "sleep_end" in data:
        config.SLEEP_END = tuple(data["sleep_end"])
    if "brightness_ring" in data:
        config.BRIGHTNESS_LED_RING = float(data["brightness_ring"])
    if "brightness_overhead" in data:
        config.BRIGHTNESS_OVERHEAD_LED = float(data["brightness_overhead"])
    if "latitude" in data:
        config.LATITUDE = float(data["latitude"])
    if "longitude" in data:
        config.LONGITUDE = float(data["longitude"])
