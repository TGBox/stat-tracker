# database.py - Hilfsfunktionen für die SQLite-Datenbank

import sqlite3
from datetime import datetime
import json # Für das Speichern komplexerer Daten im 'value'-Feld

def init_db(db_path):
    """
    Initialisiert die SQLite-Datenbank und erstellt die 'events'-Tabelle,
    falls sie noch nicht existiert.

    Args:
        db_path (str): Der vollständige Pfad zur Datenbankdatei.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source_module TEXT NOT NULL,
                event_type TEXT NOT NULL,
                value TEXT -- Kann JSON-String für komplexere Daten enthalten
            )
        ''')
        conn.commit()
        print(f"Datenbank '{db_path}' initialisiert oder bereits vorhanden.")
    except sqlite3.Error as e:
        print(f"Fehler bei der Datenbank-Initialisierung: {e}")
    finally:
        if conn:
            conn.close()

def insert_event(db_path, event_data):
    """
    Fügt ein einzelnes Event in die 'events'-Tabelle ein.

    Args:
        db_path (str): Der vollständige Pfad zur Datenbankdatei.
        event_data (dict): Ein Diktionär, das die Event-Daten enthält.
                           Erwartete Schlüssel: 'timestamp', 'source_module',
                           'event_type', 'value'.
                           'timestamp' sollte im ISO 8601 Format sein.
                           'value' wird in einen JSON-String konvertiert,
                           wenn es kein einfacher Typ ist.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Standardwerte und Typkonvertierung
        timestamp = event_data.get("timestamp", datetime.now().isoformat())
        source_module = event_data.get("source_module", "unknown")
        event_type = event_data.get("event_type", "generic_event")
        value = event_data.get("value")

        # Konvertiere 'value' in einen JSON-String, wenn es ein komplexer Typ ist
        if value is not None and not isinstance(value, (str, int, float, bool)):
            value = json.dumps(value)
        elif value is None:
            value = "null" # Speichere explizit "null" als String

        cursor.execute('''
            INSERT INTO events (timestamp, source_module, event_type, value)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, source_module, event_type, value))
        conn.commit()
        # print(f"Event eingefügt: {event_data}") # Nur zum Debuggen
    except sqlite3.Error as e:
        print(f"Fehler beim Einfügen des Events {event_data}: {e}")
    finally:
        if conn:
            conn.close()

def get_all_events(db_path):
    """
    Ruft alle Events aus der 'events'-Tabelle ab.

    Args:
        db_path (str): Der vollständige Pfad zur Datenbankdatei.

    Returns:
        list: Eine Liste von Diktionären, die die Events repräsentieren.
    """
    conn = None
    events = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row # Ermöglicht den Zugriff auf Spalten per Name
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM events ORDER BY timestamp ASC')
        rows = cursor.fetchall()
        for row in rows:
            event = dict(row)
            # Versuche, den 'value'-String zurück in ein Python-Objekt zu konvertieren
            try:
                if event['value'] == "null":
                    event['value'] = None
                else:
                    event['value'] = json.loads(event['value'])
            except (json.JSONDecodeError, TypeError):
                # Wenn es kein gültiger JSON-String ist, behalte es als String
                pass
            events.append(event)
    except sqlite3.Error as e:
        print(f"Fehler beim Abrufen von Events: {e}")
    finally:
        if conn:
            conn.close()
    return events

# Beispiel für die Nutzung (kann entfernt werden, wenn main.py die einzige Schnittstelle ist)
if __name__ == "__main__":
    test_db_path = 'test_statistics.db'
    init_db(test_db_path)

    # Beispiel-Events
    event1 = {
        "timestamp": datetime.now().isoformat(),
        "source_module": "test_module",
        "event_type": "test_event",
        "value": "Hello World"
    }
    event2 = {
        "timestamp": datetime.now().isoformat(),
        "source_module": "test_module",
        "event_type": "another_test",
        "value": {"key": "value", "number": 123}
    }

    insert_event(test_db_path, event1)
    insert_event(test_db_path, event2)

    print("\nAlle Events:")
    for event in get_all_events(test_db_path):
        print(event)

    # Aufräumen (optional)
    # import os
    # os.remove(test_db_path)
