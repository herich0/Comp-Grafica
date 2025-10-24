import cv2
import numpy as np
import pygame 
import os     

class VideoTracker:
    def __init__(self):
        print("Gerenciador de Rastreamento Iniciado.")
        self.tracker = None
        self.tracking_active = False

        template_path = "pou.png"
        self.pou_template = cv2.imread(template_path)
        
        if self.pou_template is None:
            print(f"!!! ATENÇÃO: Não foi possível carregar '{template_path}'.")
            print("!!! A detecção do Pou (6b) não irá funcionar.")
            self.pou_template = np.zeros((10,10,3), dtype=np.uint8) 
            self.pou_mask = None
        else:
            print("Template 'pou.png' carregado. Criando máscara...")
            self.pou_h, self.pou_w = self.pou_template.shape[:2]
            gray_template = cv2.cvtColor(self.pou_template, cv2.COLOR_BGR2GRAY)
            _, self.pou_mask = cv2.threshold(gray_template, 254, 255, cv2.THRESH_BINARY_INV)
            
        # Limiar para TM_SQDIFF_NORMED (menor é melhor)
        self.pou_threshold = 0.2 
        
        try:
            pygame.mixer.init()
            music_path = "musica.mp3"
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                print(f"Música '{music_path}' carregada.")
            else:
                print(f"!!! ATENÇÃO: Música '{music_path}' não encontrada.")
            self.music_playing = False
        except Exception as e:
            print(f"!!! ATENÇÃO: Erro ao inicializar o mixer do pygame: {e}")
            self.music_playing = False
            
    def start_generic_tracker(self, frame):
        """
        Pausa o vídeo e pede ao usuário para selecionar uma ROI (Região de Interesse).
        Retorna True se a seleção for válida.
        """
        roi = cv2.selectROI("Selecione o Objeto para Rastrear", frame, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Selecione o Objeto para Rastrear")
        
        if roi[2] > 0 and roi[3] > 0:
            try:
                self.tracker = cv2.TrackerCSRT_create() 
                print("Usando cv2.TrackerCSRT_create()")
            except AttributeError:
                try:
                    self.tracker = cv2.legacy.TrackerCSRT_create()
                    print("Usando cv2.legacy.TrackerCSRT_create()")
                except AttributeError:
                    print("!!! ATENÇÃO: Não foi possível criar o TrackerCSRT.")
                    print("!!! Verifique sua instalação do opencv-contrib-python.")
                    return False
                    
            self.tracker.init(frame, roi)
            self.tracking_active = True
            print(f"Iniciando rastreamento genérico em {roi}")
            return True
        else:
            print("Seleção de ROI inválida.")
            self.tracking_active = False
            return False

    def stop_generic_tracker(self):
        """Para o rastreamento genérico."""
        self.tracker = None
        self.tracking_active = False
        print("Rastreamento genérico parado.")

    def update_generic_tracker(self, frame):
        """
        Atualiza o rastreador com o novo frame e desenha a caixa.
        """
        if self.tracker and self.tracking_active:
            success, box = self.tracker.update(frame)
            
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else:
                h, w = frame.shape[:2]
                cv2.line(frame, (w//2 - 20, h//2), (w//2 + 20, h//2), (0, 0, 255), 2)
                cv2.line(frame, (w//2, h//2 - 20), (w//2, h//2 + 20), (0, 0, 255), 2)
                
        return frame

    def detect_pou(self, frame):
        """
        Procura pelo Pou (usando Template Matching com Máscara) e toca música.
        """
        if self.pou_template is None or self.pou_mask is None:
            return frame 

        # 1. Executa o template matching com a máscara
        # NOTA: Com TM_SQDIFF_NORMED, o "match" perfeito é 0.0
        result = cv2.matchTemplate(frame, self.pou_template, cv2.TM_SQDIFF_NORMED, mask=self.pou_mask)
        
        # 2. Encontra o ponto de menor "diferença"
        min_val, _max_val, min_loc, _max_loc = cv2.minMaxLoc(result)
        
        # 3. Verifica se a "diferença" é pequena o suficiente
        if min_val <= self.pou_threshold:
            # POU ENCONTRADO
            top_left = min_loc
            bottom_right = (top_left[0] + self.pou_w, top_left[1] + self.pou_h)
            cv2.rectangle(frame, top_left, bottom_right, (0, 0, 255), 3) 
            
            if not self.music_playing:
                try:
                    pygame.mixer.music.play(-1) 
                    self.music_playing = True
                    print("Pou detectado, tocando música.")
                except Exception as e:
                    print(f"Erro ao tocar música: {e}")
        else:
            # POU NÃO ENCONTRADO
            if self.music_playing:
                try:
                    pygame.mixer.music.stop()
                    self.music_playing = False
                    print("Pou perdido, parando música.")
                except Exception as e:
                    print(f"Erro ao parar música: {e}")
            
        return frame
        
    def stop_pou_detector(self):
        """Função de limpeza para parar a música."""
        if self.music_playing:
            try:
                pygame.mixer.music.stop()
                self.music_playing = False
                print("Detector do Pou desligado, parando música.")
            except Exception as e:
                print(f"Erro ao parar música: {e}")