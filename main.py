import os
import time
import subprocess
import webbrowser
import threading
import hashlib

import speech_recognition as sr
import pyttsx3
import pyautogui

# Optional fallback (Google TTS) – only used if fast TTS fails / disabled
from gtts import gTTS
import playsound

# Music library (direct links)
import musicLibrary

pyautogui.FAILSAFE = True
recognizer = sr.Recognizer()

# ---------------- CONFIG ----------------
LANG_RECOG = "en-IN"          # Hinglish recognition
CACHE_DIR = "voice_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

USE_FAST_TTS = True  # True = fast male (pyttsx3), False = Google TTS fallback (slower)

# ---------------- APP PATHS (Windows common) ----------------
PROGRAM_FILES = os.environ.get("ProgramFiles", r"C:\Program Files")
PROGRAM_FILES_X86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

APP_PATHS = {
    # Built‑ins / PATH commands
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "vscode": "code",  # requires VS Code command in PATH

    # Browsers
    "chrome": rf"{PROGRAM_FILES}\Google\Chrome\Application\chrome.exe",
    "edge":   rf"{PROGRAM_FILES}\Microsoft\Edge\Application\msedge.exe",

    # Office (adjust if your edition differs)
    "excel":  rf"{PROGRAM_FILES}\Microsoft Office\root\Office16\EXCEL.EXE",
    "word":   rf"{PROGRAM_FILES}\Microsoft Office\root\Office16\WINWORD.EXE",
    "powerpoint": rf"{PROGRAM_FILES}\Microsoft Office\root\Office16\POWERPNT.EXE",

    # Spotify (Store installs may differ)
    "spotify": rf"{PROGRAM_FILES}\Spotify\Spotify.exe",
}

def _path_exists_or_none(p):
    try:
        return p if (p and os.path.exists(p)) else None
    except Exception:
        return None

# ---------------- FAST LOCAL TTS (male) ----------------
engine_fast = None
def _init_fast_tts():
    global engine_fast
    try:
        engine_fast = pyttsx3.init()
        pick = None
        for v in engine_fast.getProperty("voices"):
            name = (getattr(v, "name", "") or "").lower()
            if "ravi" in name or "hemant" in name or "heera" in name:
                pick = v.id; break
            if ("en" in name and "india" in name) or "male" in name:
                pick = v.id
        if pick:
            engine_fast.setProperty("voice", pick)
        rate = engine_fast.getProperty("rate") or 180
        engine_fast.setProperty("rate", min(210, rate + 30))
        engine_fast.setProperty("volume", 1.0)
    except Exception:
        engine_fast = None
_init_fast_tts()

# ---------------- SPEAK (threaded + interruptible) ----------------
speak_thread = None
speak_lock = threading.Lock()

