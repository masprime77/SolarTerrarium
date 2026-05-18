# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

MicroPython firmware for a Raspberry Pi Pico W that visualizes live sky conditions with LEDs. It fetches weather from Open-Meteo (free, no key) and moon phase data from OpenWeatherMap (key required), reads a DHT22 for indoor temperature, and drives three LED outputs simultaneously.

## Deploying to the device

```bash
# Copy all firmware files to the Pico root
mpremote cp -r firmware/* :/

# Run from REPL without rebooting
import main; main.main()

# Hardware self-test
mpremote run firmware/tests/test_all_hardware.py
```

The `steps/` directory holds numbered bring-up scripts (`1_wifi_connection.py` → `6_final_test.py`) useful for isolating a single subsystem.

On power-on, `boot.py` runs first: calls `turn_all_off()` then a 3× orange breathe animation (`loading_animation`), then `main.py` starts.

## Configuration

There are two layers:

1. **`firmware/config.py`** — static defaults: Wi-Fi credentials, lat/lon, pin assignments, brightness, colors, and `SLEEP_START`/`SLEEP_END` quiet hours. The OpenWeatherMap API key lives in `firmware/api_openweather.py` (`KEY = "..."`). Neither file should be committed with real values.
2. **`config_override.json`** — runtime overrides stored on the Pico filesystem. Written by the web UI after a save; loaded at startup via `utils/config_loader.load()` which patches the live `config` module. Fields that can be overridden: `sleep_start`, `sleep_end`, `brightness_ring`, `brightness_overhead`, `latitude`, `longitude`. Wi-Fi credentials and the API key cannot be changed at runtime.

## Web UI (ALPHA 2.0)

`WebConfig` (port 80) serves a mobile-friendly HTML form for adjusting the overridable config fields. It uses a non-blocking socket (`setblocking(False)`); `web_config.poll()` is called on every iteration of all three loops (render loop, sleep-window wait, error retry). After a successful POST it writes `config_override.json` and schedules a `machine.reset()` 3 s later. Access via `http://<pico-ip>/` or `http://<config.HOSTNAME>/` if your router supports mDNS.

## Architecture

The main loop in `main.py` runs after `load_config_overrides()` patches the live `config` module. Three operating modes:

- **Render loop** (active hours, weather ok): calls `.render(weather)` on all three controllers + `web_config.poll()` at ~24 fps (11 ms sleep). Runs for a 5-minute window, then breaks to re-fetch weather.
- **Sleep loop** (quiet hours): calls `turn_all_off()`, then sleeps in 30 s intervals with `web_config.poll()` until `SLEEP_END`.
- **Error/retry loop** (weather fetch failed): renders error pattern, polls web config, retries WiFi, waits 30 s, then re-creates `WeatherService`.

`within_hours()` in `main.py` handles midnight-crossing ranges correctly (e.g., 23:30 → 07:30).

### Controllers (`firmware/controller/`)

Each controller holds state across frames and is called once per frame:

- **`SphereController`** — drives the 7-pixel NeoPixel ring. Maps the current time against sunrise/sunset to pick a sun phase color (sunrise → dawn → day → dusk → sunset), or moon phase color at night. Calls `LedNeopixel.transition()` which is **blocking** (≤2 s).
- **`AmbientController`** — drives the 32-pixel overhead strip. Dispatches to pattern methods based on WMO code × day/night: clear, cloudy (animated cloud sweep), rain/snow (random blink map via `_generate_objects`), storm (rain + random lightning flash). Rain/snow patterns are **blocking** (~15–600 ms per call via `_blinking_map`).
- **`BarController`** — drives 10 discrete GPIO LEDs. Encodes outside temp in the low 5 bits and inside temp in the high 5 bits of a bitmask (0–31 °C range per side).

### Services (`firmware/services/`)

- **`WeatherService`** — wraps Open-Meteo + OpenWeatherMap fetches with a cache and a grace window (`cache_grace_sec=15*60`). NTP sync happens in `__init__`. The UTC offset is fetched once on init; falls back to `0` on failure.
- **`WiFiService`** — thin wrapper around `network.WLAN`. `connect()` blocks up to `timeout_s`. `ensure_connected()` is called in the error branch of the main loop.

### Drivers (`firmware/drivers/`)

- **`LedNeopixel`** — extends `Blink`. Maintains a `_frame` buffer (list of RGB tuples); `show()` applies `brightness` scaling via `scale_rgb` and writes to hardware. `transition()` and `breathe()` are synchronous blocking animations.
- **`LedBar10`** — wraps 10 GPIO pins. `set_mask(mask)` is the primary method used by `BarController`.
- **`DHT22Sensor`** — caches readings with a 2 s refresh rate; called on every `WeatherService.get_now()` via `_no_format_weather`.

### Key utilities

- `scale_rgb(color, scale)` — multiplies an RGB tuple by a float, clamped to 0–255. Used everywhere for brightness and fade effects.
- `turn_all_off()` — instantiates fresh driver objects and calls `.off()` on each; safe to call from any context.

## WMO weather codes

The mapping is in `services/mapping_wmo.py`. Controllers dispatch on explicit sets of WMO integers — any code not in those sets falls through to the `_pat_unknown()` error pattern (red breathe). The full code→description table is in `WMO` dict if you need to add new codes.

## CI (GitHub Actions)

`.github/workflows/ci.yml` runs on every push/PR to `main` or `dev`. Two jobs:

**`lint-and-syntax`**
1. Syntax-checks all `firmware/**/*.py` with `python -m py_compile`.
2. Lints with `ruff` (ignores: `E402`, `F401`, `E701`, `E722` — all intentional MicroPython patterns).
3. Secrets check: fails if `firmware/api_openweather.py` contains a real-looking 32-char hex key.

**`unit-tests`** — runs `pytest tests/unit/` (26 tests, ~0.02 s).

### Running CI checks locally

```bash
# Syntax
find firmware -name "*.py" | xargs python -m py_compile

# Lint
ruff check firmware/ --ignore E402,F401,E701,E722

# Tests
python -m pytest tests/unit/ -v
```

### Unit test layout

```
tests/
└── unit/
    ├── conftest.py          # stubs machine, network, neopixel, rp2, etc. + config mock
    ├── test_scale_rgb.py    # 8 tests — brightness, clamping, truncation
    ├── test_within_hours.py # 12 tests — normal ranges and midnight-crossing sleep windows
    └── test_wmo_mapping.py  # 5 tests — known codes, coercion, unknowns, full WMO dict coverage
```

`firmware/tests/test_all_hardware.py` is a separate on-device test; run it with `mpremote run`.

The `conftest.py` stubs all MicroPython-only modules into `sys.modules` before any firmware import, so pure-logic functions can be tested with standard CPython. When adding new unit tests for code that imports hardware modules, add any missing stubs to the `_MICROPYTHON_STUBS` list in `conftest.py`.
