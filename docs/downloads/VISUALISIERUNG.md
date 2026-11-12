# Lärmampel - Visualisierung

Runde Wandscheibe mit LED-Bogen (Tacho-Prinzip) und großer dB-Anzeige in der Mitte.

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
      o   grün                                     o
        o                                         o
           o                                   o
              (Start)        [Mikro]       (Ende)
              40 dB           o o o        85 dB
```

- **Äußerer Bogen**: 45 LEDs über 270 Grad, von 7:30 Uhr im Uhrzeigersinn bis 4:30 Uhr.
  Unten bleibt eine Lücke von 90 Grad für die Mikrofonöffnung.
- **Skala**: Standard 40-85 dB(A), also genau 1 dB pro LED. Bereich ist konfigurierbar.
- **Mitte**: zwei große 7-Segment-Ziffern aus WS2812B (je ca. 120 mm hoch),
  "dB(A)" als Gravur/Aufdruck auf der Streuscheibe.

## Verhalten

| Element | Darstellung |
|---------|-------------|
| Bogen, Hintergrund | alle 45 LEDs leuchten schwach (ca. 3-5 %) in ihrer Zonenfarbe - die Skala ist immer sichtbar |
| Bogen, Pegel | LEDs vom Start bis zum aktuellen Pegel leuchten voll, jeweils in der Farbe ihrer Zone |
| Zonenfarbe | grün bis Schwelle 1, gelb bis Schwelle 2, rot darüber; Übergang optional als Farbverlauf |
| Spitzenwert | eine LED (weiß oder heller) markiert den Peak, hält 3 s und fällt dann langsam zurück |
| Ziffern | gleitender Leq über ca. 1-2 s, Aktualisierung 2x pro Sekunde, Farbe = aktuelle Zone |
| Dauer-Rot | liegt der Pegel länger als N Sekunden im roten Bereich, pulsiert der ganze Bogen rot |
| Außerhalb Zeitplan | Anzeige aus oder nur Uhrzeit in den Ziffern (gedimmt) |

Die Schwellen 1 und 2 verschieben die Farbgrenzen auf dem Bogen. Standard:
grün < 60 dB(A), gelb 60-70 dB(A), rot > 70 dB(A).

## Zeitkonstanten

| Größe | Wert | Zweck |
|---------|------|-------|
| Bogen | Leq über 250 ms, Abfall max. 10 dB/s | lebendig, aber ohne Flackern |
| Ziffern | Leq über 1-2 s | ruhig ablesbar |
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

## Gehäuseaufbau (Schichten von hinten nach vorn)

1. Rückwand 6 mm Pappelsperrholz, Schlüssellochaufhängung, Pi + Platine
2. Trägerplatte 4 mm mit Nut / Steg für den LED-Bogen und den Ziffernsegmenten
3. Lichtkammern 20-25 mm (gestapelte Lasercut-Lagen oder 3D-Druck, innen weiß):
   - ringförmiger Kanal für den Bogen, einzelne Kammern pro LED für scharfe Punkte
     oder durchgehender Kanal für ein weiches Band
   - eine Kammer pro Segment, damit Segmente nicht ineinander überstrahlen
4. Front: opales Acryl 3 mm, rund, mit Gravur der Skala (40/50/60/70/80) und "dB(A)"
5. Optional Blende aus schwarz eingefärbtem Acryl/Folie außerhalb der leuchtenden Flächen
   für hohen Kontrast

Ziffernhöhe 120 mm ist aus ca. 12-15 m gut ablesbar (Faustregel: 1 cm Zeichenhöhe
pro 1 m Leseabstand ist komfortabel, Minimum ca. 0,5 cm/m).
