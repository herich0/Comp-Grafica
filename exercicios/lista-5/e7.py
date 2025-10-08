import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('b2.jpg', cv2.IMREAD_GRAYSCALE)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

dilatada = cv2.dilate(img, kernel, iterations=1)
erodida = cv2.erode(img, kernel, iterations=1)

gradiente = cv2.subtract(dilatada, erodida)

cv2.imwrite('b2_dilatada.png', dilatada)
cv2.imwrite('b2_erodida.png', erodida)
cv2.imwrite('b2_gradiente.png', gradiente)

titles = ['Original', 'Dilatação', 'Erosão', 'Gradiente Morfológico']
images = [img, dilatada, erodida, gradiente]

plt.figure(figsize=(12,6))
for i in range(4):
    plt.subplot(2,2,i+1)
    plt.imshow(images[i], cmap='gray')
    plt.title(titles[i])
    plt.axis('off')

plt.tight_layout()
plt.show()
