import cv2
import random
import numpy as np
import mss
import keyboard
import pydirectinput
import time
import json
import os
import threading
import tkinter as tk  # Naprawione: tkinter zamiast tk
from tkinter import ttk, filedialog
from datetime import datetime

# Importy z Twoich nowych bibliotek w folderze lib
from lib.calibration import uruchom_kalibracje
from lib.vision import analizuj_procent, FILTRY
from lib.mob_logic import analizuj_hp_moba_smart
from lib.tab_main import MainTab
from lib.tab_combat import CombatTab
from lib.tab_heal import HealTab

class ProBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ABW-helper v17.2")
        self.root.geometry("420x380")

        self.config_file = 'config_roi.json'
        self.running = False
        self.roi_mob = None
        self.roi_self = None
        self.cooldowns = {}

        # Zmienne współdzielone między zakładkami
        self.val_mob = tk.StringVar(value="MOB: 0%")
        self.val_hp = tk.StringVar(value="HP: 0%")
        self.val_mp = tk.StringVar(value="MP: 0%")
        self.val_cp = tk.StringVar(value="CP: 0%")

        # Inicjalizacja UI (Zakładki pobierane z plików w lib/)
        self.tabs = ttk.Notebook(self.root)
        self.tab1 = MainTab(self.tabs, self)
        self.tab2 = CombatTab(self.tabs, self)
        self.tab3 = HealTab(self.tabs, self)

        self.tabs.add(self.tab1, text='ROI & Profile')
        self.tabs.add(self.tab2, text='Walka (Skille)')
        self.tabs.add(self.tab3, text='Auto-Leczenie')
        self.tabs.pack(expand=1, fill="both")

        # Wczytanie ostatniego profilu
        self.load_profile(auto=True)

        # Uruchomienie nasłuchiwania klawiszy w tle
        threading.Thread(target=self.keyboard_listener, daemon=True).start()

    def write_log(self, msg):
        if hasattr(self, 'log_area'):
            now = datetime.now().strftime("%H:%M:%S")
            def append():
                self.log_area.configure(state='normal')
                self.log_area.insert(tk.END, f"[{now}] {msg}\n")
                self.log_area.see(tk.END)
                self.log_area.configure(state='disabled')
            self.root.after(0, append)

    def save_profile(self, auto=False):
        data = {
            "roi_m": self.roi_mob,
            "roi_s": self.roi_self,
            "target": self.target_key.get(),
            "hp_lim": self.hp_limit.get(),
            "hp_key": self.hp_pot_key.get(),
            "mp_lim": self.mp_limit.get(),
            "mp_key": self.mp_pot_key.get(),
            "skills": [{"act": a["active"].get(), "min": a["min"].get(), "max": a["max"].get(), "k": a["key"].get(), "r": a["reuse"].get()} for a in self.actions]
        }
        if auto:
            with open(self.config_file, 'w') as f: json.dump(data, f)
        else:
            path = filedialog.asksaveasfilename(defaultextension=".json")
            if path:
                with open(path, 'w') as f: json.dump(data, f)
                self.write_log("Profil zapisany ręcznie.")

    def load_profile(self, auto=False):
        path = self.config_file if auto else filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    d = json.load(f)
                    self.roi_mob = d.get("roi_m")
                    self.roi_self = d.get("roi_s")
                    self.hp_limit.delete(0, tk.END); self.hp_limit.insert(0, d.get("hp_lim", "60"))
                    self.hp_pot_key.delete(0, tk.END); self.hp_pot_key.insert(0, d.get("hp_key", "F1"))
                    self.mp_limit.delete(0, tk.END); self.mp_limit.insert(0, d.get("mp_lim", "30"))
                    self.mp_pot_key.delete(0, tk.END); self.mp_pot_key.insert(0, d.get("mp_key", "F2"))
                    self.target_key.delete(0, tk.END); self.target_key.insert(0, d.get("target", "2"))
                    for i, s in enumerate(d.get("skills", [])):
                        if i < len(self.actions):
                            self.actions[i]["active"].set(s["act"])
                            self.actions[i]["min"].delete(0, tk.END); self.actions[i]["min"].insert(0, s["min"])
                            self.actions[i]["max"].delete(0, tk.END); self.actions[i]["max"].insert(0, s["max"])
                            self.actions[i]["key"].delete(0, tk.END); self.actions[i]["key"].insert(0, s["k"])
                            self.actions[i]["reuse"].delete(0, tk.END); self.actions[i]["reuse"].insert(0, s["r"])
                self.write_log("Profil wczytany pomyślnie.")
            except: pass

    def trigger_calibration(self):
        with mss.mss() as sct:
            img = cv2.cvtColor(np.array(sct.grab(sct.monitors[0])), cv2.COLOR_BGRA2BGR)
            self.roi_mob = uruchom_kalibracje(img, "MOB (HP)", self.roi_mob)
            self.roi_self = uruchom_kalibracje(img, "TWOJE STATY", self.roi_self)
            self.save_profile(auto=True)
            self.write_log("Kalibracja ROI zakończona.")

    def keyboard_listener(self):
        self.write_log("Skróty aktywne: Alt+K (Kalibracja), Alt+R (Start/Stop)")
        while True:
            # Sprawdzanie Alt + K (Kalibracja)
            if keyboard.is_pressed('alt+k'):
                self.root.after(0, self.trigger_calibration)
                time.sleep(1) # Delay, żeby nie wywołać kilka razy na raz

            # Sprawdzanie Alt + R (Start/Stop)
            if keyboard.is_pressed('alt+r'):
                self.root.after(0, self.toggle_bot)
                time.sleep(1) # Delay, żeby nie wywołać kilka razy na raz

            time.sleep(0.1)

    def toggle_bot(self):
        self.running = not self.running
        self.btn_toggle.config(text="STOP (alt+r)" if self.running else "START (at+r)")
        if self.running:
            threading.Thread(target=self.bot_engine, daemon=True).start()
            self.write_log("BOT START")
        else:
            self.write_log("BOT STOP")

    def bot_engine(self):
        last_t = 0
        self.cooldowns = {}
        with mss.mss() as sct:
            while self.running:
                if not self.roi_mob or not self.roi_self: continue
                try:
                    # 1. Przechwytywanie obrazu
                    f_m = cv2.cvtColor(np.array(sct.grab(self.roi_mob)), cv2.COLOR_BGRA2BGR)
                    f_s = cv2.cvtColor(np.array(sct.grab(self.roi_self)), cv2.COLOR_BGRA2BGR)
                    h3 = f_s.shape[0] // 3
                    # --- DEBUG: Zapisywanie wycinków do plików ---
                    # Wycinamy fragmenty
                    f_cp = f_s[2 : h3-2, :]
                    f_hp = f_s[h3+2 : 2*h3-2, :]
                    f_mp = f_s[2*h3+2 : -2, :]
                    # Możesz to zakomentować, gdy już wszystko ustawisz
                    cv2.imwrite("debug_cp.png", f_cp)
                    cv2.imwrite("debug_hp.png", f_hp)
                    cv2.imwrite("debug_mp.png", f_mp)
                    # ---------------------------------------------
                    # 2. Analiza (Zawsze aktywna - Live Monitoring)
                    # Dodajemy marginesy, żeby odciąć czarne ramki pasków
                    v_m = analizuj_hp_moba_smart(f_m, FILTRY["MOB"])

                    # [0:h3] to CP - odcinamy 2px z góry i dołu
                    v_c = analizuj_procent(f_s[2 : h3-2, :], FILTRY["CP"])

                    # [h3:2*h3] to HP - odcinamy 2px od granic wycinka
                    v_h = analizuj_procent(f_s[h3+2 : 2*h3-2, :], FILTRY["HP"])

                    # [2*h3:] to MP - odcinamy 2px z góry wycinka
                    v_mp = analizuj_procent(f_s[2*h3+2 : -2, :], FILTRY["MP"])

                    # Aktualizacja UI
                    self.val_mob.set(f"MOB: {v_m:.0f}%")
                    self.val_hp.set(f"HP: {v_h:.0f}%")
                    self.val_mp.set(f"MP: {v_mp:.0f}%")
                    self.val_cp.set(f"CP: {v_c:.0f}%")

                    now = time.time()

                    # 3. Logika Leczenia (Tylko jeśli zaznaczone)
                    if self.use_hp_pot.get() and v_h < float(self.hp_limit.get()):
                        # Losowe opóźnienie PRZED kliknięciem (reakcja)
                        time.sleep(random.uniform(0.02, 0.3))
                        pydirectinput.press(self.hp_pot_key.get())
                        self.write_log(f"KLIK: {self.hp_pot_key.get()} (Leczenie)")

                    if self.use_mp_pot.get() and v_mp < float(self.mp_limit.get()):
                        time.sleep(random.uniform(0.02, 0.3))
                        pydirectinput.press(self.mp_pot_key.get())
                        self.write_log(f"KLIK: {self.mp_pot_key.get()} (Mana)")

                    # 4. Logika Walki
                    # Sprawdzamy, czy w ogóle mamy jakieś aktywne skille w zakładce Combat
                    aktywne_skille = [a for a in self.actions if a["active"].get()]
                    if aktywne_skille:
                        if v_m < 1.0:
                            if now - last_t > 8.0:
                                # Nawet przy targetowaniu warto dodać mały random
                                time.sleep(random.uniform(0.02, 0.1))
                                pydirectinput.press(self.target_key.get())
                                last_t = now
                        else:
                            for i, a in enumerate(self.actions):
                                if not a["active"].get(): continue
                                if int(a["min"].get()) <= v_m <= int(a["max"].get()):
                                    if now - self.cooldowns.get(i, 0) > float(a["reuse"].get()):
                                        # Losowe opóźnienie przed użyciem skilla
                                        time.sleep(random.uniform(0.02, 0.3))
                                        pydirectinput.press(a["key"].get())
                                        self.write_log(f"KLIK: {a['key'].get()} (Skill)")
                                        self.cooldowns[i] = now
                                        break

                except Exception as e:
                    print(f"Błąd silnika: {e}")

                time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProBotApp(root)
    root.mainloop()