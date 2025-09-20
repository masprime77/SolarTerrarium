import config
from services.wifi import WiFiService
from services.http import http_get_json
from drivers.led_builtin import LedBuiltin

def main():
    led = LedBuiltin()
    wifi = WiFiService(ssid=config.WIFI_SSID, password=config.WIFI_PASSWORD, country=config.COUNTRY, host_name=config.HOSTNAME, power_save=False, led=led)

    try:
        print(config.WIFI_SSID, config.WIFI_PASSWORD)
        print("[Test M1] Connecting to Wi-Fi...")
        wifi.connect(timeout_s=60)
        print("[Test M1] Connected. IP:", wifi.ifconfig()[0])

        print("[Test M1] Fetching test JSON...")
        url = "http://ip-api.com/json"
        data = http_get_json(url, timeout=10)

        print("[Test M1] HTTP GET OK:")
        print("  City:", data.get("city"))
        print("  Country:", data.get("country"))
        print("  Lat/Lon:", data.get("lat"), ",", data.get("lon"))

        led.blink(3, 0.5)

    except Exception as e:
        print("[Test M1] ERROR:", e)
        led.blink(5, 0.2)

    finally:
        print("[Test M1] Finished.")

if __name__ == "__main__":
    main()