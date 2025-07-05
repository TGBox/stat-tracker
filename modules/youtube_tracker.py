# modules/youtube_tracker.py
import sqlite3
import os
import platform
import shutil
import datetime
from sqlite3 import Error

# --- Konfiguration ---
# Name dieses Moduls, wie er in der Datenbank erscheinen soll
MODULE_NAME = "youtube_firefox_tracker"
# Pfad zur zentralen Datenbank. Geht einen Ordner hoch ('..') und dann in 'data'.
DB_FILE = os.path.join('..', 'data', 'statistics.db')


def get_firefox_history_path():
    """
    Findet den Pfad zur Firefox-Verlaufsdatenbank ('places.sqlite')
    für das aktuelle Betriebssystem.
    """
    system = platform.system()
    
    if system == "Windows":
        # Pfad für Windows-Benutzer
        app_data = os.getenv('APPDATA')
        if not app_data:
            return None
        base_path = os.path.join(app_data, 'Mozilla', 'Firefox', 'Profiles')
    elif system == "Darwin": # macOS
        # Pfad für macOS-Benutzer
        base_path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Firefox', 'Profiles')
    elif system == "Linux":
        # Pfad für Linux-Benutzer
        base_path = os.path.join(os.path.expanduser('~'), '.mozilla', 'firefox')
    else:
        return None

    if not os.path.exists(base_path):
        return None

    # Finde den richtigen Profilordner (oft endet er auf '.default-release')
    for folder in os.listdir(base_path):
        if "default-release" in folder or "default" in folder:
            history_path = os.path.join(base_path, folder, 'places.sqlite')
            if os.path.exists(history_path):
                return history_path
    return None


def track_youtube_activity():
    """
    Liest den Firefox-Verlauf, extrahiert YouTube-Videoaufrufe der letzten 24 Stunden
    und gibt sie als Liste von Events zurück.
    
    WICHTIGER HINWEIS: Diese Methode erfasst, WANN ein Video aufgerufen wurde,
    aber nicht, WIE LANGE es angesehen wurde. Die reine Verlaufsdatenbank
    speichert die Wiedergabedauer nicht.
    """
    history_db_path = get_firefox_history_path()
    if not history_db_path:
        print("Fehler: Firefox-Verlaufsdatenbank konnte nicht gefunden werden.")
        return []

    # Erstelle eine temporäre Kopie der Datenbank, um Sperrungen zu umgehen,
    # falls Firefox gerade läuft.
    temp_db_path = "temp_history.sqlite"
    shutil.copy2(history_db_path, temp_db_path)
    print(f"Temporäre Kopie der Verlaufsdatenbank unter '{temp_db_path}' erstellt.")

    conn = None
    events = []
    try:
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Zeitstempel für "vor 24 Stunden" berechnen.
        # Firefox speichert Timestamps in Mikrosekunden seit 1970-01-01.
        yesterday_timestamp = (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1_000_000

        # SQL-Query, um YouTube-Videoaufrufe zu finden
        query = """
        SELECT
            p.url,
            p.title,
            h.visit_date
        FROM
            moz_historyvisits AS h
        JOIN
            moz_places AS p ON h.place_id = p.id
        WHERE
            p.url LIKE '%youtube.com/watch%' AND h.visit_date > ?
        ORDER BY
            h.visit_date DESC;
        """
        
        cursor.execute(query, (yesterday_timestamp,))
        
        rows = cursor.fetchall()
        print(f"{len(rows)} YouTube-Videoaufrufe in den letzten 24 Stunden gefunden.")
        
        for url, title, visit_date_us in rows:
            # Konvertiere den Mikrosekunden-Timestamp in ein lesbares Format
            timestamp_iso = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=visit_date_us)
            
            event = {
                "timestamp": timestamp_iso.isoformat(),
                "source_module": MODULE_NAME,
                "event_type": "youtube_video_watched",
                "value": title  # Speichere den Videotitel als Wert
            }
            events.append(event)

    except Error as e:
        print(f"Ein Datenbankfehler ist aufgetreten: {e}")
    finally:
        if conn:
            conn.close()
        # Lösche die temporäre Datei
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
            print(f"Temporäre Datei '{temp_db_path}' wurde gelöscht.")
    
    return events

def save_events_to_database(events):
    """
    Speichert eine Liste von Event-Diktionären in der zentralen Datenbank.
    """
    if not events:
        print("Keine neuen Events zum Speichern.")
        return

    conn = None
    try:
        # Stelle sicher, dass der Pfad zur DB korrekt ist, wenn das Skript
        # aus dem 'modules'-Ordner ausgeführt wird.
        if not os.path.exists(DB_FILE):
             print(f"Fehler: Die Datenbankdatei unter '{DB_FILE}' wurde nicht gefunden.")
             print("Bitte stelle sicher, dass du zuerst 'database.py' ausgeführt hast.")
             return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        insert_query = "INSERT INTO events (timestamp, source_module, event_type, value) VALUES (?, ?, ?, ?);"
        
        # Bereite die Daten für das Einfügen vor
        data_to_insert = [
            (e['timestamp'], e['source_module'], e['event_type'], e['value'])
            for e in events
        ]
        
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        print(f"{len(events)} neue Events wurden erfolgreich in die Datenbank geschrieben.")

    except Error as e:
        print(f"Fehler beim Schreiben in die Datenbank: {e}")
    finally:
        if conn:
            conn.close()


# --- Hauptausführung ---
if __name__ == '__main__':
    # Dieser Teil wird nur ausgeführt, wenn du das Skript direkt startest.
    # Perfekt zum Testen des Moduls.
    print("Starte YouTube-Tracker-Modul...")
    
    # 1. Daten aus Firefox extrahieren
    youtube_events = track_youtube_activity()
    
    # 2. Extrahierte Daten in die zentrale Datenbank speichern
    if youtube_events:
        print("\Gefundene Events:")
        for event in youtube_events:
            print(f"  - {event['timestamp']}: {event['value']}")
        save_events_to_database(youtube_events)
    else:
        print("Keine neuen YouTube-Aktivitäten gefunden.")
        
    print("\nYouTube-Tracker-Modul beendet.")
