#!/usr/bin/env python3
"""Lasercut-SVGs fuer die Laermampel-Variante "Farbkreis + Display".

Farbkonvention: rot = schneiden, blau = Linie gravieren/ritzen,
schwarz gefuellt = flaechig gravieren. Alle Masse in mm, ohne Kerf-Kompensation.

Aufruf: uv run --no-project python laser/generate_laser.py
"""

from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "svg"

CUT = 'fill="none" stroke="#ff0000" stroke-width="0.1"'
SCORE = 'fill="none" stroke="#0000ff" stroke-width="0.1"'
ENGRAVE = 'fill="#000000" stroke="none"'

PLY = 6.0  # Pappelsperrholz

# --- Farbkreis --------------------------------------------------------------
KREIS_D = 360.0
# 60 LEDs bei 60 LEDs/m = 1 m Streifen; Innenumfang bei 320 mm = 1005 mm
RING_INNER_D = 320.0
RING_LAYERS = 9  # 9 x 6 mm = 54 mm Abstand LED -> Streuscheibe
NOTCH_W = 14.0  # Kabeldurchfuehrung zum Displaykasten
KREIS_SCREW_R = (KREIS_D + RING_INNER_D) / 4  # Mitte der Ringwand
KREIS_SCREW_ANGLES = [30 + 60 * k for k in range(6)]  # 0 Grad bleibt fuer die Kerbe frei

INSERT_D = 4.5  # Einschraubmutter M3 fuer Holz, Herstellerangabe pruefen
M3_CLEAR = 3.4
PILOT_D = 2.0

# --- Displaykasten ----------------------------------------------------------
BOX_W, BOX_H, BOX_R = 240.0, 200.0, 12.0
WALL = 16.0
CORNER = 10.0  # Lage der M3-Verschraubung ab Aussenkante
SEG_T, SEG_L, DIGIT_GAP = 16.0, 50.0, 20.0  # 3 LEDs x 16,7 mm pro Segment
SEG_INSET = 1.5  # ergibt 3 mm Stege zwischen den Kammern
DIGIT_W = 2 * SEG_T + SEG_L
DIGIT_H = 3 * SEG_T + 2 * SEG_L
DIGIT_Y = 20.0
DIGIT_X = [
    (BOX_W - 2 * DIGIT_W - DIGIT_GAP) / 2,
    (BOX_W - 2 * DIGIT_W - DIGIT_GAP) / 2 + DIGIT_W + DIGIT_GAP,
]
MIC = (196.0, 184.0)
MIC_BOX = 16.0
PI_CENTER = (120.0, 100.0)
PI_HOLES = (58.0, 23.0)  # Lochabstand Pi Zero 2 W, M2.5

# --- Gemeinsame Rueckwand ---------------------------------------------------
GAP = 40.0
BOX_OFF = (KREIS_D + GAP, (KREIS_D - BOX_H) / 2)


def fmt(v: float) -> str:
    return f"{v:.3f}".rstrip("0").rstrip(".")


def circle(cx: float, cy: float, r: float, style: str = CUT) -> str:
    return f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" {style}/>'


def rect(x: float, y: float, w: float, h: float, rx: float = 0, style: str = CUT) -> str:
    return (
        f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" '
        f'rx="{fmt(rx)}" {style}/>'
    )


def path(d: str, style: str = CUT) -> str:
    return f'<path d="{d}" {style}/>'


def text(x: float, y: float, s: str, size: float, style: str = ENGRAVE) -> str:
    return (
        f'<text x="{fmt(x)}" y="{fmt(y)}" font-family="Baloo, Arial, sans-serif" '
        f'font-size="{fmt(size)}" text-anchor="middle" {style}>{s}</text>'
    )


def keyhole(x: float, y: float) -> str:
    # Kopf Durchmesser 10 mm, Schlitz 5 mm nach oben - Schraube rutscht in den Schlitz
    dy = math.sqrt(5**2 - 2.5**2)
    return path(
        f"M {fmt(x - 2.5)} {fmt(y - 12)} L {fmt(x + 2.5)} {fmt(y - 12)} "
        f"L {fmt(x + 2.5)} {fmt(y - dy)} A 5 5 0 1 1 {fmt(x - 2.5)} {fmt(y - dy)} Z"
    )


def write(name: str, w: float, h: float, elems: list[str], margin: float = 2.0) -> None:
    W, H = w + 2 * margin, h + 2 * margin
    body = "\n  ".join(elems)
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(W)}mm" height="{fmt(H)}mm" '
        f'viewBox="0 0 {fmt(W)} {fmt(H)}">\n'
        f'<g transform="translate({fmt(margin)} {fmt(margin)})">\n  {body}\n</g>\n</svg>\n'
    )
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


# --- Farbkreis --------------------------------------------------------------

def kreis_screw_points() -> list[tuple[float, float]]:
    c = KREIS_D / 2
    return [
        (c + KREIS_SCREW_R * math.cos(math.radians(a)), c + KREIS_SCREW_R * math.sin(math.radians(a)))
        for a in KREIS_SCREW_ANGLES
    ]


