# Laermampel - Schaltung

Raspberry Pi Zero 2 W + INMP441 (I2S) + WS2812B-Kette (SPI) + 5-V-Netzteil.
WS2812B-Kette: 45 LEDs Bogen + 2 x 21 LEDs 7-Segment-Ziffern = 87 LEDs
(Aufbau siehe `VISUALISIERUNG.md`).
Teilenummern (Pos) beziehen sich auf `TEILELISTE.md`.

## Uebersicht

```
                 +-----------+   Sicherung 4A
 Netzteil 5V/4A -| Buchse    |----[ F1 ]----+-----------------------+------------------+
                 +-----------+              |                       |                  |
                      | GND                 |  5V                 + C1 1000uF          |
                      |                     |                       |                  |
                      |              +------+------+                |                  |
                      |              | Pi Zero 2 W |                |                  |
                      |              |  Pin 2 (5V) |                |                  |
   INMP441            |              |             |           +----+-----+   +--------+-------+
   +--------+         |              |  GPIO10 ----+--> U1 -330R--> DIN   |   | 5V (Einspeisung |
   | VDD ---+---------+--------------+- 3V3 Pin 1  |  74AHCT125| Bogen    |-->| 2) Ziffer 10er  |-->
   | GND ---+---------+--------------+- GND Pin 6  |           | LED 0-44 |   | LED 45-65       |
   | SCK ---+------------------------+- GPIO18 Pin12           +----------+   +-----------------+
   | WS  ---+------------------------+- GPIO19 Pin35
   | SD  ---+------------------------+- GPIO20 Pin38           --> Ziffer 1er LED 66-86
   | L/R ---+-- GND                  +-------------+
   +--------+                                     (GND aller Teile sternfoermig am Netzteil-Minus)
```

## Pinbelegung Raspberry Pi Zero 2 W (40-pol. Stiftleiste)

| Pin | Signal | geht an |
|----:|--------|---------|
| 1 | 3V3 | INMP441 VDD |
| 2 | 5V | Versorgung aus Netzteil (hinter Sicherung) |
| 6 | GND | gemeinsame Masse |
| 12 | GPIO18 / PCM_CLK | INMP441 SCK |
| 35 | GPIO19 / PCM_FS | INMP441 WS |
| 38 | GPIO20 / PCM_DIN | INMP441 SD |
| 19 | GPIO10 / SPI0_MOSI | 74AHCT125 Pin 2 (1A) |
| 3 | GPIO2 / SDA | optional DS3231 SDA |
| 5 | GPIO3 / SCL | optional DS3231 SCL |
| 11 | GPIO17 | optional Taster gegen GND (interner Pull-up) |

Alternative Zifferanzeige HT16K33 (Pos 20) haengt ebenfalls an I2C (GPIO2/3),
Adresse 0x70 - kollidiert nicht mit der DS3231 (0x68).

GPIO18 ist durch I2S belegt. Die LEDs deshalb ueber SPI (GPIO10) treiben,
nicht ueber PWM an GPIO18.

## INMP441

| INMP441 | Pi |
|---------|----|
| VDD | 3V3 (Pin 1) - niemals 5 V |
| GND | GND |
| SCK | GPIO18 |
| WS | GPIO19 |
| SD | GPIO20 |
| L/R | GND (= linker Kanal) |

- Leitungen kurz halten (< 15-20 cm), I2S ist empfindlich auf lange Kabel.
- Mikrofon mit der Schalloeffnung zur Gehaeusefront, auf Moosgummi gelagert,
  nicht direkt auf dem Netzteil oder der LED-Matrix (Waerme, Koerperschall).
- Die Schalloeffnung des Moduls liegt je nach Board auf der Unterseite.

## Pegelwandler 74AHCT125 (U1)

```
                +----U----+
        GND --1-| 1OE  VCC|-14-- 5V  (100 nF nach GND direkt am Pin)
     GPIO10 --2-| 1A   4OE|-13-- 5V
330R -> DIN <-3-| 1Y   4A |-12-- GND
         5V --4-| 2OE  4Y |-11-- offen
        GND --5-| 2A   3OE|-10-- 5V
      offen --6-| 2Y   3A |-9--- GND
        GND --7-| GND  3Y |-8--- offen
                +---------+
```

- Pin 1 (1OE) auf GND = Kanal 1 aktiv.
- Pin 3 (1Y) ueber 330 Ohm an DIN der Matrix.
- Unbenutzte OE-Eingaenge (4, 10, 13) auf 5 V, unbenutzte A-Eingaenge (5, 9, 12) auf GND.
- Der 74AHCT125 hat TTL-Eingangsschwellen, 3,3 V vom Pi werden sicher als High erkannt.

