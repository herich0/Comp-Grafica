import cv2
import numpy as np

def to_gray(img):
    gray = img[:, :, 0] / 3 + img[:, :, 1] / 3 + img[:, :, 2] / 3
    return gray.astype('uint8')

def negative(img):
    return 255 - img

def ajuste_contraste(img, c=0, d=255):
    a = np.min(img)
    b = np.max(img)
    
    # aplica a fórmula T(r) = (r - a) * (d - c)/(b - a) + c
    new_img = (img - a) * ((d - c) / (b - a)) + c
    
    # garante que os valores fiquem dentro de [0,255]
    new_img = np.clip(new_img, 0, 255)
    return new_img.astype('uint8')

img = cv2.imread('aaa.jpg')
gray_img = to_gray(img)
#gray_img = negative(gray_img)

#cv2.imshow('Imagem em Cinza', gray_img)    
#cv2.imshow('imagem_cinza_negativa.png', gray_img)
contraste_img = ajuste_contraste(gray_img, 150, 200)
cv2.imshow('Imagem com Contraste Ajustado', contraste_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