def kreis_parts() -> None:
    c, R, r = KREIS_D / 2, KREIS_D / 2, RING_INNER_D / 2

    write("K1_kreis_rueckwand_6mm", KREIS_D, KREIS_D,
          [circle(c, c, R), keyhole(c - 110, 70), keyhole(c + 110, 70)])

    ring = [circle(c, c, R), circle(c, c, r)]
    # Kerbe als Rechteck ueber die Wand hinaus: Aussen- und Innenkontur plus
    # Rechteck schneiden das Stueck frei
    notch = rect(c + r - 10, c - NOTCH_W / 2, (R - r) + 20, NOTCH_W)
    write("K2_kreis_ring_kerbe_6mm", KREIS_D, KREIS_D, ring + [notch])
    write("K3_kreis_ring_6mm", KREIS_D, KREIS_D, ring)
    # Vorbohrung fuer Holzschrauben 3 x 16: eine Einschraubmutter waere laenger als eine Lage
    write("K4_kreis_ring_oben_6mm", KREIS_D, KREIS_D,
          ring + [circle(x, y, PILOT_D / 2) for x, y in kreis_screw_points()])
    write("K5_kreis_front_opal_3mm", KREIS_D, KREIS_D,
          [circle(c, c, R)] + [circle(x, y, M3_CLEAR / 2) for x, y in kreis_screw_points()])


# --- Displaykasten ----------------------------------------------------------

def box_outline() -> str:
    return rect(0, 0, BOX_W, BOX_H, BOX_R)


def box_corners() -> list[tuple[float, float]]:
    return [(CORNER, CORNER), (BOX_W - CORNER, CORNER),
            (CORNER, BOX_H - CORNER), (BOX_W - CORNER, BOX_H - CORNER)]


def seg_rects(x0: float, y0: float) -> dict[str, tuple[float, float, float, float, str]]:
    T, L = SEG_T, SEG_L
    return {
        "a": (x0 + T, y0, L, T, "h"),
        "b": (x0 + T + L, y0 + T, T, L, "v"),
        "c": (x0 + T + L, y0 + 2 * T + L, T, L, "v"),
        "d": (x0 + T, y0 + 2 * T + 2 * L, L, T, "h"),
        "e": (x0, y0 + 2 * T + L, T, L, "v"),
        "f": (x0, y0 + T, T, L, "v"),
        "g": (x0 + T, y0 + T + L, L, T, "h"),
    }


def all_segments():
    for di, x0 in enumerate(DIGIT_X):
        for name, r in seg_rects(x0, DIGIT_Y).items():
            yield di, name, r


def mic_grille() -> list[str]:
    mx, my = MIC
    pts = [(0.0, 0.0)] + [(4 * math.cos(math.radians(a)), 4 * math.sin(math.radians(a)))
                          for a in range(0, 360, 60)]
    return [circle(mx + dx, my + dy, 1.0) for dx, dy in pts]


def frame(insert: bool = False, notches: tuple[str, ...] = ()) -> list[str]:
    elems = [box_outline(), rect(WALL, WALL, BOX_W - 2 * WALL, BOX_H - 2 * WALL, 4)]
    if insert:
        elems += [circle(x, y, INSERT_D / 2) for x, y in box_corners()]
    if "links" in notches:  # Kabel zum Farbkreis
        elems.append(rect(-10, BOX_H / 2 - NOTCH_W / 2, WALL + 20, NOTCH_W))
    if "unten" in notches:  # Netzteilkabel
        elems.append(rect(170, BOX_H - WALL - 10, 10, WALL + 20))
    if "oben" in notches:  # Lueftung
        elems.append(rect(100, -10, 40, WALL + 20))
    return elems


