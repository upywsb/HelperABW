import cv2
import numpy as np

# Filtry kolorów
FILTRY = {
    "MOB":   (np.array([0, 70, 50]),  np.array([10, 255, 255])),
    "CP":    (np.array([20, 150, 50]), np.array([30, 255, 255])),
    "HP":    (np.array([0, 130, 50]),  np.array([10, 255, 255])),
    "MP":    (np.array([100, 150, 50]), np.array([130, 255, 255]))
}

def analizuj_procent(wycinek, filtr_hsv):
    """Oblicza procent wypełnienia paska na podstawie koloru."""
    try:
        if wycinek is None or wycinek.size == 0: return 0.0
        hsv = cv2.cvtColor(wycinek, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, filtr_hsv[0], filtr_hsv[1])
        h_h = mask.shape[0]
        # Próbkowanie 5 linii dla stabilności wyniku
        linie_y = np.linspace(int(h_h*0.2), int(h_h*0.8), 5).astype(int)
        wyniki = [mask[l, :] for l in linie_y]
        scalone = np.sum(np.array(wyniki) == 255, axis=0)
        pelne = np.sum(scalone >= 3)
        return np.clip((pelne / mask.shape[1]) * 100, 0, 100)
    except:
        return 0.0