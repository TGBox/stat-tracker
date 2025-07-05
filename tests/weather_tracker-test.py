import pytest

from modules.weather_tracker import WeatherTracker

def test_initialization():
    wt = WeatherTracker()
    assert isinstance(wt, WeatherTracker)
    assert hasattr(wt, 'records')

def test_add_record():
    wt = WeatherTracker()
    wt.add_record('2024-06-01', 25.5)
    assert len(wt.records) == 1
    assert wt.records[0]['date'] == '2024-06-01'
    assert wt.records[0]['temperature'] == 25.5

def test_get_average_temperature_empty():
    wt = WeatherTracker()
    assert wt.get_average_temperature() == 0

def test_get_average_temperature():
    wt = WeatherTracker()
    wt.add_record('2024-06-01', 20)
    wt.add_record('2024-06-02', 30)
    assert wt.get_average_temperature() == 25

def test_get_max_temperature():
    wt = WeatherTracker()
    wt.add_record('2024-06-01', 18)
    wt.add_record('2024-06-02', 22)
    wt.add_record('2024-06-03', 21)
    assert wt.get_max_temperature() == 22

def test_get_min_temperature():
    wt = WeatherTracker()
    wt.add_record('2024-06-01', 18)
    wt.add_record('2024-06-02', 22)
    wt.add_record('2024-06-03', 15)
    assert wt.get_min_temperature() == 15

def test_add_record_invalid_date():
    wt = WeatherTracker()
    with pytest.raises(ValueError):
        wt.add_record('invalid-date', 20)

def test_add_record_invalid_temperature():
    wt = WeatherTracker()
    with pytest.raises(TypeError):
        wt.add_record('2024-06-01', 'hot')