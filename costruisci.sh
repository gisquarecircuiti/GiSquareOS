#!/bin/bash
# =============================================================================
#  GiSquare OS - costruzione della ISO
#
#  Uso (su Debian 13 "trixie", anche dentro WSL su Windows):
#      sudo bash costruisci.sh             ISO normale
#      sudo bash costruisci.sh --sorgenti  ISO + archivio dei sorgenti (per la GPL)
#
#  Variabili facoltative:
#      GISQUARE_VERSIONE   versione del sistema            (predefinita: 1.0)
#      GISQUARE_SITO       sito del progetto
#      GISQUARE_DEB_URL    indirizzo da cui scaricare il .deb di GiSquare Circuiti
#      GISQUARE_LAVORO     cartella di lavoro              (predefinita: /var/tmp/gisquare-os-build)
#      GISQUARE_REPO_OS    repository GitHub di GiSquare OS, es. gisquarecircuiti/GiSquare-OS
#      GISQUARE_APT_URL    indirizzo dell'archivio degli aggiornamenti GiSquare
#
#  Il risultato finisce nella cartella "output" accanto a questo script.
# =============================================================================
set -euo pipefail

VERSIONE="${GISQUARE_VERSIONE:-1.0}"
SITO="${GISQUARE_SITO:-https://gisquarecircuiti.github.io/GiSquareCircuiti/}"
REPO_CIRCUITI="${GISQUARE_REPO_CIRCUITI:-gisquarecircuiti/GiSquareCircuiti}"
REPO_OS="${GISQUARE_REPO_OS:-}"           # repository GitHub di GiSquare OS (per l'avviso nuove versioni)
APT_URL="${GISQUARE_APT_URL:-}"           # indirizzo dell'archivio degli aggiornamenti GiSquare
LAVORO="${GISQUARE_LAVORO:-/var/tmp/gisquare-os-build}"
SORGENTI=false
[ "${1:-}" = "--sorgenti" ] && SORGENTI=true

PROGETTO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USCITA="$PROGETTO/output"

