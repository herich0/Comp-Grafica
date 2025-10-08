import cv2
import numpy as np

img = cv2.imread('gato.png', cv2.IMREAD_GRAYSCALE)

_, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

h, w = binary.shape[:2]
mask = np.zeros((h+2, w+2), np.uint8)

seed_point = (w//2, h//2)

filled = binary.copy()

cv2.floodFill(filled, mask, seed_point, 255)

filled_inv = cv2.bitwise_not(filled)

region_filled = cv2.bitwise_or(binary, filled)

cv2.imwrite('gato_preenchido.png', region_filled)

cv2.imshow('Original', binary)
cv2.imshow('Preenchimento de Região', region_filled)
cv2.waitKey(0)
cv2.destroyAllWindows()
