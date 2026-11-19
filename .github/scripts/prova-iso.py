#!/usr/bin/env python3
"""Avvia la ISO di GiSquare OS in QEMU e salva delle schermate nei momenti chiave.

Uso: prova-iso.py ISO MODALITA(bios|uefi) CARTELLA_SCHERMATE [ID_DESKTOP_CIRCUITI]
La tastiera del sistema live e' italiana: i tasti vengono inviati di conseguenza.
"""
import os, socket, subprocess, sys, time

iso, modo, uscita = sys.argv[1], sys.argv[2], sys.argv[3]
circuiti = sys.argv[4] if len(sys.argv) > 4 else ""
os.makedirs(uscita, exist_ok=True)
mon = os.path.join(uscita, f"monitor-{modo}.sock")

cmd = ["qemu-system-x86_64", "-enable-kvm", "-cpu", "host", "-m", "4096", "-smp", "2",
       "-cdrom", iso, "-boot", "d", "-vga", "std", "-display", "none",
       "-monitor", f"unix:{mon},server,nowait", "-nic", "user,model=e1000",
       "-audiodev", "none,id=a0", "-usb", "-device", "usb-tablet"]
# Chiavetta USB con lo spazio di salvataggio (persistenza), se indicata: come quella
# creata da Rufus, una partizione ext4 chiamata "persistence" con persistence.conf.
pers = os.environ.get("PERSISTENZA")
if pers:
    cmd += ["-device", "qemu-xhci,id=xhci",
            "-drive", f"if=none,id=chiavetta,format=raw,file={pers}",
            "-device", "usb-storage,bus=xhci.0,drive=chiavetta,removable=on"]
if modo == "uefi":
    subprocess.run(["cp", "/usr/share/OVMF/OVMF_VARS_4M.fd", f"/tmp/vars-{modo}.fd"], check=True)
    cmd += ["-drive", "if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd",
            "-drive", f"if=pflash,format=raw,file=/tmp/vars-{modo}.fd"]
qemu = subprocess.Popen(cmd)
inizio = time.time()

for _ in range(50):
    try:
        s = socket.socket(socket.AF_UNIX); s.connect(mon); break
    except OSError:
        time.sleep(0.2)
s.settimeout(2)

def monitor(c):
    s.sendall((c + "\n").encode())
    time.sleep(0.3)
    try:
        s.recv(65536)
    except socket.timeout:
        pass

def foto(nome):
    f = os.path.abspath(os.path.join(uscita, f"{modo}-{int(time.time()-inizio):03d}s-{nome}.png"))
    monitor(f"screendump {f} -f png")
    print("schermata:", f, flush=True)

def aspetta(fino_a):
    while time.time() - inizio < fino_a:
        if qemu.poll() is not None:
            sys.exit(f"QEMU si e' chiuso da solo (codice {qemu.returncode})")
        time.sleep(1)

# tastiera italiana: stessi tasti fisici del layout US per lettere e numeri
SPECIALI = {"-": "slash", "_": "shift-slash", ".": "dot", " ": "spc", "/": "shift-7", ":": "shift-dot"}
def scrivi(testo):
    for c in testo:
        k = SPECIALI.get(c, c)
        monitor(f"sendkey {k}")

# il menu parte da solo dopo 5 secondi: lo fotografiamo subito e non premiamo nulla
for t in (2, 4, 6):
    aspetta(t); foto("menu-avvio")
for t in (12, 20, 30, 50, 70, 90, 110, 130, 150):
    aspetta(t); foto("avvio")
aspetta(170); foto("desktop")
if circuiti:
    monitor("sendkey alt-f2"); time.sleep(3)
    scrivi(f"gtk-launch {circuiti}"); time.sleep(1); foto("comando")
    monitor("sendkey ret")
    for pausa in (15, 15, 20):
        time.sleep(pausa); foto("circuiti")
# Chromium con la pagina delle estensioni (per vedere uBlock Origin)
monitor("sendkey alt-f2"); time.sleep(3)
scrivi("chromium chrome://extensions"); time.sleep(1)
monitor("sendkey ret")
time.sleep(30)                # Chromium scarica uBlock Origin Lite al primo avvio
monitor("sendkey ctrl-l"); time.sleep(1)
scrivi("chrome://extensions"); monitor("sendkey ret")
for pausa in (8, 20):
    time.sleep(pausa); foto("chromium-estensioni")
monitor("quit")
qemu.wait(timeout=30)
