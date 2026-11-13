# Lärmampel

Selbstgebaute Lärmampel für Klassenräume und Lernorte - ein Makerspace-Projekt.
Ein MEMS-Mikrofon misst den Schallpegel, WS2812B-LEDs zeigen ihn als Ampelfarbe und
in dB(A), ein Raspberry Pi Zero 2 W protokolliert die Werte.

**Website:** https://jvanvinkenroye.github.io/laermAmpel/
(Simulator, Teileliste, Schaltung, Bauanleitung, Renderings, Downloads)

**Status:** Konzept, Simulation und Konstruktion. Die Hardware ist noch nicht gebaut;
Maße, Schaltung und Firmware sind ungetestet. Die Firmware ist noch nicht geschrieben.

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

# Renderings (Blender 5): Argument nach -- = Samples, 16 für einen Probelauf
/Applications/Blender.app/Contents/MacOS/Blender -b -P render/render_laermampel.py -- 64

# Website neu bauen und lokal ansehen
uv run --no-project python tools/build_site.py
python3 -m http.server -d docs 8000
```

## Website auf GitHub Pages

Die Seite wird aus dem Ordner `docs/` auf `main` ausgeliefert.

1. *Settings > Pages*: Source "Deploy from a branch", Branch `main`, Ordner **`/docs`**
   (nicht `/` - sonst zeigt Pages nur die README).
2. Nach jeder Änderung an Dokumenten, Simulator, SVGs oder Renderings
   `tools/build_site.py` ausführen und `docs/` mit committen und pushen.
   GitHub baut die Seite danach automatisch neu (ca. 30 s).
3. Wurde nur die Pages-Quelle umgestellt, startet kein neuer Build. Dann von Hand anstoßen:

   ```bash
   gh api -X POST repos/jvanvinkenroye/laermAmpel/pages/builds
   ```

## Bekannte Stolpersteine

- **Blender stürzt beim Start ab** (`MTLBackend::metal_is_supported`,
  `supports_barycentric_whitelist`): Blender läuft in einer Sandbox ohne GPU-Zugriff,
  z. B. aus Claude Code heraus oder mit `!` im Prompt. Blender in einem normalen
  Terminal-Fenster starten.
- **LED-Farben im Rendering blass**: Die Farbdarstellung AgX entsättigt helle Emission.
  Das Skript nutzt deshalb "Standard".
- **Lasercut-Text**: Die Gravur "dB(A)" in `D9_display_front_rauchgrau_3mm.svg` ist Text
  in Baloo - vor dem Lasern in Pfade umwandeln.
