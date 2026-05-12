import cv2
import numpy as np

# Filtr ustawiony precyzyjnie pod Twoje HP ze zdjęcia
#FILTR_HP = (np.array([0, 130, 50]), np.array([10, 255, 255]))

def analizuj_hp(wycinek):
    try:
        if wycinek is None or wycinek.size == 0: return 0.0

        # Korekta ramki (odcinamy po 2px z boków)
        wycinek = wycinek[:, 2:-2]
        h, w = wycinek.shape[:2]

        hsv = cv2.cvtColor(wycinek, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, FILTR_HP[0], FILTR_HP[1])

        # Mocniejsze 'szpachlowanie' dla HP (napisy bywają większe)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8))

        kolumny = np.sum(mask == 255, axis=0)
        licznik = np.count_nonzero(kolumny > (h * 0.15))

        procent = (licznik / w) * 100
        # HP często ma cienie na końcu - snap do 100% od 96%
        return 100.0 if procent > 96.0 else round(float(procent), 1)
    except:
        return 0.0