# Lärmampel Variante B - Farbkreis + Display

Farbkreis (Ø 360 mm, leuchtet flächig in der Ampelfarbe) und daneben ein
Displaykasten (240 x 200 mm) mit zwei 7-Segment-Ziffern und der gesamten Elektronik.
Lasercut-Vorlagen: `laser/svg/`, erzeugt von `laser/generate_laser.py`.
Vorschau im Simulator: `simulator/index.html`, Variante "Farbkreis + Display".

## Ansicht und Maße

```
 ┌──────────────────────────────────────────────────────────────┐  G1 gemeinsame Rückwand
 │       .-''''''-.                                             │  (optional, ersetzt K1 + D1)
 │    .'            '.          ┌──────────────────────┐        │
 │   /                \         │   ┌──┐    ┌──┐       │        │
 │  |    Farbkreis     |========│   │  │    │  │       │        │  ==== Kabelbrücke
 │  |    Ø 360         |        │   └──┘    └──┘       │        │
 │   \                /         │       dB(A)    (o)   │        │  (o) Mikrofon
 │    '.            .'          └──────────────────────┘        │
 │       '-......-'                                             │
 └──────────────────────────────────────────────────────────────┘
   |<---- 360 ---->|<-- 40 -->|<-------- 240 -------->|        Tiefe beider Module ca. 63 mm
```

## Schichtaufbau

### Farbkreis (von der Wand nach vorn)

| Lage | Datei | Material | Anzahl | Funktion |
|------|-------|----------|-------:|----------|
| K1 | `K1_kreis_rueckwand_6mm.svg` | Pappel 6 mm | 1 | Rückwand, Innenseite weiß = Reflektor, Schlüssellöcher |
| K2 | `K2_kreis_ring_kerbe_6mm.svg` | Pappel 6 mm | 1 | Ringlage mit Kerbe für das Kabel (rechts, Richtung Display) |
| K3 | `K3_kreis_ring_6mm.svg` | Pappel 6 mm | 7 | Ringlagen |
| K4 | `K4_kreis_ring_oben_6mm.svg` | Pappel 6 mm | 1 | oberste Ringlage mit 6 Vorbohrungen |
| K5 | `K5_kreis_front_opal_3mm.svg` | Acryl opal 3 mm | 1 | Streuscheibe |

Ring: außen Ø 360, innen Ø 320 (20 mm Wand), 9 Lagen = 54 mm Lichtraum.
Die Front wird mit 6 Holzschrauben 3 x 16 (schwarz, Linsenkopf) befestigt.

### Displaykasten (von der Wand nach vorn)

| Lage | Datei | Material | Anzahl | Funktion |
|------|-------|----------|-------:|----------|
| D1 | `D1_display_rueckwand_6mm.svg` | Pappel 6 mm | 1 | Rückwand, Pi-Befestigung, Lüftung, Schlüssellöcher |
| D2 | `D2_display_rahmen_kabel_6mm.svg` | Pappel 6 mm | 1 | Rahmen mit Kerben: links Kabel zum Kreis, unten Netzteil |
| D3 | `D3_display_rahmen_6mm.svg` | Pappel 6 mm | 1 | Rahmen |
| D4 | `D4_display_rahmen_einschraub_6mm.svg` | Pappel 6 mm | 1 | Rahmen mit Bohrungen für Einschraubmuttern |
| D5 | `D5_display_rahmen_einschraub_luft_6mm.svg` | Pappel 6 mm | 1 | wie D4, plus Lüftungskerbe oben |
| D6 | `D6_display_led_traeger_4mm.svg` | Pappel 4 mm | 1 | LED-Träger, Segmentpositionen graviert (1a ... 2g) |
| D7 | `D7_display_kammern_6mm.svg` | Pappel 6 mm | 4 | Lichtkammern (24 mm), Mikrofonschacht |
| D8 | `D8_display_front_opal_2mm.svg` | Acryl opal 2 mm | 1 | Streuscheibe |
| D9 | `D9_display_front_rauchgrau_3mm.svg` | Acryl rauchgrau 3 mm | 1 | Front ("Dead Front"), Gravur dB(A) |

