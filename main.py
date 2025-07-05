# main.py - Das Hauptprogramm für den Stat-Tracker

import os
import importlib.util
import sqlite3
from datetime import datetime
import sys

# Pfad zur Datenbankdatei
# Die Datenbankdatei wird im 'data'-Ordner erstellt.
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'statistics.db')

# Pfad zum Ordner, der die Tracker-Module enthält
MODULES_DIR = os.path.join(os.path.dirname(__file__), 'modules')

# Stelle sicher, dass der 'data'-Ordner existiert
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Importiere die Datenbank-Hilfsfunktionen
# Wir versuchen, database.py zu importieren. Wenn es nicht gefunden wird,
# wird eine Fehlermeldung ausgegeben.
try:
    # Füge das Verzeichnis des Skripts zum Python-Pfad hinzu,
    # damit database.py gefunden werden kann.
    sys.path.append(os.path.dirname(__file__))
    import database
except ImportError:
    print("Fehler: Die Datei 'database.py' konnte nicht gefunden werden.")
    print("Bitte stelle sicher, dass 'database.py' im selben Verzeichnis wie 'main.py' liegt.")
    sys.exit(1) # Beende das Programm, da die Datenbankfunktionen fehlen

def load_modules(directory):
    """
    Lädt alle Python-Module aus dem angegebenen Verzeichnis.

    Args:
        directory (str): Der Pfad zum Verzeichnis, das die Module enthält.

    Returns:
        list: Eine Liste von geladenen Modulobjekten.
    """
    loaded_modules = []
    if not os.path.exists(directory):
        print(f"Warnung: Modulverzeichnis '{directory}' nicht gefunden.")
        return loaded_modules

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Dateierweiterung .py entfernen
            module_path = os.path.join(directory, filename)

            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    print(f"Warnung: Konnte Spezifikation für Modul '{module_name}' nicht laden.")
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Überprüfe, ob das Modul eine 'track'-Funktion hat
                if hasattr(module, 'track') and callable(module.track):
                    loaded_modules.append(module)
                    print(f"Modul '{module_name}' erfolgreich geladen.")
                else:
                    print(f"Warnung: Modul '{module_name}' hat keine 'track()'-Funktion.")
            except Exception as e:
                print(f"Fehler beim Laden von Modul '{module_name}': {e}")
    return loaded_modules

def main():
    """
    Hauptfunktion des Life-Trackers.
    Initialisiert die Datenbank, lädt Module und sammelt Daten.
    """
    print(f"Starte Life-Tracker um {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Datenbankpfad: {DB_PATH}")

    # Initialisiere die Datenbank (erstellt die Tabelle, falls nicht vorhanden)
    database.init_db(DB_PATH)

    # Lade die Tracker-Module
    tracker_modules = load_modules(MODULES_DIR)

    if not tracker_modules:
        print("Keine Tracker-Module gefunden oder geladen. Beende.")
        return

    # Iteriere durch die geladenen Module und rufe ihre track()-Funktion auf
    for module in tracker_modules:
        module_name = module.__name__.split('.')[-1] # Holt den Dateinamen ohne Pfad
        print(f"\nSammle Daten von Modul: '{module_name}'...")
        try:
            # Die track()-Funktion sollte eine Liste von Event-Diktionären zurückgeben
            events_data = module.track()
            if events_data:
                for event in events_data:
                    # Füge den Modulnamen zum Event hinzu, falls nicht vorhanden
                    if "source_module" not in event:
                        event["source_module"] = module_name
                    database.insert_event(DB_PATH, event)
                print(f"'{len(events_data)}' Events von '{module_name}' in die Datenbank geschrieben.")
            else:
                print(f"Modul '{module_name}' hat keine Events zurückgegeben.")
        except Exception as e:
            print(f"Fehler beim Ausführen von Modul '{module_name}': {e}")

    print("\nDaten-Sammelprozess abgeschlossen.")

if __name__ == "__main__":
    main()