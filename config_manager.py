import cv2
import json
import os

CONFIG_FILE = 'config_roi.json'
mouse_x, mouse_y = -1, -1

def click_event(event, x, y, flags, param):
    global mouse_x, mouse_y
    if event == cv2.EVENT_LBUTTONDOWN:
        skala = param
        mouse_x, mouse_y = int(x / skala), int(y / skala)

def save_config(roi_mob, roi_self):
    with open(CONFIG_FILE, 'w') as f: 
        json.dump({"mob": roi_mob, "self": roi_self}, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f: 
                data = json.load(f)
                return data.get("mob"), data.get("self")
        except: return None, None
    return None, None

def kalibracja_obszaru(ekran, nazwa, last_roi=None):
    global mouse_x, mouse_y
    nazwa_okna = f'KALIBRACJA {nazwa}'
    cv2.namedWindow(nazwa_okna)
    skala = 1600 / ekran.shape[1]
    cv2.setMouseCallback(nazwa_okna, click_event, param=skala)
    x, y = (last_roi["left"], last_roi["top"]) if last_roi else (500, 500)
    w, h = (last_roi["width"], last_roi["height"]) if last_roi else (180, 60)
    mouse_x, mouse_y = -1, -1
    while True:
        p = ekran.copy()
        if mouse_x != -1: x, y, mouse_x, mouse_y = mouse_x, mouse_y, -1, -1
        cv2.rectangle(p, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow(nazwa_okna, cv2.resize(p, (1600, int(ekran.shape[0] * skala))))
        k = cv2.waitKey(1) & 0xFF
        if k == 13: break 
        elif k == ord('w'): y -= 1
        elif k == ord('s'): y += 1
        elif k == ord('a'): x -= 1
        elif k == ord('d'): x += 1
        elif k == ord('e'): w += 2
        elif k == ord('q'): w = max(10, w - 2)
        elif k == ord('r'): h += 2
        elif k == ord('f'): h = max(6, h - 2)
    cv2.destroyWindow(nazwa_okna)
    return {"top": y, "left": x, "width": w, "height": h}