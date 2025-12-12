# audio.py
import pygame
from config import VOLUME

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.current_music = None
        
        # Carrega efeitos sonoros (SFX)
        self.load_sfx('eat', 'eat.mp3')
        self.load_sfx('hurt', 'hurt.mp3')
        self.load_sfx('blip', 'blip.mp3')
        self.load_sfx('win', 'blip.mp3') 

        # Inicia musica padrao
        self.play_music('pou_music.mp3')

    def load_sfx(self, name, filename):
        try:
            sound = pygame.mixer.Sound(filename)
            sound.set_volume(VOLUME['SFX'])
            self.sounds[name] = sound
        except:
            print(f"AVISO: SFX '{filename}' nao encontrado.")

    def play_sfx(self, name):
        if name in self.sounds:
            self.sounds[name].set_volume(VOLUME['SFX'])
            self.sounds[name].play()

    def play_music(self, filename):
        if self.current_music == filename:
            return
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(VOLUME['MUSIC'])
            pygame.mixer.music.play(-1) 
            self.current_music = filename
        except:
            print(f"AVISO: Musica '{filename}' nao encontrada.")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None

    def update_music_volume(self):
        if self.current_music:
            pygame.mixer.music.set_volume(VOLUME['MUSIC'])