import time

def process_command(raw_string):
    # String am Komma zerlegen und Leerzeichen entfernen
    parts = [p.strip() for p in raw_string.split(",")]
    
    # Prüfen, ob mindestens Haupt- und Sub-Befehl vorhanden sind
    if len(parts) < 2:
        print(f"[FEHLER] Ungültiger String '{raw_string}' (mind. Haupt- und Sub-Befehl nötig)\n")
        return

    main_cmd = parts[0]      # Ebene 1: Hauptbefehl (z. B. "do")
    sub_cmd = parts[1]       # Ebene 2: Sub-Befehl (z. B. "set" oder "flash")
    params = parts[2:]       # Ebene 3: Parameter-Liste (Rest)

    print(f"--- Telegramm verarbeitet ---")
    print(f"Eingabe:     '{raw_string}'")
    print(f"Hauptbefehl: '{main_cmd}'")
    print(f"Sub-Befehl:  '{sub_cmd}'")
    print(f"Parameter:   {params}")

    # Logik-Verarbeitung
    if main_cmd == "sys":
            if sub_cmd == "reset":
                print("  -> Aktion [sys / reset]")
    elif main_cmd == "set":
        if sub_cmd == "color":
            print("  -> Aktion [set / color]: ", end="")
            for param in params:
                print(param + " / ", end="")
            print()
    elif main_cmd == "do":
        if sub_cmd == "all":
            for param in params:
                if param == "off":
                    print("  -> Aktion [do / all / off]")
                elif param == "def":
                    print("  -> Aktion [do / all / def]")
                elif param == "on":
                    print("  -> Aktion [do / all / on]")
                else:
                    print(f"  -> Aktion [SET]: Unbekannter Parameter '{param}'")

        elif sub_cmd == "flash":
            # Falls Parameter übergeben wurde, als Zahl interpretieren, sonst 1
            count = int(params[0]) if params and params[0].isdigit() else 1
            print(f"  -> Aktion [FLASH]: Führe Blink-Sequenz {count}-mal aus")

        else:
            print(f"  -> [FEHLER] Unbekannter Sub-Befehl: '{sub_cmd}'")
    else:
        print(f"  -> [FEHLER] Unbekannter Hauptbefehl: '{main_cmd}'")
        
    print()  # Leerzeile zur Übersicht

# --- Testläufe ---

# 1. Hauptbefehl "do", Sub-Befehl "set" mit den Parametern "all" und "def"
process_command("do,all,def")

# 2. Sub-Befehl "flash" mit numerischem Parameter
process_command("do,all,on")

# 3. Fehlerfall: Zu kurzer String
process_command("sys,reset")

process_command("set,color,10,20,30")


