import cv2

img1 = cv2.imread("exemplo.png")
img2 = cv2.imread("exemplo2.png")

print("Imagem 1:", img1.shape, img1.dtype)
print("Imagem 2:", img2.shape, img2.dtype)

# pega as dimensões da menor imagem
h = min(img1.shape[0], img2.shape[0])
w = min(img1.shape[1], img2.shape[1])

# redimensiona as duas para o mesmo tamanho
img1_resized = cv2.resize(img1, (w, h))
img2_resized = cv2.resize(img2, (w, h))

# soma
img3 = img1_resized + img2_resized
print("Imagem 3:", img3.shape, img3.dtype)

cv2.imshow("Soma", img3)
cv2.waitKey(0)
cv2.destroyAllWindows()
