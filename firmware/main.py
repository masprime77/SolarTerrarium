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
    h, m = now_tuple[3], now_tuple[4]
    start_minutes = start[0]*60 + start[1]
    end_minutes = end[0]*60 + end[1]
    now_minutes = h*60 + m

    if end_minutes > start_minutes:
        return start_minutes <= now_minutes < end_minutes
    else:
        return now_minutes >= start_minutes or now_minutes < end_minutes

def minutes_between(start, end):
    h1, m1 = start
    h2, m2 = end

    t1 = h1 * 60 + m1
    t2 = h2 * 60 + m2

    if t2 <= t1:
        t2 += 24 * 60

    return t2 - t1

def main():
    wifi = WiFiService(ssid=config.WIFI_SSID,
                       password=config.WIFI_PASSWORD,
                       country=config.COUNTRY,
                       host_name=config.HOSTNAME,
                       power_save=True)
    
    wlan = wifi.connect()
    print("WiFi connected:", wlan)

    weather_service = WeatherService(coordinates=(config.LATITUDE, config.LONGITUDE), cache_grace_sec=100)

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
        weather = weather_service.get_now(cache_max_age_s=290)
        print("Weather data:", weather)
        if weather.get("ok", False):
            if not within_hours(weather.get("time_rtc"), config.SLEEP_START, config.SLEEP_END): # off between SLEEP_START_HOUR and SLEEP_END_HOUR
                t0 = time.ticks_ms()
                while time.ticks_diff(time.ticks_ms(), t0) < 60 * 5 * 1000:
                    sphere_ctl.render(weather=weather)
                    ambient_ctl.render(weather=weather)
                    bar_ctl.render(weather=weather)
                    time.sleep_ms(11)

            else:
                turn_all_off()
                time.sleep(minutes_between(config.SLEEP_START, config.SLEEP_END) * 60)
                
        else:
            sphere_ctl.render(weather=weather)
            ambient_ctl.render(weather=weather)
            bar_ctl.render(weather=weather)
            reconnect = wifi.ensure_connected()
            if not reconnect:
                print("WiFi reconnect failed.")
            else:
                print("WiFi reconnected.")
                time.sleep(10)
                weather_service = WeatherService(coordinates=(config.LATITUDE, config.LONGITUDE), cache_grace_sec=100)
    
if __name__ == "__main__":
    main()