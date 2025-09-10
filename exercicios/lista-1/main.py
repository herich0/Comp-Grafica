import cv2
import numpy as np

# 1) Conversão para níveis de cinza
def to_gray(img):
    img = img.astype(np.float16)
    gray = img[:,:,0]/3 + img[:,:,1]/3 + img[:,:,2]/3
    return gray.astype(np.uint8)

# 2) Negativo
def negative(img):
    return 255 - img

# 3) Ajuste de contraste (Normalização)
def ajuste_contraste(img, c, d):
    a = np.min(img)
    b = np.max(img)
    if (b - a) == 0:
        return np.zeros(img.shape, dtype='uint8')
    new_img = (img - a) * ((d - c) / (b - a)) + c
    return new_img.astype(np.uint8)

# 4) Operador logarítmico
def log_operator(img):
    img = img.astype(np.float32)
    c = 255 / np.log(1 + np.max(img))
    log_img = c * np.log(img + 1)
    return log_img.astype(np.uint8)

# 5) Operador de potência
def power_law_transform(img, c, gamma):
    img = img.astype(np.float32)
    power_img = c * np.power(img, gamma)
    final_img = ajuste_contraste(power_img, 0, 255)
    return final_img

# 6) Fatiamento dos planos de bits
def bit_plane_slicing(img):
    bit_planes = []
    for i in range(8):
        # Extrai o i-ésimo bit plane da imagem
        bit_plane = np.bitwise_and(img, 2**i)
        # Normaliza o bit plane para 0 e 255 para visualização
        normalized_plane = bit_plane * 255
        bit_planes.append(normalized_plane.astype(np.uint8))
    return bit_planes

# 7) Histograma e histogramas normalizado/acumulado
def calculate_histograms(img):
    hist = np.zeros(256, dtype=int)
    for pixel in img.flatten():
        hist[pixel] += 1
    
    # Histograma Normalizado
    total_pixels = img.shape[0] * img.shape[1]
    normalized_hist = hist / total_pixels
    
    # Histograma Acumulado
    cumulative_hist = np.cumsum(hist)
    
    # Histograma Acumulado Normalizado
    normalized_cumulative_hist = cumulative_hist / total_pixels
    
    return hist, normalized_hist, cumulative_hist, normalized_cumulative_hist

# 8) Equalização de histograma
def histogram_equalization(img):
    hist, _, cumulative_hist, _ = calculate_histograms(img)
    
    # Encontra o primeiro valor não-zero
    L = 256
    cumulative_hist_nonzero = cumulative_hist[cumulative_hist > 0]
    min_val = cumulative_hist_nonzero[0]
    
    equalized_img = np.zeros_like(img)
    
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            r = img[i, j]
            # Aplica a fórmula de equalização
            s = round(((cumulative_hist[r] - min_val) / (img.size - min_val)) * (L - 1))
            equalized_img[i, j] = s
            
    return equalized_img.astype(np.uint8)

# Função para mostrar imagem e salvar
def process_and_save(img, name, output_dir="imgs/"):
    # 1) Cinza
    gray_img = to_gray(img)
    cv2.imwrite(f"{output_dir}{name}_cinza.png", gray_img)

    # 2) Negativo
    negative_img = negative(gray_img)
    cv2.imwrite(f"{output_dir}{name}_negativo.png", negative_img)

    # 3) Ajuste de contraste (Normalização)
    normalizada_img = ajuste_contraste(gray_img, 0, 100)
    cv2.imwrite(f"{output_dir}{name}_normalizada.png", normalizada_img)

    # 4) Logarítmico
    log_img = log_operator(gray_img)
    cv2.imwrite(f"{output_dir}{name}_log.png", log_img)

    # 5) Potência
    power_img = power_law_transform(gray_img, 2, 2)
    cv2.imwrite(f"{output_dir}{name}_potencia.png", power_img)
    
    # 6) Fatiamento de bits
    bit_planes = bit_plane_slicing(gray_img)
    for i, plane in enumerate(bit_planes):
        cv2.imwrite(f"{output_dir}{name}_bit_plane_{i}.png", plane)

    # 8) Equalização de Histograma
    equalized_img = histogram_equalization(gray_img)
    cv2.imwrite(f"{output_dir}{name}_equalizada.png", equalized_img)
    
    print(f"Processamento para {name} concluído.")

if __name__ == "__main__":
    # Carregue as imagens
    lena_img = cv2.imread('imgs/lena.png')
    aluno_img = cv2.imread('imgs/img_aluno.png')
    unequalized_img = cv2.imread('imgs/unequalized.jpg')

    # Verifique se as imagens foram carregadas corretamente
    if lena_img is None or aluno_img is None or unequalized_img is None:
        print("Erro: Verifique os nomes e o caminho das imagens.")
    else:
        # Processa e salva as imagens de acordo com os exercícios
        process_and_save(lena_img, "lena")
        process_and_save(aluno_img, "img_aluno")
        
        # Processa a imagem unequalized.jpg para os exercícios de histograma e equalização
        gray_unequalized = to_gray(unequalized_img)
        cv2.imwrite("Imagens/unequalized_gray.png", gray_unequalized)

        # 7) Histograma para unequalized.jpg
        hist, norm_hist, cum_hist, norm_cum_hist = calculate_histograms(gray_unequalized)
        print("Histogramas para unequalized.jpg:")
        # Aqui você pode imprimir ou plotar os resultados dos histogramas para o seu PDF
        
        # 8) Equalização de unequalized.jpg
        equalized_unequalized = histogram_equalization(gray_unequalized)
        cv2.imwrite("Imagens/unequalized_equalizada.png", equalized_unequalized)
        
        # Para o exercício 7-ii e 7-iii, você deve aplicar os algoritmos nas imagens coloridas
        # Lembre-se que o cv2.imread() lê em BGR
        b, g, r = cv2.split(aluno_img)
        hist_r, _, _, _ = calculate_histograms(r)
        hist_g, _, _, _ = calculate_histograms(g)
        hist_b, _, _, _ = calculate_histograms(b)
        print("Histogramas para os canais R, G e B de img_aluno.png calculados.")