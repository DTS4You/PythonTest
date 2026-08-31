import os

def datei_existiert(name):
    try:
        os.stat(name)
        return True
    except OSError:
        return False

# Beispiel-Anwendung:
dateiname = "libs/daten.txt"

if datei_existiert(dateiname):
    print(f"'{dateiname}' ist da. Lese Daten...")
    with open(dateiname, "r") as f:
        inhalt = f.read()
        print("Inhalt:", inhalt)
else:
    print(f"'{dateiname}' fehlt. Erstelle neue Datei...")
    with open(dateiname, "w") as f:
        f.write("Erster Log-Eintrag\n")

