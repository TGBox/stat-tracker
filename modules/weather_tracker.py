# modules/weather_tracker.py - Modul zur Abfrage und Speicherung von Wetterdaten

import requests
from datetime import datetime, timedelta
import json

def get_weather_data(latitude, longitude, timezone="Europe/Berlin"):
    """
    Ruft stündliche Wetterdaten von der Open-Meteo API ab.

    Args:
        latitude (float): Breitengrad des Standorts.
        longitude (float): Längengrad des Standorts.
        timezone (str): Zeitzone für die Abfrage.

    Returns:
        dict: Die JSON-Antwort der Open-Meteo API oder None bei einem Fehler.
    """
    # API-Endpunkt für stündliche Vorhersagen
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,weather_code,precipitation_probability,wind_speed_10m",
        "timezone": timezone,
        "forecast_days": 1 # Nur für den heutigen Tag
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Löst einen HTTPError für schlechte Antworten (4xx oder 5xx) aus
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Wetter-API-Anfrage: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der JSON-Antwort der Wetter-API: {e}")
        return None

def interpret_weather_code(wmo_code):
    """
    Interpretiert den WMO Weather Code und gibt eine lesbare Beschreibung zurück.
    Referenz: https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-20/Y9999999.pdf (Seite 27)
    Eine vollständige Liste ist komplex, hier eine vereinfachte Auswahl.
    """
    codes = {
        0: "Klarer Himmel",
        1: "Überwiegend klar",
        2: "Teilweise bewölkt",
        3: "Bewölkt",
        45: "Nebel",
        48: "Ablagernder Reifnebel",
        51: "Leichter Nieselregen",
        53: "Mäßiger Nieselregen",
        55: "Starker Nieselregen",
        56: "Leichter gefrierender Nieselregen",
        57: "Starker gefrierender Nieselregen",
        61: "Leichter Regen",
        63: "Mäßiger Regen",
        65: "Starker Regen",
        66: "Leichter gefrierender Regen",
        67: "Starker gefrierender Regen",
        71: "Leichter Schneefall",
        73: "Mäßiger Schneefall",
        75: "Starker Schneefall",
        77: "Schneegriesel",
        80: "Leichte Regenschauer",
        81: "Mäßige Regenschauer",
        82: "Starke Regenschauer",
        85: "Leichte Schneeschauer",
        86: "Starke Schneeschauer",
        95: "Gewitter (leicht oder mäßig)",
        96: "Gewitter mit leichtem Hagel",
        99: "Gewitter mit starkem Hagel"
    }
    return codes.get(wmo_code, "Unbekannt")

def check_for_warnings(weather_data_point):
    """
    Überprüft einen Wetterdatenpunkt auf potenzielle Warnungen
    basierend auf Windgeschwindigkeit und Niederschlagswahrscheinlichkeit.
    Dies ist eine vereinfachte Simulation.

    Args:
        weather_data_point (dict): Ein Diktionär mit Wetterdaten für einen Zeitpunkt.

    Returns:
        list: Eine Liste von Warnmeldungen (Strings).
    """
    warnings = []
    wind_speed = weather_data_point.get('wind_speed_10m', 0)
    precipitation_probability = weather_data_point.get('precipitation_probability', 0)
    weather_description = weather_data_point.get('weather_description', '')

    if wind_speed >= 40: # z.B. ab 40 km/h Windböen
        warnings.append(f"Windwarnung: Windgeschwindigkeit {wind_speed} km/h erwartet.")
    if precipitation_probability >= 70: # z.B. ab 70% Wahrscheinlichkeit für starken Regen
        if "Regen" in weather_description or "Schauer" in weather_description:
            warnings.append(f"Niederschlagswarnung: Hohe Regenwahrscheinlichkeit ({precipitation_probability}%) erwartet.")
    if "Gewitter" in weather_description:
        warnings.append("Gewitterwarnung: Gewitter erwartet.")
    if "Nebel" in weather_description:
        warnings.append("Sichtwarnung: Nebel erwartet.")

    return warnings

def track():
    """
    Sammelt Wetterdaten für Ulm für spezifische Tageszeiten
    und identifiziert potenzielle Warnungen.

    Returns:
        list: Eine Liste von Diktionären, die die gesammelten Events repräsentieren.
              Jedes Diktionär sollte 'timestamp', 'event_type' und 'value' enthalten.
              'source_module' wird von main.py hinzugefügt.
    """
    events = []
    # Koordinaten für Ulm, Deutschland
    ulm_latitude = 48.4011
    ulm_longitude = 9.9876

    print(f"Rufe Wetterdaten für Ulm ab (Lat: {ulm_latitude}, Lon: {ulm_longitude})...")
    weather_response = get_weather_data(ulm_latitude, ulm_longitude)

    if not weather_response or 'hourly' not in weather_response:
        print("Konnte keine Wetterdaten abrufen oder die Antwort war unerwartet.")
        events.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": "weather_fetch_failed",
            "value": "no_data_available"
        })
        return events

    hourly_data = weather_response['hourly']
    times = hourly_data['time']
    temperatures = hourly_data['temperature_2m']
    weather_codes = hourly_data['weather_code']
    precipitation_probabilities = hourly_data['precipitation_probability']
    wind_speeds = hourly_data['wind_speed_10m']

    # Gewünschte Stunden für die Abfrage
    target_hours = [8, 14, 18, 22]
    today_date = datetime.now().strftime("%Y-%m-%d")

    for i, time_str in enumerate(times):
        dt_object = datetime.fromisoformat(time_str)
        if dt_object.date().strftime("%Y-%m-%d") == today_date and dt_object.hour in target_hours:
            temp = temperatures[i]
            wmo_code = weather_codes[i]
            prec_prob = precipitation_probabilities[i]
            wind_spd = wind_speeds[i]
            weather_desc = interpret_weather_code(wmo_code)

            weather_info = {
                "time": dt_object.strftime("%H:%M"),
                "temperature_celsius": temp,
                "weather_description": weather_desc,
                "precipitation_probability_percent": prec_prob,
                "wind_speed_kmh": wind_spd
            }

            warnings = check_for_warnings({
                "weather_description": weather_desc,
                "wind_speed_10m": wind_spd,
                "precipitation_probability": prec_prob
            })

            event_value = {
                "forecast": weather_info,
                "warnings": warnings if warnings else []
            }

            events.append({
                "timestamp": dt_object.isoformat(),
                "event_type": "weather_forecast",
                "value": event_value
            })
            print(f"Wetter für {dt_object.strftime('%H:%M')} Uhr: {weather_info}")
            if warnings:
                for warning in warnings:
                    print(f"  WARNUNG: {warning}")

    if not events:
        print("Keine Wetterdaten für die Zielstunden gefunden.")

    return events

# Beispiel für die Nutzung (kann entfernt werden, wenn main.py die einzige Schnittstelle ist)
if __name__ == "__main__":
    print("Test von weather_tracker.py:")
    tracked_events = track()
    for event in tracked_events:
        print(event)
