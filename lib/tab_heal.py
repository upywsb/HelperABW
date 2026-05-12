import tkinter as tk
from tkinter import ttk

class HealTab(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.create_widgets()

    def create_widgets(self):
        h_frame = ttk.LabelFrame(self, text=" Ustawienia Przetrwania ")
        h_frame.pack(padx=10, pady=10, fill="x")
        
        # HP
        self.app.use_hp_pot = tk.BooleanVar(value=True)
        tk.Checkbutton(h_frame, text="Użyj gdy HP < ", variable=self.app.use_hp_pot).grid(row=0, column=0, sticky="w")
        self.app.hp_limit = tk.Entry(h_frame, width=5); self.app.hp_limit.insert(0, "60")
        self.app.hp_limit.grid(row=0, column=1)
        tk.Label(h_frame, text="% klawisz:").grid(row=0, column=2)
        self.app.hp_pot_key = tk.Entry(h_frame, width=5); self.app.hp_pot_key.insert(0, "F1")
        self.app.hp_pot_key.grid(row=0, column=3)

        # MP
        self.app.use_mp_pot = tk.BooleanVar(value=True)
        tk.Checkbutton(h_frame, text="Użyj gdy MP < ", variable=self.app.use_mp_pot).grid(row=1, column=0, sticky="w")
        self.app.mp_limit = tk.Entry(h_frame, width=5); self.app.mp_limit.insert(0, "30")
        self.app.mp_limit.grid(row=1, column=1)
        tk.Label(h_frame, text="% klawisz:").grid(row=1, column=2)
        self.app.mp_pot_key = tk.Entry(h_frame, width=5); self.app.mp_pot_key.insert(0, "F2")
        self.app.mp_pot_key.grid(row=1, column=3)