def _tts_cache_path(text: str, lang: str) -> str:
    h = hashlib.md5((lang + "|" + text).encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.mp3")

def _speak_worker(text: str, lang: str = "hi"):
    # 1) Fast local TTS (pyttsx3) – interruptible
    if USE_FAST_TTS and engine_fast is not None:
        try:
            engine_fast.stop()           # flush any previous utterance
            engine_fast.say(text)
            engine_fast.runAndWait()
            return
        except Exception:
            pass
    # 2) Fallback Google TTS (blocking; cannot hard-stop mid-play)
    try:
        mp3 = _tts_cache_path(text, lang)
        if not os.path.exists(mp3):
            gTTS(text=text, lang=lang).save(mp3)
        playsound.playsound(mp3)
    except Exception as e:
        print("❌ TTS error:", e)

def speak(text: str, lang: str = "hi"):
    if not text:
        return
    print(f"🗣️ {text}")
    global speak_thread
    with speak_lock:
        if USE_FAST_TTS and engine_fast is not None:
            try: engine_fast.stop()
            except Exception: pass
        speak_thread = threading.Thread(target=_speak_worker, args=(text, lang), daemon=True)
        speak_thread.start()

def stop_speaking():
    """Cut current speech immediately (pyttsx3 mode)."""
    if USE_FAST_TTS and engine_fast is not None:
        try: engine_fast.stop()
        except Exception: pass

# ---------------- HELPERS ----------------
def say_ready(): speak("Ji boliye?")
def say_didnt_get(): speak("Mujhe koi command nahi mili.")
def say_unknown(): speak("Sorry, ye command mujhe samajh nahi aayi.")
def say_ok(): speak("Theek hai.")

# ---------------- SYSTEM CONTROL (safe 10s) ----------------
def system_shutdown():
    speak("Boss, shutdown 10 second me hoga. Agar kuch save karna hai to kar lo.")
    os.system("shutdown /s /t 10")

def system_restart():
    speak("Boss, restart 10 second me hoga. Agar kuch save karna hai to kar lo.")
    os.system("shutdown /r /t 10")

def system_update_and_restart():
    speak("Boss, update and restart 10 second me hoga.")
    try:
        subprocess.Popen("UsoClient StartScan", shell=True)
        subprocess.Popen("UsoClient StartDownload", shell=True)
        subprocess.Popen("UsoClient StartInstall", shell=True)
    except Exception:
        pass
    os.system("shutdown /r /t 10")

def system_update_and_shutdown():
    speak("Boss, update and shutdown 10 second me hoga.")
    try:
        subprocess.Popen("UsoClient StartScan", shell=True)
        subprocess.Popen("UsoClient StartDownload", shell=True)
        subprocess.Popen("UsoClient StartInstall", shell=True)
    except Exception:
        pass
    os.system("shutdown /s /t 10")

# ---------------- APP OPEN ----------------
def open_app(app_key: str):
    target = APP_PATHS.get(app_key)
    # allow PATH commands like "notepad" / "calc"
    if target and ("\\" not in target and "/" not in target) and " " not in target:
        speak(f"{app_key} khol raha hoon.")
        os.system(target)
        return

    # full path case: validate or try 32-bit path alternative
    if target and not os.path.exists(target):
        alt = target.replace(PROGRAM_FILES, PROGRAM_FILES_X86) if PROGRAM_FILES in target else None
        target = _path_exists_or_none(alt)

    if target and os.path.exists(target):
        speak(f"{app_key} khol raha hoon.")
        try:
            os.startfile(target)
        except Exception as e:
            speak("Open nahi ho paya.")
            print("App open error:", e)
    else:
        speak("Is app ka sahi path nahi mila. Baad me mapping update kar denge.")

# ---------------- COMMAND PROCESSOR ----------------
def processCommand(c):
    low = (c or "").lower().strip()

    # Stop/Cancel (cut speech + exit command)
    if any(k in low for k in ["stop", "cancel", "bas", "ruk jao", "ruko"]):
        stop_speaking()
        say_ok()
        return

    # Casual talks
    if "hello" in low or "hi jarvis" in low:
        speak("Hello Boss! Kaise ho?"); return
    if "kaise ho" in low or "how are you" in low:
        speak("Main bilkul mast hoon, aap kaise ho, Boss?"); return
    if "kya chal raha hai" in low or "what's up" in low:
        speak("Bas aapke saath hi hoon, ready for command!"); return
    if "thank you" in low or "shukriya" in low or "thanks" in low:
        speak("Always welcome Boss!"); return
    if "i love you" in low or "love you jarvis" in low:
        speak("Main bhi aapko bahut pyaar karta hoon Boss, lekin thoda professional rehna padega!"); return

    # --- Play music (library first; fallback to YouTube) ---
    if low.startswith("play "):
        song = low.replace("play ", "").strip()
        link = None
        try:
            link = (
                musicLibrary.music.get(song)
                or musicLibrary.music.get(song.lower())
                or musicLibrary.music.get(song.title())
            )
        except Exception:
            link = None

        if link:
            speak(f"{song} play kar raha hoon.")
            webbrowser.open(link)
        else:
            speak(f"{song} list me nahi mila, YouTube pe search kar raha hoon.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}")
        return

    # System control
    if "update and restart" in low:
        system_update_and_restart(); return
    if "update and shutdown" in low:
        system_update_and_shutdown(); return
    if "restart" in low:
        system_restart(); return
    if "shutdown" in low or "shut down" in low:
        system_shutdown(); return

    # Open folders
    home = os.path.expanduser("~")
    if "open desktop" in low:
        os.startfile(os.path.join(home,"Desktop")); speak("Desktop khol raha hoon."); return
    if "open downloads" in low:
        os.startfile(os.path.join(home,"Downloads")); speak("Downloads khol raha hoon."); return
    if "open documents" in low:
        os.startfile(os.path.join(home,"Documents")); speak("Documents khol raha hoon."); return
    if "open pictures" in low:
        os.startfile(os.path.join(home,"Pictures")); speak("Pictures khol raha hoon."); return
    if "open videos" in low:
        os.startfile(os.path.join(home,"Videos")); speak("Videos khol raha hoon."); return
    if "open home" in low or "open home screen" in low:
        os.startfile(home); speak("Home folder khol raha hoon."); return

    # Open apps
    if low.startswith("open "):
        app = low.split("open ",1)[1].strip()
        if app == "vs code": app = "vscode"
        open_app(app); return

    # Quick websites
    if "open google" in low or "google kholo" in low:
        webbrowser.open("https://google.com"); speak("Google khol raha hoon."); return
    if "open youtube" in low or "youtube kholo" in low:
        webbrowser.open("https://youtube.com"); speak("YouTube khol raha hoon."); return
    if "open linkedin" in low or "linkedin kholo" in low:
        webbrowser.open("https://linkedin.com"); speak("LinkedIn khol raha hoon."); return
    if "open gmail" in low or "gmail kholo" in low:
        webbrowser.open("https://mail.google.com"); speak("Gmail khol raha hoon."); return
    if "open whatsapp" in low or "whatsapp kholo" in low:
        webbrowser.open("https://web.whatsapp.com"); speak("WhatsApp Web khol raha hoon."); return

    # --- Hinglish: "search maar ..." → direct URLs ---
    # Supported: google (default), youtube, linkedin, amazon, flipkart, twitter/x, instagram, wikipedia, maps
    if "search maar" in low:
        site = "google"
        for key in ["youtube", "linkedin", "amazon", "flipkart", "twitter", "x ", "instagram", "wikipedia", "wiki", "maps", "map"]:
            if key in low:
                site = key
                break

        parts = low.split("search maar", 1)
        query = parts[1].strip() if len(parts) > 1 else ""

        # remove site hints from query (Hinglish)
        for hint in [
            "youtube pe", "on youtube",
            "linkedin pe", "on linkedin",
            "amazon pe", "on amazon",
            "flipkart pe", "on flipkart",
            "twitter pe", "on twitter",
            "x pe", "on x",
            "instagram pe", "on instagram",
            "wikipedia pe", "on wikipedia", "wiki pe", "on wiki",
            "maps pe", "on maps", "map pe", "on map",
            "google pe", "on google"
        ]:
            query = query.replace(hint, "")
        query = query.strip()

        if not query:
            speak("Batao kya search karna hai."); return

        # Build direct URLs
        q_plus = query.replace(" ", "+")
        q_pct  = query.replace(" ", "%20")

        if site == "youtube":
            speak(f"{query} ke liye YouTube pe search kar raha hoon.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={q_plus}"); return
        if site == "linkedin":
            speak(f"{query} ke liye LinkedIn pe search kar raha hoon.")
            webbrowser.open(f"https://www.linkedin.com/search/results/all/?keywords={q_pct}"); return
        if site == "amazon":
            speak(f"{query} ke liye Amazon pe search kar raha hoon.")
            webbrowser.open(f"https://www.amazon.in/s?k={q_plus}"); return
        if site == "flipkart":
            speak(f"{query} ke liye Flipkart pe search kar raha hoon.")
            webbrowser.open(f"https://www.flipkart.com/search?q={q_plus}"); return
        if site == "twitter" or site.startswith("x "):
            speak(f"{query} ke liye Twitter/X pe search kar raha hoon.")
            webbrowser.open(f"https://x.com/search?q={q_pct}&src=typed_query"); return
        if site == "instagram":
            speak(f"{query} ke liye Instagram pe search kar raha hoon.")
            webbrowser.open(f"https://www.instagram.com/explore/search/keyword/?q={q_pct}"); return
        if site in ["wikipedia", "wiki"]:
            speak(f"{query} ke liye Wikipedia pe search kar raha hoon.")
            webbrowser.open(f"https://en.wikipedia.org/w/index.php?search={q_plus}"); return
        if site in ["maps", "map"]:
            speak(f"{query} ke liye Maps pe search kar raha hoon.")
            webbrowser.open(f"https://www.google.com/maps/search/{q_plus}"); return

        # default google
        speak(f"{query} ke liye Google pe search kar raha hoon.")
        webbrowser.open(f"https://www.google.com/search?q={q_plus}")
        return

    # Generic search → Google
    if low.startswith("search "):
        query = low.split("search ",1)[1].strip()
        if query:
            speak(f"{query} ke liye search kar raha hoon.")
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ','+')}")
        else:
            speak("Batao kya search karna hai.")
        return

    # Type in active window
    if low.startswith("type "):
        text = low.split("type ",1)[1].strip()
        if text:
            speak(f"{text} type kar raha hoon.")
            try:
                pyautogui.typewrite(text, interval=0.02)
            except pyautogui.FailSafeException:
                speak("Theek hai, ruk gaya.")
        else:
            speak("Batao kya type karna hai.")
        return

    # Fallback
    say_unknown()

# ---------------- MAIN LOOP ----------------
if __name__=="__main__":
    speak("Jarvis start ho raha hai...")
    while True:
        try:
            with sr.Microphone() as source:
                print("🎤 Wake word sun raha hoon...")
                recognizer.adjust_for_ambient_noise(source,duration=0.5)
                audio=recognizer.listen(source,timeout=5,phrase_time_limit=3)
                try:
                    word=recognizer.recognize_google(audio,language=LANG_RECOG).lower()
                except:
                    word=""

                if "jarvis" in word:
                    print("🟢 Wake word detected")
                    say_ready()

                    with sr.Microphone() as source:
                        print("🎤 Command sun raha hoon...")
                        recognizer.adjust_for_ambient_noise(source,duration=0.3)
                        audio=recognizer.listen(source,timeout=7,phrase_time_limit=5)
                        try:
                            command=recognizer.recognize_google(audio,language=LANG_RECOG).lower()
                        except:
                            command=""
                        if command:
                            print(f"📥 Command: {command}")
                            processCommand(command)
                        else:
                            say_didnt_get()

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except KeyboardInterrupt:
            speak("Bye! Main band ho raha hoon."); break
        except Exception as e:
            print(f"❌ Error: {e}")