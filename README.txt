GUITAR PRACTICE - practice log, timer, metronome, tuner and fretboard trainer
=============================================================================
Works on Mac and Windows. Keep this folder where it is once you've installed the app.
New installs start with a few example exercises and an empty practice log. Edit them,
add your own (Exercises > + Add exercise), and archive or delete the examples you don't use.

FIRST TIME - MAC
1. Double-click "Start Guitar Practice.command".
   If macOS says it can't be opened: right-click it > Open > Open (only needed once).
   A Terminal window opens and the app opens in Chrome (or Edge / your default browser).
2. Install it:
   - Chrome or Edge: click the install icon at the right end of the address bar,
     or the "Install app" button in the app's header.
   - Safari: File > Add to Dock.
3. Open "Guitar Practice" from the Dock or Launchpad from now on.
   You can close the Terminal window - the installed app keeps working without it.

FIRST TIME - WINDOWS
1. Double-click "Start Guitar Practice.bat".
   If Windows SmartScreen warns about it: click "More info" > "Run anyway".
   A black window opens and the app opens in your default browser.
2. Install it from Edge or Chrome: click the install icon at the right end of the
   address bar (or "..." menu > Apps > Install), or the "Install app" button in the header.
3. Open "Guitar Practice" from the Start menu from now on.
   You can close the black window - the installed app keeps working without it.

UPDATING (both)
Download the newest Guitar-Practice.zip from the Releases page on GitHub
(https://github.com/vagend/GuitarPracticeTracker/releases/latest) and copy its files
over the ones in your Guitar Practice folder. Run the Start Guitar Practice file once,
open the app, and click "Reload" when it says a new version is ready. Your practice log
is kept. The version number is shown next to the app name; Settings > What's new lists
the changes.

YOUR DATA
- Your practice log is stored inside the app on each computer. A Mac and a Windows PC
  each keep their own copy.
- Settings > Export backup saves a copy you can keep anywhere; Import backup restores it
  (also how you move your log to another computer). Export CSV gives a spreadsheet copy.
- Your own metronome sounds are kept on that computer only and aren't in backups.
- Always open it the same way (the installed app, or http://localhost:8642). Opening
  index.html directly as a file uses separate, empty storage.

FRETBOARD TRAINER
The trainer has its own "Fretboard" tab at the top and keeps its own time: while it is
running, its minutes and score go into one "Fretboard Trainer" log entry for the day.
The entry is saved when you stop or leave the Fretboard tab, and added to if you come
back later that day. Microphone features work because the app runs from localhost.

TUNER AND AUDIO INPUT
The Tuner tab listens while it is open. Pick guitar or bass, the number of strings and the
tuning under "Tuning". Your audio interface or microphone, channel, input boost, noise gate
and A4 reference are set once in Settings > Audio input (with a Test input level meter);
the tuner and the fretboard trainer both use them.

TEMPO LADDER
In the metronome, "Tempo ladder" builds speed gradually. It steps the metronome from 70% up to
110% and back down to 90%, where 110% is the exercise's ladder max (set it in the exercise
details or Edit exercise; empty means goal + 10%). Set the exercise's length in measures (Length
in the exercise details) and how many times to repeat it at each tempo; both are saved with the
exercise. Get-ready clicks
(beats only, none/1/2/4 measures) can play before each new tempo and between repeats. The
button also starts and stops the practice timer. Pausing the timer (or stopping the metronome)
pauses the ladder; Resume picks up at the same tempo and repeat after a get-ready measure. While
it runs, Previous tempo / Next tempo skip around, and Stay at this tempo keeps repeating the
current tempo until you press Move on. When it finishes it keeps playing at 90%
until you press End ladder.
