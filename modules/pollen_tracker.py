# modules/pollen_tracker.py - Modul zur Abfrage und Speicherung von Pollenflugdaten

import requests
from datetime import datetime, timedelta
import json

def get_pollen_data(latitude, longitude, timezone="Europe/Berlin"):
    """
    Ruft stündliche Pollenflugdaten von der Open-Meteo Pollen API ab.

    Args:
        latitude (float): Breitengrad des Standorts.
        longitude (float): Längengrad des Standorts.
        timezone (str): Zeitzone für die Abfrage.

    Returns:
        dict: Die JSON-Antwort der Open-Meteo Pollen API oder None bei einem Fehler.
    """
    # API-Endpunkt für Pollenflugvorhersagen
    url = "https://api.open-meteo.com/v1/pollen"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        # Hier können verschiedene Pollentypen hinzugefügt werden.
        # Eine vollständige Liste findest du in der Open-Meteo Doku.
        "hourly": "grass_pollen,birch_pollen,oak_pollen,pine_pollen,hazel_pollen,ragweed_pollen,alder_pollen,cypress_pollen,plane_pollen,poplar_pollen,olive_pollen,elm_pollen,juniper_pollen,ambrosia_pollen",
        "timezone": timezone,
        "forecast_days": 1 # Nur für den heutigen Tag
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Löst einen HTTPError für schlechte Antworten (4xx oder 5xx) aus
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Pollen-API-Anfrage: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der JSON-Antwort der Pollen-API: {e}")
        return None

def interpret_pollen_level(level):
    """
    Interpretiert den numerischen Pollenfluglevel (0-4) und gibt eine
    lesbare Beschreibung zurück.

    Args:
        level (int): Der numerische Pollenfluglevel.

    Returns:
        str: Die beschreibende Stufe des Pollenflugs.
    """
    if level == 0:
        return "Kein Risiko"
    elif level == 1:
        return "Niedrig"
    elif level == 2:
        return "Mittel"
    elif level == 3:
        return "Hoch"
    elif level == 4:
        return "Sehr Hoch"
    else:
        return "Unbekannt"

def track():
    """
    Sammelt Pollenflugdaten für Ulm für den heutigen Tag.

    Returns:
        list: Eine Liste von Diktionären, die die gesammelten Events repräsentieren.
              Jedes Diktionär sollte 'timestamp', 'event_type' und 'value' enthalten.
              'source_module' wird von main.py hinzugefügt.
    """
    events = []
    # Koordinaten für Ulm, Deutschland
    ulm_latitude = 48.4011
    ulm_longitude = 9.9876

    print(f"Rufe Pollenflugdaten für Ulm ab (Lat: {ulm_latitude}, Lon: {ulm_longitude})...")
    pollen_response = get_pollen_data(ulm_latitude, ulm_longitude)

    if not pollen_response or 'hourly' not in pollen_response:
        print("Konnte keine Pollenflugdaten abrufen oder die Antwort war unerwartet.")
        events.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": "pollen_fetch_failed",
            "value": "no_data_available"
        })
        return events

    hourly_data = pollen_response['hourly']
    times = hourly_data['time']
    
    today_date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Finde den Index für die heutige Tagesmitte oder den ersten Eintrag des Tages
    # Wir nehmen den ersten Eintrag des heutigen Tages, da Pollenflug oft als Tageswert
    # oder als Höchstwert für den Tag relevant ist, nicht unbedingt stündlich.
    today_index = -1
    for i, time_str in enumerate(times):
        dt_object = datetime.fromisoformat(time_str)
        if dt_object.date().strftime("%Y-%m-%d") == today_date_str:
            today_index = i
            break

    if today_index == -1:
        print("Keine Pollenflugdaten für den heutigen Tag gefunden.")
        events.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": "pollen_no_data_today",
            "value": "no_data_for_current_day"
        })
        return events

    # Sammle die Pollenwerte für den heutigen Tag
    pollen_data_today = {}
    # Iteriere über alle Pollentypen, die in der hourly_data vorhanden sind
    for key, values in hourly_data.items():
        if key.endswith('_pollen'):
            pollen_type = key.replace('_pollen', '')
            # Nimm den Wert für den gefundenen heutigen Index
            if i < len(values): # Stelle sicher, dass der Index gültig ist
                level = values[today_index]
                pollen_data_today[pollen_type] = {
                    "level_numeric": level,
                    "level_description": interpret_pollen_level(level)
                }
            else:
                pollen_data_today[pollen_type] = {
                    "level_numeric": -1, # Indikator für fehlende Daten
                    "level_description": "Daten nicht verfügbar"
                }

    if pollen_data_today:
        event_value = {
            "date": today_date_str,
            "pollen_types": pollen_data_today
        }

        events.append({
            "timestamp": datetime.now().isoformat(), # Aktueller Zeitstempel für das Event
            "event_type": "pollen_forecast_daily",
            "value": event_value
        })
        print(f"Pollenflugdaten für heute ({today_date_str}):")
        for pollen_type, data in pollen_data_today.items():
            print(f"  {pollen_type.capitalize()}: {data['level_description']} (Level: {data['level_numeric']})")
    else:
        print("Konnte keine spezifischen Pollenflugdaten für heute extrahieren.")
        events.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": "pollen_extraction_failed",
            "value": "no_specific_pollen_data"
        })

    return events

# Beispiel für die Nutzung (kann entfernt werden, wenn main.py die einzige Schnittstelle ist)
if __name__ == "__main__":
    print("Test von pollen_tracker.py:")
    tracked_events = track()
    for event in tracked_events:
        print(event)
