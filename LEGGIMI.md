# GiSquare OS

**Il sistema operativo leggero e portatile, con GiSquare Circuiti integrato.**
Basato su **Debian 13**: funziona da chiavetta USB (salvando i tuoi file) oppure si installa
sul computer. Pensato per la scuola, il laboratorio e i PC che hanno qualche anno.

## Cosa contiene

- **GiSquare Circuiti**, il simulatore di circuiti, e per passare ai circuiti reali
  **Arduino IDE**, **Fritzing** e **Thonny** (Python e MicroPython): le schede USB
  (Arduino, ESP32, Raspberry Pi Pico) funzionano senza configurare nulla.
- **Per la classe:** lavagna **Xournal++** per la LIM, calcolatrice, tastiera su schermo.
- **Internet:** **Chromium** (predefinito, con il blocco della pubblicità uBlock Origin Lite,
  disattivabile) e **Firefox** con uBlock Origin.
- **Ufficio:** AbiWord e Gnumeric; LibreOffice, GIMP, Inkscape, Audacity e Shotcut si
  installano con un clic da **Installa altri programmi**; il negozio **Programmi** con Flathub
  per tutto il resto (es. GeoGebra).
- **Stampanti e scanner:** quasi tutte le stampanti di rete e USB funzionano senza driver.
- **Audio, video e Bluetooth:** VLC, cuffie e altoparlanti Bluetooth.
- **Recupero dati:** PhotoRec, TestDisk, ddrescue, GParted, SMART; dalla chiavetta i dischi
  del computer sono protetti in sola lettura.
- **Sicurezza:** aggiornamenti automatici di Debian, firewall attivo, aggiornamenti firmati
  delle parti GiSquare.
- **Benvenuto** al primo avvio e **guida integrata**, tutto in italiano.

**Requisiti:** PC a 64 bit (in pratica dal 2008 in poi), almeno 2 GB di RAM (consigliati 4 GB),
avvio da USB (BIOS o UEFI, anche con Secure Boot).

## Provarlo: la chiavetta in 15 minuti

1. Scarica la ISO dalla pagina **[Releases](../../releases/latest)**. Se è divisa in parti,
   le istruzioni per ricomporla sono nella pagina della release.
2. Scrivila su una chiavetta da **almeno 16 GB** con **[Rufus](https://rufus.ie)**, spostando il
   cursore **«Dimensione partizione persistente»**: è lo spazio dove si salvano i tuoi file.
3. Avvia il PC dalla chiavetta (tasto del menu di avvio: F12, F9, F11, F8 o Esc).

Tutti i passaggi, con le immagini: **[guida PDF «La chiavetta che salva i tuoi file»](documenti/GiSquare-OS-chiavetta-con-salvataggio.pdf)**.

Per installarlo sul computer: dalla chiavetta, doppio clic su **Installa GiSquare OS**.

## Aggiornamenti

Sul computer installato gli aggiornamenti di Debian e delle parti GiSquare arrivano da soli;
GiSquare Circuiti si aggiorna da solo. Dalla chiavetta, quando esce una versione nuova compare
un avviso con i passi per aggiornarla senza perdere i file. Dettagli: [AGGIORNAMENTI.md](AGGIORNAMENTI.md).

---

## Per chi sviluppa: costruire la ISO

### Su GitHub (consigliato)
**Actions → Costruisci GiSquare OS → Run workflow.** In circa mezz'ora la ISO compare nelle
**Releases**. Spunta **ufficiale** solo per le versioni da pubblicare (crea la release `v<versione>`
e l'archivio firmato degli aggiornamenti, vedi [AGGIORNAMENTI.md](AGGIORNAMENTI.md)).

**Actions → Prova la ISO** avvia la ISO in una macchina virtuale (BIOS con chiavetta di
salvataggio, e UEFI), apre GiSquare Circuiti e Chromium e salva le schermate nel ramo `schermate`.

### Sul proprio PC (Debian 13, anche dentro WSL su Windows)
```
sudo bash costruisci.sh
```
Su Windows: installa Debian in WSL (`wsl --install -d Debian` in PowerShell come amministratore),
poi doppio clic su **`Costruisci-GiSquare-OS.bat`**. Servono circa 15 GB liberi e Internet.
Il `.deb` di GiSquare Circuiti si scarica da solo dall'ultima release (oppure mettilo in `pacchetti/`).

### Struttura del progetto
```
costruisci.sh                script di costruzione (live-build su Debian 13)
config/package-lists/        programmi inclusi (un pacchetto Debian per riga)
config/includes.chroot/      file GiSquare: grafica, script, impostazioni
pacchetto/                   pacchetto gisquare-os (configura, control, postinst)
config/hooks/normal/         durante la build applica pacchetto/configura
grafica/                     generatore di logo, sfondi, menu di avvio, icone
documenti/                   guide in PDF
.github/workflows/           costruzione, pubblicazione e prova automatica
```

**Aggiungere o togliere un programma:** modifica `config/package-lists/gisquare.list.chroot`.
**Rigenerare la grafica:** `python3 grafica/genera-grafica.py` (servono `librsvg2-bin`,
`fonts-inter` e `fonts-noto-core`).

## Licenze

Il progetto GiSquare OS (script, configurazione, grafica) è rilasciato con licenza
**GNU GPL versione 3** ([LICENSE](LICENSE)). La ISO contiene programmi di Debian con le loro
licenze libere e **GiSquare Circuiti**, programma gratuito con la sua licenza d'uso.
Dettagli in [LICENZE.md](LICENZE.md).

GiSquare OS è basato su Debian ma non è un prodotto ufficiale del Progetto Debian.
