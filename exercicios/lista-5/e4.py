import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('cachorro.png', cv2.IMREAD_GRAYSCALE)

_, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

erosion = cv2.erode(binary, kernel, iterations=1)
borda_interna = cv2.subtract(binary, erosion)

dilation = cv2.dilate(binary, kernel, iterations=1)
borda_externa = cv2.subtract(dilation, binary)

cv2.imwrite('cachorro_borda_interna.png', borda_interna)
cv2.imwrite('cachorro_borda_externa.png', borda_externa)

titles = ['Original', 'Borda Interna', 'Borda Externa']
images = [binary, borda_interna, borda_externa]

plt.figure(figsize=(12,4))
for i in range(3):
    plt.subplot(1,3,i+1)
    plt.imshow(images[i], cmap='gray')
    plt.title(titles[i])
    plt.axis('off')

plt.tight_layout()
plt.show()
