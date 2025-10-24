import cv2
import numpy as np

def to_gray_manual(img):
    if len(img.shape) == 2:
        return img
    
    b = img[:, :, 0]
    g = img[:, :, 1]
    r = img[:, :, 2]
    
    gray = (b + g + r) / 3.0
    
    return gray.astype(np.uint8)

def otsu_threshold_manual(img):
    gray = to_gray_manual(img)
    
    hist = np.zeros(256, dtype=int)
    for pixel in gray.flatten():
        hist[pixel] += 1
        
    total_pixels = gray.size
    
    best_threshold = 0
    max_variance = 0.0
    
    for t in range(256):
        w_bg = np.sum(hist[:t]) / total_pixels
        w_fg = np.sum(hist[t:]) / total_pixels

        if w_bg == 0 or w_fg == 0:
            continue

        sum_bg = 0
        for i in range(t):
            sum_bg += i * hist[i]
        mean_bg = sum_bg / (w_bg * total_pixels)

        sum_fg = 0
        for i in range(t, 256):
            sum_fg += i * hist[i]
        mean_fg = sum_fg / (w_fg * total_pixels)

        variance = w_bg * w_fg * ((mean_bg - mean_fg) ** 2)

        if variance > max_variance:
            max_variance = variance
            best_threshold = t
            
    _, binary_img = cv2.threshold(gray, best_threshold, 255, cv2.THRESH_BINARY)
    
    return binary_img

def to_gray_cv(img):
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img

def negative(img):
    return 255 - img

def otsu_threshold_cv(img):
    gray = to_gray_cv(img)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary

def log_transform(img):
    img = img.astype(np.float32)
    c = 255 / np.log(1 + np.max(img))
    log_img = c * np.log(img + 1)
    return np.uint8(log_img)

def power_transform(img, gamma=1.0):
    img = img / 255.0
    power_img = np.power(img, gamma)
    return np.uint8(power_img * 255)