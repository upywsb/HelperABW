import tkinter as tk
from tkinter import ttk

class CombatTab(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.create_widgets()

    def create_widgets(self):
        header_f = ttk.Frame(self); header_f.pack(fill="x", padx=10, pady=5)
        tk.Label(header_f, text="Używaj |  Max % | Min % | Klawisz | Reuse(s)", font=("Arial", 8, "bold")).pack()

        self.app.actions = []
        for i in range(6):
            f = ttk.Frame(self); f.pack(fill="x", padx=10, pady=2)
            active = tk.BooleanVar()
            tk.Checkbutton(f, variable=active).pack(side="left")
            max_h = tk.Entry(f, width=5); max_h.insert(0, "100"); max_h.pack(side="left", padx=2)

            tk.Label(f, text="-").pack(side="left")
            min_h = tk.Entry(f, width=5); min_h.insert(0, "0"); min_h.pack(side="left", padx=2)

            tk.Label(f, text="% HP, Key:").pack(side="left", padx=2)
            key = tk.Entry(f, width=5); key.insert(0, str(i+1)); key.pack(side="left", padx=2)

            tk.Label(f, text="Reuse:").pack(side="left", padx=2)
            reuse = tk.Entry(f, width=5); reuse.insert(0, "2"); reuse.pack(side="left", padx=2)

            self.app.actions.append({
                "active": active,
                "max": max_h,
                "min": min_h,
                "key": key,
                "reuse": reuse
            })

        target_f = ttk.LabelFrame(self, text=" Ustawienia Targetu ")
        target_f.pack(fill="x", padx=10, pady=10)
        tk.Label(target_f, text="Klawisz Next Target:").pack(side="left", padx=5)

        self.app.target_key = tk.Entry(target_f, width=5)
        self.app.target_key.insert(0, "2")
        self.app.target_key.pack(side="left", padx=5)