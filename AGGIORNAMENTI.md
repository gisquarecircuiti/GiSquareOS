# Aggiornamenti di GiSquare OS

## Come funzionano

| Cosa | Sistema installato sul PC | Chiavetta |
|---|---|---|
| Programmi e sicurezza di **Debian** | automatici (ogni giorno) | si rifà la chiavetta con la ISO nuova |
| **GiSquare Circuiti** | si aggiorna da solo | si aggiorna da solo |
| **Parti GiSquare OS** (pacchetto `gisquare-os`) | automatici, dall'archivio degli aggiornamenti GiSquare | si rifà la chiavetta con la ISO nuova |
| **Avviso "è uscita una nuova versione"** | solo per le versioni principali (2.0, 3.0…) | per ogni nuova versione |

Le parti GiSquare (grafica, Benvenuto, Installa altri programmi, Salvataggio, guida,
impostazioni) sono il pacchetto **`gisquare-os`**, che `costruisci.sh` crea da
`config/includes.chroot/` e `pacchetto/configura`. A ogni aggiornamento del pacchetto,
`configura` riapplica le personalizzazioni.

L'archivio degli aggiornamenti è un repository APT **firmato**, pubblicato sulle pagine
GitHub del progetto (`https://<account>.github.io/<repository>/apt`). I computer accettano
solo aggiornamenti firmati con la chiave GiSquare.

## Attivarli (una volta sola, sul repository pubblico)

### 1. Crea la chiave di firma

Nella finestra **Debian** (WSL) sul PC:

```
gpg --batch --passphrase '' --quick-gen-key "GiSquare OS (aggiornamenti) <gisquare.circuiti@gmail.com>" ed25519 sign never
gpg --armor --export gisquare.circuiti@gmail.com > chiave-aggiornamenti.asc
gpg --armor --export-secret-keys gisquare.circuiti@gmail.com > CHIAVE-PRIVATA-NON-CONDIVIDERE.asc
```

### 2. Metti la chiave privata nei segreti di GitHub

Repository → **Settings → Secrets and variables → Actions → New repository secret**:
- Nome: `GISQUARE_CHIAVE_FIRMA`
- Valore: tutto il contenuto di `CHIAVE-PRIVATA-NON-CONDIVIDERE.asc` (dalla riga `-----BEGIN` alla riga `-----END`).

Poi **salva una copia del file in un posto sicuro** (per esempio una chiavetta in un cassetto)
e cancellalo dal PC. **Non mandarlo a nessuno e non metterlo nel repository**: chi ha questa
chiave può pubblicare aggiornamenti per tutti i computer con GiSquare OS.

### 3. Metti la chiave pubblica nel repository

Il file `chiave-aggiornamenti.asc` (quello **senza** "PRIVATA") va nella cartella principale
del repository. Non è segreto: serve ai computer per controllare le firme.

### 4. Indirizzo dell'archivio e pagine GitHub

- **Settings → Secrets and variables → Actions → Variables → New repository variable**:
  `GISQUARE_APT_URL` = `https://<account>.github.io/<repository>/apt`
- **Settings → Pages → Build and deployment → Source: GitHub Actions**.

### 5. Pubblica la versione ufficiale

**Actions → Costruisci GiSquare OS → Run workflow**, versione `1.0`, spunta **ufficiale**.
Il workflow crea la release `v1.0` e pubblica l'archivio firmato con il pacchetto `gisquare-os`.

Da qui in poi, per ogni nuova versione (1.1, 1.2…) basta ripetere il punto 5 con il numero
nuovo: i computer installati ricevono il pacchetto aggiornato da soli, le chiavette vedono
l'avviso della nuova versione.

## Se la chiave privata va persa o finisce in mani sbagliate

Crea una chiave nuova (punti 1–3) e pubblica subito una versione nuova: le ISO nuove useranno
la chiave nuova. I computer già installati con la vecchia chiave vanno aggiornati a mano
(o reinstallati): per questo la chiave privata va custodita con cura.
