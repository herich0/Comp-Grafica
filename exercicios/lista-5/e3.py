import cv2
import numpy as np

imagem = cv2.imread("ruidos.png", cv2.IMREAD_GRAYSCALE)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20,20))

abertura = cv2.morphologyEx(imagem, cv2.MORPH_OPEN, kernel)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))

fechamento = cv2.morphologyEx(imagem, cv2.MORPH_CLOSE, kernel)

cv2.imwrite("resultado_abertura.png", abertura)
cv2.imwrite("resultado_fechamento.png", fechamento)

cv2.imshow("Original", imagem)
cv2.imshow("Abertura", abertura)
cv2.imshow("Fechamento", fechamento)
cv2.waitKey(0)
cv2.destroyAllWindows()
