import cv2
import numpy as np

def morf_erosao_manual(img):
    kernel = np.ones((5, 5), np.uint8)
    k_h, k_w = kernel.shape
    pad_h, pad_w = k_h // 2, k_w // 2

    if len(img.shape) == 3:
        img_proc = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_proc = img.copy()

    h, w = img_proc.shape
    padded_img = np.pad(img_proc, [(pad_h, pad_h), (pad_w, pad_w)], mode='constant', constant_values=255)
    output = np.zeros_like(img_proc)

    for y in range(h):
        for x in range(w):
            neighborhood = padded_img[y:y+k_h, x:x+k_w]
            valores = neighborhood[kernel == 1]
            output[y, x] = np.min(valores)
            
    return output

def morf_dilatacao_manual(img):
    kernel = np.ones((5, 5), np.uint8)
    k_h, k_w = kernel.shape
    pad_h, pad_w = k_h // 2, k_w // 2

    if len(img.shape) == 3:
        img_proc = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_proc = img.copy()

    h, w = img_proc.shape
    padded_img = np.pad(img_proc, [(pad_h, pad_h), (pad_w, pad_w)], mode='constant', constant_values=0)
    output = np.zeros_like(img_proc)

    for y in range(h):
        for x in range(w):
            neighborhood = padded_img[y:y+k_h, x:x+k_w]
            valores = neighborhood[kernel == 1]
            output[y, x] = np.max(valores)
            
    return output

def morf_abertura_manual(img):
    erosao = morf_erosao_manual(img)
    abertura = morf_dilatacao_manual(erosao)
    return abertura

def morf_fechamento_manual(img):
    dilatacao = morf_dilatacao_manual(img)
    fechamento = morf_erosao_manual(dilatacao)
    return fechamento

def morf_erosao_cv(img):
    kernel = np.ones((5,5), np.uint8)
    return cv2.erode(img, kernel, iterations=1)

def morf_dilatacao_cv(img):
    kernel = np.ones((5,5), np.uint8)
    return cv2.dilate(img, kernel, iterations=1)

def morf_abertura_cv(img):
    kernel = np.ones((5,5), np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

def morf_fechamento_cv(img):
    kernel = np.ones((5,5), np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)