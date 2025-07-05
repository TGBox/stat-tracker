# modules/holiday_and_appointment_tracker.py - Modul zur Abfrage von Feiertagen und Terminen

import requests
from datetime import datetime, timedelta, date
import json
import calendar # Für die Wochenberechnung

def get_public_holidays(year, country_code="DE"):
    """
    Ruft öffentliche Feiertage für ein bestimmtes Jahr und Land von date.nager.at ab.

    Args:
        year (int): Das Jahr, für das die Feiertage abgerufen werden sollen.
        country_code (str): Der ISO 3166-1 Alpha-2 Ländercode (z.B. "DE" für Deutschland).

    Returns:
        list: Eine Liste von Diktionären, die die Feiertage repräsentieren, oder None bei einem Fehler.
              Jeder Feiertag hat die Schlüssel 'date', 'localName', 'name', 'countryCode', 'fixed', 'global'.
    """
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Löst einen HTTPError für schlechte Antworten (4xx oder 5xx) aus
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Feiertags-API-Anfrage: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der JSON-Antwort der Feiertags-API: {e}")
        return None

def get_appointments_from_calendar():
    """
    Simuliert das Abrufen von Terminen aus einem Kalender.
    In einer realen Anwendung würde hier die Integration mit einer Kalender-API
    (z.B. Google Calendar API mit OAuth2) oder das Parsen einer .ics-Datei erfolgen.

    Returns:
        list: Eine Liste von Diktionären, die die Termine repräsentieren.
              Jeder Termin sollte 'date' (als datetime.date Objekt), 'time' (optional),
              'title' und 'description' enthalten.
    """
    print("Simuliere das Abrufen von Kalenderterminen...")
    # Beispiel-Termine (ersetze dies durch echte Kalenderdaten)
    today = date.today()
    appointments = [
        {
            "date": today,
            "time": "10:00",
            "title": "Zahnarzttermin",
            "description": "Routineuntersuchung"
        },
        {
            "date": today + timedelta(days=2), # Übermorgen
            "time": "15:30",
            "title": "Meeting mit Team",
            "description": "Projektbesprechung Q3"
        },
        {
            "date": today + timedelta(days=5), # In 5 Tagen
            "time": None, # Ganztägiger Termin
            "title": "Geburtstag von Anna",
            "description": "Nicht vergessen anzurufen!"
        },
        {
            "date": today - timedelta(days=3), # Termin aus der letzten Woche (wird ignoriert)
            "time": "09:00",
            "title": "Vergangener Termin",
            "description": "Dieser sollte nicht angezeigt werden."
        }
    ]
    return appointments

def track():
    """
    Sammelt Feiertage und persönliche Termine für die aktuelle Woche und
    speichert diese als Events.

    Returns:
        list: Eine Liste von Diktionären, die die gesammelten Events repräsentieren.
              Jedes Diktionär sollte 'timestamp', 'event_type' und 'value' enthalten.
              'source_module' wird von main.py hinzugefügt.
    """
    events = []
    current_date = date.today()
    current_year = current_date.year

    # Bestimme den Beginn und das Ende der aktuellen Woche (Montag bis Sonntag)
    # Montag ist 0, Sonntag ist 6
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    print(f"Prüfe Feiertage und Termine für die Woche vom {start_of_week.strftime('%Y-%m-%d')} bis {end_of_week.strftime('%Y-%m-%d')}")

    # 1. Feiertage abrufen und filtern
    holidays = get_public_holidays(current_year, "DE")
    if holidays:
        for holiday in holidays:
            holiday_date_str = holiday['date']
            holiday_date = datetime.strptime(holiday_date_str, '%Y-%m-%d').date()

            if start_of_week <= holiday_date <= end_of_week:
                event_value = {
                    "date": holiday_date_str,
                    "name": holiday['name'],
                    "local_name": holiday['localName'],
                    "type": "public_holiday"
                }
                events.append({
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "weekly_holiday_reminder",
                    "value": event_value
                })
                print(f"  Feiertag gefunden: {holiday['localName']} am {holiday_date_str}")
    else:
        print("  Konnte keine Feiertagsdaten abrufen.")

    # 2. Termine abrufen und filtern
    appointments = get_appointments_from_calendar()
    if appointments:
        for appt in appointments:
            appt_date = appt['date'] # Dies ist bereits ein datetime.date Objekt

            if start_of_week <= appt_date <= end_of_week:
                event_value = {
                    "date": appt_date.isoformat(),
                    "time": appt.get('time'),
                    "title": appt['title'],
                    "description": appt.get('description'),
                    "type": "personal_appointment"
                }
                events.append({
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "weekly_appointment_reminder",
                    "value": event_value
                })
                print(f"  Termin gefunden: {appt['title']} am {appt_date.isoformat()} um {appt.get('time', 'ganztägig')}")
    else:
        print("  Konnte keine Kalendertermine abrufen.")

    if not events:
        print("Keine Feiertage oder Termine für diese Woche gefunden.")

    return events

# Beispiel für die Nutzung (kann entfernt werden, wenn main.py die einzige Schnittstelle ist)
if __name__ == "__main__":
    print("Test von holiday_and_appointment_tracker.py:")
    tracked_events = track()
    for event in tracked_events:
        print(event)