msg()    { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
avviso() { printf '\033[1;33mATTENZIONE: %s\033[0m\n' "$*"; }
errore() { printf '\n\033[1;31mERRORE: %s\033[0m\n' "$*" >&2; exit 1; }

# --- 0. Controlli preliminari -------------------------------------------------
if [ "$(id -u)" -ne 0 ]; then
    exec sudo --preserve-env=GISQUARE_VERSIONE,GISQUARE_SITO,GISQUARE_DEB_URL,GISQUARE_LAVORO,GISQUARE_REPO_CIRCUITI,GISQUARE_REPO_OS,GISQUARE_APT_URL \
        bash "$0" "$@"
fi

# shellcheck disable=SC1091
. /etc/os-release
if [ "${VERSION_CODENAME:-}" != "trixie" ]; then
    if [ "${VERSION_CODENAME:-}" = "bookworm" ]; then
        avviso "Questo computer usa Debian 12 (bookworm): per costruire GiSquare OS serve Debian 13 (trixie)."
        risposta="n"
        if [ -t 0 ]; then
            read -r -p "Aggiorno ora questo Debian alla versione 13? [s/N] " risposta
        fi
        [ "$risposta" = "s" ] || [ "$risposta" = "S" ] || errore "Aggiorna a Debian 13 e riprova."
        msg "Aggiornamento di Debian 12 -> 13 (può richiedere 10-20 minuti)"
        sed -i 's/bookworm/trixie/g' /etc/apt/sources.list 2>/dev/null || true
        find /etc/apt/sources.list.d -type f \( -name '*.list' -o -name '*.sources' \) \
            -exec sed -i 's/bookworm/trixie/g' {} +
        apt-get update -q
        DEBIAN_FRONTEND=noninteractive apt-get -y -q -o Dpkg::Options::=--force-confold full-upgrade
    else
        errore "Serve Debian 13 (trixie). Sistema trovato: ${PRETTY_NAME:-sconosciuto}."
    fi
fi

mkdir -p "$(dirname "$LAVORO")"
spazio=$(df --output=avail -BG "$(dirname "$LAVORO")" | tail -1 | tr -dc '0-9')
[ "$spazio" -ge 15 ] || avviso "Spazio libero: ${spazio} GB. Ne servono almeno 15."

# --- 1. Strumenti di build ------------------------------------------------------
msg "Installo gli strumenti necessari"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q --no-install-recommends \
    live-build debootstrap squashfs-tools xorriso isolinux syslinux-common syslinux-utils \
    grub-pc-bin grub-efi-amd64-bin mtools dosfstools librsvg2-bin rsync curl ca-certificates

# --- 2. Pacchetto di GiSquare Circuiti -------------------------------------------
msg "Cerco il pacchetto di GiSquare Circuiti"
mkdir -p "$PROGETTO/pacchetti"
DEB="$(find "$PROGETTO/pacchetti" -maxdepth 1 -name '*.deb' -print | sort | tail -1)"
if [ -z "$DEB" ] && [ -n "${GISQUARE_DEB_URL:-}" ]; then
    echo "Scarico $GISQUARE_DEB_URL"
    curl -fL --retry 3 -o "$PROGETTO/pacchetti/gisquare-circuiti.deb" "$GISQUARE_DEB_URL"
    DEB="$PROGETTO/pacchetti/gisquare-circuiti.deb"
fi
if [ -z "$DEB" ]; then
    echo "Nessun .deb nella cartella pacchetti: provo l'ultima versione pubblicata su GitHub..."
    url=$(curl -fsSL "https://api.github.com/repos/$REPO_CIRCUITI/releases/latest" 2>/dev/null \
          | grep -o '"browser_download_url": *"[^"]*amd64\.deb"' | head -1 | sed 's/.*"\(http[^"]*\)"/\1/' || true)
    if [ -n "$url" ]; then
        curl -fL --retry 3 -o "$PROGETTO/pacchetti/$(basename "$url")" "$url"
        DEB="$PROGETTO/pacchetti/$(basename "$url")"
    fi
fi
[ -n "$DEB" ] || errore "Copia il file .deb di GiSquare Circuiti nella cartella 'pacchetti' e riprova."
[ "$(dpkg-deb -f "$DEB" Package 2>/dev/null)" = "gisquare-circuiti" ] \
    || errore "$DEB non sembra il pacchetto di GiSquare Circuiti."
echo "Uso: $(basename "$DEB") (versione $(dpkg-deb -f "$DEB" Version))"

# --- 3. Cartella di lavoro --------------------------------------------------------
msg "Preparo la cartella di lavoro: $LAVORO"
mkdir -p "$LAVORO" "$USCITA"
cd "$LAVORO"
if [ -d config ]; then
    lb clean || true          # tiene la cache dei pacchetti: le build successive sono più veloci
fi
rm -rf config auto ./*.iso ./*.contents ./*.files ./*.packages ./*.zsync

# Copia senza proprietario e permessi originali (da Windows arriverebbero sbagliati)
rsync -rlt --chmod=D755,F644 "$PROGETTO/config/" "$LAVORO/config/"
chmod 755 config/hooks/normal/*
mkdir -p config/packages.chroot

# --- 3b. Pacchetto gisquare-os ---------------------------------------------------------
# Le parti GiSquare (config/includes.chroot e lo script pacchetto/configura) diventano il
# pacchetto "gisquare-os": la ISO lo installa e i computer con GiSquare OS installato
# ricevono le versioni nuove insieme agli aggiornamenti di Debian.
msg "Preparo il pacchetto gisquare-os"
PKG="$LAVORO/pacchetto-gisquare-os"
rm -rf "$PKG"
mkdir -p "$PKG/DEBIAN" "$PKG/usr/share/gisquare-os" "$PKG/usr/lib/gisquare-os"
mv config/includes.chroot "$PKG/usr/share/gisquare-os/sistema"
SIS="$PKG/usr/share/gisquare-os/sistema"
chmod 755 "$SIS"/usr/local/bin/* "$SIS/usr/local/lib/gisquare-os/installa-programmi"
cat > "$SIS/etc/gisquare-os-release" <<EOF
GISQUARE_VERSIONE="$VERSIONE"
GISQUARE_SITO="$SITO"
GISQUARE_REPO_OS="$REPO_OS"
EOF
# Archivio degli aggiornamenti GiSquare: attivo solo se c'è l'indirizzo e la chiave pubblica
if [ -n "$APT_URL" ] && [ -f "$PROGETTO/chiave-aggiornamenti.asc" ]; then
    mkdir -p "$SIS/etc/apt/sources.list.d" "$SIS/etc/apt/apt.conf.d" "$SIS/usr/share/keyrings"
    cp "$PROGETTO/chiave-aggiornamenti.asc" "$SIS/usr/share/keyrings/gisquare-os.asc"
    cat > "$SIS/etc/apt/sources.list.d/gisquare-os.sources" <<EOF
# GiSquare OS - aggiornamenti delle parti GiSquare (firmati con la chiave GiSquare)
Types: deb
URIs: $APT_URL
Suites: trixie
Components: main
Signed-By: /usr/share/keyrings/gisquare-os.asc
EOF
    cat > "$SIS/etc/apt/apt.conf.d/52gisquare-os" <<'EOF'
// GiSquare OS: anche gli aggiornamenti GiSquare si installano da soli
Unattended-Upgrade::Origins-Pattern:: "origin=GiSquare OS";
EOF
    echo "Aggiornamenti GiSquare attivi: $APT_URL"
else
    avviso "Aggiornamenti GiSquare non attivi (servono GISQUARE_APT_URL e chiave-aggiornamenti.asc)"
fi
install -m 755 "$PROGETTO/pacchetto/configura" "$PKG/usr/lib/gisquare-os/configura"
install -m 755 "$PROGETTO/pacchetto/postinst" "$PKG/DEBIAN/postinst"
VERSIONE_PACCHETTO="$VERSIONE.$(date -u +%Y%m%d%H%M)"
sed -e "s|@VERSIONE@|$VERSIONE_PACCHETTO|" -e "s|@SITO@|$SITO|" "$PROGETTO/pacchetto/control" > "$PKG/DEBIAN/control"
dpkg-deb --root-owner-group -Zxz --build "$PKG" "config/packages.chroot/gisquare-os_${VERSIONE_PACCHETTO}_all.deb" >/dev/null
cp "config/packages.chroot/gisquare-os_${VERSIONE_PACCHETTO}_all.deb" "$USCITA/"
echo "Pacchetto: gisquare-os $VERSIONE_PACCHETTO"

mkdir -p config/packages.chroot
# live-build accetta solo nomi del tipo nome_versione_architettura.deb: con un altro nome
# (es. GiSquare-Circuiti-1.1.0-linux-amd64.deb) il pacchetto viene saltato senza errori.
DEB_NOME="$(dpkg-deb -f "$DEB" Package)_$(dpkg-deb -f "$DEB" Version | sed 's/^[0-9]*://')_$(dpkg-deb -f "$DEB" Architecture).deb"
cp "$DEB" "config/packages.chroot/$DEB_NOME"
echo "Pacchetto locale: config/packages.chroot/$DEB_NOME"

# --- 4. Verifica dei pacchetti -------------------------------------------------------
msg "Controllo che tutti i pacchetti esistano in Debian 13"
LISTA=config/package-lists/gisquare.list.chroot
INDISPENSABILI="live-boot live-config xorg xfce4 lightdm firefox-esr calamares"
mancanti=""
while read -r p; do
    case "$p" in ''|'#'*) continue ;; esac
    # "apt-cache show" risponde ok anche per i nomi "virtuali" senza un pacchetto vero
    # (es. hfsprogs in Debian 13): controllo che ci sia una versione installabile.
    # (Niente "| grep -q": con pipefail grep chiude la pipe in anticipo e il controllo fallisce.)
    candidato=$(LC_ALL=C apt-cache policy "$p" 2>/dev/null | sed -n 's/^ *Candidate: *//p' || true)
    case "$candidato" in ''|'(none)') mancanti="$mancanti $p" ;; esac
