#!/usr/bin/env python3
"""Genera la grafica di GiSquare OS (logo, sfondi, menu di avvio, accesso, caricamento, installer).

Lo stile riprende il sito di GiSquare Circuiti: blu notte sfumato con un alone azzurro,
"orbite" sottili, titoli con carattere graziato e "OS" in corsivo azzurro, scritte
piccole in maiuscolo e spaziate.

Uso:  python3 grafica/genera-grafica.py
Serve rsvg-convert (pacchetto librsvg2-bin) e i font Inter (fonts-inter) e
Noto Serif (fonts-noto-core).
I file finiscono direttamente in config/includes.chroot/ e in grafica/avvio/.
"""
import base64
import os
import random
import subprocess

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
DATI = os.path.join(RADICE, "config/includes.chroot/usr/share/gisquare-os")
ICONE = os.path.join(RADICE, "config/includes.chroot/usr/share/icons/hicolor")
PLYMOUTH = os.path.join(RADICE, "config/includes.chroot/usr/share/plymouth/themes/gisquare")
AVVIO = os.path.join(QUI, "avvio")

# --- Colori del sito di GiSquare Circuiti -------------------------------------------
NOTTE_1 = "#121f35"      # sfumatura dello sfondo, da sinistra in alto...
NOTTE_2 = "#172b46"
NOTTE_3 = "#223a5a"      # ...a destra in basso
AZZURRO = "#6dc8ff"      # accento (pulsanti, "OS" in corsivo, orbite)
TESTO = "#f5f8fc"
TESTO_2 = "#c5d1e2"      # testo secondario
META = "#a1b0c6"         # scritte piccole in maiuscolo
# --- Colori del marchio "Gi" -----------------------------------------------------------
BLU_CHIARO = "#16345f"
BLU_SCURO = "#0a1426"
VERDE = "#35d0a5"
AMBRA = "#ffb84a"

SERIF = "Noto Serif"
SANS = "Inter"

# Il marchio "Gi" di GiSquare Circuiti (coordinate su 256x256)
MARCHIO = f"""
<path d="M138 95A52 52 0 1 0 150 136H110" fill="none" stroke="{VERDE}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="138" cy="95" r="10" fill="{AMBRA}"/><circle cx="110" cy="136" r="10" fill="{AMBRA}"/>
<path d="M150 136V186H192V112" fill="none" stroke="{VERDE}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="192" cy="80" r="13" fill="{AMBRA}"/>
"""


def logo_os(id_gr="g"):
    """Logo di GiSquare OS: il marchio Gi dentro un 'chip' con i piedini."""
    piedini = []
    for i in range(5):
        p = 64 + i * 32
        piedini += [
            f'<rect x="{p-5}" y="6" width="10" height="22" rx="4"/>',
            f'<rect x="{p-5}" y="228" width="10" height="22" rx="4"/>',
            f'<rect x="6" y="{p-5}" width="22" height="10" rx="4"/>',
            f'<rect x="228" y="{p-5}" width="22" height="10" rx="4"/>',
        ]
    return f"""
<defs><linearGradient id="{id_gr}" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{BLU_CHIARO}"/><stop offset="1" stop-color="{BLU_SCURO}"/></linearGradient></defs>
<g fill="{VERDE}" opacity="0.85">{''.join(piedini)}</g>
<rect x="22" y="22" width="212" height="212" rx="40" fill="url(#{id_gr})" stroke="{VERDE}" stroke-opacity="0.35" stroke-width="3"/>
<g transform="translate(128 128) scale(0.86) translate(-128 -128)">{MARCHIO}</g>
"""


