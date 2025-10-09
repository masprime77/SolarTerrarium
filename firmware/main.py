import time
import config

from services.wifi import WiFiService   
from services.weather_service import WeatherService
from drivers.led_neopixel import LedNeopixel
from drivers.led_bar10 import LedBar10
from controller.sphere_controller import SphereController
from controller.ambient_controller import AmbientController
from controller.bar_controller import BarController

from utils.turn_all_off import turn_all_off

def within_hours(now_tuple, start, end):
    hour, minute = now_tuple[3], now_tuple[4]
    return ((hour == start[0] and minute >= start[1]) or (0 < hour <= end[0] and minute <= end[1]))

def main():
    wifi = WiFiService(ssid=config.WIFI_SSID,
                       password=config.WIFI_PASSWORD,
                       country=config.COUNTRY,
                       host_name=config.HOSTNAME,
                       power_save=True)
    wifi.connect()
    weather_service = WeatherService(coordinates=(config.LATITUDE, config.LONGITUDE))

    sphere = LedNeopixel(pin=config.PIN_LED_RING,
                         pixel_count=config.PIXEL_COUNT_RING,
                         brightness=config.BRIGHTNESS_LED_RING,
                         auto_show=False)
    ambient = LedNeopixel(pin=config.PIN_OVERHEAD_LED,
                          pixel_count=config.PIXEL_COUNT_OVERHEAD,
                          brightness=config.BRIGHTNESS_OVERHEAD_LED,
                          auto_show=False)

    sphere_ctl = SphereController(led=sphere, fps=24)
    ambient_ctl = AmbientController(led=ambient, fps=24)
    bar_ctl = BarController(min_temp_c=0, max_temp_c=36)

    while True:
        wifi.ensure_connected()
        weather = weather_service.get_now(cache_max_age_s=290)
        if not within_hours(weather.get("time_rtc"), config.SLEEP_START, config.SLEEP_END): # off between SLEEP_START_HOUR and SLEEP_END_HOUR
            print("Current time:", weather.get("time_rtc"))
            print(weather)
            t0 = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), t0) < 60 * 5 * 1000:
                sphere_ctl.render(weather=weather)
                ambient_ctl.render(weather=weather)
                bar_ctl.render(weather=weather)
                time.sleep_ms(11)

        else:
            turn_all_off()
            time.sleep(30 * 60)
    
if __name__ == "__main__":
    main()