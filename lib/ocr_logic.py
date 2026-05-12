import cv2
import numpy as np
import os

class DigitRecognizer:
    def __init__(self, templates_path='tample/'):
        self.templates = {}
        # Wczytujemy wzorce cyfr 0-9 oraz znaku /
        for i in range(10):
            path = os.path.join(templates_path, f"{i}.png")
            if os.path.exists(path):
                # Wczytujemy w skali szarości dla szybkości
                self.templates[str(i)] = cv2.imread(path, 0)
        
        sep_path = os.path.join(templates_path, "sep.png") # Znak "/"
        if os.path.exists(sep_path):
            self.templates["/"] = cv2.imread(sep_path, 0)

    def rozpoznaj_tekst(self, wycinek):
        if wycinek is None or wycinek.size == 0: return "0"
        
        # Konwersja do skali szarości i zwiększenie kontrastu
        gray = cv2.cvtColor(wycinek, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        found_digits = []

        # Przeszukujemy wycinek pod kątem każdego wzorca
        for char, temp in self.templates.items():
            res = cv2.matchTemplate(thresh, temp, cv2.TM_CCOEFF_NORMED)
            threshold = 0.85 # Próg dopasowania
            loc = np.where(res >= threshold)

            for pt in zip(*loc[::-1]):
                # pt[0] to pozycja X znaleziona na obrazku
                found_digits.append((pt[0], char))

        # Sortujemy znalezione znaki od lewej do prawej
        found_digits.sort(key=lambda x: x[0])

        # Usuwamy duplikaty blisko siebie (te same cyfry nakładające się)
        final_string = ""
        last_x = -10
        for x, char in found_digits:
            if x > last_x + 3: # Zakładamy, że cyfra ma min. 3px szerokości
                final_string += char
                last_x = x

        return final_string if final_string else "0"

def parsuj_staty(tekst):
    """Zamienia tekst typu '500/1000' na (500, 1000)"""
    try:
        if "/" in tekst:
            obecne, max_val = tekst.split("/")
            return int(obecne), int(max_val)
        return int(tekst), 0
    except:
        return 0, 0