def svg(w, h, corpo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{corpo}</svg>')


def piste(w, h, n, seme, opacita=0.07, zona=None, colore=AZZURRO, spessore=2):
    """Piste di circuito stampato casuali (tratti orizzontali, verticali e a 45°)."""
    rnd = random.Random(seme)
    passo = 24
    out = []
    x0, y0, x1, y1 = zona if zona else (0, 0, w, h)
    for _ in range(n):
        x = rnd.randrange(int(x0 / passo), int(x1 / passo)) * passo
        y = rnd.randrange(int(y0 / passo), int(y1 / passo)) * passo
        punti = [(x, y)]
        d = rnd.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
        for _ in range(rnd.randint(2, 5)):
            lung = rnd.randint(2, 9) * passo
            x += d[0] * lung
            y += d[1] * lung
            punti.append((x, y))
            if d[0] == 0 or d[1] == 0:          # dritto -> diagonale
                d = rnd.choice([(1, d[1]), (-1, d[1])]) if d[0] == 0 else rnd.choice([(d[0], 1), (d[0], -1)])
            else:                                 # diagonale -> dritto
                d = rnd.choice([(d[0], 0), (0, d[1])])
        pts = " ".join(f"{a},{b}" for a, b in punti)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{colore}" stroke-width="{spessore}" '
                   f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacita}"/>')
        xe, ye = punti[-1]
        out.append(f'<circle cx="{xe}" cy="{ye}" r="{spessore * 2.5}" fill="none" stroke="{colore}" '
                   f'stroke-width="{spessore}" opacity="{opacita * 1.8:.2f}"/>')
    return "".join(out)


def fondo(w, h, id_gr="sf", alone=(0.76, 0.42), forza_alone=0.16):
    """Sfondo del sito: sfumatura blu notte a 128° con un alone azzurro."""
    ax, ay = alone[0] * w, alone[1] * h
    r = 0.42 * max(w, h)
    return (f'<defs>'
            f'<linearGradient id="{id_gr}" x1="0" y1="0" x2="1" y2="0.78">'
            f'<stop offset="0" stop-color="{NOTTE_1}"/><stop offset="0.55" stop-color="{NOTTE_2}"/>'
            f'<stop offset="1" stop-color="{NOTTE_3}"/></linearGradient>'
            f'<radialGradient id="{id_gr}a" cx="{ax}" cy="{ay}" r="{r}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{AZZURRO}" stop-opacity="{forza_alone}"/>'
            f'<stop offset="1" stop-color="{AZZURRO}" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#{id_gr})"/>'
            f'<rect width="{w}" height="{h}" fill="url(#{id_gr}a)"/>')