- D1-D5 werden zur "Wanne" verleimt, D6 + 4x D7 zum "Frontmodul".
- Frontmodul, D8 und D9 hängen mit 4x M3 x 40 an Einschraubmuttern in D4/D5.
  Zum Öffnen nur diese 4 Schrauben lösen; die Elektronik liegt dann frei.
- Die Einschraubmuttern (M3 für Holz) brauchen je nach Hersteller 4-5 mm Bohrung -
  vorher prüfen und ggf. `INSERT_D` im Generator anpassen.

## Den LED-Ring bauen

### Material

- 1 m WS2812B-Streifen, 60 LEDs/m, **IP30** (ohne Silikonmantel), 10 mm breit,
  selbstklebend (3M-Klebeband auf der Rückseite).
  60 LEDs x 16,7 mm = 1000 mm, der Innenumfang bei Ø 320 mm ist 1005 mm -
  der Streifen passt genau einmal herum, es bleiben ca. 5 mm Luft an der Kerbe.
- Litze 0,5 mm2 rot/schwarz, 0,14 mm2 für Daten, JST-SM-Stecker 3-polig.

### Schritte

1. **Ringlagen schneiden und verleimen.**
   Reihenfolge: K1 - K2 - 7x K3 - K4. Die beim Schneiden anfallenden Innenscheiben
   (Ø 320) eignen sich als Zentrierkern: Kern einlegen, Lagen darüberschieben,
   ausrichten, mit Holzleim verleimen und spannen. Kerbe in K2 zeigt nach rechts
   (zum Display), Vorbohrungen in K4 liegen oben.
2. **Innen schleifen und weiß lackieren.**
   Innenwand und Innenseite der Rückwand matt weiß (z. B. Acryllack seidenmatt).
   Das ist der Reflektor - weiß statt Holzton bringt deutlich mehr und neutraleres Licht.
3. **Streifen vorher testen.**
   Mit dem Pi oder einem Mikrocontroller alle 60 LEDs einmal rot, grün, blau
   durchschalten. Ein defekter Pixel unterbricht sonst alles danach.
4. **Anschlüsse löten.**
   Am Anfang (DIN-Seite, Pfeilrichtung beachten): 5V, GND, DIN.
   Am Ende zusätzlich 5V und GND (Einspeisung an beiden Enden, verhindert
   Spannungsabfall und Farbverschiebung). DOUT am Ende bleibt frei.
5. **Streifen einkleben.**
   Start direkt neben der Kerbe, LEDs zeigen zur Kreismitte, Streifen auf halber Tiefe
   der Ringwand (ca. 25-30 mm von der Rückwand). Im Uhrzeigersinn rundherum
   andrücken. Der Streifen wird nur über die flache Seite gebogen - das geht
   problemlos. Wo der Kleber nicht hält: einzelne Tropfen Heißkleber oder
   kleine Kabelbinder-Sockel.
6. **Kabel durch die Kerbe führen.**
   Anfang und Ende treffen sich an der Kerbe. Die 5 Adern (5V, GND, DIN vom Anfang,
   5V, GND vom Ende) zusammenfassen und durch die Kerbe nach außen, mit JST-Stecker.
7. **Lichttest vor dem Schließen.**
   Opalscheibe auflegen, Ring in Grün, Gelb und Rot leuchten lassen und
   prüfen, ob die Fläche gleichmäßig ist. Erst dann K5 verschrauben.

### Gleichmäßigkeit

Mit LEDs nur am Rand ist die Mitte etwas dunkler als der Rand (im Simulator so
dargestellt) - das sieht aus wie eine Ringleuchte und wirkt meist gut. Wenn die
Fläche ganz gleichmäßig sein soll:

- **Zweiter Ring innen:** 24-30 LEDs auf der Rückwand bei ca. Ø 180 mm, nach vorn
  gerichtet. Bei 54 mm Abstand zur Opalscheibe verschwimmen sie gut. Zusammen ca. 90 LEDs.
- **Opal mit höherer Streuung** (Lichtdurchlässigkeit ca. 30 %) - gleichmäßiger, aber dunkler.
- **Halo (optional):** ein zusätzlicher Streifen außen an der Rückseite der Ringwand,
  zur Wand gerichtet, erzeugt den farbigen Lichthof wie im Simulator.

