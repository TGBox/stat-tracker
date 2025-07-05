# modules/shopping_list_tracker.py - Modul zur Verarbeitung von Einkaufszetteln

import base64
import json
from datetime import datetime
import requests
import os

# API-Schlüssel für die Gemini API.
# Im Canvas-Kontext wird dieser automatisch bereitgestellt, wenn er leer ist.
# Für lokale Tests musst du hier deinen eigenen API-Schlüssel einfügen.
API_KEY = "" # LASS DIESEN STRING LEER, WENN DU IM CANVAS BIST

def process_image_with_gemini(base64_image_data, prompt_text):
    """
    Sendet ein Base64-kodiertes Bild an die Gemini API zur Bildanalyse.

    Args:
        base64_image_data (str): Das Base64-kodierte Bild.
        prompt_text (str): Der Text-Prompt für die Gemini API.

    Returns:
        dict: Das JSON-Ergebnis der Gemini API oder None bei einem Fehler.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt_text},
                    {
                        "inlineData": {
                            "mimeType": "image/png", # Oder "image/jpeg" je nach Bildformat
                            "data": base64_image_data
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "items": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                },
                "propertyOrdering": ["items"]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Löst einen HTTPError für schlechte Antworten (4xx oder 5xx) aus
        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            
            # Der Inhalt ist bereits JSON, da responseMimeType gesetzt wurde
            json_string = result["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(json_string)
        else:
            print("Fehler: Unerwartete Antwortstruktur von der Gemini API.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der API-Anfrage: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der JSON-Antwort: {e}")
        print(f"Rohantwort: {response.text}")
        return None
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return None

def track():
    """
    Verarbeitet ein simuliertes Bild eines Einkaufszettels und extrahiert die Artikel.
    In einer realen Anwendung würde hier der Pfad zum Bild übergeben oder
    ein Mechanismus zum Hochladen von Bildern implementiert.

    Returns:
        list: Eine Liste von Diktionären, die die gesammelten Events repräsentieren.
              Jedes Diktionär sollte 'timestamp', 'event_type' und 'value' enthalten.
              'source_module' wird von main.py hinzugefügt.
    """
    events = []
    current_time = datetime.now()

    print("Simuliere die Verarbeitung eines Einkaufszettel-Bildes...")

    # --- SIMULIERTE BILDDATEN ---
    # In einer realen Anwendung würdest du hier ein Bild von der Festplatte laden
    # und es in Base64 kodieren.
    # Beispiel:
    # with open("path/to/your/shopping_list.png", "rb") as image_file:
    #     base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    #
    # Für diese Demonstration verwenden wir ein kleines, generisches Base64-Bild.
    # Dieses Bild ist ein Platzhalter und enthält keinen lesbaren Text.
    # Für echte Tests müsstest du ein Base64-kodiertes Bild eines Einkaufszettels verwenden.
    # Du kannst ein Bild online in Base64 konvertieren, z.B. auf base64.guru/converter/encode/image
    #
    # Beispiel-Prompt: "Was steht auf diesem Einkaufszettel? Gib die Artikel als JSON-Array zurück."
    # Das Modell ist angewiesen, ein JSON-Schema zu verwenden, das ein Array von Strings erwartet.

    # Ein sehr kleines, leeres PNG-Bild (Platzhalter)
    # Ersetze dies durch ein echtes Base64-Bild deines Einkaufszettels für Tests!
    # Ein echtes Bild würde hier viel länger sein.
    simulated_base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

    # Alternativ, um die Funktionalität zu demonstrieren, ohne ein echtes Bild hochladen zu müssen,
    # könnten wir die Antwort des LLM simulieren, wenn kein echtes Bild verfügbar ist.
    # Für die Demonstration der API-Integration bleiben wir jedoch beim Aufruf.

    prompt = "Extrahiere eine Liste von Artikeln von diesem Einkaufszettel. Gib die Antwort als JSON-Objekt mit einem Schlüssel 'items' zurück, dessen Wert ein Array von Strings ist. Beispiel: {\"items\": [\"Milch\", \"Brot\", \"Eier\"]}"

    # Verarbeite das simulierte Bild
    api_response = process_image_with_gemini(simulated_base64_image, prompt)

    if api_response and "items" in api_response:
        shopping_list_items = api_response["items"]
        print(f"Erkannte Artikel: {shopping_list_items}")

        events.append({
            "timestamp": current_time.isoformat(),
            "event_type": "shopping_list_processed",
            "value": {"items": shopping_list_items} # Speichere die Liste der Artikel
        })
    else:
        print("Konnte keine Artikel vom Einkaufszettel-Bild extrahieren oder API-Fehler.")
        events.append({
            "timestamp": current_time.isoformat(),
            "event_type": "shopping_list_processing_failed",
            "value": "no_items_extracted"
        })

    return events

# Beispiel für die Nutzung (kann entfernt werden, wenn main.py die einzige Schnittstelle ist)
if __name__ == "__main__":
    print("Test von shopping_list_tracker.py:")
    # Um dies lokal zu testen, musst du ein echtes Base64-kodiertes Bild
    # eines Einkaufszettels in der `track()`-Funktion einfügen,
    # wo `simulated_base64_image` definiert ist.
    # Stelle auch sicher, dass dein API_KEY gesetzt ist.
    tracked_events = track()
    for event in tracked_events:
        print(event)
