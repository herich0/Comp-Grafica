import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os, datetime
import matplotlib.pyplot as plt

from funcoes.conversoes import (to_gray_manual, otsu_threshold_manual, 
                                to_gray_cv, otsu_threshold_cv, 
                                negative, log_transform, power_transform)
from funcoes.filtros import (filtro_media_manual, filtro_mediana_manual, 
                             filtro_media_cv, filtro_mediana_cv, filtro_canny_cv)
from funcoes.morfologia import (morf_erosao_manual, morf_dilatacao_manual, 
                                morf_abertura_manual, morf_fechamento_manual,
                                morf_erosao_cv, morf_dilatacao_cv, 
                                morf_abertura_cv, morf_fechamento_cv)
from funcoes.histograma import *
from funcoes.regioes import *

from funcoes.video_tracker import VideoTracker 

class PDIApp:
    def __init__(self, master):
        self.master = master
        master.title("Trabalho Prático - PDI (Herich Gabriel)")
        master.geometry("1200x720")
        master.configure(bg="#222")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.original_img = None
        self.img = None
        self.resizing = False
        
        self.static_original_img = None 
        self.cap = None                 
        self.feed_active = False      
        self.active_operation = None    

        self.tracker_manager = VideoTracker()
        self.tracking_mode = "none" 

        self.create_menu()
        self.create_popup_button_bar()

        main_content_frame = Frame(self.master, bg="#222")
        main_content_frame.pack(fill=BOTH, expand=True)

        left_panel = Frame(main_content_frame, width=290, bg="#222")
        left_panel.pack(side=LEFT, fill=Y, padx=10, pady=(20, 10)) 
        left_panel.pack_propagate(False) 

        self.frame_imagens = Frame(main_content_frame, bg="#222")
        self.frame_imagens.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10), pady=(0, 10))
        
        self.frame_imagens.bind("<Configure>", self.on_resize)

        self.create_dual_canvas_content(self.frame_imagens)
        self.create_tabs(left_panel)
        
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Chamado quando a janela principal é fechada."""
        print("Fechando a aplicação...")
        self.stop_feed() 
        self.master.destroy()

    def on_resize(self, event):
        if self.resizing:
            return
        self.resizing = True
        self.master.after(200, self._update_resize)

    def _update_resize(self):
        if self.original_img is not None and self.img is not None:
            orig_w = self.canvas_original.winfo_width()
            orig_h = self.canvas_original.winfo_height()
            proc_w = self.canvas_resultado.winfo_width()
            proc_h = self.canvas_resultado.winfo_height()
            if orig_w <= 1 or proc_w <= 1:
                self.resizing = False
                return
            target_w = min(orig_w, proc_w)
            target_h = min(orig_h, proc_h)
            self.show_images(self.original_img, self.img, target_w, target_h)
        self.resizing = False

    def create_menu(self):
        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        arquivo_menu = Menu(menubar, tearoff=0)
        arquivo_menu.add_command(label="Abrir Imagem", command=self.open_image)
        arquivo_menu.add_command(label="Salvar Resultado", command=self.save_image_auto)
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Sair", command=self.on_closing)
        menubar.add_cascade(label="Arquivo", menu=arquivo_menu)

    def create_dual_canvas_content(self, parent_frame):
        labels_frame = Frame(parent_frame, bg="#222")
        labels_frame.pack(fill=X, pady=(20, 5)) 
        Label(labels_frame, text="Original", bg="#222", fg="#ccc", font=("Arial", 11, "bold")).pack(side=LEFT, fill=X, expand=True)
        Label(labels_frame, text="Processada", bg="#222", fg="#ccc", font=("Arial", 11, "bold")).pack(side=LEFT, fill=X, expand=True)
        canvas_container = Frame(parent_frame, bg="#222")
        canvas_container.pack(fill=BOTH, expand=True, pady=(0, 10))
        ttk.Separator(canvas_container, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5)
        self.canvas_original = Label(canvas_container, bg="#333")
        self.canvas_original.pack(side=LEFT, expand=True, fill=BOTH, padx=5)
        self.canvas_resultado = Label(canvas_container, bg="#333")
        self.canvas_resultado.pack(side=LEFT, expand=True, fill=BOTH, padx=5)

    def create_tabs(self, parent_frame):
        notebook = ttk.Notebook(parent_frame)
        notebook.pack(fill=BOTH, expand=True)
        self.tab_conversoes = Frame(notebook, bg="#111")
        self.tab_filtros = Frame(notebook, bg="#111")
        self.tab_analises = Frame(notebook, bg="#111")
        notebook.add(self.tab_conversoes, text="Conversões")
        notebook.add(self.tab_filtros, text="Filtros e Morfologia")
        notebook.add(self.tab_analises, text="Análises")
        self.create_tab_conversoes()
        self.create_tab_filtros()
        self.create_tab_analises()
    
    def create_popup_button_bar(self):
        bottom_frame = Frame(self.master, bg="#111", height=50)
        bottom_frame.pack(side=BOTTOM, fill=X)
        bottom_frame.pack_propagate(False)
        self.btn_actions = Button(bottom_frame, text="☰ Ações e Vídeo", 
                                  bg="#007bff", fg="white", 
                                  font=("Arial", 12, "bold"), 
                                  command=self.open_actions_popup)
        self.btn_actions.pack(pady=8)

    def open_actions_popup(self):
        popup = Toplevel(self.master)
        popup.title("Ações")
        popup.geometry("300x450") 
        popup.configure(bg="#222")
        popup.resizable(False, False)
        popup.transient(self.master) 
        popup.grab_set() 
        
        try:
            x = self.master.winfo_x()
            y = self.master.winfo_y()
            w = self.master.winfo_width()
            h = self.master.winfo_height()
            popup.geometry(f"+{x + (w // 2) - 150}+{y + (h // 2) - 225}")
        except: pass 

        Label(popup, text="Arquivo", bg="#222", fg="#fff", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        Button(popup, text="📤 Inserir Imagem", bg="#007bff", fg="white", width=25, command=self.open_image).pack(pady=3)
        Button(popup, text="🔁 Restaurar Original", bg="#ffc107", fg="black", width=25, command=self.restore_original).pack(pady=3)
        Button(popup, text="💾 Salvar Resultado", bg="#28a745", fg="white", width=25, command=self.save_image_auto).pack(pady=3)
        
        ttk.Separator(popup, orient=HORIZONTAL).pack(fill=X, padx=20, pady=15)

        Label(popup, text="Fonte de Vídeo (Req. 2)", bg="#222", fg="#fff", font=("Arial", 12, "bold")).pack(pady=5)
        
        Button(popup, text="📹 Abrir Câmera", width=25, command=self.start_camera_feed).pack(pady=3)
        Button(popup, text="🎞️ Abrir Arquivo de Vídeo", width=25, command=self.start_video_file_feed).pack(pady=3)

        btn_stop_text = "⏹️ Fechar Vídeo/Câmera"
        btn_stop_color_bg = "#dc3545" if self.feed_active else None
        btn_stop_color_fg = "white" if self.feed_active else "black"
        
        btn_stop = Button(popup, text=btn_stop_text,
                          fg=btn_stop_color_fg,
                          width=25, command=self.stop_feed)
        if btn_stop_color_bg:
            btn_stop.config(bg=btn_stop_color_bg)
        btn_stop.pack(pady=3)
        
        ttk.Separator(popup, orient=HORIZONTAL).pack(fill=X, padx=20, pady=15)
        
        Label(popup, text="Operações de Vídeo (Req. 6)", bg="#222", fg="#fff", font=("Arial", 12, "bold")).pack(pady=5)
        
        btn_track_text = "Parar Rastreamento" if self.tracking_mode == "generic" else "🎯 Rastrear Objeto (6a)"
        btn_track_color = "#ffc107" if self.tracking_mode == "generic" else None
        btn_track = Button(popup, text=btn_track_text, width=25, 
                           command=self.toggle_generic_tracking_from_popup)
        if btn_track_color:
            btn_track.config(bg=btn_track_color)
        btn_track.pack(pady=3)

        btn_pou_text = "Parar Detector Pou" if self.tracking_mode == "pou" else "👽 Detectar Pou (6b)"
        btn_pou_color = "#ffc107" if self.tracking_mode == "pou" else None
        btn_pou = Button(popup, text=btn_pou_text, width=25, 
                         command=self.toggle_pou_detection_from_popup)
        if btn_pou_color:
            btn_pou.config(bg=btn_pou_color)
        btn_pou.pack(pady=3)
        
        ttk.Separator(popup, orient=HORIZONTAL).pack(fill=X, padx=20, pady=15)
        Button(popup, text="Fechar", width=15, command=popup.destroy).pack(pady=5)
    
    def set_tracking_mode(self, new_mode):
        if self.tracking_mode == "generic" and new_mode != "generic":
            self.tracker_manager.stop_generic_tracker()
        if self.tracking_mode == "pou" and new_mode != "pou":
            self.tracker_manager.stop_pou_detector()
        self.tracking_mode = new_mode
        if new_mode != "none":
            self.active_operation = None
    
    def toggle_generic_tracking_from_popup(self):
        if self.tracking_mode == "generic":
            self.set_tracking_mode("none")
            messagebox.showinfo("Rastreamento", "Rastreamento genérico parado.", parent=self.master)
        
        elif self.feed_active and self.original_img is not None:
            self.feed_active = False 
            if self.tracker_manager.start_generic_tracker(self.original_img):
                self.set_tracking_mode("generic")
                messagebox.showinfo("Rastreamento", "Objeto selecionado. Rastreamento iniciado.", parent=self.master)
            self.feed_active = True 
            self.update_video_feed() 
        elif not self.feed_active:
            messagebox.showwarning("Aviso", "Abra a câmera ou um vídeo antes de rastrear.", parent=self.master)
        self.close_popup()

    def toggle_pou_detection_from_popup(self):
        if self.tracking_mode == "pou":
            self.set_tracking_mode("none")
            messagebox.showinfo("Detector", "Detector do Pou desligado.", parent=self.master)
        else:
            if not self.feed_active:
                 messagebox.showwarning("Aviso", "Abra e a câmera ou um vídeo antes de detectar.", parent=self.master)
                 return
            self.set_tracking_mode("pou")
            messagebox.showinfo("Detector", "Detector do Pou ATIVADO.", parent=self.master)
        self.close_popup()
    
    def create_tab_conversoes(self):
        f = self.tab_conversoes
        Label(f, text="Conversões", bg="#111", fg="#fff", font=("Arial", 12, "bold")).pack(pady=5)
        Button(f, text="Cinza", command=self.apply_gray, width=25).pack(pady=2)
        Button(f, text="Negativo", command=self.apply_negative, width=25).pack(pady=2)
        Button(f, text="Otsu (Binária)", command=self.apply_otsu, width=25).pack(pady=2)
        Button(f, text="Logarítmica", command=self.apply_log, width=25).pack(pady=2)
        Label(f, text="Potência (γ)", bg="#111", fg="#fff", font=("Arial", 12, "bold")).pack(pady=5)
        self.gamma_slider = Scale(f, from_=0.1, to=3.0, resolution=0.1,
                                  orient=HORIZONTAL, length=200, bg="#111",
                                  fg="#fff", troughcolor="#444")
        self.gamma_slider.set(1.0)
        self.gamma_slider.pack(pady=5)
        Button(f, text="Aplicar Potência", command=self.apply_power, width=25).pack(pady=2)

    def create_tab_filtros(self):
        f = self.tab_filtros
        Label(f, text="Filtros", bg="#111", fg="#fff", font=("Arial", 12, "bold")).pack(pady=5)
        Button(f, text="Suavização pela Média", command=self.apply_media, width=25).pack(pady=2)
        Button(f, text="Suavização pela Mediana", command=self.apply_mediana, width=25).pack(pady=2)
        Label(f, text="Tamanho do kernel", bg="#111", fg="#fff").pack()
        self.kernel_slider = Scale(f, from_=3, to=15, resolution=2, orient=HORIZONTAL,
                                     length=200, bg="#111", fg="#fff", troughcolor="#444")
        self.kernel_slider.set(5)
        self.kernel_slider.pack(pady=3)
        Button(f, text="Detector de Canny", command=self.apply_canny, width=25).pack(pady=10)
        Label(f, text="Morfologia", bg="#111", fg="#fff", font=("Arial", 12, "bold")).pack(pady=5)
        Button(f, text="Erosão", command=self.apply_erosao, width=25).pack(pady=2)
        Button(f, text="Dilatação", command=self.apply_dilatacao, width=25).pack(pady=2)
        Button(f, text="Abertura", command=self.apply_abertura, width=25).pack(pady=2)
        Button(f, text="Fechamento", command=self.apply_fechamento, width=25).pack(pady=2)

    def create_tab_analises(self):
        f = self.tab_analises
        Label(f, text="Análises", bg="#111", fg="#fff", font=("Arial", 12, "bold")).pack(pady=5)
        Button(f, text="Exibir Histograma", command=self.show_hist, width=25).pack(pady=2)
        Button(f, text="Calcular Área/Perímetro", command=self.show_measures, width=25).pack(pady=5)
        Button(f, text="Contar Objetos", command=self.show_object_count, width=25).pack(pady=5)

    def start_camera_feed(self):
        """Prepara o feed da webcam e pergunta o que fazer."""
        self.stop_feed() 
        
        cap = cv2.VideoCapture(0) 
        if not cap.isOpened():
            cap = cv2.VideoCapture(1)
            if not cap.isOpened():
                messagebox.showerror("Erro de Câmera", "Não foi possível acessar a câmera (0 ou 1).")
                return
        
        self.cap = cap
        self.close_popup()
        self.prompt_video_action() 

    def start_video_file_feed(self):
        """Abre um arquivo de vídeo e pergunta o que fazer."""
        self.stop_feed()
        
        file_path = filedialog.askopenfilename(filetypes=[("Vídeos", "*.mp4 *.avi *.mkv *.mov")])
        if not file_path:
            return
            
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            messagebox.showerror("Erro ao Abrir Vídeo", f"Não foi possível ler o arquivo:\n{file_path}")
            return
            
        self.cap = cap
        self.close_popup()
        self.prompt_video_action() 
        
    def prompt_video_action(self):
        """Mostra um popup perguntando qual ação de vídeo executar."""
        
        self.close_popup() 
        
        popup = Toplevel(self.master)
        popup.title("Ação de Vídeo")
        popup.geometry("300x200")
        popup.configure(bg="#222")
        popup.resizable(False, False)
        popup.transient(self.master)
        popup.grab_set()
        
        try:
            x = self.master.winfo_x()
            y = self.master.winfo_y()
            w = self.master.winfo_width()
            h = self.master.winfo_height()
            popup.geometry(f"+{x + (w // 2) - 150}+{y + (h // 2) - 100}")
        except: pass

        Label(popup, text="Qual ação executar?", bg="#222", fg="#fff", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        def _select_action(action):
            popup.destroy()
            self._start_feed(action)

        Button(popup, text="Apenas Reproduzir", width=25, command=lambda: _select_action("none")).pack(pady=5)
        Button(popup, text="🎯 Rastrear Objeto (6a)", width=25, command=lambda: _select_action("generic")).pack(pady=5)
        Button(popup, text="👽 Detectar Pou (6b)", width=25, command=lambda: _select_action("pou")).pack(pady=5)
        
        def _on_close_prompt():
            self.stop_feed() 
            popup.destroy()
        
        popup.protocol("WM_DELETE_WINDOW", _on_close_prompt)

    def _start_feed(self, mode):
        """Função interna para iniciar o loop de feed com o modo selecionado."""
        if not self.cap or not self.cap.isOpened():
            print("Erro: _start_feed chamado sem um 'cap' válido.")
            return

        if self.original_img is not None:
            self.static_original_img = self.original_img.copy()

        if mode == "generic":
            ret, frame = self.cap.read()
            if not ret:
                messagebox.showerror("Erro de Vídeo", "Não foi possível ler o primeiro frame do vídeo.")
                self.stop_feed()
                return

            if self.tracker_manager.start_generic_tracker(frame):
                self.set_tracking_mode("generic")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                self.stop_feed()
                return
        else:
            self.set_tracking_mode(mode)
        
        self.feed_active = True
        self.update_video_feed()

    def stop_feed(self):
        """Para qualquer feed de vídeo ou câmera que esteja ativo."""
        self.feed_active = False
        if self.cap:
            self.cap.release()
        self.cap = None
        
        self.set_tracking_mode("none") 
        
        if self.static_original_img is not None:
            self.original_img = self.static_original_img.copy()
            self.img = self.apply_active_operation(self.original_img.copy(), use_cv=False)
            self._update_resize()
        else:
            self.original_img = None
            self.img = None
            empty_img = ImageTk.PhotoImage(Image.new("RGB", (1, 1), "black"))
            self.canvas_original.config(image=empty_img)
            self.canvas_resultado.config(image=empty_img)
            self.canvas_original.image = empty_img 
            self.canvas_resultado.image = empty_img 

        self.close_popup()
        
    def close_popup(self):
        """Fecha qualquer popup de Ações aberto."""
        try:
            for w in self.master.winfo_children():
                if isinstance(w, Toplevel) and (w.title() == "Ações" or w.title() == "Ação de Vídeo"):
                    w.destroy()
        except: pass

    def update_video_feed(self):
        if not self.feed_active or not self.cap:
            return

        ret, frame = self.cap.read()
        
        if not ret:
            print("Fim do vídeo.")
            self.stop_feed()
            messagebox.showinfo("Fim do Vídeo", "A reprodução do vídeo terminou.")
            return

        try:
            if self.cap.get(cv2.CAP_PROP_BACKEND) == cv2.CAP_V4L2: 
                 frame = cv2.flip(frame, 1)
        except:
             pass 

        self.original_img = frame.copy()
        processed_frame = self.apply_active_operation(frame.copy(), use_cv=True)
        
        if len(processed_frame.shape) == 2:
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)

        final_processed_frame = processed_frame 
        
        if self.tracking_mode == "generic":
            final_processed_frame = self.tracker_manager.update_generic_tracker(processed_frame)
        elif self.tracking_mode == "pou":
            final_processed_frame = self.tracker_manager.detect_pou(processed_frame)

        self.img = final_processed_frame
        
        orig_w = self.canvas_original.winfo_width() or 480
        orig_h = self.canvas_original.winfo_height() or 670
        proc_w = self.canvas_resultado.winfo_width() or 480
        proc_h = self.canvas_resultado.winfo_height() or 670
        target_w = min(orig_w, proc_w)
        target_h = min(orig_h, proc_h)
        
        self.show_images(self.original_img, self.img, target_w, target_h)
        
        self.master.after(20, self.update_video_feed)

    def apply_active_operation(self, frame, use_cv=True):
        op = self.active_operation
        if self.tracking_mode != "none":
            return frame
        if op is None:
            return frame
        try:
            if op == "gray":
                return to_gray_cv(frame) if use_cv else to_gray_manual(frame)
            if op == "negative":
                return negative(frame) 
            if op == "otsu":
                return otsu_threshold_cv(frame) if use_cv else otsu_threshold_manual(frame)
            if op == "log":
                return log_transform(frame) 
            if op == "power":
                gamma = float(self.gamma_slider.get())
                return power_transform(frame, gamma) 
            if op == "media":
                k = int(self.kernel_slider.get())
                return filtro_media_cv(frame, k) if use_cv else filtro_media_manual(frame, k)
            if op == "mediana":
                k = int(self.kernel_slider.get())
                return filtro_mediana_cv(frame, k) if use_cv else filtro_mediana_manual(frame, k)
            if op == "canny":
                return filtro_canny_cv(frame) 
            if op == "erosao":
                return morf_erosao_cv(frame) if use_cv else morf_erosao_manual(frame)
            if op == "dilatacao":
                return morf_dilatacao_cv(frame) if use_cv else morf_dilatacao_manual(frame)
            if op == "abertura":
                return morf_abertura_cv(frame) if use_cv else morf_abertura_manual(frame)
            if op == "fechamento":
                return morf_fechamento_cv(frame) if use_cv else morf_fechamento_manual(frame)
        except Exception as e:
            print(f"Erro na operação '{op}' (CV={use_cv}): {e}")
            return frame
        return frame

    def open_image(self):
        self.stop_feed() 
        file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif")])
        if not file_path:
            return
        self.original_img = cv2.imread(file_path)
        if self.original_img is None:
            messagebox.showerror("Erro ao Abrir", 
                                 f"Não foi possível ler o arquivo:\n{file_path}\n\n"
                                 "Certifique-se de que é um arquivo de imagem válido.")
            return 
        self.static_original_img = self.original_img.copy() 
        self.img = self.original_img.copy()
        self.active_operation = None 
        self.master.after(100, self._update_resize)

    def restore_original(self):
        self.active_operation = None 
        self.set_tracking_mode("none") 
        if self.feed_active:
            return 
        if self.original_img is not None:
            self.img = self.original_img.copy()
            self.master.after(100, self._update_resize)

    def show_images(self, original, processed, target_w, target_h):
        if target_w <= 1 or target_h <= 1:
            return 
        def _to_rgb_safe(img):
            if len(img.shape) == 2: 
                return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 3: 
                return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img 
        rgb_orig = _to_rgb_safe(original)
        rgb_proc = _to_rgb_safe(processed)
        def resize_keep_aspect(img, max_w, max_h):
            h, w = img.shape[:2]
            ratio = min(max_w / w, max_h / h)
            new_size = (int(w * ratio), int(h * ratio))
            resized = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
            return Image.fromarray(resized)
        
        try:
            im_pil_orig = resize_keep_aspect(rgb_orig, target_w, target_h)
            im_pil_proc = resize_keep_aspect(rgb_proc, target_w, target_h)
            
            self.tk_img_orig = ImageTk.PhotoImage(image=im_pil_orig)
            self.tk_img_proc = ImageTk.PhotoImage(image=im_pil_proc)

            self.canvas_original.config(image=self.tk_img_orig)
            self.canvas_resultado.config(image=self.tk_img_proc)
            
            # Guarda as referências para evitar o "garbage collector"
            self.canvas_original.image = self.tk_img_orig
            self.canvas_resultado.image = self.tk_img_proc
            
        except Exception as e:
            print(f"Erro ao exibir imagem (provavelmente fechando): {e}")

    def save_image_auto(self):
        if self.img is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada!")
            return
        os.makedirs("resultados", exist_ok=True)
        filename = f"resultado_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join("resultados", filename)
        cv2.imwrite(path, self.img)
        messagebox.showinfo("Salvo", f"Imagem salva em:\n{path}")

    def apply_gray(self):
        self.active_operation = "gray"
        self.set_tracking_mode("none") 
        if not self.feed_active: 
            if self.img is None: return
            self.img = to_gray_manual(self.img) 
            self._update_resize()
            
    def apply_negative(self):
        self.active_operation = "negative"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            self.img = negative(self.img) 
            self._update_resize()
            
    def apply_otsu(self):
        self.active_operation = "otsu"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            self.img = otsu_threshold_manual(self.img) 
            self._update_resize()
            
    def apply_log(self):
        self.active_operation = "log"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            self.img = log_transform(self.img) 
            self._update_resize()
            
    def apply_power(self):
        self.active_operation = "power"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            gamma = float(self.gamma_slider.get())
            self.img = power_transform(self.img, gamma) 
            self._update_resize()
            
    def apply_media(self):
        self.active_operation = "media"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            k = int(self.kernel_slider.get())
            self.img = filtro_media_manual(self.img, k) 
            self._update_resize()
            
    def apply_mediana(self):
        self.active_operation = "mediana"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            k = int(self.kernel_slider.get())
            self.img = filtro_mediana_manual(self.img, k) 
            self._update_resize()
            
    def apply_canny(self):
        self.active_operation = "canny"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            self.img = filtro_canny_cv(self.img) 
            self._update_resize()
            
    def apply_erosao(self):
        self.active_operation = "erosao"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            self.img = morf_erosao_manual(self.img) 
            self._update_resize()
            
    def apply_dilatacao(self):
        self.active_operation = "dilatacao"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            self.img = morf_dilatacao_manual(self.img) 
            self._update_resize()
            
    def apply_abertura(self):
        self.active_operation = "abertura"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            self.img = morf_abertura_manual(self.img) 
            self._update_resize()
            
    def apply_fechamento(self):
        self.active_operation = "fechamento"
        self.set_tracking_mode("none") 
        if not self.feed_active:
            if self.img is None: return
            self.img = morf_fechamento_manual(self.img) 
            self._update_resize()

    def show_hist(self):
        if self.img is None: return
        gray = to_gray_manual(self.img.copy()) 
        hist, _, _, _ = calculate_histograms(gray)
        plt.figure("Histograma")
        plt.bar(range(256), hist, color='gray')
        plt.title("Histograma da Imagem")
        plt.xlabel("Intensidade")
        plt.ylabel("Frequência")
        plt.show()
        
    def show_measures(self):
        if self.img is None: return
        binary = otsu_threshold_manual(self.img.copy()) 
        area, perimetro, diametro = medidas_objetos(binary)
        messagebox.showinfo("Medidas", f"Medidas do maior objeto (Otsu):\n\nÁrea: {area}\nPerímetro: {perimetro}\nDiâmetro: {diametro}")
        
    def show_object_count(self):
        if self.img is None: return
        binary = otsu_threshold_manual(self.img.copy()) 
        num, boxes = contar_objetos(binary)
        img_para_desenhar = self.img.copy()
        if len(img_para_desenhar.shape) == 2:
            img_para_desenhar = cv2.cvtColor(img_para_desenhar, cv2.COLOR_GRAY2BGR)
        elif img_para_desenhar.shape[2] == 4:
            img_para_desenhar = cv2.cvtColor(img_para_desenhar, cv2.COLOR_BGRA2BGR)
        color = (0, 255, 0) 
        thickness = 2
        for (x1, y1, x2, y2) in boxes:
            cv2.rectangle(img_para_desenhar, (x1, y1), (x2, y2), color, thickness)
        self.img = img_para_desenhar 
        self._update_resize()
        messagebox.showinfo("Contagem de Objetos", f"Quantidade de objetos encontrados: {num}")