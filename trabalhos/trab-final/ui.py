# ui.py
from OpenGL.GL import *
from OpenGL.GLUT import *
import OpenGL.GLUT as GLUT
import os 
from config import VOLUME, CONTROLS

class UI:
    def __init__(self):
        self.menus = {
            'MAIN_MENU': ["JOGAR", "CONFIGURACOES", "SAIR"],
            'PLAY_MENU': ["CLASSICO", "SOBREVIVENCIA", "VERSUS (P1 x P2)", "VOLTAR"],
            'DIFFICULTY_MENU': ["FACIL", "MEDIO", "DIFICIL", "VOLTAR"],
            'PAUSE_MENU': ["RESUMIR", "VISUALIZAR 3D", "CONFIGURACOES", "MENU PRINCIPAL"],
            'SETTINGS_MENU': [
                "MUSICA: ", "SFX: ", 
                "P1 ESQUERDA: ", "P1 DIREITA: ", 
                "VOLTAR"
            ]
        }
        self.selected_index = 0
        self.previous_screen = 'MAIN_MENU'
        
    def reset_selection(self):
        self.selected_index = 0

    def draw_text(self, x, y, text, color=(1, 1, 1), size='SMALL'):
        glColor3f(*color)
        glRasterPos2f(x, y)
        font = GLUT.GLUT_BITMAP_HELVETICA_18 if size == 'SMALL' else GLUT.GLUT_BITMAP_TIMES_ROMAN_24
        for char in text:
            glutBitmapCharacter(font, ord(char))
    
    def get_key_name(self, key_bytes):
        s = str(key_bytes).replace("b'", "").replace("'", "").upper()
        if s == "\\R": return "ENTER"; 
        if s == " ": return "ESPACO"
        return s

    def draw_ui(self, width, height, game_state):
        glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST); glDisable(GL_TEXTURE_2D)
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

        if game_state.current_screen in ['PLAYING', 'PAUSE_MENU', 'INSPECT', 'SETTINGS_MENU']:
            if game_state.score > 0 or game_state.lives < 3 or game_state.selected_mode == 'VERSUS':
                self.draw_text(20, height - 40, f"SCORE: {game_state.score}", (1, 1, 0), 'BIG')
                if game_state.selected_mode in ['SURVIVAL', 'VERSUS']:
                    lives_text = "VIDAS: " + ("<3 " * game_state.lives)
                    self.draw_text(width - 150, height - 40, lives_text, (0, 1, 0))

            if game_state.current_screen == 'INSPECT':
                self.draw_text(width/2 - 120, 50, "MODO VISUALIZACAO", (0, 1, 1), 'BIG')
                self.draw_text(width/2 - 150, 20, "Mouse: Girar | ESC: Voltar", (1, 1, 1))
            
            if game_state.game_over:
                msg = "P2 VENCEU!" if game_state.selected_mode == 'VERSUS' and not game_state.victory else "GAME OVER"
                if game_state.victory and game_state.selected_mode == 'CLASSIC': msg = "VOCE VENCEU!"
                self.draw_text(width/2 - 60, height/2, msg, (1, 0, 0), 'BIG')
                self.draw_text(width/2 - 90, height/2 - 30, "ENTER para Menu", (1, 1, 1))

        if game_state.current_screen == 'BINDING_KEY':
            action_name = game_state.binding_action.replace('_', ' ')
            self.draw_text(width/2 - 200, height/2, f"PRESSIONE NOVA TECLA PARA: {action_name}", (1, 1, 0), 'BIG')

        elif game_state.current_screen not in ['PLAYING', 'INSPECT', 'BINDING_KEY']:
            options = self.menus.get(game_state.current_screen, [])
            if game_state.current_screen in ['PAUSE_MENU', 'SETTINGS_MENU']:
                glEnable(GL_BLEND); glColor4f(0, 0, 0, 0.8)
                glBegin(GL_QUADS); glVertex2f(0, 0); glVertex2f(width, 0); glVertex2f(width, height); glVertex2f(0, height); glEnd()
                glDisable(GL_BLEND)

            self.draw_text(width/2 - 100, height/2 + 200, "MENU", (1, 1, 0), 'BIG')

            start_y = height/2 + 100 
            spacing = 35

            for i, option in enumerate(options):
                color = (0, 1, 0) if i == self.selected_index else (0.5, 0.5, 0.5)
                prefix = "> " if i == self.selected_index else "  "
                display_text = prefix + option
                
                if game_state.current_screen == 'SETTINGS_MENU':
                    if "MUSICA" in option: display_text += f"{int(VOLUME['MUSIC']*100)}%"
                    elif "SFX" in option: display_text += f"{int(VOLUME['SFX']*100)}%"
                    elif "P1 ESQUERDA" in option: display_text += self.get_key_name(CONTROLS['LEFT'])
                    elif "P1 DIREITA" in option: display_text += self.get_key_name(CONTROLS['RIGHT'])

                self.draw_text(width/2 - 100, start_y - (i * spacing), display_text, color)
                
                if game_state.current_screen == 'SETTINGS_MENU' and i == self.selected_index and ("MUSICA" in option or "SFX" in option):
                     self.draw_text(width/2 + 150, start_y - (i * spacing), "< Setas >", (0.3, 0.3, 0.3))

        glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)

    def navigate(self, direction, game_state):
        options = self.menus.get(game_state.current_screen, [])
        if not options: return
        self.selected_index += direction
        if self.selected_index < 0: self.selected_index = len(options) - 1
        elif self.selected_index >= len(options): self.selected_index = 0

    def adjust_volume(self, direction, game_state, audio_manager):
        options = self.menus['SETTINGS_MENU']
        selected = options[self.selected_index]
        change = 0.1 * direction
        if "MUSICA" in selected:
            VOLUME['MUSIC'] = max(0.0, min(1.0, VOLUME['MUSIC'] + change)); audio_manager.update_music_volume(); audio_manager.play_sfx('blip')
        elif "SFX" in selected:
            VOLUME['SFX'] = max(0.0, min(1.0, VOLUME['SFX'] + change)); audio_manager.play_sfx('blip')

    def select_option(self, game_state, audio_manager):
        options = self.menus.get(game_state.current_screen, [])
        if not options: return
        selection = options[self.selected_index]
        audio_manager.play_sfx('blip')
        
        if game_state.current_screen == 'MAIN_MENU':
            if selection == "JOGAR": game_state.current_screen = 'PLAY_MENU'; self.reset_selection()
            elif selection == "CONFIGURACOES": game_state.current_screen = 'SETTINGS_MENU'; self.previous_screen = 'MAIN_MENU'; self.reset_selection()
            elif selection == "SAIR": os._exit(0)

        elif game_state.current_screen == 'PLAY_MENU':
            if selection == "VOLTAR": game_state.current_screen = 'MAIN_MENU'; self.reset_selection()
            elif selection == "CLASSICO": game_state.selected_mode = "CLASSIC"; game_state.current_screen = 'DIFFICULTY_MENU'; self.reset_selection()
            elif selection == "SOBREVIVENCIA": game_state.selected_mode = "SURVIVAL"; game_state.current_screen = 'DIFFICULTY_MENU'; self.reset_selection()
            elif "VERSUS" in selection: game_state.selected_mode = "VERSUS"; game_state.current_screen = 'DIFFICULTY_MENU'; self.reset_selection()

        elif game_state.current_screen == 'DIFFICULTY_MENU':
            if selection == "VOLTAR": game_state.current_screen = 'PLAY_MENU'; self.reset_selection()
            else: game_state.selected_difficulty = selection; game_state.start_game()

        elif game_state.current_screen == 'PAUSE_MENU':
            if selection == "RESUMIR": game_state.current_screen = 'PLAYING'
            elif selection == "VISUALIZAR 3D": game_state.current_screen = 'INSPECT'
            elif selection == "CONFIGURACOES": game_state.current_screen = 'SETTINGS_MENU'; self.previous_screen = 'PAUSE_MENU'; self.reset_selection()
            elif selection == "MENU PRINCIPAL": game_state.current_screen = 'MAIN_MENU'; self.reset_selection()

        elif game_state.current_screen == 'SETTINGS_MENU':
            if selection == "VOLTAR": game_state.current_screen = self.previous_screen; self.reset_selection()
            elif "P1 ESQUERDA" in selection: game_state.binding_action = 'LEFT'; game_state.current_screen = 'BINDING_KEY'
            elif "P1 DIREITA" in selection: game_state.binding_action = 'RIGHT'; game_state.current_screen = 'BINDING_KEY'