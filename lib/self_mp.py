import cv2
import numpy as np

# Filtr ustawiony pod niebieski kolor many
#FILTR_MP = (np.array([100, 150, 50]), np.array([130, 255, 255]))

def analizuj_mp(wycinek):
    try:
        if wycinek is None or wycinek.size == 0: return 0.0

        # Przy manie odcinamy tylko 1px, ramki bywają subtelniejsze
        wycinek = wycinek[:, 1:-1]
        h, w = wycinek.shape[:2]

        hsv = cv2.cvtColor(wycinek, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, FILTR_MP[0], FILTR_MP[1])

        # Mana jest zazwyczaj czystsza - mniejszy kernel morfologiczny
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((2,2), np.uint8))

        kolumny = np.sum(mask == 255, axis=0)
        # Mana bywa cieńsza - próg 10% wysokości wystarczy
        licznik = np.count_nonzero(kolumny > (h * 0.10))

        procent = (licznik / w) * 100
        # Mana szybciej dobija do 100%
        return 100.0 if procent > 97.5 else round(float(procent), 1)
    except:
        return 0.0