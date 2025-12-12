# main.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys, cv2, os
import numpy as np
from config import *
from state import GameState
from objects import Player, StarManager
from ui import UI
from audio import AudioManager

game_state = GameState()
player = Player()
star_manager = StarManager()
ui = UI()
audio_manager = AudioManager()

window_w, window_h = 800, 600
tex_food_id, tex_pou_id = 0, 0
last_mouse_x, last_mouse_y = 0, 0

def load_texture(filename):
    tid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tid)
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        img = np.zeros((64, 64, 3), dtype=np.uint8); img[:] = [255, 0, 255] 
    
    if img is not None:
        if len(img.shape) > 2 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA); fmt = GL_RGBA
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB); fmt = GL_RGB

        img = cv2.flip(img, 0)
        h, w, _ = img.shape
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, fmt, w, h, 0, fmt, GL_UNSIGNED_BYTE, img.tobytes())
    return tid

def init():
    global tex_food_id, tex_pou_id
    # Fundo Azul Celeste (Céu)
    glClearColor(0.4, 0.7, 1.0, 1.0) 
    
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 20.0, 20.0, 1.0]) 
    glEnable(GL_COLOR_MATERIAL); glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    tex_pou_id = load_texture('pou_face.png')
    tex_food_id = load_texture('food.png')

def set_camera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    aspect = window_w / window_h
    zoom = game_state.inspect_zoom if game_state.current_screen == 'INSPECT' else ORTHO_ZOOM
    bottom = -FLOOR_OFFSET; top = (zoom * 2) - FLOOR_OFFSET
    if window_w >= window_h: glOrtho(-zoom * aspect, zoom * aspect, bottom, top, -50, 50)
    else: glOrtho(-zoom, zoom, bottom / aspect, top / aspect, -50, 50)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    if game_state.current_screen == 'INSPECT':
        glRotatef(game_state.inspect_rot_x, 1.0, 0.0, 0.0)
        glRotatef(game_state.inspect_rot_y, 0.0, 1.0, 0.0)
    else:
        glRotatef(12.0, 1.0, 0.0, 0.0) 
        glRotatef(game_state.target_angle, 0.0, 1.0, 0.0)

def draw_cage():
    glDisable(GL_LIGHTING); glLineWidth(1.5)
    w, d = GRID_WIDTH / 2.0, GRID_DEPTH / 2.0
    h_top, h_bot = 16.0, -0.5
    glColor4f(0.3, 0.3, 0.3, 0.5)
    glBegin(GL_LINES)
    for x in [-w, w]:
        for z in [-d, d]: glVertex3f(x, h_bot, z); glVertex3f(x, h_top, z)
    for h in [h_bot, h_top]:
        glVertex3f(-w, h, -d); glVertex3f( w, h, -d)
        glVertex3f( w, h, -d); glVertex3f( w, h,  d)
        glVertex3f( w, h,  d); glVertex3f(-w, h,  d)
        glVertex3f(-w, h,  d); glVertex3f(-w, h, -d)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_floor():
    glDisable(GL_LIGHTING)
    half_width, half_depth = int(GRID_WIDTH / 2), int(GRID_DEPTH / 2)
    glBegin(GL_QUADS); glNormal3f(0, 1, 0)
    for x in range(-half_width, half_width + 1):
        for z in range(-half_depth, half_depth + 1):
            # Chão de Grama (Verde)
            if (x + z) % 2 == 0: glColor3f(0.2, 0.8, 0.2) 
            else: glColor3f(0.1, 0.6, 0.1) 
            glVertex3f(x-0.5, -0.5, z-0.5); glVertex3f(x-0.5, -0.5, z+0.5)
            glVertex3f(x+0.5, -0.5, z+0.5); glVertex3f(x+0.5, -0.5, z-0.5)
    glEnd()
    glEnable(GL_LIGHTING)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if game_state.current_screen not in ['MAIN_MENU', 'PLAY_MENU', 'DIFFICULTY_MENU', 'SETTINGS_MENU', 'BINDING_KEY']:
        set_camera(); draw_floor(); draw_cage()
        player.draw(tex_pou_id) 
        star_manager.draw(game_state.target_angle, tex_food_id, game_state)
    ui.draw_ui(window_w, window_h, game_state)
    glutSwapBuffers()

def update(value):
    if game_state.current_screen == 'PLAYING' and not game_state.game_over:
        time_scale = game_state.get_time_scale()
        score = star_manager.update(time_scale, player, game_state, audio_manager)
        game_state.score += score
        if game_state.game_over:
            audio_manager.stop_music(); audio_manager.play_music('pou_game_over.mp3')
    glutPostRedisplay(); glutTimerFunc(16, update, 0)

