# Laermampel - Visualisierung

Runde Wandscheibe mit LED-Bogen (Tacho-Prinzip) und grosser dB-Anzeige in der Mitte.

## Frontansicht (Durchmesser ca. 38 cm)

```
                    .  o  o  o  o  o  .
               o                          o
           o                                  o
        o          gelb        |      rot         o
      o                                             o
     o                                               o
    o        +-------+  +-------+                     o
    o        |       |  |       |                     o
    o        |   6   |  |   8   |    dB(A)            o
    o        |       |  |       |                     o
     o       +-------+  +-------+                    o
      o   gruen                                     o
        o                                         o
           o                                   o
              (Start)        [Mikro]       (Ende)
              40 dB           o o o        85 dB
```

- **Aeusserer Bogen**: 45 LEDs ueber 270 Grad, von 7:30 Uhr im Uhrzeigersinn bis 4:30 Uhr.
  Unten bleibt eine Luecke von 90 Grad fuer die Mikrofonoeffnung.
- **Skala**: Standard 40-85 dB(A), also genau 1 dB pro LED. Bereich ist konfigurierbar.
- **Mitte**: zwei grosse 7-Segment-Ziffern aus WS2812B (je ca. 120 mm hoch),
  "dB(A)" als Gravur/Aufdruck auf der Streuscheibe.

## Verhalten

| Element | Darstellung |
|---------|-------------|
| Bogen, Hintergrund | alle 45 LEDs leuchten schwach (ca. 3-5 %) in ihrer Zonenfarbe - die Skala ist immer sichtbar |
| Bogen, Pegel | LEDs vom Start bis zum aktuellen Pegel leuchten voll, jeweils in der Farbe ihrer Zone |
| Zonenfarbe | gruen bis Schwelle 1, gelb bis Schwelle 2, rot darueber; Uebergang optional als Farbverlauf |
| Spitzenwert | eine LED (weiss oder heller) markiert den Peak, haelt 3 s und faellt dann langsam zurueck |
| Ziffern | gleitender Leq ueber ca. 1-2 s, Aktualisierung 2x pro Sekunde, Farbe = aktuelle Zone |
| Dauer-Rot | liegt der Pegel laenger als N Sekunden im roten Bereich, pulsiert der ganze Bogen rot |
| Ausserhalb Zeitplan | Anzeige aus oder nur Uhrzeit in den Ziffern (gedimmt) |

Die Schwellen 1 und 2 verschieben die Farbgrenzen auf dem Bogen. Standard:
gruen < 60 dB(A), gelb 60-70 dB(A), rot > 70 dB(A).

## Zeitkonstanten

| Groesse | Wert | Zweck |
|---------|------|-------|
| Bogen | Leq ueber 250 ms, Abfall max. 10 dB/s | lebendig, aber ohne Flackern |
| Ziffern | Leq ueber 1-2 s | ruhig ablesbar |
| Zonenwechsel | Hysterese 2 dB, Haltezeit 2 s | kein Hin- und Herspringen |
| Logging | Leq, Lmax, L90 pro Minute | Datensicherung |

## LED-Kette (eine Datenleitung)

```
Pi GPIO10 -> 74AHCT125 -> 330R -> [Bogen LED 0..44] -> [Ziffer Zehner 45..65] -> [Ziffer Einer 66..86]
```

Ziffer: 7 Segmente x 3 LEDs = 21 LEDs, Segmentreihenfolge a, b, c, d, e, f, g:

```
      aaa
     f   b
     f   b
     f   b
      ggg
     e   c
     e   c
     e   c
      ddd
```

Gesamt: 45 + 2 x 21 = 87 LEDs.

## Gehaeuseaufbau (Schichten von hinten nach vorn)

1. Rueckwand 6 mm Pappelsperrholz, Schluessellochaufhaengung, Pi + Platine
2. Traegerplatte 4 mm mit Nut / Steg fuer den LED-Bogen und den Ziffernsegmenten
3. Lichtkammern 20-25 mm (gestapelte Lasercut-Lagen oder 3D-Druck, innen weiss):
   - ringfoermiger Kanal fuer den Bogen, einzelne Kammern pro LED fuer scharfe Punkte
     oder durchgehender Kanal fuer ein weiches Band
   - eine Kammer pro Segment, damit Segmente nicht ineinander ueberstrahlen
4. Front: opales Acryl 3 mm, rund, mit Gravur der Skala (40/50/60/70/80) und "dB(A)"
5. Optional Blende aus schwarz eingefaerbtem Acryl/Folie ausserhalb der leuchtenden Flaechen
   fuer hohen Kontrast

Ziffernhoehe 120 mm ist aus ca. 12-15 m gut ablesbar (Faustregel: 1 cm Zeichenhoehe
pro 1 m Leseabstand ist komfortabel, Minimum ca. 0,5 cm/m).
