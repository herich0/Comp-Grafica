import cv2
import numpy as np
from collections import deque
import os

# Define os caminhos das pastas de entrada e saída
INPUT_DIR = 'imgs'
OUTPUT_DIR = 'results'

def ensure_dirs_exist():
    if not os.path.exists(INPUT_DIR):
        print(f"Criando pasta de entrada: '{INPUT_DIR}'")
        os.makedirs(INPUT_DIR)
        print(f"Por favor, coloque as imagens originais aqui.")
    if not os.path.exists(OUTPUT_DIR):
        print(f"Criando pasta de resultados: '{OUTPUT_DIR}'")
        os.makedirs(OUTPUT_DIR)

def load_image(filename):
    path = os.path.join(INPUT_DIR, filename)
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"A imagem '{path}' não foi encontrada.")
    return img

def save_image(filename, image):
    path = os.path.join(OUTPUT_DIR, filename)
    cv2.imwrite(path, image)
    print(f" - Salvo: {path}")

def exercicio_1_filtro_mediana(input_image_path='circuito.tif'):
    img = load_image(input_image_path)
    print("✅ Executando Exercício 1: Filtro de Mediana...")
    resultado = img.copy()
    for i in range(1, 4):
        resultado = cv2.medianBlur(resultado, 3)
        save_image(f"circuito_mediana_{i}.tif", resultado)

def exercicio_2_detecao_pontos(input_image_path='pontos.png'):
    img = load_image(input_image_path)
    print("✅ Executando Exercício 2: Detecção de Pontos...")
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)
    filtrada = cv2.filter2D(img, ddepth=-1, kernel=kernel)
    _, limiarizada = cv2.threshold(filtrada, 200, 255, cv2.THRESH_BINARY)
    save_image('pontos_filtrada.png', filtrada)
    save_image('pontos_detectados.png', limiarizada)

def exercicio_3_detecao_linhas(input_image_path='linhas.png'):
    img = load_image(input_image_path)
    print("✅ Executando Exercício 3: Detecção de Linhas...")
    kernels = {
        'horizontal': np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]], dtype=np.float32),
        '45': np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]], dtype=np.float32),
        'vertical': np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]], dtype=np.float32),
        'neg45': np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]], dtype=np.float32)
    }
    combined_result = np.zeros_like(img, dtype=np.uint8)
    for name, kernel in kernels.items():
        filtered = cv2.filter2D(img, ddepth=-1, kernel=kernel)
        _, binarized = cv2.threshold(filtered, 150, 255, cv2.THRESH_BINARY)
        save_image(f"linhas_{name}.png", binarized)
        combined_result = cv2.bitwise_or(combined_result, binarized)
    save_image('linhas_detectadas.png', combined_result)

def exercicio_4_detector_canny(input_image_path='igreja.png'):
    img = load_image(input_image_path)
    print("✅ Executando Exercício 4: Detector de Canny...")
    edges = cv2.Canny(img, threshold1=100, threshold2=200)
    save_image('igreja_canny.png', edges)

def exercicio_5_crescimento_regiao(input_image_path='root.jpg', seed_point=(100, 150), threshold=15):
    path = os.path.join(INPUT_DIR, input_image_path)
    img_color = cv2.imread(path)
    if img_color is None:
        raise FileNotFoundError(f"A imagem '{path}' não foi encontrada.")

    print("✅ Executando Exercício 5: Crescimento de Região...")
    gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    
    h, w = gray.shape
    mask = np.zeros((h, w), np.uint8)
    seed_value = int(gray[seed_point[1], seed_point[0]])
    queue = deque([seed_point])
    mask[seed_point[1], seed_point[0]] = 255
    
    neighbors = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    
    while queue:
        x, y = queue.popleft()
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] == 0:
                if abs(int(gray[ny, nx]) - seed_value) <= threshold:
                    mask[ny, nx] = 255
                    queue.append((nx, ny))
    
    highlighted = img_color.copy()
    highlighted[mask == 255] = [255, 0, 0]
    
    save_image('root_gray.png', gray)
    save_image('root_region_mask.png', mask)
    save_image('root_highlighted.png', highlighted)

def exercicio_6_otsu(image_list=['harewood.jpg', 'nuts.jpg', 'snow.jpg', 'img_aluno.png']):
    print("✅ Executando Exercício 6: Método de Otsu...")
    for nome in image_list:
        try:
            img = load_image(nome)
            _, otsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            save_image(f"{os.path.splitext(nome)[0]}_otsu.png", otsu)
        except FileNotFoundError as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    ensure_dirs_exist()
    try:
        exercicio_1_filtro_mediana()
        print("-" * 30)
        exercicio_2_detecao_pontos()
        print("-" * 30)
        exercicio_3_detecao_linhas()
        print("-" * 30)
        exercicio_4_detector_canny()
        print("-" * 30)
        exercicio_6_otsu()
        print("-" * 30)
        exercicio_5_crescimento_regiao()
        print("-" * 30)
        print("🎉 Todos os exercícios concluídos com sucesso!")
    except FileNotFoundError as e:
        print(f"Erro: {e}\nPor favor, garanta que as imagens estão na pasta '{INPUT_DIR}'.")