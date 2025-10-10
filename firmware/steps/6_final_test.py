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

def demo_sequence():
    """
    Return demo weather data for all sun and moon phases + sleep hours.
    Each item: (label, duration_s, weather_dict)
    """
    time_s = 5  # duration per phase (seconds)

    # Example sunrise/sunset for a given day
    sunrise = "2025-10-09T07:30"
    sunset  = "2025-10-09T18:45"

    # Synthetic timestamps for demonstration
    t_sleep_morning = "2025-10-09T06:30"   # before sunrise (sleep)
    t_sunrise       = "2025-10-09T07:35"
    t_dawn          = "2025-10-09T09:00"
    t_day           = "2025-10-09T13:00"
    t_dusk          = "2025-10-09T17:30"
    t_sunset        = "2025-10-09T18:40"
    t_night         = "2025-10-09T21:00"
    t_sleep_night   = "2025-10-09T23:40"   # after 23:30 (sleep)


    def iso_to_rtc_tuple(ts_iso):
        date, hm = ts_iso.split("T")
        y, m, d = [int(x) for x in date.split("-")]
        hh, mm = [int(x) for x in hm.split(":")]
        sec = time.mktime((y, m, d, hh, mm, 0, 0, 0))
        lt  = time.localtime(sec)
        return (lt[0], lt[1], lt[2], lt[3], lt[4], lt[5], lt[6], lt[7])

    def make_entry(label, t, is_day, moon_phase=None):
        return (
            label,
            time_s,
            {
                "ok": True,
                "wmo": 45,
                "time": t,
                "time_rtc": iso_to_rtc_tuple(t),
                "sunrise": sunrise,
                "sunset": sunset,
                "moonrise": "2025-10-09T19:20",
                "moonset": "2025-10-09T10:30",
                "moon_phase": moon_phase,
                "is_day": sunrise is not None and sunset is not None and t is not None and sunrise <= t <= sunset,
                "temp_inside_C": 10,
                "age_s": 0,
            },
        )

    seq = [
        # 😴 Sleep hours
        make_entry("sleep_morning", t_sleep_morning, False),

        # ☀️ Sun phases
        make_entry("sunrise", t_sunrise, True),
        make_entry("dawn",    t_dawn,    True),
        make_entry("day",     t_day,     True),
        make_entry("dusk",    t_dusk,    True),
        make_entry("sunset",  t_sunset,  True),

        # 🌙 Moon phases
        make_entry("new_moon",        t_night, False, 0.00),
        make_entry("waxing_crescent", t_night, False, 0.125),
        make_entry("first_quarter",   t_night, False, 0.25),
        make_entry("waxing_gibbous",  t_night, False, 0.375),
        make_entry("full_moon",       t_night, False, 0.50),
        make_entry("waning_gibbous",  t_night, False, 0.625),
        make_entry("last_quarter",    t_night, False, 0.75),
        make_entry("waning_crescent", t_night, False, 0.875),

        # 😴 Sleep hours
        make_entry("sleep_night",   t_sleep_night,   False),
    ]

    return seq

def within_hours(now_tuple, start, end):
    h, m = now_tuple[3], now_tuple[4]
    start_minutes = start[0]*60 + start[1]
    end_minutes = end[0]*60 + end[1]
    now_minutes = h*60 + m

    if end_minutes > start_minutes:
        return start_minutes <= now_minutes < end_minutes
    else:
        return now_minutes >= start_minutes or now_minutes < end_minutes

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

    for label, duration_s, weather_getted in demo_sequence():
        wifi.ensure_connected()
        weather = weather_getted
        print(f"Demoing: {label} for {duration_s} seconds")
        if not within_hours(weather.get("time_rtc"), config.SLEEP_START, config.SLEEP_END): # off between SLEEP_START_HOUR and SLEEP_END_HOUR
            # print("Current time:", weather.get("time_rtc"))
            # print(weather)
            t0 = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), t0) < duration_s * 1000:
                sphere_ctl.render(weather=weather)
                ambient_ctl.render(weather=weather)
                bar_ctl.render(weather=weather)
                time.sleep_ms(11)

        else:
            turn_all_off()
            print("Sleeping... Zzz...")
            time.sleep(5)
    
if __name__ == "__main__":
    main()