import cv2
import numpy as np
import matplotlib.pyplot as plt
import os # Importar para verificar arquivos

# --- Funções de Processamento de Imagem ---

def proc_morfologia_basica(caminho_img):
    img_orig = cv2.imread(caminho_img, cv2.IMREAD_GRAYSCALE)
    if img_orig is None:
        print(f"Erro: Não foi possível carregar a imagem em {caminho_img}")
        return

    _, img_bin = cv2.threshold(img_orig, 127, 255, cv2.THRESH_BINARY)
    matriz_bin = img_bin // 255

    elemento_a = np.ones((3, 3), dtype=np.uint8)
    elemento_b = np.array([[0,1,0],[1,1,1],[0,1,0]], dtype=np.uint8)

    erosao_a = cv2.erode(matriz_bin, elemento_a, iterations=1) * 255
    erosao_b = cv2.erode(matriz_bin, elemento_b, iterations=1) * 255
    dilatacao_a = cv2.dilate(matriz_bin, elemento_a, iterations=1) * 255
    dilatacao_b = cv2.dilate(matriz_bin, elemento_b, iterations=1) * 255

    titulos_plt = ['Imagem Inicial', 'Erosao A', 'Erosao B', 'Dilatacao A', 'Dilatacao B']
    imagens_plt = [img_bin, erosao_a, erosao_b, dilatacao_a, dilatacao_b]

    plt.figure(figsize=(12,6))
    for idx in range(5):
        plt.subplot(2,3,idx+1)
        plt.imshow(imagens_plt[idx], cmap='gray')
        plt.title(titulos_plt[idx])
        plt.axis('off')

    plt.tight_layout()
    plt.show()

def proc_erosao_restauracao(caminho_img):
    img_base = cv2.imread(caminho_img, cv2.IMREAD_GRAYSCALE)
    if img_base is None:
        print(f"Erro: Não foi possível carregar a imagem em {caminho_img}")
        return

    _, img_bin = cv2.threshold(img_base, 127, 255, cv2.THRESH_BINARY)

    matriz_estruturante = np.ones((50,50), np.uint8)
    passo_erosao = cv2.erode(img_bin, matriz_estruturante, iterations=1)
    passo_restauracao = cv2.dilate(passo_erosao, matriz_estruturante, iterations=1)

    cv2.imwrite('quadrados_erosao_mod.png', passo_erosao)
    cv2.imwrite('quadrados_dilatacao_mod.png', passo_restauracao)

    nomes = ['Base', 'Apos Erosao', 'Apos Dilatacao']
    dados = [img_bin, passo_erosao, passo_restauracao]

    plt.figure(figsize=(12,4))
    for i_p in range(3):
        plt.subplot(1,3,i_p+1)
        plt.imshow(dados[i_p], cmap='gray')
        plt.title(nomes[i_p])
        plt.axis('off')

    plt.tight_layout()
    plt.show()

def proc_abertura_fechamento(caminho_img):
    img_ruido = cv2.imread(caminho_img, cv2.IMREAD_GRAYSCALE)
    if img_ruido is None:
        print(f"Erro: Não foi possível carregar a imagem em {caminho_img}")
        return

    kernel_abrir = cv2.getStructuringElement(cv2.MORPH_RECT, (20,20))
    imagem_aberta = cv2.morphologyEx(img_ruido, cv2.MORPH_OPEN, kernel_abrir)

    kernel_fechar = cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))
    imagem_fechada = cv2.morphologyEx(img_ruido, cv2.MORPH_CLOSE, kernel_fechar)

    cv2.imwrite("ruidos_abertura_mod.png", imagem_aberta)
    cv2.imwrite("ruidos_fechamento_mod.png", imagem_fechada)

    cv2.imshow("Base Ruidosa", img_ruido)
    cv2.imshow("Tratamento Abertura", imagem_aberta)
    cv2.imshow("Tratamento Fechamento", imagem_fechada)
    cv2.waitKey(1) # WaitKey 1 para nao travar o loop, depois chamamos destroyAll

def proc_bordas_morfologicas(caminho_img):
    img_alvo = cv2.imread(caminho_img, cv2.IMREAD_GRAYSCALE)
    if img_alvo is None:
        print(f"Erro: Não foi possível carregar a imagem em {caminho_img}")
        return

    _, bin_alvo = cv2.threshold(img_alvo, 127, 255, cv2.THRESH_BINARY)

    kernel_borda = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    imagem_erodida = cv2.erode(bin_alvo, kernel_borda, iterations=1)
    limite_interno = cv2.subtract(bin_alvo, imagem_erodida)

    imagem_dilatada = cv2.dilate(bin_alvo, kernel_borda, iterations=1)
    limite_externo = cv2.subtract(imagem_dilatada, bin_alvo)

    cv2.imwrite('borda_interna_mod.png', limite_interno)
    cv2.imwrite('borda_externa_mod.png', limite_externo)

    etiquetas = ['Binaria Base', 'Limite Interno', 'Limite Externo']
    conjunto_imagens = [bin_alvo, limite_interno, limite_externo]

    plt.figure(figsize=(12,4))
    for k in range(3):
        plt.subplot(1,3,k+1)
        plt.imshow(conjunto_imagens[k], cmap='gray')
        plt.title(etiquetas[k])
        plt.axis('off')

    plt.tight_layout()
    plt.show()