## LED-Kette (Bogen + Ziffern)

- Eine einzige Datenleitung: DOUT des Bogens (LED 44) -> DIN der Zehnerziffer,
  deren DOUT -> DIN der Einerziffer. Datenrichtung beachten (Pfeil auf dem Streifen).
- Die Ziffernsegmente sind je 3 LEDs lange Streifenstuecke (50 mm), mit kurzen
  3-adrigen Litzen (5V, DIN/DOUT, GND) in Segmentreihenfolge a-b-c-d-e-f-g verbunden.
- 5 V und GND mit 0,5 mm2 direkt vom Netzteil, nicht ueber den Pi.
  Zweite Einspeisung am Anfang der Ziffern (LED 45), damit die vielen
  Loetbruecken keinen Spannungsabfall verursachen.
- C1 1000 uF direkt an der ersten Einspeisung (Polung beachten).

## Strombudget

| Verbraucher | Strom |
|-------------|------:|
| Pi Zero 2 W unter Last | ca. 0,5 A |
| 87 LEDs, eine Grundfarbe (rot/gruen), 100 % | ca. 1,7 A |
| 87 LEDs, gelb (rot + gruen), 100 % | ca. 3,5 A |
| 87 LEDs, weiss, 100 % | ca. 5,2 A (nie zulassen) |

In der Praxis leuchten nie alle LEDs voll (Bogen nur bis zum Pegel, Ziffer
"88" = 42 LEDs). Helligkeit in der Software auf ca. 70 % begrenzen, dann bleibt
das Gesamtsystem sicher unter 3 A. Die Sicherung schuetzt bei Fehlern.

## Hinweise

- Einspeisung ueber Pin 2 umgeht die Polyfuse des Pi - daher die externe Sicherung F1.
- Keine Spannung gleichzeitig ueber den Micro-USB-Port des Pi einspeisen.
- Alle Massen verbinden (Netzteil, Pi, 74AHCT125, Matrix, Mikrofon).

## Konfiguration (/boot/firmware/config.txt)

```
dtparam=spi=on
dtparam=i2s=on
# INMP441 als I2S-Mikrofon; verbreitet ist das Overlay der Google VoiceHAT,
# Alternative: adau7002-simple. Vor dem Einsatz mit arecord -l pruefen.
dtoverlay=googlevoicehat-soundcard
# optional RTC
# dtoverlay=i2c-rtc,ds3231
```

Funktionstest Mikrofon:

```
arecord -l
arecord -D plughw:0 -c1 -r 48000 -f S32_LE -t wav -d 5 test.wav
```

## Mikrofon und Messgenauigkeit (INMP441, Datenblatt)

| Kenngroesse | Wert |
|-------------|------|
| Empfindlichkeit | -26 dBFS @ 94 dB SPL, Toleranz +-1 dB |
| Eigenrauschen (EIN) | ca. 33 dB(A) SPL |
| Signal-Rausch-Abstand | 61 dB(A) |
| Max. Schalldruck (AOP) | 120 dB SPL |
| Frequenzgang | ca. 60 Hz - 15 kHz |

Praktisch nutzbarer Bereich: ca. 40-115 dB(A). Ein Klassenraum liegt bei
35-90 dB(A) und wird damit voll abgedeckt. Siehe Antwort im Chat / README
fuer die Einordnung der Genauigkeit.

---

## Variante B - Farbkreis + Display

Pi, Mikrofon und Pegelwandler wie oben. Geaenderte LED-Kette (102 LEDs):

```
GPIO10 -> 74AHCT125 -> 330R -> Ziffer 1 (LED 0-20) -> Ziffer 2 (LED 21-41)
       -> JST -> Kabelbruecke -> Ring Anfang (LED 42) ... Ring Ende (LED 101)

5V/GND:  Netzteil -> F1 4A -> Ziffern-Einspeisung
                           -> JST -> Ring Anfang (5V, GND)
                           -> JST -> Ring Ende   (5V, GND)
```

- C1 1000 uF an der Ziffern-Einspeisung, ein zweiter 470-1000 uF am Ring-Anfang.
- Ring an beiden Enden einspeisen, damit die Farbe rundherum gleich bleibt.
- Strom: 102 LEDs in Gruen oder Rot bei 70 % ca. 1,4 A, in Gelb ca. 2,3 A
  (+0,5 A Pi). Mit Zusatzring innen und Halo: Netzteil 5 V / 6 A, Sicherung 6 A.
- Details zum Aufbau: `GEHAEUSE_FARBKREIS.md`.
