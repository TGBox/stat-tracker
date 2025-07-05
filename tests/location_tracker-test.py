import pytest

from modules.location_tracker import (
    LocationTracker,
    LocationNotFoundError,
    InvalidLocationError
)

def test_initialization_with_valid_location():
    tracker = LocationTracker("New York")
    assert tracker.current_location == "New York"

def test_initialization_with_invalid_location():
    with pytest.raises(InvalidLocationError):
        LocationTracker("")

def test_update_location_success():
    tracker = LocationTracker("Paris")
    tracker.update_location("London")
    assert tracker.current_location == "London"

def test_update_location_invalid():
    tracker = LocationTracker("Paris")
    with pytest.raises(InvalidLocationError):
        tracker.update_location("")

def test_get_location_history():
    tracker = LocationTracker("Berlin")
    tracker.update_location("Munich")
    tracker.update_location("Hamburg")
    history = tracker.get_location_history()
    assert history == ["Berlin", "Munich", "Hamburg"]

def test_find_location_in_history_found():
    tracker = LocationTracker("Tokyo")
    tracker.update_location("Osaka")
    tracker.update_location("Kyoto")
    idx = tracker.find_location_in_history("Osaka")
    assert idx == 1

def test_find_location_in_history_not_found():
    tracker = LocationTracker("Delhi")
    tracker.update_location("Mumbai")
    with pytest.raises(LocationNotFoundError):
        tracker.find_location_in_history("Chennai")

def test_reset_history():
    tracker = LocationTracker("Madrid")
    tracker.update_location("Barcelona")
    tracker.reset_history()
    assert tracker.get_location_history() == []

def test_repr_and_str():
    tracker = LocationTracker("Rome")
    assert "Rome" in repr(tracker)
    assert "Rome" in str(tracker)