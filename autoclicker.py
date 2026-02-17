import sys
import time
import random
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from pynput import mouse, keyboard


# Global Vars
DEBUG = False

class MouseRecorder:
    def __init__(self, app):
        self.App = app
        self.events = []
        self.recording = False
        self.listener = None
        self.record_moves = self.App.moves_var.get();
        self.record_clicks = self.App.clicks_var.get()
        self.paused = False
        self.stop_playback = False

    def on_move(self, x, y):
        if self.recording and self.record_moves:
            self.events.append(("move", time.time(), (x, y)))

    def on_click(self, x, y, button, pressed):
        if self.recording and self.record_clicks:
            log("click registered")
            self.events.append(("click", time.time(), (x, y, button.name, pressed)))

    def start_recording(self):
        log("recording started")
        self.events = []
        self.recording = True
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )
        self.listener.start()

    def stop_recording(self):
        log("recording stopped")
        self.recording = False
        if self.listener:
            self.listener.stop()

    def pause(self):
        log("paused")
        self.paused = True

    def resume(self):
        log("resumed")
        self.paused = False

    def stop(self):
        log("playback stopped")
        self.stop_playback = True

    def playback(self, update_status_callback=None):
        log("Starting playback")

        if not self.events:
            if update_status_callback:
                update_status_callback("No events to play")
            return

        controller = mouse.Controller()
        prev_time = self.events[0][1]

        for event in self.events:
            log(f"doing event: {event}")

            etype, timestamp, data = event
            delay = timestamp - prev_time
            time.sleep(max(0, delay + random.uniform(-0.01, 0.01)))
            #time.sleep(delay)

           # PAUSE
            while self.paused:
                if(self.stop_playback):
                    return
                time.sleep(0.1)

            if(self.stop_playback):
                log("Got stop playback in playback loop")
                return

            if etype == "move":
                x, y = data
                controller.position = (x, y)

            elif etype == "click":
                x, y, button_name, pressed = data
                log(f"doing click at: {x}, {y}")
                controller.position = (x, y)
                btn = getattr(mouse.Button, button_name)
                if pressed:
                    controller.press(btn)
                else:
                    controller.release(btn)

            prev_time = timestamp

        if update_status_callback:
            log("playback finished")
            update_status_callback("Playback finished")

    def save_to_file(self, path):
        with open(path, "w") as f:
            json.dump(self.events, f, indent=2)
            log("Saved to file")

    def load_from_file(self, path):
        with open(path, "r") as f:
            self.events = json.load(f)
            log("loaded from file")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Circuitree Labs Autoclicker")

        # Checkbox Default Values
        self.moves_var = tk.BooleanVar(value=False)
        self.clicks_var = tk.BooleanVar(value=True)
        self.loop_var = tk.BooleanVar(value=False)


        self.recorder = MouseRecorder(self)
        # ---------------- UI ELEMENTS ----------------
        self.status_label = tk.Label(root, text="Idle", fg="purple")
        self.status_label.pack(pady=5)


        # Main layout setup
        self.left_frame = ttk.Frame(root, style="TFrame")
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)


        self.right_frame = ttk.Frame(root, style="TFrame")
        self.right_frame.pack(side="right", fill="y", padx=10, pady=10)

        # Recording Panel (left side)
        ttk.Label(self.left_frame, text="Recording", style="TLabel").pack(pady=5)
        #self.label_record(self.left_frame, text="Recording", bg=BG_DARK, fg=FG_LIGHT).pack(pady=5)

        self.record_btn = ttk.Button(self.left_frame, text="Record", style="Accent.TButton", command=self.start_record)
        self.record_btn.pack(pady=5)

        self.stop_btn = ttk.Button(self.left_frame, text="Stop", style="Accent.TButton", command=self.stop_record)
        self.stop_btn.pack(pady=5)

        # Playback Panel (right side)

        ttk.Label(self.left_frame, text="Playback", style="TLabel").pack(pady=5)


        self.play_btn = ttk.Button(self.right_frame, text="Playback", style="Accent.TButton", command=self.start_playback)
        self.play_btn.pack(pady=5)

        self.pause_btn = ttk.Button(self.right_frame, text="Play/Pause Playback", style="Accent.TButton", command=self.playpause_playback)
        self.pause_btn.pack(pady=5)

        self.stopplay_btn = ttk.Button(self.right_frame, text="Stop Playback", style="Accent.TButton", command=self.stop_playback)
        self.stopplay_btn.pack(pady=5)


        # Checkboxes
        tk.Checkbutton(self.left_frame, text="Record Mouse Movement", variable=self.moves_var,
                       command=self.update_record_options).pack()
        tk.Checkbutton(self.left_frame, text="Record Mouse Clicks", variable=self.clicks_var,
                       command=self.update_record_options).pack()
        tk.Checkbutton(self.right_frame, text="Loop Playback", variable=self.loop_var,
                       command=self.update_record_options).pack()

        # Event listbox
        self.event_list = tk.Listbox(root, width=60, height=12)
        self.event_list.pack(pady=5)

        self.save_btn = ttk.Button(root, text="Record", style="Accent.TButton", command=self.save_recording)
        # Save/Load
        self.save_btn = ttk.Button(self.left_frame, text="Save Recording", style="Accent.TButton", command=self.save_recording)
        self.save_btn.pack(pady=5)

        self.load_btn = ttk.Button(self.left_frame, text="Load Recording", style="Accent.TButton", command=self.load_recording)
        self.load_btn.pack(pady=5)

        # Quit button
        self.quit_btn = ttk.Button(root, text="Quit", style="Accent.TButton", command=root.destroy)
        self.quit_btn.pack(pady=5)

        # ---------------- HOTKEY SETTINGS ----------------
        tk.Label(self.left_frame, text="Recording Hotkeys:").pack(pady=5)
        tk.Label(self.right_frame, text="Playback Hotkeys:").pack(pady=5)

        self.record_hotkey = tk.StringVar(value="<ctrl>+<alt>+r")
        self.stop_hotkey = tk.StringVar(value="<ctrl>+<alt>+s")
        self.play_hotkey = tk.StringVar(value="<ctrl>+p")
        self.playpause_hotkey = tk.StringVar(value="<ctrl>+<space>")
        self.stopplayback_hotkey = tk.StringVar(value="<ctrl>+s")

        tk.Label(self.left_frame, text="StartRecording Hotkey").pack(pady=3)
        tk.Entry(self.left_frame, textvariable=self.record_hotkey).pack(pady=3)

        tk.Label(self.left_frame, text="Stop Recording Hotkey").pack(pady=3)
        tk.Entry(self.left_frame, textvariable=self.stop_hotkey).pack(pady=3)

        tk.Label(self.right_frame, text="Start Playback Hotkey").pack(pady=3)
        tk.Entry(self.right_frame, textvariable=self.play_hotkey).pack(pady=3)

        tk.Label(self.right_frame, text="Pause/Resume Playback Hotkey").pack(pady=3)
        tk.Entry(self.right_frame, textvariable=self.playpause_hotkey).pack(pady=3)

        tk.Label(self.right_frame, text="Stop Playback Hotkey").pack(pady=3)
        tk.Entry(self.right_frame, textvariable=self.stopplayback_hotkey).pack(pady=3)

        self.apply_hotkeys_btn = ttk.Button(root, text="Apply Hotkeys", style="Accent.TButton", command=self.apply_hotkeys)
        self.apply_hotkeys_btn.pack(pady=5)

        # Start hotkeys immediately
        self.hotkey_listener = None
        self.apply_hotkeys()

    # ---------------- LOGIC ----------------
    def update_record_options(self):
        self.recorder.record_moves = self.moves_var.get()
        self.recorder.record_clicks = self.clicks_var.get()
        log("update record")

    def start_record(self):
        self.status_label.config(text="Recording...", fg="red")
        self.event_list.delete(0, tk.END)
        self.recorder.start_recording()
        log("start recording")

    def stop_record(self):
        self.recorder.stop_recording()
        self.status_label.config(text="Stopped", fg="orange")
        self.refresh_event_list()
        log("stop recording")


    def start_playback(self):
        self.record_btn.config(state="disabled")
        self.play_btn.config(state="disabled")
        self.status_label.config(text="Playing...", fg="blue")
        log("Start playback")

        if(self.loop_var.get()):
            loops = 99
        else:
            loops = 1

        def playbackloop():
            self.recorder.stop_playback = False
            self.recorder.paused = False
            for _ in range(loops):
                self.recorder.playback(self.update_status)
                if (self.recorder.stop_playback):
                    break

            self.record_btn.config(state="normal")
            self.play_btn.config(state="normal")


        threading.Thread(target=playbackloop, daemon=True).start() 

    def stop_playback(self):
        log('Stop Playback Clicked')
        self.recorder.stop()
        self.recorder.paused = False
        self.status_label.config(text="Stopped Playback", fg="red")
        self.record_btn.config(state="normal")
        self.play_btn.config(state="normal")

    def playpause_playback(self):
        log('Play/Pause')
        if(self.recorder.paused):
            self.recorder.resume()
            self.status_label.config(text="Resumed Playback", fg="blue")
            log("Resumed Playback")
        else:
            self.recorder.pause()
            self.status_label.config(text="Paused Playback", fg="yellow")
            log("Paused Playback")

    def update_status(self, text):
        self.status_label.config(text=text, fg="green")
        log("update status")

    def refresh_event_list(self):
        self.event_list.delete(0, tk.END)
        for e in self.recorder.events:
            self.event_list.insert(tk.END, str(e))

    def save_recording(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if path:
            self.recorder.save_to_file(path)
            messagebox.showinfo("Saved", "Recording saved successfully")
            log("Saved recording")

    def load_recording(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")]
        )
        if path:
            self.recorder.load_from_file(path)
            self.refresh_event_list()
            messagebox.showinfo("Loaded", "Recording loaded successfully")
            log("Loaded recording")

    # ---------------- HOTKEY HANDLING ----------------
    def apply_hotkeys(self):
        # Stop previous listener
        try:
            if self.hotkey_listener:
                self.hotkey_listener.stop()
        except:
            pass

        # Build new hotkey map
        hotkeys = {
            self.record_hotkey.get(): self.start_record,
            self.stop_hotkey.get(): self.stop_record,
            self.play_hotkey.get(): self.start_playback,
            self.playpause_hotkey.get(): self.playpause_playback,
            self.stopplayback_hotkey.get(): self.stop_playback
        }

        # Create listener
        try:
            # Create global hotkey listener; invalid strings will raise
            self.hotkey_listener = keyboard.GlobalHotKeys(hotkeys)
            self.hotkey_listener.start()
            self.status_label.config(text="Hotkeys applied", fg="green")
        except Exception as e:
            # If user enters an invalid hotkey string, show error instead of crashing
            self.status_label.config(text=f"Hotkey error: {e}", fg="red")

def log(string):
    if (DEBUG):
        print(string)

def Banner(text):
   print("=" * 20)
   print(text)
   print("=" * 20)
   return

if __name__ == "__main__":
    Banner("Starting Program...")

    if (len(sys.argv) > 1):
            for _ in sys.argv:
                if(_.lower() == "debug" or _ == "-d"):
                    DEBUG = True
                    print("Debug enabled")

    root = tk.Tk()
    style = ttk.Style()

    BG_DARK = "#1a1b26"
    FG_LIGHT = "#c0caf5"
    ACCENT_BLUE = "#41a6ff"

    root.configure(bg=BG_DARK) # Set window background color
    # Configure specific styles
    style.configure("TFrame", background=BG_DARK)
    style.configure("TLabel", background=BG_DARK, foreground=FG_LIGHT)
    style.configure("TButton", background=ACCENT_BLUE, foreground=BG_DARK, borderwidth=0, padding=5)
    style.map("TButton", background=[('active', ACCENT_BLUE)])


    style.configure(
        "Accent.TButton",
        background="#41a6ff",
        foreground="#1a1b26",
        padding=6,
        borderwidth=0,
        focusthickness=3,
        focuscolor="none"
    )

    style.map(
        "Accent.TButton",
        background=[("active", "#5ab0ff")],
        foreground=[("active", "#000000")]
    )

    app = App(root)
    root.mainloop()
