import cv2
import numpy as np

_calib_x, _calib_y = -1, -1

def _click_event(event, x, y, flags, param):
    global _calib_x, _calib_y
    if event == cv2.EVENT_LBUTTONDOWN:
        skala = param
        _calib_x, _calib_y = int(x / skala), int(y / skala)

def uruchom_kalibracje(ekran, nazwa, last_roi=None):
    global _calib_x, _calib_y
    nazwa_okna = f'KALIBRACJA {nazwa}'
    
    cv2.namedWindow(nazwa_okna, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(nazwa_okna, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    
    screen_h, screen_w = ekran.shape[:2]
    target_w = 1400 
    skala = target_w / screen_w
    target_h = int(screen_h * skala)
    
    cv2.resizeWindow(nazwa_okna, target_w, target_h)
    cv2.setMouseCallback(nazwa_okna, _click_event, param=skala)
    
    x, y = (last_roi["left"], last_roi["top"]) if last_roi else (screen_w // 2, screen_h // 2)
    w, h = (last_roi["width"], last_roi["height"]) if last_roi else (180, 60)
    _calib_x, _calib_y = -1, -1
    success = False

    while True:
        if cv2.getWindowProperty(nazwa_okna, cv2.WND_PROP_VISIBLE) < 1:
            break

        p = ekran.copy()
        
        if _calib_x != -1:
            x, y = _calib_x - (w // 2), _calib_y - (h // 2)
            _calib_x, _calib_y = -1, -1

        # Zabezpieczenie zakresu
        x, y = max(0, x), max(0, y)
        x, y = min(screen_w - w, x), min(screen_h - h, y)

        # --- SEKCJA ZOOM x8 ---
        roi_img = ekran[int(y):int(y+h), int(x):int(x+w)]
        
        if roi_img.size > 0:
            zoom_factor = 8 # Twoja zmiana na x8
            # Obliczamy rozmiar lupy, ale ograniczamy go do max 40% wysokości ekranu
            max_zoom_h = int(screen_h * 0.4)
            actual_zoom_h = h * zoom_factor
            actual_zoom_w = w * zoom_factor
            
            if actual_zoom_h > max_zoom_h:
                # Jeśli x8 to za dużo dla ekranu, bot lekko skoryguje podgląd
                reduction = max_zoom_h / actual_zoom_h
                actual_zoom_h = int(actual_zoom_h * reduction)
                actual_zoom_w = int(actual_zoom_w * reduction)

            zoom_view = cv2.resize(roi_img, (actual_zoom_w, actual_zoom_h), interpolation=cv2.INTER_NEAREST)
            zoom_view = cv2.copyMakeBorder(zoom_view, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(0, 255, 0))
            
            zh, zw = zoom_view.shape[:2]
            # Wstawiamy w prawy dolny róg
            p[screen_h-zh-10 : screen_h-10, screen_w-zw-10 : screen_w-10] = zoom_view
            cv2.putText(p, f"LUPA x8", (screen_w-zw-10, screen_h-zh-20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Rysowanie głównej ramki i linii podziału
        cv2.rectangle(p, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)
        if "STATY" in nazwa:
            h3 = h // 3
            cv2.line(p, (int(x), int(y+h3)), (int(x+w), int(y+h3)), (255,255,255), 1)
            cv2.line(p, (int(x), int(y+2*h3)), (int(x+w), int(y+2*h3)), (255,255,255), 1)
            
        cv2.imshow(nazwa_okna, cv2.resize(p, (target_w, target_h)))
        
        key = cv2.waitKey(1) & 0xFF
        if key == 13: # ENTER
            success = True
            break
        elif key == 27: # ESC
            break
        elif key == ord('w'): y -= 1
        elif key == ord('s'): y += 1
        elif key == ord('a'): x -= 1
        elif key == ord('d'): x += 1
        elif key == ord('e'): w += 2
        elif key == ord('q'): w = max(4, w - 2)
        elif key == ord('r'): h += 2
        elif key == ord('f'): h = max(4, h - 2)
        
    cv2.destroyWindow(nazwa_okna)
    
    if success:
        return {"top": int(y), "left": int(x), "width": int(w), "height": int(h)}
    return last_roi