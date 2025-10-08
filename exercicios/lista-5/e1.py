import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('figura1.png', cv2.IMREAD_GRAYSCALE)

_, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

binary = binary // 255

SE_a = np.ones((3, 3), dtype=np.uint8)            
SE_b = np.array([[0,1,0],
                 [1,1,1],
                 [0,1,0]], dtype=np.uint8)        

erosion_a  = cv2.erode(binary, SE_a, iterations=1)
erosion_b  = cv2.erode(binary, SE_b, iterations=1)
dilation_a = cv2.dilate(binary, SE_a, iterations=1)
dilation_b = cv2.dilate(binary, SE_b, iterations=1)

erosion_a  = erosion_a * 255
erosion_b  = erosion_b * 255
dilation_a = dilation_a * 255
dilation_b = dilation_b * 255

titles = ['Original', 'Erosão SE(a)', 'Erosão SE(b)', 'Dilatação SE(a)', 'Dilatação SE(b)']
images = [binary*255, erosion_a, erosion_b, dilation_a, dilation_b]

plt.figure(figsize=(12,6))
for i in range(5):
    plt.subplot(2,3,i+1)
    plt.imshow(images[i], cmap='gray')
    plt.title(titles[i])
    plt.axis('off')

plt.tight_layout()
plt.show()
