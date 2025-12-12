# state.py
import time
from config import *

class GameState:
    def __init__(self):
        self.reset_game_data()
        
        self.current_screen = 'MAIN_MENU' 
        self.selected_mode = 'CLASSIC'
        self.selected_difficulty = 'MEDIO'
        
        # Controle de qual tecla estamos trocando (bind)
        self.binding_action = None 
        
        # Câmera
        self.target_angle = 0.0
        self.last_rotation_time = 0
        self.slow_mo_start_time = 0
        self.inspect_rot_x = 20.0
        self.inspect_rot_y = 0.0
        self.inspect_zoom = ORTHO_ZOOM
        
        # Estado do Player 2 (Spawner)
        self.p2_last_drop_time = 0

    def reset_game_data(self):
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.victory = False

    def start_game(self):
        self.reset_game_data()
        self.current_screen = 'PLAYING'
        self.lives = MODES[self.selected_mode]['lives']
        self.inspect_rot_x, self.inspect_rot_y = 20.0, 0.0

    def take_damage(self):
        if self.selected_mode in ['SURVIVAL', 'VERSUS']:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.victory = False # P2 ganhou
                return True
        return False
    
    def p2_can_drop(self):
        now = time.time()
        if now - self.p2_last_drop_time >= P2_DROP_COOLDOWN:
            self.p2_last_drop_time = now
            return True
        return False

    def request_rotation(self, direction):
        if self.current_screen != 'PLAYING' or self.game_over: return False
        now = time.time()
        if now - self.last_rotation_time < CAMERA_COOLDOWN: return False
        if direction == 'LEFT': self.target_angle -= 90
        elif direction == 'RIGHT': self.target_angle += 90
        self.last_rotation_time = now
        self.slow_mo_start_time = now
        return True

    def get_time_scale(self):
        if self.current_screen in ['PAUSE_MENU', 'INSPECT', 'MAIN_MENU', 'SETTINGS_MENU', 'BINDING_KEY']: return 0.0
        if self.game_over: return 0.0
        now = time.time()
        if now - self.slow_mo_start_time < SLOW_MO_DURATION: return SLOW_MO_FACTOR
        return 1.0
    
    def get_current_settings(self):
        return DIFFICULTIES[self.selected_difficulty]