def box_parts() -> None:
    px, py = PI_CENTER
    hx, hy = PI_HOLES[0] / 2, PI_HOLES[1] / 2
    back = [box_outline(), keyhole(40, 40), keyhole(BOX_W - 40, 40)]
    back += [circle(px + sx * hx, py + sy * hy, 1.35) for sx in (-1, 1) for sy in (-1, 1)]
    back += [rect(100, 150 + 8 * k, 40, 3, 1.5) for k in range(3)]
    write("D1_display_rueckwand_6mm", BOX_W, BOX_H, back)

    write("D2_display_rahmen_kabel_6mm", BOX_W, BOX_H, frame(notches=("links", "unten")))
    write("D3_display_rahmen_6mm", BOX_W, BOX_H, frame())
    write("D4_display_rahmen_einschraub_6mm", BOX_W, BOX_H, frame(insert=True))
    write("D5_display_rahmen_einschraub_luft_6mm", BOX_W, BOX_H,
          frame(insert=True, notches=("oben",)))

    # LED-Traeger: Bohrungen fuer Kabelbruecken zwischen den Segmenten, LED-Positionen graviert
    carrier = [box_outline()] + [circle(x, y, M3_CLEAR / 2) for x, y in box_corners()]
    order = 0
    for di, name, (x, y, w, h, d) in all_segments():
        order += 1
        if d == "h":
            ends = [(x + 4, y + h / 2), (x + w - 4, y + h / 2)]
            leds = [(x + w * f, y + h / 2) for f in (1 / 6, 3 / 6, 5 / 6)]
        else:
            ends = [(x + w / 2, y + 4), (x + w / 2, y + h - 4)]
            leds = [(x + w / 2, y + h * f) for f in (1 / 6, 3 / 6, 5 / 6)]
        carrier += [circle(ex, ey, 1.75) for ex, ey in ends]
        carrier += [rect(x + SEG_INSET, y + SEG_INSET, w - 2 * SEG_INSET, h - 2 * SEG_INSET, 2, SCORE)]
        carrier += [circle(lx, ly, 2.5, SCORE) for lx, ly in leds]
        label = f"{di + 1}{name}"
        # Beschriftung zwischen zwei LED-Positionen, damit sie nicht unter dem Streifen liegt
        ty = y + h / 2 + 6 if d == "h" else y + h / 3 + 1.4
        carrier.append(text(x + w / 2, ty, label, 4))
    carrier.append(rect(110, 170, 20, 8, 2))  # Kabelschlitz zur Elektronik
    carrier.append(circle(MIC[0], MIC[1], 3))  # Mikrofonkabel
    write("D6_display_led_traeger_4mm", BOX_W, BOX_H, carrier)

    chamber = [box_outline()] + [circle(x, y, M3_CLEAR / 2) for x, y in box_corners()]
    for _, _, (x, y, w, h, _) in all_segments():
        chamber.append(rect(x + SEG_INSET, y + SEG_INSET, w - 2 * SEG_INSET, h - 2 * SEG_INSET, 2))
    chamber.append(rect(MIC[0] - MIC_BOX / 2, MIC[1] - MIC_BOX / 2, MIC_BOX, MIC_BOX, 2))
    write("D7_display_kammern_6mm", BOX_W, BOX_H, chamber)

    front = [box_outline()] + [circle(x, y, M3_CLEAR / 2) for x, y in box_corners()] + mic_grille()
    write("D8_display_front_opal_2mm", BOX_W, BOX_H, front)
    write("D9_display_front_rauchgrau_3mm", BOX_W, BOX_H,
          front + [text(BOX_W / 2 - 10, DIGIT_Y + DIGIT_H + 14, "dB(A)", 10)])


# --- Gemeinsame Rueckwand (optional, ersetzt K1 und D1) ---------------------

def shared_back() -> None:
    c, R = KREIS_D / 2, KREIS_D / 2
    bx, by = BOX_OFF
    y1, y2 = by, by + BOX_H
    xi = c + math.sqrt(R**2 - (c - y1) ** 2)
    xr, rr = bx + BOX_W, BOX_R
    outline = path(
        f"M {fmt(xi)} {fmt(y1)} L {fmt(xr - rr)} {fmt(y1)} "
        f"A {fmt(rr)} {fmt(rr)} 0 0 1 {fmt(xr)} {fmt(y1 + rr)} "
        f"L {fmt(xr)} {fmt(y2 - rr)} A {fmt(rr)} {fmt(rr)} 0 0 1 {fmt(xr - rr)} {fmt(y2)} "
        f"L {fmt(xi)} {fmt(y2)} A {fmt(R)} {fmt(R)} 0 1 1 {fmt(xi)} {fmt(y1)} Z"
    )
    elems = [outline, keyhole(c - 110, 70), keyhole(c + 110, 70), keyhole(bx + BOX_W / 2, by + 40)]
    # Senkbohrungen fuer Holzschrauben von hinten in Ringwand und Kastenrahmen
    for a in (45, 135, 225, 315):
        elems.append(circle(c + KREIS_SCREW_R * math.cos(math.radians(a)),
                            c + KREIS_SCREW_R * math.sin(math.radians(a)), 1.75))
    for x, y in [(8, 50), (8, 150), (BOX_W - 8, 50), (BOX_W - 8, 150)]:
        elems.append(circle(bx + x, by + y, 1.75))
    # Pi-Befestigung und Lueftung wie D1
    px, py = PI_CENTER
    hx, hy = PI_HOLES[0] / 2, PI_HOLES[1] / 2
    elems += [circle(bx + px + sx * hx, by + py + sy * hy, 1.35) for sx in (-1, 1) for sy in (-1, 1)]
    elems += [rect(bx + 100, by + 150 + 8 * k, 40, 3, 1.5) for k in range(3)]
    # Umriss der Module als Montagehilfe
    elems += [circle(c, c, R - 0.5, SCORE), rect(bx + 0.5, by + 0.5, BOX_W - 1, BOX_H - 1, BOX_R, SCORE)]
    write("G1_gemeinsame_rueckwand_6mm", bx + BOX_W, KREIS_D, elems)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    kreis_parts()
    box_parts()
    shared_back()
    for f in sorted(OUT.glob("*.svg")):
        print(f.relative_to(OUT.parent))


if __name__ == "__main__":
    main()
