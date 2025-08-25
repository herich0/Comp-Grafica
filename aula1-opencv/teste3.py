import cv2
img = cv2.imread('exemplo.png')
recorte = img[150:250, 350:450]
img[0:100, 0:100] = recorte
cv2.imshow('Recorte', img)
cv2.waitKey(0)
cv2.destroyAllWindows()