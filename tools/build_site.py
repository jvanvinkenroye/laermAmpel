#!/usr/bin/env python3
"""Baut die GitHub-Pages-Seite nach docs/.

Quelle sind die Markdown-Dokumente im Projektordner, der Simulator, die Renderbilder
und die Lasercut-Vorlagen. Keine externen Abhaengigkeiten, damit der Build ueberall
laeuft.

Aufruf: uv run --no-project python tools/build_site.py
"""

from __future__ import annotations

import html
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

PAGES = [
    ("teileliste.html", "Teileliste", "TEILELISTE.md"),
    ("schaltung.html", "Schaltung", "SCHALTUNG.md"),
    ("gehaeuse.html", "Gehäuse & Bau", "GEHAEUSE_FARBKREIS.md"),
    ("tacho.html", "Tacho-Variante", "VISUALISIERUNG.md"),
]
NAV = [("index.html", "Start"), ("simulator/index.html", "Simulator")] + [
    (f, t) for f, t, _ in PAGES
]
RENDERS = [
    ("laermampel_gruen.png", "Grün", "unter 60 dB(A)"),
    ("laermampel_gelb.png", "Gelb", "60 bis 70 dB(A)"),
    ("laermampel_rot.png", "Rot", "über 70 dB(A)"),
]
LASER_PREVIEW = [
    ("K2_kreis_ring_kerbe_6mm.svg", "Ringlage mit Kabelkerbe"),
    ("D6_display_led_traeger_4mm.svg", "LED-Träger mit Segmentfeldern"),
    ("D7_display_kammern_6mm.svg", "Lichtkammern"),
    ("G1_gemeinsame_rueckwand_6mm.svg", "Gemeinsame Rückwand"),
]


# --- Markdown (nur der Umfang, den die Projektdokumente nutzen) ---------------

