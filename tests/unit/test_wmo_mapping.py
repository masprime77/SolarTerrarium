from services.mapping_wmo import label_for, WMO


def test_known_codes_return_correct_label():
    assert label_for(0) == "Clear sky"
    assert label_for(3) == "Overcast"
    assert label_for(61) == "Slight rain"
    assert label_for(95) == "Thunderstorm (light or moderate)"
    assert label_for(99) == "Thunderstorm with heavy hail"


def test_string_int_is_coerced():
    assert label_for("0") == "Clear sky"
    assert label_for("80") == "Slight rain showers"


def test_unknown_code_returns_unknown():
    assert label_for(999) == "Unknown"
    assert label_for(-1) == "Unknown"


def test_non_numeric_returns_unknown():
    assert label_for("abc") == "Unknown"
    assert label_for(None) == "Unknown"


def test_all_wmo_codes_are_in_dict():
    # Ensures the WMO dict covers all expected standard codes without gaps
    expected = {
        0, 1, 2, 3,
        45, 48,
        51, 53, 55, 56, 57,
        61, 63, 65, 66, 67,
        71, 73, 75, 77,
        80, 81, 82, 85, 86,
        95, 96, 99,
    }
    assert expected == set(WMO.keys())
