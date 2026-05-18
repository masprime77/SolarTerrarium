from main import within_hours


def _t(h, m):
    """Build a minimal time tuple with hours at index 3 and minutes at index 4."""
    return (0, 0, 0, h, m, 0, 0, 0)


# --- Normal range (start < end, no midnight crossing) ---

def test_normal_inside():
    assert within_hours(_t(12, 0), (8, 0), (20, 0)) is True


def test_normal_at_start_inclusive():
    assert within_hours(_t(8, 0), (8, 0), (20, 0)) is True


def test_normal_at_end_exclusive():
    assert within_hours(_t(20, 0), (8, 0), (20, 0)) is False


def test_normal_before_start():
    assert within_hours(_t(7, 59), (8, 0), (20, 0)) is False


def test_normal_after_end():
    assert within_hours(_t(23, 0), (8, 0), (20, 0)) is False


# --- Midnight-crossing range (start > end, e.g. sleep 23:30 → 07:30) ---

def test_midnight_cross_at_start_inclusive():
    assert within_hours(_t(23, 30), (23, 30), (7, 30)) is True


def test_midnight_cross_just_before_midnight():
    assert within_hours(_t(23, 59), (23, 30), (7, 30)) is True


def test_midnight_cross_at_midnight():
    assert within_hours(_t(0, 0), (23, 30), (7, 30)) is True


def test_midnight_cross_early_morning_inside():
    assert within_hours(_t(4, 0), (23, 30), (7, 30)) is True


def test_midnight_cross_just_before_end():
    assert within_hours(_t(7, 29), (23, 30), (7, 30)) is True


def test_midnight_cross_at_end_exclusive():
    assert within_hours(_t(7, 30), (23, 30), (7, 30)) is False


def test_midnight_cross_midday_outside():
    assert within_hours(_t(12, 0), (23, 30), (7, 30)) is False


def test_midnight_cross_just_before_start():
    assert within_hours(_t(23, 29), (23, 30), (7, 30)) is False
