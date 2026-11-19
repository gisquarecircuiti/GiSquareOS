"""GiSquare OS - aspetto comune delle finestre GiSquare (Benvenuto, Installa altri programmi).

Stesso stile del sito di GiSquare Circuiti: blu notte sfumato, accento azzurro,
titoli con carattere graziato e "OS" in corsivo azzurro.
"""
import os

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, Gtk  # noqa: E402

CSS = b"""
.gisquare {
    background-image: linear-gradient(128deg, #121f35 0%, #172b46 55%, #223a5a 100%);
    color: #f5f8fc;
    font-family: Inter, "Open Sans", sans-serif;
}
.gisquare label { color: #f5f8fc; }
.gisquare .occhiello { color: #c5d1e2; font-size: 9pt; font-weight: 600; letter-spacing: 2px; }
.gisquare .titolo { font-family: "Noto Serif", serif; font-size: 30pt; }
.gisquare .sottotitolo { color: #c5d1e2; font-size: 11.5pt; }
.gisquare .tenue { color: #a1b0c6; font-size: 9.5pt; }
.gisquare .scheda {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(220, 233, 248, 0.14);
    border-radius: 10px;
    padding: 14px;
    box-shadow: none;
    color: #f5f8fc;
}
.gisquare .scheda:hover {
    background-color: rgba(109, 200, 255, 0.12);
    border-color: rgba(109, 200, 255, 0.55);
}
.gisquare .scheda .nome { font-size: 11.5pt; font-weight: 700; }
.gisquare .scheda .descrizione { color: #c5d1e2; font-size: 9.5pt; }
.gisquare .primario {
    background-image: none;
    background-color: #6dc8ff;
    color: #172941;
    border: none;
    border-radius: 4px;
    padding: 8px 22px;
    font-weight: 700;
    box-shadow: none;
}
.gisquare .primario label { color: #172941; }
.gisquare .primario:hover { background-color: #b7e7ff; }
.gisquare .primario:disabled { background-color: rgba(109, 200, 255, 0.35); }
.gisquare .secondario {
    background-image: none;
    background-color: transparent;
    color: #e5edf7;
    border: 1px solid rgba(220, 233, 248, 0.35);
    border-radius: 4px;
    padding: 8px 18px;
    box-shadow: none;
}
.gisquare .secondario:hover { border-color: #6dc8ff; }
.gisquare .avviso {
    background-color: rgba(255, 184, 74, 0.14);
    border: 1px solid rgba(255, 184, 74, 0.65);
    border-radius: 8px;
    padding: 12px 14px;
}
.gisquare .avviso label { color: #ffe3b8; }
.gisquare .ok {
    background-color: rgba(53, 208, 165, 0.12);
    border: 1px solid rgba(53, 208, 165, 0.6);
    border-radius: 8px;
    padding: 12px 14px;
}
.gisquare .ok label { color: #c9f5e8; }
.gisquare .avviso button, .gisquare .ok button { padding: 4px 14px; }
.gisquare .barra {
    background-color: rgba(10, 20, 38, 0.55);
    border-top: 1px solid rgba(220, 233, 248, 0.14);
    padding: 14px 22px;
}
.gisquare .spunta label { font-size: 11.5pt; font-weight: 600; }
.gisquare check {
    min-width: 20px; min-height: 20px;
    border: 2px solid #6dc8ff; border-radius: 4px;
    background-image: none; background-color: transparent;
}
.gisquare check:checked { background-color: #6dc8ff; color: #172941; }
.gisquare .stato-ok { color: #35d0a5; font-weight: 600; }
.gisquare progressbar trough { background-color: rgba(255, 255, 255, 0.10); border: none; min-height: 8px; border-radius: 4px; }
.gisquare progressbar progress { background-color: #6dc8ff; border: none; min-height: 8px; border-radius: 4px; }
"""


def applica_stile():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def classe(widget, *nomi):
    for n in nomi:
        widget.get_style_context().add_class(n)
    return widget


