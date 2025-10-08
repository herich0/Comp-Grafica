import cv2
import numpy as np

img = cv2.imread('quadrados.png')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

x = int(input("Informe a coordenada x do ponto inicial: "))
y = int(input("Informe a coordenada y do ponto inicial: "))
seed_point = (x, y)

h, w = binary.shape[:2]
mask = np.zeros((h+2, w+2), np.uint8)

component_img = np.zeros_like(img)

flood_filled = binary.copy()
cv2.floodFill(flood_filled, mask, seed_point, 255)

component = mask[1:-1, 1:-1]  

component_img[component == 1] = (0, 255, 255)

cv2.imwrite('quadrado80_amarelo.png', component_img)

cv2.imshow('Componente Conectado - Quadrado 80 px', component_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
