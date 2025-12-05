# SolarTerrarium

Firmware for a Raspberry Pi Pico W “solar terrarium” that paints live sky conditions with LEDs. The board connects to Wi‑Fi, pulls current weather and moon data, reads a local DHT22 for indoor conditions, and visualizes everything with a NeoPixel ring, an overhead strip, and a 10‑LED bar graph.

## What it does
- Connects to Wi‑Fi on boot and keeps the link alive.
- Fetches current weather from Open‑Meteo and moon data from OpenWeather.
- Animates the LED ring through sun/moon phases and the overhead strip through day/night/cloud/rain/snow/storm scenes.
- Shows indoor vs. outdoor temperature on the 10‑LED bar (5 LEDs each).
- Obeys quiet hours defined in `config.py` to turn all lights off.

## Hardware used (default pins)
- Raspberry Pi Pico W (MicroPython)
- DHT22 on `PIN_DHT22_SENSOR = 2`
- NeoPixel ring (7 px) on `PIN_LED_RING = 14`
- NeoPixel strip/overhead (32 px) on `PIN_OVERHEAD_LED = 15`
- 10 single LEDs (or bar graph) on `PIN_LED_BAR10 = [16,17,18,19,20,21,22,26,27,28]`
- Stable 5V supply sized for the LED load; common ground between LEDs and Pico.

## Repo map
- `firmware/main.py` – entry point; orchestrates Wi‑Fi, weather fetch, controllers, and sleep window.
- `firmware/controller/` – renderers for sphere (sun/moon), ambient strip (sky effects), and bar graph (temperature).
- `firmware/services/` – Wi‑Fi, HTTP, weather/mapping helpers, DHT22 integration.
- `firmware/drivers/` – LED and sensor drivers.
- `firmware/tests/` – quick hardware checks and demos; `steps/` holds incremental bring‑up scripts.
- `firmware/config.py` – all tunables (Wi‑Fi, coords, pins, colors, sleep hours, brightness).
- `firmware/api_openweather.py` – OpenWeather API key for moon data.

## Setup
1) Flash MicroPython for Pico W (recent stable build).  
2) Clone this repo locally.  
3) Edit `firmware/config.py` with your Wi‑Fi SSID/password, latitude/longitude, sleep hours, LED counts/pins, and brightness. Avoid committing private credentials.  
4) Put your OpenWeather API key in `firmware/api_openweather.py` (`KEY = "..."`).  
5) Copy the contents of `firmware/` to the Pico so `boot.py` and `main.py` live at the board root (e.g., `mpremote cp -r firmware/* :/`).  
6) Power‑cycle; `boot.py` runs a short animation, then `main.py` starts the live display.

## Running & testing
- Manual start from REPL: `import main; main.main()`.
- Hardware check: run `tests/test_all_hardware.py` to blink/breathe LEDs and read the DHT22.
- Step demos: scripts in `steps/` exercise Wi‑Fi, weather fetch, ambient patterns, thermometer bar, and full test.
- If lights stay off during quiet hours, adjust `SLEEP_START`/`SLEEP_END` in `config.py`.

## Behavior notes
- Weather responses are cached briefly; the device will reuse the last good reading for a grace period if requests fail.
- Wi‑Fi reconnects automatically; the built‑in LED indicates link status during connect.
- Brightness limits (`BRIGHTNESS_LED_RING`, `BRIGHTNESS_OVERHEAD_LED`) are applied to every frame; lower them for USB‑powered setups.