done < <(cat "$LISTA")
for p in $mancanti; do
    sed -i "s/^$p\$/# MANCANTE: $p/" "$LISTA"
done
if [ -n "$mancanti" ]; then
    avviso "pacchetti non trovati e saltati:$mancanti"
    for p in $INDISPENSABILI; do
        case " $mancanti " in *" $p "*) errore "Manca un pacchetto indispensabile: $p" ;; esac
    done
fi

# --- 5. Configurazione di live-build -------------------------------------------------
msg "Configuro live-build"
AIUTO="$(lb config --help 2>&1 || true)"
supporta() { grep -q -- "$1" <<<"$AIUTO"; }

OPZIONI=(
    --mode debian
    --distribution trixie
    --archive-areas "main non-free-firmware"
    --security true
    --updates true
    --debian-installer none
    --firmware-chroot true
    --firmware-binary true
    --linux-flavours amd64
    --apt-recommends true
    --bootloaders "syslinux,grub-efi"
    --iso-application "GiSquare OS"
    --iso-publisher "GiSquare OS - $SITO"
    --iso-volume "GISQUARE_OS_$VERSIONE"
    --image-name "GiSquare-OS"
    --checksums sha256
    --cache true
    --bootappend-live "boot=live components quiet splash locales=it_IT.UTF-8 keyboard-layouts=it timezone=Europe/Rome username=gisquare user-fullname=GiSquare hostname=gisquare-os persistence persistence-media=removable-usb"
    # "Avvio sicuro": stesse impostazioni (salvataggio, italiano) ma senza driver grafico
    # e con tutte le scritte visibili; niente noapic/nosmp, che bloccano i PC moderni.
    --bootappend-live-failsafe "boot=live components nomodeset locales=it_IT.UTF-8 keyboard-layouts=it timezone=Europe/Rome username=gisquare user-fullname=GiSquare hostname=gisquare-os persistence persistence-media=removable-usb"
)
if supporta '--architecture '; then OPZIONI+=(--architecture amd64); else OPZIONI+=(--architectures amd64); fi
supporta '--uefi-secure-boot' && OPZIONI+=(--uefi-secure-boot enable)
supporta '--memtest' && OPZIONI+=(--memtest memtest86+)
# zstd: si decomprime molto più in fretta di xz sui processori vecchi
supporta '--chroot-squashfs-compression-type' && OPZIONI+=(--chroot-squashfs-compression-type zstd)
if $SORGENTI; then
    OPZIONI+=(--source true --source-images iso)