def mouse_click(button, state, x, y):
    global last_mouse_x, last_mouse_y
    if state == GLUT_DOWN: last_mouse_x, last_mouse_y = x, y

def mouse_motion(x, y):
    global last_mouse_x, last_mouse_y
    if game_state.current_screen == 'INSPECT':
        game_state.inspect_rot_y += (x - last_mouse_x) * 0.5
        game_state.inspect_rot_x += (y - last_mouse_y) * 0.5
        last_mouse_x, last_mouse_y = x, y; glutPostRedisplay()

def keyboard(key, x, y):
    if game_state.current_screen == 'BINDING_KEY':
        action = game_state.binding_action
        if action in CONTROLS: CONTROLS[action] = key
        game_state.current_screen = 'SETTINGS_MENU'; audio_manager.play_sfx('blip'); return

    if key == b'\x1b' or key == b'p': 
        if game_state.current_screen == 'PLAYING': game_state.current_screen = 'PAUSE_MENU'
        elif game_state.current_screen in ['PAUSE_MENU', 'INSPECT']: game_state.current_screen = 'PLAYING'
        return

    if game_state.game_over:
        if key == b'\r' or key == b'\n':
            game_state.current_screen = 'MAIN_MENU'; game_state.game_over = False
            audio_manager.stop_music(); audio_manager.play_music('pou_music.mp3')
        return

    if game_state.current_screen not in ['PLAYING', 'INSPECT']:
        if key == b'\r' or key == b'\n': ui.select_option(game_state, audio_manager)
        return

    if game_state.current_screen == 'PLAYING':
        if key == CONTROLS['LEFT']: player.move_relative(-1, game_state.target_angle)
        if key == CONTROLS['RIGHT']: player.move_relative(1, game_state.target_angle)
        
        if game_state.selected_mode == 'VERSUS':
            p2_key = None
            try: val = int(key); 
            except: pass
            else:
                if 1 <= val <= 9: p2_key = val

            if p2_key and game_state.p2_can_drop():
                vis_x, vis_z = 0, 0
                if p2_key in [1, 4, 7]: vis_x = -1
                elif p2_key in [2, 5, 8]: vis_x = 0
                elif p2_key in [3, 6, 9]: vis_x = 1
                if p2_key in [7, 8, 9]: vis_z = -1 
                elif p2_key in [4, 5, 6]: vis_z = 0
                elif p2_key in [1, 2, 3]: vis_z = 1 
                
                angle = game_state.target_angle % 360
                final_gx, final_gz = 0, 0
                if angle == 0: final_gx = vis_x; final_gz = vis_z
                elif angle == 90: final_gx = -vis_z; final_gz = vis_x
                elif angle == 180: final_gx = -vis_x; final_gz = -vis_z
                elif angle == 270: final_gx = vis_z; final_gz = -vis_x
                star_manager.spawn_in_region(final_gx + 1, final_gz + 1)
    glutPostRedisplay()

def special_keys(key, x, y):
    if game_state.current_screen == 'SETTINGS_MENU':
        if key == GLUT_KEY_LEFT: ui.adjust_volume(-1, game_state, audio_manager)
        elif key == GLUT_KEY_RIGHT: ui.adjust_volume(1, game_state, audio_manager)
        elif key == GLUT_KEY_UP: ui.navigate(-1, game_state)
        elif key == GLUT_KEY_DOWN: ui.navigate(1, game_state)
        return

    if game_state.current_screen not in ['PLAYING', 'INSPECT']:
        if key == GLUT_KEY_UP: ui.navigate(-1, game_state); audio_manager.play_sfx('blip')
        if key == GLUT_KEY_DOWN: ui.navigate(1, game_state); audio_manager.play_sfx('blip')
        return

    if game_state.current_screen == 'PLAYING':
        if key == GLUT_KEY_LEFT: game_state.request_rotation('LEFT')
        elif key == GLUT_KEY_RIGHT: game_state.request_rotation('RIGHT')
    glutPostRedisplay()

def reshape(w, h):
    global window_w, window_h; window_w, window_h = w, h; glViewport(0, 0, w, h)

def main():
    glutInit(sys.argv); glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_ALPHA)
    glutInitWindowSize(800, 600); glutCreateWindow(b"Coleta de Estrelas - Pou Edition")
    init()
    glutDisplayFunc(display); glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard); glutSpecialFunc(special_keys)
    glutMouseFunc(mouse_click); glutMotionFunc(mouse_motion)
    glutTimerFunc(0, update, 0); glutMainLoop()

if __name__ == "__main__": main()