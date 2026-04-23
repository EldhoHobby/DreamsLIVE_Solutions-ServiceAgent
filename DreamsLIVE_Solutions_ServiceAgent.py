import os
# --- CRITICAL STABILITY FIXES ---
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1" 

import tkinter as tk
import threading
import queue
import pyaudio
import numpy as np
import json
import time

# --- DEFENSIVE IMPORTS ---
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# --- CONFIGURATION ---
MODEL_SIZE = "tiny"    # 'tiny' is the fastest for CPU usage
DEVICE = "cpu"         # Forces CPU to avoid GPU library crashes
COMPUTE_TYPE = "int8" 
LANGUAGE = None        # Set to 'ml' for Malayalam or 'en' for English to go even faster

# --- GLOBAL STATE ---
speech_queue = queue.Queue()
audio_level_queue = queue.Queue()
is_listening = False
is_clap_mode = False
CONFIG = {}
TRIGGERS = {}

# --- CLAP DETECTION SETTINGS ---
CLAP_THRESHOLD = 15000  # Sensitivity (higher = less sensitive)
CLAP_COOLDOWN = 0.5      # Seconds between triggers
last_clap_time = 0

def load_config():
    global CONFIG, TRIGGERS
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                CONFIG = json.load(f)
                TRIGGERS = CONFIG.get("triggers", {})
        else:
            speech_queue.put("SYSTEM: config.json not found.")
    except Exception as e:
        speech_queue.put(f"SYSTEM: Error loading config: {e}")

def handle_trigger(trigger_name, action):
    # Placeholder for actual file opening logic
    speech_queue.put(f"ACTION: Executing '{action}' for '{trigger_name}'")
    # In a real scenario, we'd look for the file in ServiceFiles/
    # For now, we just log it.

