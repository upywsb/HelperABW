import tkinter as tk
from tkinter import ttk, scrolledtext

class MainTab(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.create_widgets()

    def create_widgets(self):
        # Profile & ROI
        p_frame = ttk.LabelFrame(self, text=" Zarządzanie Profilem ")
        p_frame.pack(padx=10, pady=5, fill="x")
        ttk.Button(p_frame, text="Zapisz Profil", command=self.app.save_profile).pack(side="left", padx=5, pady=5)
        ttk.Button(p_frame, text="Wczytaj Profil", command=self.app.load_profile).pack(side="left", padx=5, pady=5)

        ctrl_frame = ttk.LabelFrame(self, text=" Kalibracja i Start ")
        ctrl_frame.pack(padx=10, pady=5, fill="x")
        ttk.Button(ctrl_frame, text="SKALIBRUJ ROI (alt+k)", command=self.app.trigger_calibration).pack(fill="x", pady=2)
        self.app.btn_toggle = ttk.Button(ctrl_frame, text="START BOT (alt+r)", command=self.app.toggle_bot)
        self.app.btn_toggle.pack(fill="x", pady=2)
        # Statystyki
        stat_frame = ttk.LabelFrame(self, text=" Monitoring Live ")
        stat_frame.pack(padx=10, pady=5, fill="x")

        # Główny napis MOB zostaje na górze
        tk.Label(stat_frame, textvariable=self.app.val_mob, font=("Arial", 16, "bold"), fg="red").pack()

        # Nowy kontener na statystyki poziome
        stats_row = tk.Frame(stat_frame)
        stats_row.pack(pady=5)

        # Etykiety CP, HP, MP obok siebie
        tk.Label(stats_row, textvariable=self.app.val_cp, font=("Arial", 11), fg="Goldenrod").pack(side="left", padx=10)
        tk.Label(stats_row, textvariable=self.app.val_hp, font=("Arial", 11), fg="darkred").pack(side="left", padx=10)
        tk.Label(stats_row, textvariable=self.app.val_mp, font=("Arial", 11), fg="blue").pack(side="left", padx=10)
        # # Statystyki
        # stat_frame = ttk.LabelFrame(self, text=" Monitoring Live ")
        # stat_frame.pack(padx=10, pady=5, fill="x")
        # tk.Label(stat_frame, textvariable=self.app.val_mob, font=("Arial", 16, "bold"), fg="red").pack()
        # tk.Label(stat_frame, textvariable=self.app.val_cp, font=("Arial", 11), fg="Goldenrod").pack()
        # tk.Label(stat_frame, textvariable=self.app.val_hp, font=("Arial", 11), fg="darkred").pack()
        # tk.Label(stat_frame, textvariable=self.app.val_mp, font=("Arial", 11), fg="blue").pack()

        # Logi
        log_frame = ttk.LabelFrame(self, text=" Dziennik Działań ")
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.app.log_area = scrolledtext.ScrolledText(log_frame, height=4, font=("Consolas", 8), state='disabled', bg="#f8f8f8")
        self.app.log_area.pack(fill="both", expand=True, padx=5, pady=5)