### Verkabelung zum Display

```
Pi GPIO10 -> 74AHCT125 -> 330R -> Ziffern (LED 0-41) -> Kabelbrücke -> Ring (LED 42-101)
5V/GND vom Netzteil:  Ziffern-Einspeisung  +  beide Enden des Rings
```

Das Kabel läuft aus der Kerbe in K2 durch eine kleine Kabelbrücke (3D-Druck oder
Holzkanal 12 x 12 mm, 40 mm lang) in die Kerbe links in D2.
Bei getrennter Montage (zwei Einzelgehäuse) bis ca. 2 m Kabel möglich, dann
0,75 mm2 für 5V/GND.

## Alternative Bauweisen für den runden Korpus

Die Vorlagen in `laser/` nutzen gestapelte Ringe. Andere Wege zum runden Gehäuse:

| Bauweise | Vorteile | Nachteile |
|----------|----------|-----------|
| **Gestapelte Ringe** (Vorlagen K1-K5) | sehr stabil und maßhaltig, nur Lasern und Leimen, schöne Schichtkante | viel Verschnitt (9 Innenscheiben Ø 320, ca. 1,2 m2), lange Laserzeit, ca. 2 kg |
| **Kerf-Bending** (Schlitzmuster, "Living Hinge") | kaum Verschnitt, leicht, glatte Außenseite | Muster per Probeschnitt abstimmen, Schlitze lassen Licht durch (innen bekleben oder weiß streichen) |
| **3D-Druck in Segmenten** | LED-Halter, Kabelkanal und Schraubdome direkt integriert | 30-50 h Druckzeit bei Ø 360 x 54 mm |
| **Fertigteil umbauen** (Tortenring, runde Holzschachtel, LED-Panel-Leuchte) | schnellster Prototyp | Maße vom Fertigteil vorgegeben |

### Kerf-Bending im Detail

- Streifen 1131 x 54 mm (Umfang π x 360), Pappelsperrholz 3 mm mit versetztem
  Schlitzmuster. Biegebirke oder Flugzeugsperrholz 1,5 mm biegt sich bei diesem
  Radius auch ohne Schlitze.
- Formgeber: Rückwand Ø 354 mm (360 - 2 x 3 mm Streifendicke) und vorn ein schmaler
  Ring, um den der Streifen gelegt und verleimt wird.
- Stoß überlappend oder mit innenliegender Lasche verbinden.
- Der Streifen ist für die meisten Laser zu lang: in 2-3 Stücke teilen und mit
  Laschen verbinden.
- Noch nicht im Generator enthalten - braucht die Bettgröße des Lasers.

## Displaykasten bauen (Kurzfassung)

1. D1-D5 verleimen, Einschraubmuttern in D4/D5 eindrehen.
2. Pi Zero 2 W mit Abstandsbolzen M2.5 auf D1, Platine mit 74AHCT125 und Sicherung daneben.
3. Auf D6: 14 Streifenstücke a 3 LEDs auf die gravierten Felder kleben,
   Reihenfolge 1a-1b-...-1g-2a-...-2g. Verbindungen hinten durch die Bohrungen.
4. INMP441 auf Moosgummi im Mikrofonschacht, Schallöffnung zur Front.
5. D6 + 4x D7 verleimen (innen weiß lackiert), Kabel durch den Schlitz in D6 zur Elektronik.
6. Front D8 + D9 auflegen, alles mit 4x M3 x 40 verschrauben.

## Laserhinweise

- Farben: rot = schneiden, blau = ritzen/gravieren (Linie), schwarz = flächig gravieren.
- Maße ohne Kerf-Kompensation. Für Passungen (Zentrierkern, Bohrungen) ggf.
  Probeschnitt machen.
- Die Gravur "dB(A)" auf D9 ist Text in Baloo: vor dem Lasern in Pfade umwandeln
  (Inkscape: Pfad > Objekt in Pfad) oder Schrift installieren. Auf Rauchglas
  von hinten gravieren, dann bleibt die Front glatt.
- Bettgröße: Kreisteile brauchen 364 x 364 mm, G1 braucht 644 x 364 mm.
