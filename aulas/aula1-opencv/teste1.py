import cv2

img = cv2.imread("exemplo.png")
cv2.imshow("Titulo", img)

# Espera tecla (0 = infinito). Se for ESC (27), fecha.
key = cv2.waitKey(0)
if key == 27:  # tecla ESC
    cv2.destroyAllWindows()