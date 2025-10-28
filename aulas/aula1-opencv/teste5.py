import cv2
import numpy as np

img1 = cv2.imread("flamengo-logo-6.png")
img2 = cv2.imread("exemplo2.png")

print("Imagem 1:", img1.shape, img1.dtype)
print("Imagem 2:", img2.shape, img2.dtype)

# Redimensiona img2 para o tamanho da img1
img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

# Combinação ponderada (10% da img1 + 90% da img2)
img3 = img1 * 0.1 + img2
img3 = img3.astype(np.uint8)

print("Imagem 3:", img3.shape, img3.dtype)

cv2.imshow("Soma", img3)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('união-flasco.avif', img3)
