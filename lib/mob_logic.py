import cv2
import numpy as np
FILTRY = {
    "MOB": (np.array([0, 70, 50]), np.array([10, 255, 255]))
}
def analizuj_hp_moba_smart(wycinek, filtr_hsv):
    """
    Zaawansowana analiza HP Moba z mapowaniem skali (74% -> 100%)
    oraz progiem odcięcia (3% -> 0%).
    """
    try:
        if wycinek is None or wycinek.size == 0: return 0.0

        # 1. Obcinamy brzegi o 2 piksele
        wycinek = wycinek[2:-2, 2:-2]

        hsv = cv2.cvtColor(wycinek, cv2.COLOR_BGR2HSV)

        # Maska dla koloru HP (czerwony)
        mask_hp = cv2.inRange(hsv, filtr_hsv[0], filtr_hsv[1])

        # Maska dla napisu (biały/jasny)
        mask_text = cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 60, 255]))

        h, w = mask_hp.shape
        wiersze_hp = []

        for i in range(h):
            ile_tekstu = np.sum(mask_text[i, :] == 255)
            if ile_tekstu < (w * 0.05):
                ile_hp = np.sum(mask_hp[i, :] == 255)
                wiersze_hp.append(ile_hp / w)

        if not wiersze_hp:
            clean_hp = cv2.bitwise_and(mask_hp, mask_hp, mask=cv2.bitwise_not(mask_text))
            raw_percent = (np.sum(clean_hp == 255) / clean_hp.size) * 100
        else:
            raw_percent = (sum(wiersze_hp) / len(wiersze_hp)) * 100

        # --- NOWA LOGIKA SKALOWANIA (MAPOWANIE) ---
        # Twoje dane: 74% to realne 100%, a poniżej 3% to 0%
        MAX_DETECTED = 90.0
        MIN_THRESHOLD = 0.0

        if raw_percent < MIN_THRESHOLD:
            return 0.0

        # Skalowanie: (wartość - dół) / (góra - dół) * 100
        scaled_percent = ((raw_percent - MIN_THRESHOLD) / (MAX_DETECTED - MIN_THRESHOLD)) * 100

        # Zabezpieczenie przed wyjściem poza zakres 0-100
        return float(np.clip(scaled_percent, 0.0, 100.0))

    except Exception as e:
        print(f"Błąd analizy HP Moba: {e}")
        return 0.0