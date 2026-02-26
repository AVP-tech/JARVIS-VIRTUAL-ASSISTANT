# JARVIS - Voice Assistant (Python)

A Windows-focused voice assistant built in Python with wake-word detection (`jarvis`), Hinglish command support, local TTS output, and practical desktop automation.

# Why this project stands out

- Wake-word flow: listens continuously for `jarvis`, then captures command input.
- Hinglish-first UX: supports casual bilingual commands (Hindi + English).
- Fast local voice replies: uses `pyttsx3` first, with Google TTS fallback.
- Desktop productivity actions: open apps/folders, browse websites, and search instantly.
- System controls: restart/shutdown/update-and-restart/update-and-shutdown with safety timer.
- Typing automation: can type dictated text in active windows.
- Music shortcuts: song name to direct YouTube links through a custom music library.

# Tech Stack

- Language: Python
- Speech recognition: `SpeechRecognition` (Google recognizer backend)
- Text-to-speech: `pyttsx3` (primary), `gTTS` + `playsound` (fallback)
- Automation: `pyautogui`
- System/web ops: `os`, `subprocess`, `webbrowser`, `threading`

# Project Structure

```text
JARVIS/
├─ main.py
├─ musicLibrary.py
├─ client.py
├─ main.spec
├─ client.spec
├─ voice_cache/
├─ build/
├─ start_jarvis.bat
└─ README.md
```

# Features in detail

- Wake word + command pipeline: detects `jarvis`, then listens for command.
- Smart command handling: app launch, folder open, websites, search, typing, and music play.
- Hinglish search: `search maar <query> <site> pe` for YouTube/LinkedIn/Amazon/Flipkart/X/Instagram/Wikipedia/Maps.
- System power commands: `restart`, `shutdown`, `update and restart`, `update and shutdown` (with 10-second delay).

# Setup (Windows)

1. Clone and move into project.

```powershell
git clone <your-repo-url>
cd JARVIS
```

2. Create and activate virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies.

```powershell
pip install SpeechRecognition pyttsx3 pyautogui gTTS playsound pyaudio
```

4. Run the assistant.

```powershell
python main.py
```

# Auto-Start on Windows (run JARVIS at boot)

**Method 1: Startup Folder (easy)**

1. Keep `start_jarvis.bat` in the project root (already included).
2. Press `Win + R`, type `shell:startup`, and press Enter.
3. Copy `start_jarvis.bat` (or its shortcut) into that Startup folder.
4. Restart Windows and verify JARVIS starts automatically after login.

**Method 2: Task Scheduler (recommended/reliable)**

1. Open Task Scheduler and click Create Task.
2. In General: set name `JARVIS Auto Start`, select Run only when user is logged on.
3. In Triggers: create a new trigger `At log on` for your user.
4. In Actions: Start a program.
   - Program/script: `C:\Users\NIKITA PANDEY\Desktop\JARVIS\.venv\Scripts\python.exe`
   - Add arguments: `main.py`
   - Start in: `C:\Users\NIKITA PANDEY\Desktop\JARVIS`
5. Click OK, then right-click task and Run once for testing.

# Build Executable (optional)

```powershell
pyinstaller main.spec
pyinstaller client.spec
```

Artifacts will appear under `build/` and `dist/`.

# Customization

- Add songs in `musicLibrary.py`.
- Update app paths in `APP_PATHS` inside `main.py`.
- Set `USE_FAST_TTS = True/False` in `main.py` based on voice preference.

# Advanced upgrades roadmap

- Offline voice pipeline: add Porcupine/Vosk/Whisper for low-latency private recognition.
- Better intent engine: switch from keyword matching to intent classification + slot extraction.
- Memory layer: store user preferences, last commands, and reminder history.
- Plugin architecture: split commands into modular plugins (`apps`, `system`, `web`, `music`).
- Safety and observability: add action confirmations, logs, crash recovery, and health checks.

# Recruiter notes

This project demonstrates practical voice-AI UX design, event-driven command routing, OS-level automation, and production-minded features like fallback TTS and safe shutdown timers.

# Known limitations

- Optimized for Windows paths/commands.
- Recognition quality depends on mic and network.
- Some app paths can differ system to system.

# License

For portfolio/demo use. Add MIT license if you plan public distribution.
