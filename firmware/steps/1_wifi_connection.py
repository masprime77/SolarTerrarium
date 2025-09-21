import config
from services.wifi import WiFiService

def main():
    wifi = WiFiService(
        ssid=config.WIFI_SSID,
        password=config.WIFI_PASSWORD,
        country=config.COUNTRY,
        host_name=config.HOSTNAME,
        power_save=False)

    print("Running WiFi connection step...")
    wifi.connect(timeout_s=30)
    print("Connected: ", wifi.ifconfig()[0] if wifi.is_connected() else "No connection")
    print("WiFi connection step finished.")

if __name__ == "__main__":
    main()