fi
lb config "${OPZIONI[@]}"

# --- 6. Grafica e testi del menu di avvio della chiavetta ---------------------------
# live-build (Debian 13) usa un solo sfondo, config/bootloaders/splash.svg, e lo converte
# da solo in 640x480 (menu BIOS/ISOLINUX) e 800x600 (menu UEFI/GRUB).
# Le voci del menu GRUB vengono generate da live-build al posto di @LINUX_LIVE@ in
# grub.cfg: le sostituiamo con voci nostre in italiano.
# Nota: con "set -euo pipefail" un grep che non trova nulla fermerebbe lo script,
# quindi qui si usano solo sed (che non fallisce se non trova il testo).
msg "Applico la grafica GiSquare al menu di avvio"
B=config/bootloaders
mkdir -p "$B"
for d in /usr/share/live/build/bootloaders/*; do
    if [ -d "$d" ]; then cp -a "$d" "$B/"; fi
done
[ -f "$B/grub-pc/grub.cfg" ] && [ -f "$B/syslinux_common/live.cfg.in" ] \
    || errore "File del menu di avvio di live-build non trovati in /usr/share/live/build/bootloaders"
cp "$PROGETTO/grafica/avvio/splash.svg.in" "$B/splash.svg"
rm -f "$B/grub-legacy/splash.xpm.gz"

# Menu BIOS (ISOLINUX): niente lettere accentate, il menu BIOS non le mostra bene
sed -i -e 's/^\(\s*menu label\) ^Live system (@FLAVOUR@)$/\1 ^Avvia GiSquare OS/' \
       -e 's/^\(\s*menu label\) Live system (@FLAVOUR@ fail-safe mode)$/\1 Avvia GiSquare OS (avvio sicuro)/' \
       "$B/syslinux_common/live.cfg.in"
sed -i -e 's/^menu title Boot menu.*/menu title Scegli come avviare/' \
       -e 's/menu label ^Utilities/menu label ^Strumenti/' \
       -e 's/menu title Utilities/menu title Strumenti/' \
       -e 's/menu label ^Back\.\./menu label ^Indietro/' \
       "$B/syslinux_common/menu.cfg"
sed -i -e 's/^menu tabmsg .*/menu tabmsg INVIO: avvia     TAB: modifica la voce/' \
       -e 's/^menu color sel\s.*/menu color sel\t\t* #ff172941 #ff6dc8ff none/' \
       -e 's/^menu color hotsel\s.*/menu color hotsel\t1;7;37;40 #ff172941 #ff6dc8ff none/' \
       -e 's/^menu color title\s.*/menu color title\t* #ffc5d1e2 */' \
       "$B/syslinux_common/stdmenu.cfg"
echo 'menu autoboot Avvio automatico tra # second{o,i}...' >> "$B/syslinux_common/stdmenu.cfg"
# Avvio automatico dopo 5 secondi (ISOLINUX conta in decimi di secondo)
sed -i -e 's/^timeout .*/timeout 50/' "$B/isolinux/isolinux.cfg"

