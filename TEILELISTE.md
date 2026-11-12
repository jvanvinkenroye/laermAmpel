# Laermampel - Teileliste

Raspberry Pi Zero 2 W als Komplettgeraet (Messung, Anzeige, Logging, Weboberflaeche),
runde Wandscheibe mit LED-Bogen und grosser dB-Anzeige (siehe `VISUALISIERUNG.md`).

Preise sind grobe Richtwerte (Stand 2026), je nach Haendler.

## Elektronik

| Pos | Anzahl | Teil | Spezifikation / Hinweis | ca. Preis |
|----:|-------:|------|-------------------------|----------:|
| 1 | 1 | Raspberry Pi Zero 2 W | mit vorgeloeteter Stiftleiste (Zero 2 WH) spart Arbeit | 20 EUR |
| 2 | 1 | microSD-Karte 32 GB | "High Endurance" / A1 | 10 EUR |
| 3 | 1 | INMP441 I2S-MEMS-Mikrofonmodul | 24 bit, -26 dBFS @ 94 dB SPL, 3,3 V | 4 EUR |
| 4 | 2 m | WS2812B-LED-Streifen 60 LEDs/m | 5 V, 10 mm breit, IP30 (ohne Silikon, laesst sich gut biegen); benoetigt: 45 LEDs Bogen + 42 LEDs Ziffern = 87 LEDs | 10-15 EUR |
| 5 | 1 | 74AHCT125 (DIP-14) | Pegelwandler 3,3 V -> 5 V fuer LED-Datenleitung | 1 EUR |
| 6 | 1 | IC-Fassung DIP-14 | optional | 0,20 EUR |
| 7 | 1 | Widerstand 330 Ohm | in Serie zur Datenleitung DIN | 0,10 EUR |
| 8 | 1 | Elko 1000 uF / 16 V | an der LED-Einspeisung | 0,50 EUR |
| 9 | 1 | Keramikkondensator 100 nF | Abblockung am 74AHCT125 | 0,10 EUR |
| 10 | 1 | Netzteil 5 V / 4 A | Hohlstecker 5,5/2,1 mm, geschlossenes Steckernetzteil | 12 EUR |
| 11 | 1 | Hohlsteckerbuchse 5,5/2,1 mm, Einbau | | 1 EUR |
| 12 | 1 | Feinsicherung 4 A traege + Halter | oder Polyfuse 4 A | 2 EUR |
| 13 | 1 | Lochrasterplatine ca. 50x70 mm | oder Pi-Zero-Proto-HAT | 2 EUR |
| 14 | 1 | Buchsenleiste 2x20 | wenn Platine als HAT aufgesteckt wird | 1 EUR |
| 15 | - | Litze 0,14 mm2 (Signale), 0,5 mm2 (5 V/GND LED) | fuer Bruecken zwischen Streifenstuecken: 3-adrig, ca. 2 m | 5 EUR |
| 16 | 1 | JST-SM-3-Pin-Steckerpaar | Trennstelle zwischen Rueckwand und Front | 1 EUR |

### Optional

| Pos | Anzahl | Teil | Zweck | ca. Preis |
|----:|-------:|------|-------|----------:|
| 17 | 1 | DS3231 RTC-Modul (I2C) | korrekte Zeitstempel auch ohne Netz nach Stromausfall | 3 EUR |
| 18 | 1 | Taster 12 mm, Einbau | Helligkeit / Stummschaltung / WLAN-Setup | 1 EUR |
| 19 | 1 | Referenz-Schallpegelmesser (Klasse 2) | einmalig zur Kalibrierung, ggf. ausleihen | 30-150 EUR |
| 20 | 1 | Adafruit 1,2" 4-Digit 7-Segment mit HT16K33-Backpack (I2C) | Alternative zu den WS2812-Ziffern: einfacher, aber nur 30 mm Ziffernhoehe und einfarbig | 15 EUR |

## Gehaeuse und Montage

