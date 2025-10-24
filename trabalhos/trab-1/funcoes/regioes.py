import cv2
import numpy as np
from collections import deque

def medidas_objetos(img_bin):
    _, thresh = cv2.threshold(img_bin, 127, 255, cv2.THRESH_BINARY)
    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contornos) == 0:
        return 0, 0, 0

    contorno_maior = max(contornos, key=cv2.contourArea)
    area = cv2.contourArea(contorno_maior)
    perimetro = cv2.arcLength(contorno_maior, True)
    diametro = np.sqrt(4 * area / np.pi)
    return round(area, 2), round(perimetro, 2), round(diametro, 2)

def contar_objetos(img_bin):
    _, bin_img = cv2.threshold(img_bin, 127, 255, cv2.THRESH_BINARY)
    h, w = bin_img.shape
    mask = np.zeros((h, w), np.uint8)
    num_objetos = 0
    bounding_boxes = [] 

    for y in range(h):
        for x in range(w):
            if bin_img[y, x] == 255 and mask[y, x] == 0:
                num_objetos += 1
                box = flood_fill(bin_img, mask, (x, y)) 
                bounding_boxes.append(box)
                
    return num_objetos, bounding_boxes 

def flood_fill(img, mask, seed_point):
    h, w = img.shape
    q = deque([seed_point])
    
    min_x, min_y = w, h
    max_x, max_y = 0, 0

    while q:
        x, y = q.popleft()
        
        if x < 0 or x >= w or y < 0 or y >= h: 
            continue
        
        if img[y, x] == 255 and mask[y, x] == 0:
            mask[y, x] = 255 
            
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            
            q.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])

    return (min_x, min_y, max_x, max_y)