def proc_preenchimento_regiao(caminho_img):
    img_orig = cv2.imread(caminho_img, cv2.IMREAD_GRAYSCALE)
    if img_orig is None:
        print(f"Erro: Não foi possível carregar a imagem em {caminho_img}")
        return

    _, img_bin = cv2.threshold(img_orig, 127, 255, cv2.THRESH_BINARY)

    altura, largura = img_bin.shape[:2]
    mascara_preench = np.zeros((altura+2, largura+2), np.uint8)
    ponto_semente = (largura//2, altura//2)

    copia_preencher = img_bin.copy()
    cv2.floodFill(copia_preencher, mascara_preench, ponto_semente, 255)

    regiao_completa = cv2.bitwise_or(img_bin, copia_preencher)

    cv2.imwrite('regiao_preenchida_mod.png', regiao_completa)

    cv2.imshow('Imagem Binaria', img_bin)
    cv2.imshow('Preenchimento de Regiao', regiao_completa)
    cv2.waitKey(1) # WaitKey 1 para nao travar o loop, depois chamamos destroyAll

def proc_componente_conectado(caminho_img):
    img_rgb = cv2.imread(caminho_img)
    if img_rgb is None:
        print(f"Erro: Não foi possível carregar a imagem em {caminho_img}")
        return

    img_cinza = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    _, img_bin = cv2.threshold(img_cinza, 127, 255, cv2.THRESH_BINARY)

    # Coordenadas de entrada (Hardcoded para evitar prompt no loop)
    # Supondo que 'quadrados.png' tem um ponto inicial relevante em (200, 200)
    ponto_start = (200, 200)

    h_cc, w_cc = img_bin.shape[:2]
    mascara_cc = np.zeros((h_cc+2, w_cc+2), np.uint8)
    imagem_componente = np.zeros_like(img_rgb)

    copia_cc = img_bin.copy()
    cv2.floodFill(copia_cc, mascara_cc, ponto_start, 255)

    componente = mascara_cc[1:-1, 1:-1]
    imagem_componente[componente == 1] = (0, 255, 255) # Cor amarela BGR

    cv2.imwrite('componente_destacado_mod.png', imagem_componente)
    cv2.imshow('Componente Conectado', imagem_componente)
    cv2.waitKey(1) # WaitKey 1 para nao travar o loop, depois chamamos destroyAll

def proc_gradiente_morfologico(caminho_img):
    img_g = cv2.imread(caminho_img, cv2.IMREAD_GRAYSCALE)
    if img_g is None:
        print(f"Erro: Não foi possível carregar a imagem em {caminho_img}")
        return

    kernel_g = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    img_dilatada = cv2.dilate(img_g, kernel_g, iterations=1)
    img_erodida = cv2.erode(img_g, kernel_g, iterations=1)
    img_gradiente = cv2.subtract(img_dilatada, img_erodida)

    cv2.imwrite('gradiente_dilatada_mod.png', img_dilatada)
    cv2.imwrite('gradiente_erodida_mod.png', img_erodida)
    cv2.imwrite('gradiente_resultado_mod.png', img_gradiente)

    titulos_g = ['Base', 'Dilatacao', 'Erosao', 'Gradiente']
    imagens_g = [img_g, img_dilatada, img_erodida, img_gradiente]

    plt.figure(figsize=(12,6))
    for i_g in range(4):
        plt.subplot(2,2,i_g+1)
        plt.imshow(imagens_g[i_g], cmap='gray')
        plt.title(titulos_g[i_g])
        plt.axis('off')

    plt.tight_layout()
    plt.show()

# --- Execução Principal ---

if __name__ == '__main__':
    # Lista de arquivos de imagem esperados
    arquivos = {
        'figura1.png': proc_morfologia_basica,
        'quadrados.png': proc_erosao_restauracao,
        'ruidos.png': proc_abertura_fechamento,
        'cachorro.png': proc_bordas_morfologicas,
        'gato.png': proc_preenchimento_regiao,
        'quadrados.png_cc': proc_componente_conectado, # Usando o mesmo arquivo
        'b2.jpg': proc_gradiente_morfologico,
    }

    # Verifica se os arquivos de imagem necessários existem (para evitar erros)
    for nome_arquivo, funcao in arquivos.items():
        if nome_arquivo == 'quadrados.png_cc':
            # Usa o arquivo 'quadrados.png' para a função de componente conectado
            if not os.path.exists('quadrados.png'):
                print("Arquivo 'quadrados.png' nao encontrado. Pulando a tarefa de Componente Conectado.")
                continue
            funcao('quadrados.png')
        elif os.path.exists(nome_arquivo):
            print(f"Executando tarefa para: {nome_arquivo}...")
            funcao(nome_arquivo)
        else:
            print(f"Arquivo '{nome_arquivo}' nao encontrado. Pulando esta tarefa.")

    # Fechar todas as janelas do OpenCV (cv2.imshow) abertas
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Todas as tarefas concluidas.")