def orbite(cx, cy, r, spessore=1.5):
    """Due cerchi sottili attorno all'alone, uno pieno e uno tratteggiato (come nel sito)."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{AZZURRO}" '
            f'stroke-opacity="0.18" stroke-width="{spessore}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.68:.0f}" fill="none" stroke="{AZZURRO}" '
            f'stroke-opacity="0.13" stroke-width="{spessore}" stroke-dasharray="{spessore * 5} {spessore * 5}"/>')


def occhiello(x, y, testo, dim, ancora="start"):
    """Scritta piccola in maiuscolo, spaziata, con il puntino azzurro luminoso davanti."""
    r = dim * 0.32
    if ancora == "start":
        punto = (f'<circle cx="{x + r}" cy="{y - dim * 0.36:.1f}" r="{r * 2.2:.1f}" fill="{AZZURRO}" opacity="0.25"/>'
                 f'<circle cx="{x + r}" cy="{y - dim * 0.36:.1f}" r="{r:.1f}" fill="{AZZURRO}"/>')
        x_t = x + r * 2 + dim * 0.8
    else:
        punto, x_t = "", x
    return punto + (f'<text x="{x_t}" y="{y}" font-family="{SANS}" font-weight="600" font-size="{dim}" '
                    f'letter-spacing="{dim * 0.15:.1f}" fill="{TESTO_2}" text-anchor="{ancora}">{testo}</text>')


def titolo(x, y, dim, ancora="start"):
    """'GiSquare OS' con il carattere graziato del sito e 'OS' in corsivo azzurro."""
    return (f'<text x="{x}" y="{y}" font-family="{SERIF}" font-weight="400" font-size="{dim}" '
            f'letter-spacing="{-dim * 0.035:.1f}" text-anchor="{ancora}" fill="{TESTO}">GiSquare '
            f'<tspan font-style="italic" fill="{AZZURRO}">OS</tspan></text>')


def testo(x, y, dim, contenuto, colore=TESTO_2, ancora="start", peso=400, spaziatura=0):
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-weight="{peso}" font-size="{dim}" '
            f'letter-spacing="{spaziatura}" fill="{colore}" text-anchor="{ancora}">{contenuto}</text>')


def meta(x, y, dim, voci, ancora="start"):
    """Riga di voci maiuscole separate da puntini azzurri (es. DEBIAN 13 · USB · ITALIANO)."""
    sep = f'<tspan fill="{AZZURRO}">   ·   </tspan>'
    # xml:space="preserve": altrimenti gli spazi attorno ai puntini vengono compressi
    return (f'<text xml:space="preserve" x="{x}" y="{y}" font-family="{SANS}" font-weight="500" font-size="{dim}" '
            f'letter-spacing="{dim * 0.12:.1f}" fill="{META}" text-anchor="{ancora}">{sep.join(voci)}</text>')


def logo_in(x, y, lato, id_gr):
    return f'<g transform="translate({x} {y}) scale({lato / 256})">{logo_os(id_gr)}</g>'


def logo_con_alone(cx, cy, lato, id_gr):
    """Logo centrato in (cx, cy) con un'ombra morbida sotto, come la finestra nel sito."""
    return (f'<defs><filter id="{id_gr}o" x="-50%" y="-50%" width="200%" height="200%">'
            f'<feGaussianBlur stdDeviation="{lato * 0.09:.1f}"/></filter></defs>'
            f'<rect x="{cx - lato * 0.38:.0f}" y="{cy - lato * 0.30:.0f}" width="{lato * 0.76:.0f}" '
            f'height="{lato * 0.76:.0f}" rx="{lato * 0.15:.0f}" fill="#000" opacity="0.35" filter="url(#{id_gr}o)"/>'
            + logo_in(cx - lato / 2, cy - lato / 2, lato, id_gr))


def scrivi(percorso, contenuto):
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, "w", encoding="utf-8") as f:
        f.write(contenuto)


def png(sorgente_svg, destinazione, w=None, h=None):
    os.makedirs(os.path.dirname(destinazione), exist_ok=True)
    cmd = ["rsvg-convert", sorgente_svg, "-o", destinazione]
    if w:
        cmd += ["-w", str(w)]
    if h:
        cmd += ["-h", str(h)]
    subprocess.run(cmd, check=True)


def svg_con_png(percorso_png, w, h):
    """SVG che contiene un PNG: non dipende dai font del computer che lo converte."""
    with open(percorso_png, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"><image width="{w}" height="{h}" '
            f'xlink:href="data:image/png;base64,{b64}"/></svg>\n')


