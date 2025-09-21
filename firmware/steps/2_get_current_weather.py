import config
import time
from services.wifi import WiFiService
from services.weather_service import WeatherService
from utils.turn_all_off import turn_all_off

def main():
    wifi = WiFiService(
        ssid=config.WIFI_SSID,
        password=config.WIFI_PASSWORD,
        country=config.COUNTRY,
        host_name=config.HOSTNAME,
        power_save=False)

    print(f"Connecting to '{config.WIFI_SSID}'...")
    wifi.connect(timeout_s=30)
    print("Connected: ", wifi.ifconfig()[0] if wifi.is_connected() else "No connection")

    wth_ser = WeatherService(
        coordinates=(config.LATITUDE, config.LONGITUDE))
    
    wth_now = wth_ser.get_now(cache_max_age_s=10, timeout=10)
    print("Current weather: ", wth_now)

    time.sleep(3)

    turn_all_off()

if __name__ == "__main__":
    main()