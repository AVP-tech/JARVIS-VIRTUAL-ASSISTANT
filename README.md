# JARVIS — Virtual Assistant

> A Hinglish (Hindi + English) AI-powered voice assistant built with Python.

JARVIS listens for a wake word, understands spoken commands in both Hindi and English, and automates everyday desktop tasks — all hands-free.

## ✨ Features

| Category | Capabilities |
|---|---|
| 🎙️ Voice | Wake-word detection · Speech-to-text · Text-to-speech |
| 🖥️ Desktop | Open/close apps · File & folder operations · Screenshot |
| 🌐 Web | Search Google/YouTube · Open websites · Fetch news & weather |
| 🎵 Media | Play music · Volume & playback control |
| 🤖 AI | Answer questions · Small talk · Date & time queries |
| ⚙️ System | Windows auto-start · Battery status · System info |

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Speech:** `SpeechRecognition`, `pyttsx3` / `gTTS`
- **Automation:** `pyautogui`, `os`, `subprocess`
- **AI/NLP:** `wikipedia`, `wolframalpha`, `openai` (optional)

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/AVP-tech/JARVIS-VIRTUAL-ASSISTANT.git
cd JARVIS-VIRTUAL-ASSISTANT

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run JARVIS (check repo for the correct entry-point file)
python main.py
```

> Say **"Hey JARVIS"** to wake it up, then speak your command.

## 📄 License

MIT
