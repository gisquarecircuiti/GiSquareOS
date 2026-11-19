# Licenze di GiSquare OS

*Promemoria tecnico, non è un parere legale.*

## Cosa c'è dentro la ISO

| Componente | Licenza | Note |
|---|---|---|
| Debian 13 (sezione `main`) | libere (GPL, LGPL, MIT, BSD, MPL…) | ridistribuibili; tutto ciò che è in `main` rispetta le linee guida Debian sul software libero |
| Firmware (sezione `non-free-firmware`) | proprietarie ma **ridistribuibili** | servono per Wi-Fi e schede video dei PC; Debian li include nelle sue immagini ufficiali dalla versione 12 |
| Script, configurazione e grafica di GiSquare OS | **GPL-3.0** (file `LICENSE`) | sono opera tua |
| GiSquare Circuiti | la tua licenza d'uso (`LICENZA-D-USO.md`) | programma gratuito ma non libero |

## Obblighi da rispettare

1. **Sorgenti (GPL):** chi distribuisce la ISO deve rendere disponibili i sorgenti dei programmi GPL inclusi.
   La soluzione più semplice: costruisci anche l'archivio dei sorgenti con `costruisci.sh --sorgenti` e pubblicalo accanto alla ISO, nello stesso posto.
2. **Marchio Debian:** si può scrivere "basato su Debian", ma non usare il logo Debian né far sembrare GiSquare OS un prodotto ufficiale Debian. La guida interna e il menu di avvio lo dicono già.
3. **Firefox:** è incluso il pacchetto `firefox-esr` di Debian senza modifiche, cosa permessa dalle regole sul marchio Mozilla.

## GiSquare Circuiti dentro la ISO

**Decisione attuale: la licenza d'uso di GiSquare Circuiti resta invariata.** Il punto 3 vieta a
chiunque di ridistribuire il programma fuori dal canale ufficiale:
- tu, come autore, pubblichi la ISO sul canale ufficiale (GitHub e sito GiSquare): va bene;
- chi la scarica, formalmente, non potrebbe passarla ad altri. Per questo la pagina web e il
  LEGGIMI invitano a **scaricarla sempre dalla pagina ufficiale**, senza dire che si può
  ridistribuire.

Se in futuro vorrai permetterlo, basta aggiungere alla licenza d'uso una frase come:
> *È consentito copiare e distribuire gratuitamente l'immagine di sistema "GiSquare OS" pubblicata dal Licenziante, senza modificarla, anche se contiene il Programma.*

ricordandoti di aumentare `eulaVersion`.

## Sorgenti GPL

La ISO contiene molti programmi GPL presi da Debian. Il modo più semplice per rispettare
l'obbligo dei sorgenti è pubblicare, accanto a ogni release ufficiale, l'archivio dei sorgenti
creato da `costruisci.sh --sorgenti`. È molto grande (diversi GB): se non entra nelle release
di GitHub va messo su un altro spazio (per esempio SourceForge) con il link nella pagina della
release. I sorgenti di tutti i pacchetti sono comunque disponibili anche su
`snapshot.debian.org`, ma da soli non bastano a coprire l'obbligo di chi distribuisce la ISO.

## Verificare il nome

Come già annotato per GiSquare Circuiti, prima della diffusione pubblica conviene verificare su TMview/EUIPO e UIBM che "GiSquare OS" sia libero.
