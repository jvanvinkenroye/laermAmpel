# Lärmampel

Selbstgebaute Lärmampel für Klassenräume und Lernorte - ein Makerspace-Projekt.
Ein MEMS-Mikrofon misst den Schallpegel, WS2812B-LEDs zeigen ihn als Ampelfarbe und
in dB(A), ein Raspberry Pi Zero 2 W protokolliert die Werte.

**Status:** Konzept, Simulation und Konstruktion. Die Hardware ist noch nicht gebaut.

## Inhalt

| Pfad | Inhalt |
|------|--------|
| `TEILELISTE.md` | Teileliste für beide Bauformen |
| `SCHALTUNG.md` | Schaltung, Pinbelegung, Strombudget, Messgenauigkeit |
| `GEHAEUSE_FARBKREIS.md` | Gehäuse und Bau der Variante Farbkreis + Display |
| `VISUALISIERUNG.md` | Variante Tacho-Scheibe |
| `simulator/` | Browser-Simulator beider Bauformen (eine HTML-Datei) |
| `laser/` | Lasercut-Generator `generate_laser.py` und erzeugte SVGs |
| `render/` | Blender-Skript und Renderings |
| `tools/build_site.py` | baut die Website nach `docs/` |
| `docs/` | erzeugte Website für GitHub Pages - nicht von Hand bearbeiten |

## Befehle

```bash
# Lasercut-SVGs neu erzeugen
uv run --no-project python laser/generate_laser.py

# Renderings (Blender 5, außerhalb einer Sandbox ausführen)
/Applications/Blender.app/Contents/MacOS/Blender -b -P render/render_laermampel.py -- 64

# Website neu bauen und lokal ansehen
uv run --no-project python tools/build_site.py
python3 -m http.server -d docs 8000
```

## Website auf GitHub Pages

1. Repository auf GitHub anlegen und pushen.
2. *Settings > Pages*: Source "Deploy from a branch", Branch `main`, Ordner `/docs`.
3. Nach jeder Änderung an Dokumenten, Simulator, SVGs oder Renderings
   `tools/build_site.py` ausführen und `docs/` mit committen.
