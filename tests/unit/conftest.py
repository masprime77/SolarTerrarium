import os
import sys
import types
from unittest.mock import MagicMock

# Add firmware/ to path so firmware modules resolve correctly
FIRMWARE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "firmware"))
sys.path.insert(0, FIRMWARE_DIR)

# Stub MicroPython-only modules before any firmware imports happen
_MICROPYTHON_STUBS = [
    "machine", "network", "neopixel", "dht",
    "utime", "ujson", "urequests", "uos",
    "ntptime", "socket", "rp2",
]
for _mod in _MICROPYTHON_STUBS:
    sys.modules.setdefault(_mod, MagicMock())

# Stub config with safe defaults so any firmware import that touches config works
_config = types.ModuleType("config")
_config.WIFI_SSID = "test_ssid"
_config.WIFI_PASSWORD = "test_pass"
_config.COUNTRY = "US"
_config.HOSTNAME = "pico"
_config.LATITUDE = 0.0
_config.LONGITUDE = 0.0
_config.PIN_LED_RING = 0
_config.PIN_OVERHEAD_LED = 1
_config.PIN_LED_BAR10 = list(range(10))
_config.PIXEL_COUNT_RING = 7
_config.PIXEL_COUNT_OVERHEAD = 32
_config.BRIGHTNESS_LED_RING = 0.8
_config.BRIGHTNESS_OVERHEAD_LED = 0.8
_config.SLEEP_START = (23, 0)
_config.SLEEP_END = (7, 0)
sys.modules["config"] = _config
