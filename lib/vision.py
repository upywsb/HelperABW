import cv2
import numpy as np

# Filtry kolorów
FILTRY = {
    "MOB":   (np.array([0, 70, 50]),  np.array([10, 255, 255])),
    "CP":    (np.array([15, 100, 100]), np.array([35, 255, 255])),  # Szerszy żółty
    "HP":    (np.array([0, 100, 80]),   np.array([10, 255, 255])),  # Mocniejsza czerwień
    "MP":    (np.array([100, 120, 100]), np.array([130, 255, 255])) # Głęboki niebieski
}

def analizuj_procent(wycinek, filtr_hsv):
    try:
        if wycinek is None or wycinek.size == 0:
            return 0.0

        # Konwersja na HSV i nałożenie filtra koloru
        hsv = cv2.cvtColor(wycinek, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, filtr_hsv[0], filtr_hsv[1])

        # Pobieramy wymiary wycinka
        h_h, w_w = mask.shape

        # Sprawdzamy 3 linie poziome (góra, środek, dół), aby ominąć szum
        # np. 20%, 50% i 80% wysokości paska
        linie_y = [int(h_h * 0.2), int(h_h * 0.5), int(h_h * 0.8)]

        # Łączymy wyniki z tych linii:
        # jeśli w danej kolumnie (X) na którejkolwiek linii jest kolor -> True
        aktywne_punkty = np.any(mask[linie_y, :] == 255, axis=0)

        # Szukamy indeksów wszystkich kolumn, w których znaleziono kolor
        kolorowe_indeksy = np.where(aktywne_punkty == True)[0]

        if len(kolorowe_indeksy) == 0:
            return 0.0

        # Kluczowa zmiana: bierzemy ostatni (najbardziej wysunięty na prawo)
        # indeks kolumny z kolorem. To nasza krawędź paska.
        ostatni_piksel = kolorowe_indeksy[-1]

        # Obliczamy procent względem całkowitej szerokości (w_w)
        procent = (ostatni_piksel / (w_w - 1)) * 100

        return round(float(procent), 1)
    except Exception as e:
        # Opcjonalnie: print(f"Błąd analizy: {e}")
        return 0.0