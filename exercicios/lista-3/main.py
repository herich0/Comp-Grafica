import cv2
import numpy as np
from matplotlib import pyplot as plt

def get_fourier_spectrum(img_gray):
    dft = cv2.dft(np.float32(img_gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))
    return magnitude_spectrum

def apply_gaussian_filter(img_gray, cutoff_freq, filter_type='lowpass'):
    dft = cv2.dft(np.float32(img_gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    rows, cols = img_gray.shape
    crow, ccol = rows // 2, cols // 2
    filter_mask = np.zeros((rows, cols, 2), np.float32)
    for i in range(rows):
        for j in range(cols):
            dist = np.sqrt((i - crow)**2 + (j - ccol)**2)
            gauss_val = np.exp(-(dist**2) / (2 * cutoff_freq**2))
            filter_mask[i, j, :] = gauss_val
    if filter_type == 'highpass':
        filter_mask = 1 - filter_mask
    fshift = dft_shift * filter_mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX)
    return img_back.astype(np.uint8)

def apply_band_reject_filter(img_gray, filter_mask_img):
    filter_mask = cv2.resize(filter_mask_img, (img_gray.shape[1], img_gray.shape[0]), interpolation=cv2.INTER_LINEAR)
    filter_mask = filter_mask.astype(np.float32) / 255.0
    filter_mask_2ch = np.stack([filter_mask, filter_mask], axis=-1)
    dft = cv2.dft(np.float32(img_gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    fshift_filtered = dft_shift * filter_mask_2ch
    f_ishift = np.fft.ifftshift(fshift_filtered)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX)
    return img_back.astype(np.uint8)

def create_and_apply_custom_filters(img_gray):
    rows, cols = img_gray.shape
    crow, ccol = rows // 2, cols // 2
    
    # Cria as máscaras com 3 canais (BGR) para serem compatíveis com cvtColor
    passband_filter = np.zeros((rows, cols, 3), np.uint8)
    rejectband_filter = np.ones((rows, cols, 3), np.uint8) * 255
    
    # Círculo externo (passa-banda)
    cv2.circle(passband_filter, (ccol, crow), 80, (255, 255, 255), -1)
    # Círculo interno (removendo do passa-banda)
    cv2.circle(passband_filter, (ccol, crow), 30, (0, 0, 0), -1)
    
    # Círculo interno (rejeita-banda)
    cv2.circle(rejectband_filter, (ccol, crow), 30, (0, 0, 0), -1)
    # Círculo externo (removendo do rejeita-banda)
    cv2.circle(rejectband_filter, (ccol, crow), 80, (255, 255, 255), -1)

    # Converte as máscaras BGR para cinza
    passband_filter = cv2.cvtColor(passband_filter, cv2.COLOR_BGR2GRAY)
    rejectband_filter = cv2.cvtColor(rejectband_filter, cv2.COLOR_BGR2GRAY)
    
    passband_filtered = apply_band_reject_filter(img_gray, passband_filter)
    rejectband_filtered = apply_band_reject_filter(img_gray, rejectband_filter)
    
    return passband_filtered, rejectband_filtered

def process_image(img_path, output_dir, file_name, cutoff=30):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Erro ao carregar a imagem: {img_path}")
        return
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1) Gerar e salvar o espectro de Fourier
    magnitude_spectrum = get_fourier_spectrum(img_gray)
    cv2.imwrite(f"{output_dir}{file_name}_espectro.png", magnitude_spectrum)
    
    # 2) Filtros passa-baixa e passa-alta
    lowpass_img = apply_gaussian_filter(img_gray, cutoff, 'lowpass')
    highpass_img = apply_gaussian_filter(img_gray, cutoff, 'highpass')
    cv2.imwrite(f"{output_dir}{file_name}_passabaixa.png", lowpass_img)
    cv2.imwrite(f"{output_dir}{file_name}_passaalta.png", highpass_img)

if __name__ == "__main__":
    image_list = ["arara.png", "barra1.png", "barra2.png", "barra3.png", "barra4.png", "teste.tif", "img_aluno.png"]
    output_folder = "resultados/"
    
    import os
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for img_file in image_list:
        file_name = img_file.split('.')[0]
        full_path = f"images/{img_file}"
            
        process_image(full_path, output_folder, file_name)

    # 3) Filtro rejeita-banda na arara
    arara_img = cv2.imread("images/arara.png", cv2.IMREAD_GRAYSCALE)
    arara_filtro_mask = cv2.imread("images/arara_filtro.png", cv2.IMREAD_GRAYSCALE)
    if arara_img is not None and arara_filtro_mask is not None:
        arara_filtered = apply_band_reject_filter(arara_img, arara_filtro_mask)
        cv2.imwrite(f"{output_folder}arara_rejeita_banda.png", arara_filtered)
        print("Filtro rejeita-banda na arara aplicado com sucesso.")

    # 4) Filtros customizados em teste.tif e img_aluno
    teste_img = cv2.imread("images/teste.tif", cv2.IMREAD_GRAYSCALE)
    aluno_img = cv2.imread("images/image_aluno.png", cv2.IMREAD_GRAYSCALE)
    
    if teste_img is not None:
        teste_passband, teste_rejectband = create_and_apply_custom_filters(teste_img)
        cv2.imwrite(f"{output_folder}teste_passabanda.png", teste_passband)
        cv2.imwrite(f"{output_folder}teste_rejeitabanda.png", teste_rejectband)
    
    if aluno_img is not None:
        aluno_passband, aluno_rejectband = create_and_apply_custom_filters(aluno_img)
        cv2.imwrite(f"{output_folder}img_aluno_passabanda.png", aluno_passband)
        cv2.imwrite(f"{output_folder}img_aluno_rejeitabanda.png", aluno_rejectband)