| Pos | Anzahl | Teil | Hinweis | ca. Preis |
|----:|-------:|------|---------|----------:|
| 21 | 1 | Opales Acryl 3 mm (Opal 30-50 %), rund ca. 380 mm | Frontscheibe, mit Skalengravur | 15 EUR |
| 22 | 1 | Rueckwand Pappelsperrholz 6 mm, rund ca. 380 mm | Lasercut | 5 EUR |
| 23 | 3-4 | Lagen Pappelsperrholz/MDF 6 mm | Lichtkammern fuer Bogen und Segmente, innen weiss lackiert, ca. 20-25 mm Gesamthoehe; alternativ 3D-Druck in weissem PLA | 10 EUR |
| 24 | 1 | Schwarze Folie oder Lack | Abdeckung der nicht leuchtenden Flaechen fuer mehr Kontrast | 3 EUR |
| 25 | 1 | Schaumstoff / Moosgummi | Entkopplung des Mikrofons vom Gehaeuse | 1 EUR |
| 26 | 1 | Akustikstoff oder Lochgitter | vor der Mikrofonoeffnung (Staubschutz) | 1 EUR |
| 27 | 2 | Schluessellochbeschlaege | Wandaufhaengung | 2 EUR |
| 28 | 4 | Abstandsbolzen M2,5 x 10 mm + Schrauben | Pi-Befestigung | 2 EUR |
| 29 | 8 | Holzschrauben 3 x 30 mm oder Gewindestangen M3 | Schichten verschrauben | 2 EUR |

## Summe

Ca. 100-120 EUR ohne Referenz-Messgeraet.

## Werkzeug

Loetkolben, Multimeter, Abisolierzange, Lasercutter oder 3D-Drucker.

---

# Variante B - Farbkreis + Display

Elektronik wie oben (Pos 1-3, 5-16), aber mit diesen Aenderungen.
Aufbau und Lasercut-Teile: `GEHAEUSE_FARBKREIS.md`, `laser/svg/`.

## Abweichungen Elektronik

| Pos | Anzahl | Teil | Hinweis | ca. Preis |
|----:|-------:|------|---------|----------:|
| B4 | 2 m | WS2812B-Streifen 60 LEDs/m, IP30, 10 mm | 1 m Ring (60 LEDs) + 0,7 m Ziffern (42 LEDs) | 10-15 EUR |
| B4a | 0,5 m | WS2812B-Streifen 60 LEDs/m | optional: zweiter Ring innen (ca. 30 LEDs) | 4 EUR |
| B4b | 1 m | WS2812B-Streifen 60 LEDs/m | optional: Halo an der Wand | 6 EUR |
| B10 | 1 | Netzteil 5 V / 4 A | reicht fuer 102 LEDs bei begrenzter Helligkeit; mit B4a + B4b: 5 V / 6 A | 12 EUR |
| B16 | 2 | JST-SM-Steckerpaar 3-polig + 2-polig | Trennstelle Ring / Display | 2 EUR |

## Gehaeuse

| Pos | Anzahl | Teil | Hinweis | ca. Preis |
|----:|-------:|------|---------|----------:|
| B20 | ca. 1,6 m2 | Pappelsperrholz 6 mm | K1-K4: 10 Platten 364 x 364; D1-D5, D7: 9 Platten 244 x 204 | 45 EUR |
| B21 | 1 | Pappelsperrholz 4 mm, 240 x 200 | D6 LED-Traeger | 2 EUR |
| B22 | 1 | Acryl opal 3 mm, 400 x 400 | K5 Kreisfront | 15 EUR |
| B23 | 1 | Acryl opal 2 mm, 250 x 210 | D8 | 5 EUR |
| B24 | 1 | Acryl rauchgrau 3 mm, 250 x 210 | D9 Front Display | 6 EUR |
| B25 | 1 | Pappelsperrholz 6 mm, 644 x 364 | optional G1 gemeinsame Rueckwand | 8 EUR |
| B26 | 6 | Holzschraube 3 x 16, Linsenkopf schwarz | Kreisfront | 1 EUR |
| B27 | 4 | Einschraubmutter M3 fuer Holz | Displaykasten | 2 EUR |
| B28 | 4 | Linsenkopfschraube M3 x 40, schwarz | Displayfront | 1 EUR |
| B29 | 4 | Abstandsbolzen M2.5 x 10 + Schrauben | Pi | 2 EUR |
| B30 | - | Holzleim, Acryllack weiss seidenmatt | Lichtraeume innen weiss | 8 EUR |
| B31 | 1 | Kabelbruecke 40 x 12 x 12 mm | 3D-Druck oder Holzleiste | - |

Summe Variante B: ca. 150-180 EUR ohne Referenz-Messgeraet.
