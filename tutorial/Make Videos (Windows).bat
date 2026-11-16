@echo off
rem Windows: sets up a private Python environment next to this file, installs edge-tts into it, and makes the videos.
rem Double-click it. From a command window you can add options, e.g.  "Make Videos (Windows).bat" 05 --rate -5%%
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (py -m venv .venv)
if not exist .venv\Scripts\python.exe (echo Could not create the environment. Install Python 3 from python.org and try again. & pause & exit /b 1)
.venv\Scripts\python.exe -m pip install -q edge-tts
if errorlevel 1 (echo Could not install edge-tts. Is the internet connected? & pause & exit /b 1)
.venv\Scripts\python.exe make_videos.py %*
if not errorlevel 1 start "" finished
pause