# Menu UEFI (GRUB)
cat > "$B/voci-gisquare.cfg.tmp" <<'VOCI'
menuentry "Avvia GiSquare OS" --hotkey=l {
	linux	@KERNEL_LIVE@ @APPEND_LIVE@
	initrd	@INITRD_LIVE@
}
menuentry "Avvia GiSquare OS (avvio sicuro)" {
	linux	@KERNEL_LIVE@ @LB_BOOTAPPEND_LIVE_FAILSAFE@
	initrd	@INITRD_LIVE@
}
VOCI
sed -i -e "/^@LINUX_LIVE@\$/r $B/voci-gisquare.cfg.tmp" -e '/^@LINUX_LIVE@$/d' \
       -e "s/'Utilities\.\.\.'/'Strumenti...'/" \
       -e 's/"UEFI Firmware Settings"/"Impostazioni del firmware UEFI"/' \
       -e 's/"Verify integrity of the boot medium"/"Verifica l'"'"'integrità della chiavetta"/' \
       "$B/grub-pc/grub.cfg"
rm -f "$B/voci-gisquare.cfg.tmp"
# Avvio automatico dopo 5 secondi
sed -i -e 's/^set default=0$/set default=0\nset timeout=5/' "$B/grub-pc/config.cfg"
# Niente bip all'avvio (live-build mette di serie un suono nel menu GRUB)
sed -i -e '/^insmod play$/d' -e '/^play /d' "$B/grub-pc/config.cfg"
sed -i -e 's/^title-text:.*/title-text: ""/' \
       -e 's/selected_item_color\s*=.*/selected_item_color = "#6dc8ff"/' \
       -e 's/item_color = "#a8a8a8"/item_color = "#c5d1e2"/' \
       -e 's/fg_color = "#ffffff"/fg_color = "#6dc8ff"/' \
       -e 's/bg_color = "#a8a8a8"/bg_color = "#263a55"/' \
       -e 's/text_color = "#000000"/text_color = "#f5f8fc"/' \
       -e 's/text = "@TIMEOUT_NOTIFICATION_LONG@"/text = "Avvio automatico tra %d secondi"/' \
       -e 's/text = "@KEYMAP_SHORT@"/text = "Invio: avvia     e: modifica     c: riga di comando"/' \
       "$B/grub-pc/live-theme/theme.txt"

echo "Menu BIOS:"; sed -n 's/^\s*menu label /  - /p' "$B/syslinux_common/live.cfg.in"
echo "Menu UEFI:"; sed -n 's/^menuentry "\([^"]*\)".*/  - \1/p' "$B/grub-pc/grub.cfg"

# --- 7. Build -------------------------------------------------------------------------
LOG="$USCITA/build-$(date +%Y%m%d-%H%M).log"
msg "Costruisco la ISO: ci vogliono 30-60 minuti (registro: $LOG)"
if ! lb build 2>&1 | tee "$LOG"; then
    errore "La build non è riuscita. Guarda le ultime righe del registro: $LOG"
fi

# Controllo finale: GiSquare Circuiti deve essere davvero installato nel sistema
if ! awk '/^Package: gisquare-circuiti$/{p=1} p&&/^Status:/{print; exit}' chroot/var/lib/dpkg/status 2>/dev/null \
        | grep -q "install ok installed"; then
    errore "GiSquare Circuiti non risulta installato nella ISO. Guarda il registro: $LOG"
fi
echo "GiSquare Circuiti installato nella ISO: ok"

ISO="$(find "$LAVORO" -maxdepth 1 -name '*.iso' ! -name '*source*' -print | head -1)"
[ -n "$ISO" ] || errore "ISO non trovata. Guarda il registro: $LOG"
NOME="GiSquare-OS-$VERSIONE-amd64.iso"
mv -f "$ISO" "$USCITA/$NOME"
(cd "$USCITA" && sha256sum "$NOME" > "$NOME.sha256")
if $SORGENTI; then
    find "$LAVORO" -maxdepth 1 -name '*source*' -exec mv -f {} "$USCITA/" \;
fi

msg "Fatto!"
echo "ISO:       $USCITA/$NOME  ($(du -h "$USCITA/$NOME" | cut -f1))"
echo "Controllo: $USCITA/$NOME.sha256"
echo
echo "Per scriverla su una chiavetta da Windows usa Rufus (vedi LEGGIMI.md)."
