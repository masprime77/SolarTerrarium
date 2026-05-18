from utils.scale_rgb import scale_rgb


def test_full_brightness_unchanged():
    assert scale_rgb((255, 128, 64), 1.0) == (255, 128, 64)


def test_half_brightness():
    assert scale_rgb((200, 100, 50), 0.5) == (100, 50, 25)


def test_zero_scale_is_black():
    assert scale_rgb((255, 255, 255), 0.0) == (0, 0, 0)


def test_clamp_upper():
    assert scale_rgb((255, 255, 255), 2.0) == (255, 255, 255)


def test_clamp_lower_negative_scale():
    assert scale_rgb((255, 128, 64), -1.0) == (0, 0, 0)


def test_partial_clamp():
    # Only the red channel overflows
    assert scale_rgb((200, 100, 50), 2.0) == (255, 200, 100)


def test_truncates_not_rounds():
    # int() truncates toward zero, not rounds
    assert scale_rgb((3, 3, 3), 0.9) == (2, 2, 2)


def test_black_input():
    assert scale_rgb((0, 0, 0), 1.0) == (0, 0, 0)
