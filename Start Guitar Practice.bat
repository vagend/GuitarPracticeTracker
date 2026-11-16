@echo off
rem Starts the Guitar Practice app on Windows and opens it in your browser.
rem Only needed the first time (to install it) and after you get a new version.
rem Once installed, the app opens from the Start menu without this running.
title Guitar Practice
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-windows.ps1"
if errorlevel 1 pause
