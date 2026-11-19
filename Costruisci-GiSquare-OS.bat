@echo off
rem ==========================================================================
rem  GiSquare OS - costruzione della ISO su Windows (tramite WSL + Debian)
rem  Fai doppio clic su questo file. La prima volta leggi LEGGIMI.md.
rem ==========================================================================
chcp 65001 >nul
title GiSquare OS - costruzione della ISO
set WSL_UTF8=1

echo.
echo   GiSquare OS - costruzione della ISO
echo   -----------------------------------
echo.

wsl --status >nul 2>&1
if errorlevel 1 (
    echo  WSL non e' installato.
    echo  Apri "Windows PowerShell" come amministratore e scrivi:
    echo.
    echo      wsl --install -d Debian
    echo.
    echo  Poi riavvia il PC, apri "Debian" dal menu Start, crea utente e password,
    echo  e fai di nuovo doppio clic su questo file.
    echo.
    pause
    exit /b 1
)

wsl -l -q | findstr /i /c:"Debian" >nul
if errorlevel 1 (
    echo  In WSL manca Debian. Apri "Windows PowerShell" e scrivi:
    echo.
    echo      wsl --install -d Debian
    echo.
    echo  Poi apri "Debian" dal menu Start, crea utente e password,
    echo  e fai di nuovo doppio clic su questo file.
    echo.
    pause
    exit /b 1
)

echo  Avvio la costruzione dentro Debian (WSL). Non chiudere questa finestra.
echo  La prima volta ci vogliono 30-60 minuti.
echo.
wsl -d Debian -u root --cd "%~dp0." -- bash ./costruisci.sh %*
if errorlevel 1 (
    echo.
    echo  La costruzione NON e' riuscita: leggi i messaggi qui sopra
    echo  e il registro nella cartella "output".
) else (
    echo.
    echo  La ISO e' pronta nella cartella "output".
    explorer "%~dp0output"
)
echo.
pause
