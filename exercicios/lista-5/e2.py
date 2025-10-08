import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('quadrados.png', cv2.IMREAD_GRAYSCALE)

_, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

kernel = np.ones((50,50), np.uint8)
eroded = cv2.erode(binary, kernel, iterations=1)

restored = cv2.dilate(eroded, kernel, iterations=1)

titles = ['Original', 'Após Erosão', 'Após Dilatação']
images = [binary, eroded, restored]

cv2.imwrite('quadrados_erosao.png', eroded)
cv2.imwrite('quadrados_dilatacao.png', restored)

plt.figure(figsize=(12,4))
for i in range(3):
    plt.subplot(1,3,i+1)
    plt.imshow(images[i], cmap='gray')
    plt.title(titles[i])
    plt.axis('off')

plt.tight_layout()
plt.show()