def audio_transcription_thread():
    global is_listening
    
    if not WHISPER_AVAILABLE:
        speech_queue.put("ERROR: 'faster-whisper' library not found.")
        speech_queue.put("Please run setup_env.bat to install dependencies.")
        is_listening = False
        return

    try:
        # Load the fastest available model
        speech_queue.put(f"SYSTEM: Loading {MODEL_SIZE} engine...")
        model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
        speech_queue.put(">>> DREAMS-LIVE ONLINE: Listening...")
        
        # Audio Setup
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=2000
        )
    except Exception as e:
        speech_queue.put(f"ERROR: {e}")
        is_listening = False
        return

    audio_buffer = []

    while is_listening:
        try:
            # Read smaller chunks for faster VU response
            data = stream.read(2000, exception_on_overflow=False)
            audio_int16 = np.frombuffer(data, np.int16)
            
            # Update VU Meter
            peak = np.abs(audio_int16).max()
            audio_level_queue.put(min(100, int((peak / 32767) * 100)))

            # CLAP DETECTION
            global last_clap_time
            if is_clap_mode and peak > CLAP_THRESHOLD:
                current_time = time.time()
                if current_time - last_clap_time > CLAP_COOLDOWN:
                    if PYAUTOGUI_AVAILABLE:
                        speech_queue.put("ACTION: CLAP DETECTED! → Next Slide")
                        try:
                            pyautogui.press('right')
                        except Exception as e:
                            speech_queue.put(f"ERROR: Slide change failed: {e}")
                    else:
                        speech_queue.put("ACTION: CLAP DETECTED! (Slide change skipped - pyautogui missing)")
                    last_clap_time = current_time

            # Accumulate audio
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            audio_buffer.extend(audio_float32)

            # SPEED OPTIMIZATION: Process every 0.8 seconds (12800 samples)
            if len(audio_buffer) >= 12800:
                segments, _ = model.transcribe(
                    np.array(audio_buffer), 
                    beam_size=1,       # FASTEST: No extra guessing
                    language=LANGUAGE, 
                    vad_filter=True,   # Ignores floor noise
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
                
                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        speech_queue.put(f"RESULT:{text}")
                        # Keyword Trigger Check
                        text_lower = text.lower()
                        for name, info in TRIGGERS.items():
                            keyword = info.get("keyword", "").lower()
                            if keyword and keyword in text_lower:
                                speech_queue.put(f"SYSTEM: Keyword '{keyword}' detected!")
                                handle_trigger(name, info.get("action", "open"))
                
                # Clear buffer but keep 0.3s overlap to avoid cutting words
                audio_buffer = audio_buffer[-4800:] 

        except Exception as e:
            speech_queue.put(f"SYSTEM ERROR: {e}")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

# --- UI INTERFACE ---
root = tk.Tk()
root.title("DreamsLIVE Solutions - Service Agent")
root.geometry("600x650")
root.configure(bg="#f8f9fa")

# Header
header = tk.Frame(root, bg="#202124", pady=15)
header.pack(fill="x")
tk.Label(header, text="DIAGNOSTIC VOICE INTERFACE", fg="#e8eaed", bg="#202124", font=("Nirmala UI", 12, "bold")).pack()

# VU Meter
vu_canvas = tk.Canvas(root, height=12, bg="#dee2e6", highlightthickness=0)
vu_canvas.pack(fill="x", padx=30, pady=20)
vu_bar = vu_canvas.create_rectangle(0, 0, 0, 12, fill="#1a73e8")

# Log Display
log_box = tk.Text(root, height=18, font=("Nirmala UI", 11), state='disabled', bg="white", relief="flat", padx=15, pady=15)
log_box.pack(fill="both", expand=True, padx=30, pady=10)

def update_ui():
    # VU Meter Animation
    try:
        while True:
            level = audio_level_queue.get_nowait()
            w = vu_canvas.winfo_width()
            vu_canvas.coords(vu_bar, 0, 0, (level / 100) * w, 12)
    except queue.Empty: pass
    
    # Text Updates
    try:
        while True:
            msg = speech_queue.get_nowait()
            log_box.config(state='normal')
            if msg.startswith("RESULT:"):
                log_box.insert(tk.END, f"● {msg.replace('RESULT:', '')}\n")
            elif msg.startswith("ACTION:"):
                log_box.insert(tk.END, f"▶ {msg}\n", "action")
                log_box.tag_config("action", foreground="#1e8e3e", font=("Nirmala UI", 11, "bold"))
            else:
                log_box.insert(tk.END, f"[SYSTEM] {msg}\n")
            log_box.see(tk.END)
            log_box.config(state='disabled')
    except queue.Empty: pass
    root.after(40, update_ui)

def toggle_clap():
    global is_clap_mode

    if not PYAUTOGUI_AVAILABLE and not is_clap_mode:
        speech_queue.put("WARNING: 'pyautogui' not found. Slide control disabled.")
        speech_queue.put("Please run setup_env.bat to install dependencies.")

    is_clap_mode = not is_clap_mode
    if is_clap_mode:
        clap_btn.config(text="CLAP MODE: ON", bg="#1e8e3e")
        speech_queue.put("SYSTEM: Clap Detection Enabled.")
    else:
        clap_btn.config(text="CLAP MODE: OFF", bg="#5f6368")
        speech_queue.put("SYSTEM: Clap Detection Disabled.")

def toggle():
    global is_listening
    if not is_listening:
        load_config()
        is_listening = True
        btn.config(text="STOP SERVICE", bg="#d93025")
        threading.Thread(target=audio_transcription_thread, daemon=True).start()
    else:
        is_listening = False
        btn.config(text="START SERVICE", bg="#1a73e8")

# Controls Frame
controls = tk.Frame(root, bg="#f8f9fa")
controls.pack(fill="x", padx=30, pady=10)

# Main Start Button
btn = tk.Button(controls, text="START SERVICE", bg="#1a73e8", fg="white", font=("Nirmala UI", 10, "bold"),
               command=toggle, pady=12, relief="flat", cursor="hand2")
btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

# Clap Toggle Button
clap_btn = tk.Button(controls, text="CLAP MODE: OFF", bg="#5f6368", fg="white", font=("Nirmala UI", 10, "bold"),
                    command=toggle_clap, pady=12, relief="flat", cursor="hand2")
clap_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

update_ui()
root.mainloop()