# objects.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
from config import *

class Player:
    def __init__(self):
        self.x = 0.0
        self.z = 0.0
    
    def move_relative(self, direction, camera_angle):
        angle = camera_angle % 360
        dx, dz = 0, 0
        if angle == 0: dx = direction; dz = 0
        elif angle == 90: dx = 0; dz = direction
        elif angle == 180: dx = -direction; dz = 0
        elif angle == 270: dx = 0; dz = -direction
        self.move_grid(dx, dz)

    def move_grid(self, dx, dz):
        new_x = self.x + (dx * GRID_STEP)
        new_z = self.z + (dz * GRID_STEP)
        limit = (GRID_WIDTH - 1) / 2 
        if -limit <= new_x <= limit: self.x = new_x
        if -limit <= new_z <= limit: self.z = new_z

    def draw(self, texture_id):
        glPushMatrix()
        glTranslatef(self.x, 0.5, self.z)
        glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # O Pou continua BRANCO
        glColor3f(1.0, 1.0, 1.0) 
        
        s = 0.45 
        glBegin(GL_QUADS)
        glNormal3f(0,0,1); glTexCoord2f(0,0); glVertex3f(-s,-s,s); glTexCoord2f(1,0); glVertex3f(s,-s,s); glTexCoord2f(1,1); glVertex3f(s,s,s); glTexCoord2f(0,1); glVertex3f(-s,s,s)
        glNormal3f(0,0,-1); glTexCoord2f(0,0); glVertex3f(s,-s,-s); glTexCoord2f(1,0); glVertex3f(-s,-s,-s); glTexCoord2f(1,1); glVertex3f(-s,s,-s); glTexCoord2f(0,1); glVertex3f(s,s,-s)
        glNormal3f(1,0,0); glTexCoord2f(0,0); glVertex3f(s,-s,s); glTexCoord2f(1,0); glVertex3f(s,-s,-s); glTexCoord2f(1,1); glVertex3f(s,s,-s); glTexCoord2f(0,1); glVertex3f(s,s,s)
        glNormal3f(-1,0,0); glTexCoord2f(0,0); glVertex3f(-s,-s,-s); glTexCoord2f(1,0); glVertex3f(-s,-s,s); glTexCoord2f(1,1); glVertex3f(-s,s,s); glTexCoord2f(0,1); glVertex3f(-s,s,-s)
        glNormal3f(0,1,0); glTexCoord2f(0,0); glVertex3f(-s,s,s); glTexCoord2f(1,0); glVertex3f(s,s,s); glTexCoord2f(1,1); glVertex3f(s,s,-s); glTexCoord2f(0,1); glVertex3f(-s,s,-s)
        glNormal3f(0,-1,0); glTexCoord2f(0,0); glVertex3f(-s,-s,-s); glTexCoord2f(1,0); glVertex3f(s,-s,-s); glTexCoord2f(1,1); glVertex3f(s,-s,s); glTexCoord2f(0,1); glVertex3f(-s,-s,s)
        glEnd(); glDisable(GL_TEXTURE_2D); glPopMatrix()

class StarManager:
    def __init__(self):
        self.stars = []
        self.spawn_timer = 0.0
        self.quadric = gluNewQuadric()
        gluQuadricTexture(self.quadric, GL_TRUE)
    
    def spawn_random(self):
        limit = int((GRID_WIDTH - 1) / 2)
        x_grid = random.randint(-limit, limit) * GRID_STEP
        z_grid = random.randint(-limit, limit) * GRID_STEP
        self.create_star(x_grid, z_grid)

    def spawn_in_region(self, region_x, region_z):
        start_x_idx = (region_x * 3) - 4
        start_z_idx = (region_z * 3) - 4
        rand_x = random.randint(start_x_idx, start_x_idx + 2)
        rand_z = random.randint(start_z_idx, start_z_idx + 2)
        self.create_star(rand_x * GRID_STEP, rand_z * GRID_STEP)

    def create_star(self, x, z):
        rand_val = random.random(); cumulative = 0; star_type = 'NORMAL'
        for stype, data in STAR_TYPES.items():
            cumulative += data['chance']
            if rand_val <= cumulative: star_type = stype; break
        self.stars.append({'x': float(x), 'y': 15.0, 'z': float(z), 'type': star_type})

    def update(self, time_scale, player, game_state, audio_manager):
        settings = game_state.get_current_settings()
        
        if game_state.selected_mode != 'VERSUS':
            self.spawn_timer += 0.016 * time_scale
            if self.spawn_timer >= settings['spawn_time']: self.spawn_random(); self.spawn_timer = 0.0
        
        speed = settings['speed'] * time_scale; score_increment = 0
        for s in self.stars[:]:
            s['y'] -= speed
            if s['y'] < 1.0 and abs(s['x'] - player.x) < 0.45 and abs(s['z'] - player.z) < 0.45:
                self.stars.remove(s); points = STAR_TYPES[s['type']]['points']; score_increment += points; audio_manager.play_sfx('eat')
            elif s['y'] < -2.0:
                self.stars.remove(s); damage = game_state.take_damage()
                if damage: audio_manager.play_sfx('hurt')
        
        if game_state.selected_mode == 'CLASSIC' and (game_state.score + score_increment) >= WIN_SCORE:
            game_state.game_over = True; game_state.victory = True
        return score_increment

    def draw(self, camera_angle, texture_id, game_state):
        glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, texture_id)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for s in self.stars:
            glPushMatrix(); glTranslatef(s['x'], s['y'], s['z']); glRotatef(s['y'] * 40, 1, 1, 1) 
            
            # Cor da raridade aplicada sobre a textura da comida
            color = STAR_TYPES[s['type']]['color']
            glColor3f(*color) 
            
            gluSphere(self.quadric, 0.4, 16, 16); glPopMatrix()

        glDisable(GL_BLEND); glDisable(GL_TEXTURE_2D)