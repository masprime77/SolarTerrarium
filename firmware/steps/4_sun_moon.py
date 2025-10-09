import config
import time
from utils.turn_all_off import turn_all_off
from drivers.led_neopixel import LedNeopixel
from controller.sphere_controller import SphereController

def _iso(date, hm):  # "YYYY-MM-DD", "HH:MM" -> "YYYY-MM-DDTHH:MM"
    return f"{date}T{hm}"

def _parse_hm(hm):
    h, m = hm.split(":")
    return int(h), int(m)

def _add_minutes_iso(date, hm, minutes):
    # simple minute math for "HH:MM" within same/next day (enough for tests)
    h, m = _parse_hm(hm)
    total = h * 60 + m + minutes
    total %= (24 * 60)
    nh, nm = divmod(total, 60)
    return _iso(date, f"{nh:02d}:{nm:02d}")

# ---------- SUN MOCKS ----------
def mock_weather_sun(phase,
                     date="2025-10-09",
                     sunrise_hm="07:38",
                     sunset_hm="18:46",
                     wmo=1,
                     temp_inside_C=None,
                     age_s=0):
    """
    phase ∈ {"sunrise","dawn","day","dusk","sunset"}
    Chooses 'time' inside each window so your dispatcher hits the right pattern.
    """
    if phase == "sunrise":
        t = _add_minutes_iso(date, sunrise_hm, 30)     # sunrise + 30 min
    elif phase == "dawn":
        t = _add_minutes_iso(date, sunrise_hm, 90)     # sunrise + 90 min
    elif phase == "day":
        # Middle of the day (roughly halfway between sunrise & sunset)
        t = _iso(date, "13:00")
    elif phase == "dusk":
        t = _add_minutes_iso(date, sunset_hm, -90)     # sunset - 90 min
    elif phase == "sunset":
        t = _add_minutes_iso(date, sunset_hm, -30)     # sunset - 30 min
    else:
        raise ValueError("phase must be one of: sunrise, dawn, day, dusk, sunset")

    return {
        "ok": True,
        "wmo": wmo,
        "is_day": True,
        "time": t,
        "sunrise": _iso(date, sunrise_hm),
        "sunset":  _iso(date, sunset_hm),
        # no moon data needed for sun tests
        "moonrise": None,
        "moonset":  None,
        "moon_phase": None,
        "temp_inside_C": temp_inside_C,
        "age_s": age_s,
    }

# ---------- MOON MOCKS ----------
# midpoints for each lunar bucket you’re using
_MOON_PHASE_VAL = {
    "new":              0.00,   # could also use 0.98 to hit the wrap bucket
    "waxing_crescent":  0.125,
    "first_quarter":    0.25,
    "waxing_gibbous":   0.375,
    "full":             0.50,
    "waning_gibbous":   0.625,
    "last_quarter":     0.75,
    "waning_crescent":  0.875,
}

def mock_weather_moon(phase_name,
                      date="2025-10-09",
                      time_hm="20:15",
                      sunrise_hm="07:38",
                      sunset_hm="18:46",
                      moonrise_hm="19:27",
                      moonset_hm="22:56",
                      wmo=1,
                      temp_inside_C=None,
                      age_s=0):
    """
    phase_name ∈ {
      "new","waxing_crescent","first_quarter","waxing_gibbous",
      "full","waning_gibbous","last_quarter","waning_crescent"
    }
    Always returns is_day=False (night), with a moon_phase value that will
    trigger your corresponding moon pattern logic.
    """
    if phase_name not in _MOON_PHASE_VAL:
        raise ValueError("unknown moon phase name")

    return {
        "ok": True,
        "wmo": wmo,
        "is_day": False,
        "time": _iso(date, time_hm),                 # e.g., evening time
        "sunrise": _iso(date, sunrise_hm),
        "sunset":  _iso(date, sunset_hm),
        "moonrise": _iso(date, moonrise_hm),
        "moonset":  _iso(date, moonset_hm),
        "moon_phase": _MOON_PHASE_VAL[phase_name],
        "temp_inside_C": temp_inside_C,
        "age_s": age_s,
    }

def demo_sequence(time_s=10 ):
    return [
        ("Sunrise", mock_weather_sun("sunrise"), time_s),
        ("Dawn",    mock_weather_sun("dawn"),    time_s),
        ("Day",     mock_weather_sun("day"),     time_s),
        ("Dusk",    mock_weather_sun("dusk"),    time_s),
        ("Sunset",  mock_weather_sun("sunset"),  time_s),

        ("Moon: New",              mock_weather_moon("new"),              time_s),
        ("Moon: Waxing Crescent",  mock_weather_moon("waxing_crescent"),  time_s),
        ("Moon: First Quarter",    mock_weather_moon("first_quarter"),    time_s),
        ("Moon: Waxing Gibbous",   mock_weather_moon("waxing_gibbous"),   time_s),
        ("Moon: Full",             mock_weather_moon("full"),             time_s),
        ("Moon: Waning Gibbous",   mock_weather_moon("waning_gibbous"),   time_s),
        ("Moon: Last Quarter",     mock_weather_moon("last_quarter"),     time_s),
        ("Moon: Waning Crescent",  mock_weather_moon("waning_crescent"),  time_s),
    ]

def main():
    ring = LedNeopixel(pin=config.PIN_LED_RING, pixel_count=config.PIXEL_COUNT_RING, brightness=config.BRIGHTNESS_LED_RING, auto_show=True)
    sph_ctl = SphereController(led=ring, fps=24)

    for label, weather, duration_s in demo_sequence():
        print(f"Demo: {label} for {duration_s}s")
        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < duration_s * 1000:
            sph_ctl.render(weather)
            time.sleep_ms(10)

    turn_all_off()

if __name__ == "__main__":
    main()