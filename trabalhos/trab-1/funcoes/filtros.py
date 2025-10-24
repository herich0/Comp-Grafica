import cv2
import numpy as np

def filtro_media_manual(img, ksize=3):
    h, w = img.shape[:2]
    channels = img.shape[2] if len(img.shape) == 3 else 1
    
    output = np.zeros(img.shape, dtype=img.dtype)
    pad = ksize // 2
    
    padded_img = np.pad(img, [(pad, pad), (pad, pad), (0, 0)] if channels == 3 else [(pad, pad), (pad, pad)], mode='edge')
    
    for y in range(h):
        for x in range(w):
            if channels == 3:
                for c in range(channels):
                    neighborhood = padded_img[y:y+ksize, x:x+ksize, c]
                    output[y, x, c] = np.mean(neighborhood)
            else:
                neighborhood = padded_img[y:y+ksize, x:x+ksize]
                output[y, x] = np.mean(neighborhood)
                
    return output.astype(np.uint8)


def filtro_mediana_manual(img, ksize=3):
    h, w = img.shape[:2]
    channels = img.shape[2] if len(img.shape) == 3 else 1
    
    output = np.zeros(img.shape, dtype=img.dtype)
    pad = ksize // 2
    
    padded_img = np.pad(img, [(pad, pad), (pad, pad), (0, 0)] if channels == 3 else [(pad, pad), (pad, pad)], mode='edge')
    
    for y in range(h):
        for x in range(w):
            if channels == 3:
                for c in range(channels):
                    neighborhood = padded_img[y:y+ksize, x:x+ksize, c]
                    output[y, x, c] = np.median(neighborhood)
            else:
                neighborhood = padded_img[y:y+ksize, x:x+ksize]
                output[y, x] = np.median(neighborhood)
                
    return output.astype(np.uint8)

def filtro_media_cv(img, ksize=3):
    return cv2.blur(img, (ksize, ksize))

def filtro_mediana_cv(img, ksize=3):
    return cv2.medianBlur(img, ksize)

def filtro_canny_cv(img, t1=100, t2=200):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    edges = cv2.Canny(gray, t1, t2)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)