def etichetta(testo, *classi, markup=False, xalign=0.0, avvolgi=False):
    lab = Gtk.Label()
    if markup:
        lab.set_markup(testo)
    else:
        lab.set_text(testo)
    lab.set_xalign(xalign)
    if avvolgi:
        lab.set_line_wrap(True)
        lab.set_max_width_chars(60)
    return classe(lab, *classi)


def intestazione(occhiello, sottotitolo=None):
    """Logo + piccola scritta maiuscola + 'GiSquare OS' come nel sito."""
    riga = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
    logo = Gtk.Image.new_from_icon_name("gisquare-os", Gtk.IconSize.DIALOG)
    logo.set_pixel_size(72)
    riga.pack_start(logo, False, False, 0)
    testi = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    testi.set_valign(Gtk.Align.CENTER)
    testi.pack_start(etichetta("●  " + occhiello.upper(), "occhiello", markup=False), False, False, 0)
    testi.pack_start(etichetta('GiSquare <span foreground="#6dc8ff"><i>OS</i></span>', "titolo",
                               markup=True), False, False, 0)
    riga.pack_start(testi, True, True, 0)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box.pack_start(riga, False, False, 0)
    if sottotitolo:
        box.pack_start(etichetta(sottotitolo, "sottotitolo", avvolgi=True), False, False, 0)
    return box


def finestra(titolo, larghezza, altezza):
    applica_stile()
    win = Gtk.Window(title=titolo)
    win.set_default_size(larghezza, altezza)
    win.set_position(Gtk.WindowPosition.CENTER)
    win.set_icon_name("gisquare-os")
    classe(win, "gisquare")
    win.connect("destroy", Gtk.main_quit)
    return win


def trova_desktop(*nomi):
    """Primo file .desktop esistente tra quelli indicati (accetta anche prefissi con '*')."""
    cartella = "/usr/share/applications"
    for n in nomi:
        if n.endswith("*"):
            for f in sorted(os.listdir(cartella)):
                if f.startswith(n[:-1]) and f.endswith(".desktop"):
                    return f
        elif os.path.exists(os.path.join(cartella, n)):
            return n
    return None


def avvia(desktop_id):
    info = Gio.DesktopAppInfo.new(desktop_id)
    if info:
        info.launch([], None)


def live_senza_salvataggio():
    """True se il sistema gira da chiavetta senza spazio di salvataggio (persistenza)."""
    if not os.path.isdir("/run/live"):
        return False
    try:
        with open("/proc/mounts") as f:
            return " /run/live/persistence" not in f.read()
    except OSError:
        return False


def stato_salvataggio():
    """Dove finiscono i file dell'utente.

    Restituisce un dizionario con 'modo': 'installato', 'chiavetta' (con salvataggio)
    oppure 'senza' (chiavetta senza salvataggio); per 'chiavetta' anche 'totale' e
    'libero' in byte dello spazio di salvataggio.
    """
    if not os.path.isdir("/run/live"):
        return {"modo": "installato"}
    punti = []
    try:
        with open("/proc/mounts") as f:
            for riga in f:
                campi = riga.split()
                if len(campi) > 1 and campi[1].startswith("/run/live/persistence/"):
                    punti.append(campi[1])
    except OSError:
        pass
    if not punti:
        return {"modo": "senza"}
    st = os.statvfs(punti[0])
    return {"modo": "chiavetta", "totale": st.f_blocks * st.f_frsize, "libero": st.f_bavail * st.f_frsize}


def gb(byte):
    return f"{byte / 1024 ** 3:.1f}".replace(".", ",") + " GB"


def apri(percorso_o_url):
    Gio.AppInfo.launch_default_for_uri(
        percorso_o_url if "://" in percorso_o_url else Gio.File.new_for_path(percorso_o_url).get_uri(), None)


GUIDA_CHIAVETTA = "file:///usr/share/gisquare-os/guida.html#chiavetta"