def main():
    tmp = os.path.join(QUI, "sorgenti")
    os.makedirs(tmp, exist_ok=True)

    def genera(nome, w, h, corpo, *destinazioni):
        scrivi(os.path.join(tmp, nome + ".svg"), svg(w, h, corpo))
        for d in destinazioni:
            png(os.path.join(tmp, nome + ".svg"), d)

    # 1. Logo e icone (invariati: sono il marchio)
    logo = svg(256, 256, logo_os())
    scrivi(os.path.join(tmp, "logo.svg"), logo)
    scrivi(os.path.join(DATI, "logo.svg"), logo)
    scrivi(os.path.join(ICONE, "scalable/apps/gisquare-os.svg"), logo)
    for lato in (16, 22, 24, 32, 48, 64, 128, 256):
        png(os.path.join(tmp, "logo.svg"),
            os.path.join(ICONE, f"{lato}x{lato}/apps/gisquare-os.png"), lato, lato)
    png(os.path.join(tmp, "logo.svg"), os.path.join(DATI, "logo-256.png"), 256, 256)
    png(os.path.join(tmp, "logo.svg"), os.path.join(DATI, "logo-128.png"), 128, 128)

    # 2. Sfondo del desktop (1920x1080). A sinistra restano libere le icone del desktop,
    #    in basso al centro c'è la barra dei programmi.
    W, H = 1920, 1080
    cx, cy = 1440, 470
    genera("sfondo", W, H,
           fondo(W, H, alone=(cx / W, cy / H))
           + piste(W, H, 34, 7, 0.06, zona=(900, 0, W, H))
           + orbite(cx, cy, 380, 2)
           + logo_con_alone(cx, cy, 250, "l1")
           + occhiello(330, 395, "SISTEMA OPERATIVO PER LA SCUOLA", 19)
           + titolo(322, 560, 150)
           + testo(330, 645, 30, "Leggero, portatile, con GiSquare Circuiti integrato.")
           + meta(330, 735, 17, ["DEBIAN 13", "DA CHIAVETTA USB", "IN ITALIANO"])
           + f'<line x1="330" y1="930" x2="{W - 220}" y2="930" stroke="#dce9f8" stroke-opacity="0.18" stroke-width="1.5"/>',
           os.path.join(DATI, "sfondo.png"))

    # 3. Schermata di accesso: niente scritte, le orbite attorno al riquadro di accesso
    genera("accesso", W, H,
           fondo(W, H, "sa", alone=(0.5, 0.55), forza_alone=0.20)
           + piste(W, H, 40, 9, 0.05)
           + orbite(W / 2, H * 0.55, 470, 2)
           + logo_in(64, 56, 72, "la") + titolo(152, 108, 46),
           os.path.join(DATI, "accesso.png"))

    # 4. Menu GRUB del sistema installato (1024x768, il menu sta al centro)
    gw, gh = 1024, 768
    genera("grub", gw, gh,
           fondo(gw, gh, "sg", alone=(0.82, 0.30))
           + orbite(gw * 0.82, gh * 0.30, 250)
           + logo_in(48, 40, 64, "l2") + titolo(126, 88, 40)
           + occhiello(48, gh - 34, "AVVIO DEL SISTEMA", 12),
           os.path.join(DATI, "grub.png"))

    # 5. Menu di avvio della chiavetta (640x480; live-build lo porta anche a 800x600)
    aw, ah = 640, 480
    genera("splash", aw, ah,
           fondo(aw, ah, "sv", alone=(0.86, 0.12), forza_alone=0.20)
           + orbite(aw * 0.86, ah * 0.12, 190, 1)
           + logo_in(26, 22, 50, "l3") + titolo(88, 60, 31)
           + occhiello(28, 104, "AVVIO DA CHIAVETTA USB", 9)
           + testo(aw - 22, ah - 16, 10, "BASATO SU DEBIAN", META, "end", 500, 1.2),
           os.path.join(AVVIO, "splash.png"))
    scrivi(os.path.join(AVVIO, "splash.svg.in"), svg_con_png(os.path.join(AVVIO, "splash.png"), aw, ah))

    # 6. Schermata di caricamento (Plymouth): logo e scritta su fondo trasparente,
    #    lo sfondo sfumato lo disegna Plymouth con gli stessi colori
    pw, ph = 640, 360
    genera("caricamento", pw, ph,
           logo_con_alone(pw / 2, 110, 150, "lp")
           + titolo(pw / 2, 268, 60, "middle")
           + meta(pw / 2, 318, 14, ["AVVIO IN CORSO"], "middle"),
           os.path.join(PLYMOUTH, "watermark.png"))
    # Rotellina azzurra (30 fotogrammi, sostituisce quella grigia del tema "spinner")
    for f in range(30):
        tacche = "".join(
            f'<rect x="-1.6" y="-14" width="3.2" height="7" rx="1.6" fill="{AZZURRO}" '
            f'opacity="{0.15 + 0.85 * ((i - f * 12 / 30) % 12) / 11:.2f}" transform="rotate({i * 30})"/>'
            for i in range(12))
        genera(f"rotellina-{f + 1:02d}", 32, 32, f'<g transform="translate(16 16)">{tacche}</g>',
               os.path.join(PLYMOUTH, f"throbber-{f + 1:04d}.png"))

    # 7. Installer (Calamares)
    genera("benvenuto", 800, 300,
           fondo(800, 300, "sb", alone=(0.18, 0.5), forza_alone=0.22)
           + orbite(160, 150, 130, 1.2)
           + logo_in(85, 75, 150, "l4")
           + occhiello(300, 110, "INSTALLAZIONE SUL COMPUTER", 12)
           + titolo(294, 190, 66),
           os.path.join(DATI, "installer/benvenuto.png"))
    png(os.path.join(tmp, "logo.svg"), os.path.join(DATI, "installer/logo.png"), 128, 128)

    # Diapositive mostrate durante la copia dei file (titolo graziato con parola in corsivo)
    diapositive = [
        ("01", "Pronto per", "studiare",
         "Browser, ufficio, stampanti e GiSquare Circuiti già installati."),
        ("02", "Dal simulatore al", "circuito vero",
         "Arduino IDE, Fritzing e Thonny per passare alla pratica."),
        ("03", "Recupero dati", "incluso",
         "Strumenti per salvare i file da dischi e PC che non si avviano più."),
    ]
    for i, (num, prima, corsivo, descr) in enumerate(diapositive, 1):
        genera(f"diapositiva{i}", 800, 440,
               fondo(800, 440, f"sd{i}", alone=(0.84, 0.30))
               + orbite(672, 132, 150, 1.2)
               + logo_in(612, 72, 120, f"ld{i}")
               + testo(64, 96, 13, f"{num} / 03", AZZURRO, peso=600, spaziatura=2)
               + f'<text x="64" y="250" font-family="{SERIF}" font-size="50" letter-spacing="-1.6" fill="{TESTO}">'
                 f'{prima}</text>'
               + f'<text x="64" y="310" font-family="{SERIF}" font-style="italic" font-size="50" '
                 f'letter-spacing="-1.6" fill="{AZZURRO}">{corsivo}</text>'
               + testo(66, 370, 17, descr),
               os.path.join(DATI, f"installer/diapositiva{i}.png"))

    # 8. Icone GiSquare dei collegamenti (Installa, Recupero dati, Guida, Programmi):
    #    riquadro blu notte con alone azzurro, tratti azzurri e verdi, dettaglio ambra
    def riquadro(id_):
        return (f'<defs><linearGradient id="{id_}" x1="0" y1="0" x2="1" y2="1">'
                f'<stop offset="0" stop-color="{NOTTE_3}"/><stop offset="1" stop-color="{NOTTE_1}"/></linearGradient>'
                f'<radialGradient id="{id_}g" cx="0.3" cy="0.25" r="0.75">'
                f'<stop offset="0" stop-color="{AZZURRO}" stop-opacity="0.30"/>'
                f'<stop offset="1" stop-color="{AZZURRO}" stop-opacity="0"/></radialGradient></defs>'
                f'<rect x="16" y="16" width="224" height="224" rx="56" fill="url(#{id_})"/>'
                f'<rect x="16" y="16" width="224" height="224" rx="56" fill="url(#{id_}g)"/>'
                f'<rect x="17.5" y="17.5" width="221" height="221" rx="54.5" fill="none" '
                f'stroke="{AZZURRO}" stroke-opacity="0.35" stroke-width="3"/>')
    T = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    icone = {
        # vassoio (il disco del computer) con freccia verde che entra
        "gisquare-installa": riquadro("ia")
            + f'<rect x="58" y="146" width="140" height="48" rx="14" {T} stroke="{AZZURRO}" stroke-width="12"/>'
            + f'<circle cx="170" cy="170" r="7" fill="{AMBRA}"/>'
            + f'<path d="M128 54V124M96 96L128 128L160 96" {T} stroke="{VERDE}" stroke-width="14"/>',
        # disco con freccia circolare verde (si torna indietro, si recupera)
        "gisquare-recupero": riquadro("ir")
            + f'<rect x="58" y="58" width="140" height="140" rx="24" {T} stroke="{AZZURRO}" stroke-width="12"/>'
            + f'<line x1="58" y1="158" x2="198" y2="158" stroke="{AZZURRO}" stroke-width="10"/>'
            + f'<circle cx="172" cy="178" r="7" fill="{AMBRA}"/>'
            + f'<path d="M150 108A24 24 0 1 1 138 87" {T} stroke="{VERDE}" stroke-width="12"/>'
            + f'<path d="M126 74L141 86L128 100" {T} stroke="{VERDE}" stroke-width="11"/>',
        # libro aperto con segnalibro ambra
        "gisquare-guida": riquadro("ig")
            + f'<path d="M128 84C108 70 82 68 58 72V186C82 182 108 184 128 198C148 184 174 182 198 186V72C174 68 148 70 128 84Z" '
              f'{T} stroke="{AZZURRO}" stroke-width="12"/>'
            + f'<line x1="128" y1="88" x2="128" y2="192" stroke="{AZZURRO}" stroke-width="10"/>'
            + f'<path d="M154 70V118L167 107L180 118V70Z" fill="{AMBRA}"/>',
        # chiavetta USB con la spunta verde (i file sono al sicuro)
        "gisquare-salvataggio": riquadro("is")
            + f'<rect x="100" y="48" width="56" height="44" rx="6" {T} stroke="{AZZURRO}" stroke-width="10"/>'
            + f'<rect x="113" y="62" width="10" height="10" rx="2" fill="{AZZURRO}"/>'
            + f'<rect x="133" y="62" width="10" height="10" rx="2" fill="{AZZURRO}"/>'
            + f'<rect x="80" y="92" width="96" height="118" rx="20" {T} stroke="{AZZURRO}" stroke-width="12"/>'
            + f'<path d="M104 152L122 170L154 134" {T} stroke="{VERDE}" stroke-width="13"/>'
            + f'<circle cx="160" cy="194" r="7" fill="{AMBRA}"/>',
        # quattro riquadri (i programmi), uno verde con il "+"
        "gisquare-programmi": riquadro("ip")
            + f'<rect x="62" y="62" width="56" height="56" rx="14" {T} stroke="{AZZURRO}" stroke-width="11"/>'
            + f'<rect x="138" y="62" width="56" height="56" rx="14" {T} stroke="{AZZURRO}" stroke-width="11"/>'
            + f'<rect x="62" y="138" width="56" height="56" rx="14" {T} stroke="{AZZURRO}" stroke-width="11"/>'
            + f'<path d="M166 140V192M140 166H192" {T} stroke="{VERDE}" stroke-width="13"/>'
            + f'<circle cx="194" cy="62" r="9" fill="{AMBRA}"/>',
    }
    for nome, corpo in icone.items():
        contenuto = svg(256, 256, corpo)
        scrivi(os.path.join(tmp, nome + ".svg"), contenuto)
        scrivi(os.path.join(ICONE, f"scalable/apps/{nome}.svg"), contenuto)
        for lato in (48, 64, 128):
            png(os.path.join(tmp, nome + ".svg"), os.path.join(ICONE, f"{lato}x{lato}/apps/{nome}.png"), lato, lato)

    print("Grafica generata.")


if __name__ == "__main__":
    main()