def slug(text: str) -> str:
    s = text.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def inline(text: str) -> str:
    codes: list[str] = []

    def keep_code(m: re.Match[str]) -> str:
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def table(rows: list[str]) -> str:
    def cells(line: str) -> list[str]:
        return [c.strip() for c in line.strip().strip("|").split("|")]

    head, sep, body = cells(rows[0]), cells(rows[1]), [cells(r) for r in rows[2:]]
    align = ["right" if s.endswith(":") else "left" for s in sep]
    out = ['<div class="table-wrap"><table><thead><tr>']
    out += [f'<th style="text-align:{a}">{inline(c)}</th>' for c, a in zip(head, align)]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>")
        out += [f'<td style="text-align:{a}">{inline(c)}</td>' for c, a in zip(r, align)]
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def markdown(md: str) -> tuple[str, str, list[tuple[str, str]]]:
    """Liefert (Titel, HTML, Liste der h2-Ueberschriften)."""
    lines = md.splitlines()
    out: list[str] = []
    toc: list[tuple[str, str]] = []
    title = ""
    para: list[str] = []
    items: list[str] = []
    list_tag = ""
    i = 0

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    def flush_list() -> None:
        nonlocal list_tag
        if items:
            out.append(f"<{list_tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items)
                       + f"</{list_tag}>")
            items.clear()
        list_tag = ""

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_para(); flush_list()
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(block))}</code></pre>")
        elif m := re.match(r"^(#{1,4})\s+(.*)", line):
            flush_para(); flush_list()
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1 and not title:
                title = text
            else:
                anchor = slug(text)
                if level == 2:
                    toc.append((anchor, text))
                out.append(f'<h{level} id="{anchor}">{inline(text)}</h{level}>')
        elif stripped == "---":
            flush_para(); flush_list()
            out.append("<hr>")
        elif stripped.startswith("|") and i + 1 < len(lines) and re.match(
                r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            flush_para(); flush_list()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(table(rows))
            continue
        elif m := re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", line):
            flush_para()
            tag = "ol" if m.group(2)[0].isdigit() else "ul"
            if list_tag and list_tag != tag:
                flush_list()
            list_tag = tag
            items.append(m.group(3))
        elif not stripped:
            flush_para(); flush_list()
        elif items and line.startswith(" "):
            items[-1] += " " + stripped  # Fortsetzungszeile eines Listenpunkts
        else:
            flush_list()
            para.append(stripped)
        i += 1
    flush_para(); flush_list()
    return title, "\n".join(out), toc


# --- Seitenrahmen -------------------------------------------------------------

def page(title: str, body: str, active: str, description: str = "") -> str:
    on = ' class="on"'
    nav = "".join(
        f'<a href="{href}"{on if href == active else ""}>{label}</a>' for href, label in NAV
    )
    desc = html.escape(description or "Lärmampel - ein Makerspace-Projekt", quote=True)
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/site.css">
<link rel="icon" href="assets/logos/spacie-green.svg">
</head>
<body>
<header class="top">
  <div class="brand">
    <a href="index.html" class="name">Lärmampel</a>
    <span class="sub">Makerspace-Projekt</span>
  </div>
  <div class="logos">
    <img src="assets/logos/Makerspace.svg" alt="Makerspace Uni Stuttgart">
    <img class="tik" src="assets/logos/tik-logo.svg" alt="TIK">
  </div>
</header>
<nav class="main">{nav}</nav>
<div class="titleline"></div>
<main>
{body}
</main>
<footer>
  Makerspace Uni Stuttgart · Lärmampel · Konzept und Simulation, keine geeichte Messung
</footer>
</body>
</html>
"""


def doc_page(md_file: str, href: str) -> str:
    title, body, toc = markdown((ROOT / md_file).read_text(encoding="utf-8"))
    toc_html = ""
    if len(toc) > 2:
        links = "".join(f'<li><a href="#{a}">{inline(t)}</a></li>' for a, t in toc)
        toc_html = f'<aside class="toc"><h2>Inhalt</h2><ul>{links}</ul></aside>'
    content = (
        f'<article class="doc"><h1>{inline(title)}</h1>'
        f'<p class="srcnote">Quelle: <code>{md_file}</code></p>{body}</article>'
    )
    return page(f"{title} - Lärmampel", f'<div class="doclayout">{toc_html}{content}</div>',
                href)


def index_page(have_renders: list[tuple[str, str, str]], downloads: list[tuple[str, str, str]]
               ) -> str:
    hero_img = (
        f'<img class="hero-img" src="img/{have_renders[0][0]}" '
        f'alt="Rendering der Lärmampel: Farbkreis und Display an der Wand">'
        if have_renders else ""
    )
    gallery = "".join(
        f'<figure><a href="img/{f}"><img src="img/{f}" alt="Lärmampel in {name}" '
        f'loading="lazy"></a><figcaption><b>{name}</b> {cap}</figcaption></figure>'
        for f, name, cap in have_renders
    )
    laser = "".join(
        f'<figure class="laser"><a href="laser/{f}"><img src="laser/preview/{f}" '
        f'alt="{cap}" loading="lazy"></a><figcaption>{cap}</figcaption></figure>'
        for f, cap in LASER_PREVIEW if (DOCS / "laser" / f).exists()
    )
    dl = "".join(
        f'<li><a href="{href}">{label}</a> <span>{hint}</span></li>'
        for href, label, hint in downloads
    )
    steps = [
        ("Teile besorgen", "Pi Zero 2 W, Mikrofon INMP441, WS2812B-Streifen, Netzteil, "
         "Sperrholz und Acryl.", "teileliste.html"),
        ("Gehäuse lasern", "15 Vorlagen für Farbkreis und Displaykasten, parametrisch "
         "erzeugt.", "gehaeuse.html"),
        ("Elektronik verdrahten", "Eine Datenleitung für alle 102 LEDs, Pegelwandler, "
         "Absicherung.", "schaltung.html"),
        ("Kalibrieren", "Einmal gegen einen Schallpegelmesser abgleichen, Offset "
         "eintragen.", "schaltung.html#mikrofon-und-messgenauigkeit-inmp441-datenblatt"),
        ("Aufhängen", "Zwei Schlüssellöcher, ein Netzteil, Daten per WLAN.",
         "gehaeuse.html"),
    ]
    steps_html = "".join(
        f'<li><span class="nr">{n}</span><div><a href="{href}"><b>{t}</b></a>'
        f"<p>{d}</p></div></li>"
        for n, (t, d, href) in enumerate(steps, 1)
    )
    body = f"""
<section class="hero">
  <div class="hero-text">
    <h1>Lärmampel</h1>
    <p class="lead">Eine Lärmampel für Klassenräume und Lernorte, selbst gebaut im
    Makerspace: Sie misst den Schallpegel, zeigt ihn als Farbe und in dB(A) und
    protokolliert die Werte im Netz.</p>
    <div class="cta">
      <a class="btn primary" href="simulator/index.html">Simulator öffnen</a>
      <a class="btn" href="gehaeuse.html">Bauanleitung</a>
    </div>
    <div class="warn"><b>Projektstatus:</b> Konzept, Simulation und Konstruktion.
    Die Hardware ist noch nicht gebaut; Maße, Schaltung und Firmware sind ungetestet.</div>
  </div>
  {hero_img}
</section>

<section>
  <h2>So sieht sie aus</h2>
  <p>Rendering der Bauform „Farbkreis + Display“ in den drei Ampelstufen. Maße wie in
  den Lasercut-Vorlagen: Farbkreis Ø 360 mm, Displaykasten 240 × 200 mm.</p>
  <div class="gallery">{gallery}</div>
</section>

<section>
  <h2>Zwei Bauformen</h2>
  <div class="cards">
    <a class="card" href="gehaeuse.html">
      <h3>Farbkreis + Display</h3>
      <p>Eine runde Leuchtfläche in der Ampelfarbe, indirekt beleuchtet von 60 LEDs,
      daneben ein Displaykasten mit zwei 7-Segment-Ziffern hinter Rauchglas.
      102 LEDs, Gehäuse aus gelasertem Pappelsperrholz.</p>
      <span class="more">Gehäuse und Bau</span>
    </a>
    <a class="card" href="tacho.html">
      <h3>Tacho-Scheibe</h3>
      <p>Eine runde Scheibe mit 45-LED-Bogen über 270 Grad, der mit dem Pegel von
      Grün über Gelb nach Rot wandert, und großen Ziffern in der Mitte. 87 LEDs.</p>
      <span class="more">Visualisierung</span>
    </a>
  </div>
</section>

<section>
  <h2>Technik</h2>
  <div class="facts">
    <div class="box"><h3>Messen</h3><p>MEMS-Mikrofon INMP441 über I2S. Nutzbar
    ca. 40-115 dB(A), nach Kalibrierung etwa ±1-2 dB - genug für eine Ampel, aber
    keine geeichte Messung.</p></div>
    <div class="box"><h3>Anzeigen</h3><p>WS2812B-LEDs an einer Datenleitung,
    Farbe mit Hysterese und Haltezeit, Spitzenwert, Warnung bei Dauer-Rot.</p></div>
    <div class="box"><h3>Speichern</h3><p>Raspberry Pi Zero 2 W: Leq, Lmax und L90
    pro Minute in SQLite, nächtliche Sicherung auf NAS oder Server, Weboberfläche.</p></div>
    <div class="box magenta"><h3>Datenschutz</h3><p>Es werden nur Pegelwerte
    berechnet und gespeichert, niemals Audio.</p></div>
  </div>
</section>

<section>
  <h2>Ausprobieren im Simulator</h2>
  <div class="sim">
    <p>Der Simulator im Browser zeigt beide Bauformen mit derselben Logik, die die
    Firmware bekommen soll. Klassenraum simulieren, Schieberegler oder das eigene
    Mikrofon, Schwellen und Zeitkonstanten einstellen, LED-Strom ablesen.</p>
    <a class="btn primary" href="simulator/index.html">Simulator öffnen</a>
  </div>
</section>

<section>
  <h2>In fünf Schritten zur Lärmampel</h2>
  <ol class="steps">{steps_html}</ol>
</section>

<section>
  <h2>Lasercut-Vorlagen</h2>
  <p>Rot = schneiden, Blau = ritzen, Schwarz = gravieren. Erzeugt von
  <code>laser/generate_laser.py</code>, alle Maße zentral änderbar.</p>
  <div class="gallery laser-gallery">{laser}</div>
</section>

<section>
  <h2>Downloads</h2>
  <ul class="downloads">{dl}</ul>
</section>
"""
    return page("Lärmampel - Makerspace-Projekt", body, "index.html",
                "Selbstgebaute Lärmampel mit Raspberry Pi, MEMS-Mikrofon und WS2812B: "
                "Simulator, Teileliste, Schaltung, Lasercut-Vorlagen und Renderings.")


CSS = """
@font-face { font-family: "Baloo"; src: url("fonts/Baloo-Regular.ttf") format("truetype"); }
@font-face { font-family: "UniStuttgart"; src: url("fonts/UniStuttgartSans-Light.ttf")
  format("truetype"); font-weight: 300 400; }
@font-face { font-family: "UniStuttgart"; src: url("fonts/UniStuttgartSans-Bold.ttf")
  format("truetype"); font-weight: 600 700; }
:root {
  --ms-anthrazit: #3A3D40; --ms-blau: #007FE1; --ms-magenta: #D13788;
  --ms-gruen: #38C23A; --ms-grau-hg: #F2F4F6; --ms-warn-bg: #fff0f4;
  --muted: #6c7279; --line: #dde2e8;
  --display: "Baloo", Arial, "Helvetica Neue", sans-serif;
  --body: "UniStuttgart", Arial, "Helvetica Neue", sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: #fff; color: var(--ms-anthrazit);
  font: 16px/1.55 var(--body); }
a { color: var(--ms-blau); }
img { max-width: 100%; height: auto; }
h1, h2, h3 { font-family: var(--display); font-weight: 400; line-height: 1.15; }
h2 { font-size: 28px; margin: 0 0 12px; }
h3 { font-size: 20px; margin: 0 0 6px; }
code { font-size: .92em; background: var(--ms-grau-hg); padding: 1px 5px; border-radius: 3px; }

header.top, nav.main, .titleline, main, footer { max-width: 1120px; margin: 0 auto; }
header.top { display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 18px 20px 6px; }
.brand .name { font-family: var(--display); font-size: 30px; color: var(--ms-anthrazit);
  text-decoration: none; }
.brand .sub { display: block; color: var(--muted); font-size: 14px; margin-top: -4px; }
.logos { display: flex; align-items: center; gap: 14px; }
.logos img { height: 46px; width: auto; }
.logos img.tik { height: 50px; }
nav.main { display: flex; flex-wrap: wrap; gap: 4px; padding: 6px 20px 0; }
nav.main a { text-decoration: none; color: var(--ms-anthrazit); padding: 6px 12px;
  border-radius: 4px; }
nav.main a:hover { color: var(--ms-blau); background: var(--ms-grau-hg); }
nav.main a.on { background: var(--ms-blau); color: #fff; font-weight: 700; }
.titleline { border-top: 1.5px solid var(--ms-magenta); margin-top: 10px; }
main { padding: 8px 20px 40px; }
section { margin: 44px 0; }
footer { padding: 14px 20px 30px; border-top: 1px solid var(--line); color: var(--muted);
  font-size: 14px; }

.hero { display: grid; grid-template-columns: 1fr 1.25fr; gap: 28px; align-items: center;
  margin-top: 28px; }
.hero h1 { font-size: 54px; margin: 0 0 8px; }
.lead { font-size: 19px; margin: 0 0 20px; }
.hero-img { border-radius: 6px; box-shadow: 0 10px 30px rgba(0,0,0,.12); }
.cta { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
.btn { display: inline-block; padding: 10px 18px; border-radius: 4px; text-decoration: none;
  border: 1px solid var(--ms-blau); color: var(--ms-blau); font-weight: 700; }
.btn.primary { background: var(--ms-blau); color: #fff; }
.btn:hover { filter: brightness(1.08); }
.warn { background: var(--ms-warn-bg); border-left: 3px solid var(--ms-magenta);
  padding: 10px 12px; border-radius: 4px; font-size: 15px; }
.warn b { color: var(--ms-magenta); }

.gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.gallery figure { margin: 0; }
.gallery img { border-radius: 4px; display: block; width: 100%; }
.gallery figcaption { font-size: 15px; color: var(--muted); margin-top: 4px; }
.gallery figcaption b { color: var(--ms-anthrazit); }
.laser-gallery { grid-template-columns: repeat(4, 1fr); }
.laser img { background: #fff; border: 1px solid var(--line); padding: 8px;
  aspect-ratio: 1; object-fit: contain; }

.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.card, .box { background: var(--ms-grau-hg); border-radius: 4px; padding: 16px 18px; }
.card { text-decoration: none; color: inherit; border-left: 3px solid var(--ms-blau); }
.card:hover { box-shadow: 0 4px 14px rgba(0,0,0,.08); }
.card h3, .box h3 { color: var(--ms-blau); text-transform: uppercase; font-size: 18px; }
.box.magenta h3 { color: var(--ms-magenta); }
.card p, .box p { margin: 0; }
.card .more { display: inline-block; margin-top: 10px; color: var(--ms-blau); font-weight: 700; }
.facts { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.sim { background: var(--ms-grau-hg); border-radius: 4px; padding: 18px; display: flex;
  gap: 18px; align-items: center; justify-content: space-between; }
.sim p { margin: 0; max-width: 760px; }

.steps { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.steps li { display: flex; gap: 12px; align-items: flex-start; }
.steps .nr { flex: none; width: 34px; height: 34px; border-radius: 50%; background: var(--ms-blau);
  color: #fff; font-family: var(--display); font-size: 19px; display: grid; place-items: center; }
.steps p { margin: 2px 0 0; color: var(--muted); }
.downloads { padding-left: 20px; }
.downloads li { margin: 6px 0; }
.downloads span { color: var(--muted); font-size: 14px; }

.doclayout { display: grid; grid-template-columns: 230px minmax(0, 1fr); gap: 32px;
  margin-top: 24px; }
.toc { position: sticky; top: 16px; align-self: start; background: var(--ms-grau-hg);
  border-radius: 4px; padding: 12px 14px; font-size: 15px; }
.toc h2 { font-size: 17px; color: var(--ms-blau); text-transform: uppercase; margin: 0 0 6px; }
.toc ul { list-style: none; padding: 0; margin: 0; }
.toc li { margin: 4px 0; }
.toc a { text-decoration: none; }
.doc h1 { font-size: 38px; margin: 0; }
.doc .srcnote { color: var(--muted); font-size: 14px; margin: 2px 0 18px; }
.doc h2 { margin-top: 34px; padding-bottom: 4px; border-bottom: 1px solid var(--line); }
.doc h3 { margin-top: 22px; color: var(--ms-blau); }
.table-wrap { overflow-x: auto; margin: 12px 0; }
table { border-collapse: collapse; width: 100%; font-size: 15px; }
th { background: var(--ms-grau-hg); font-weight: 700; }
th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
pre { background: #2b2e33; color: #e8eaed; padding: 14px; border-radius: 4px; overflow-x: auto;
  font-size: 13px; line-height: 1.35; }
pre code { background: none; padding: 0; color: inherit; }
hr { border: 0; border-top: 1.5px solid var(--ms-magenta); margin: 40px 0; }

@media (max-width: 900px) {
  .hero, .cards, .doclayout { grid-template-columns: 1fr; }
  .facts { grid-template-columns: 1fr 1fr; }
  .gallery { grid-template-columns: 1fr; }
  .laser-gallery { grid-template-columns: 1fr 1fr; }
  .toc { position: static; }
  .sim { flex-direction: column; align-items: flex-start; }
}
@media (max-width: 560px) {
  header.top { flex-direction: column-reverse; align-items: flex-start; padding: 14px 16px 4px; }
  nav.main, main, footer { padding-left: 16px; padding-right: 16px; }
  .hero h1 { font-size: 40px; }
  .facts { grid-template-columns: 1fr; }
}
"""


def build() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    (DOCS / "assets").mkdir(parents=True)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

    shutil.copytree(ROOT / "simulator", DOCS / "simulator")
    shutil.copytree(ROOT / "simulator" / "assets" / "fonts", DOCS / "assets" / "fonts")
    shutil.copytree(ROOT / "simulator" / "assets" / "logos", DOCS / "assets" / "logos")
    (DOCS / "assets" / "site.css").write_text(CSS, encoding="utf-8")
    sim = DOCS / "simulator" / "index.html"
    sim.write_text(sim.read_text(encoding="utf-8").replace(
        "<h1>Lärmampel Simulator</h1>",
        '<h1>Lärmampel Simulator</h1>\n    <p><a href="../index.html">'
        "Zurück zur Projektseite</a></p>", 1), encoding="utf-8")
    shutil.copytree(ROOT / "laser" / "svg", DOCS / "laser")
    # Vorschau mit dicken Linien; die Haarlinien der Laserdateien verschwinden verkleinert
    (DOCS / "laser" / "preview").mkdir()
    for f, _ in LASER_PREVIEW:
        svg = (ROOT / "laser" / "svg" / f).read_text(encoding="utf-8")
        (DOCS / "laser" / "preview" / f).write_text(
            svg.replace('stroke-width="0.1"', 'stroke-width="1.6"'), encoding="utf-8")

    have = []
    (DOCS / "img").mkdir()
    for f, name, cap in RENDERS:
        src = ROOT / "render" / f
        if src.exists():
            shutil.copy2(src, DOCS / "img" / f)
            have.append((f, name, cap))

    dl_dir = DOCS / "downloads"
    dl_dir.mkdir()
    with zipfile.ZipFile(dl_dir / "laermampel-laser.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for svg in sorted((ROOT / "laser" / "svg").glob("*.svg")):
            z.write(svg, f"svg/{svg.name}")
        z.write(ROOT / "laser" / "generate_laser.py", "generate_laser.py")
    downloads = [
        ("downloads/laermampel-laser.zip", "Lasercut-Vorlagen (ZIP)",
         "15 SVGs + Generator-Skript"),
    ]
    for name, label, hint in [
        ("laermampel.blend", "Blender-Szene (.blend)", "Farbkreis + Display, Blender 5"),
        ("render_laermampel.py", "Render-Skript", "erzeugt die Szene aus den Maßen"),
    ]:
        if (ROOT / "render" / name).exists():
            shutil.copy2(ROOT / "render" / name, dl_dir / name)
            downloads.append((f"downloads/{name}", label, hint))
    for _, _, md in PAGES:
        shutil.copy2(ROOT / md, dl_dir / md)
    downloads.append(("downloads/TEILELISTE.md", "Dokumente als Markdown",
                      "Teileliste, Schaltung, Gehäuse, Tacho-Variante"))

    (DOCS / "index.html").write_text(index_page(have, downloads), encoding="utf-8")
    for href, _, md in PAGES:
        (DOCS / href).write_text(doc_page(md, href), encoding="utf-8")

    for p in sorted(DOCS.rglob("*")):
        if p.is_file() and p.suffix in {".html", ".zip"}:
            print(p.relative_to(ROOT))


if __name__ == "__main__":
    build()
