import cv2
img = cv2.imread('exemplo.png')
print(img.shape)
print(img.size)
print(img.dtype)
print('[B G R]: {}'.format(img[50, 50]))
img[100:200, 150:250] = [255, 255, 255]
img[150, 200] = [0, 0, 0]
img[150:250, 350:450, [0, 1]] = 0
cv2.imshow('Pixels', img)
cv2.waitKey(0)
cv2.destroyAllWindows()