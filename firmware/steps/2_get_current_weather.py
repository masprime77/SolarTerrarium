import config
from drivers.led_builtin import LedBuiltin
from services.wifi import WiFiService
from services.weather_service import WeatherService

def main():
    led_builtin = LedBuiltin()

    wifi = WiFiService(
        ssid=config.WIFI_SSID,
        password=config.WIFI_PASSWORD,
        country=config.COUNTRY,
        host_name=config.HOSTNAME,
        power_save=False,
        led=led_builtin)

    print(f"Connecting to '{config.WIFI_SSID}'...")
    wifi.connect(timeout_s=30)
    print("Connected: ", wifi.ifconfig()[0] if wifi.is_connected() else "No connection")

    wth_ser = WeatherService(
        coordinates=(config.LATITUDE, config.LONGITUDE))
    
    wth_now = wth_ser.get_now(cache_max_age_s=10, timeout=10)
    print("Current weather: ", wth_now)
    

if __name__ == "__main__":
    main()