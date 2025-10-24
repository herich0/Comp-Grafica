import numpy as np

def calculate_histograms(img):
    hist = np.zeros(256, dtype=int)
    for pixel in img.flatten():
        hist[pixel] += 1
    total = img.size
    norm_hist = hist / total
    cum_hist = np.cumsum(hist)
    norm_cum = cum_hist / total
    return hist, norm_hist, cum_hist, norm_cum