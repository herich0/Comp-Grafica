# config.py

# Dimensões do Cenário
GRID_WIDTH = 9.0  
GRID_DEPTH = 9.0
GRID_STEP = 1.0

# Gameplay Geral
PLAYER_SPEED_MOVE = 0.15
WIN_SCORE = 500

# Configurações de Câmera
ORTHO_ZOOM = 8.0
FLOOR_OFFSET = 2.0

# Controles Player 1
CONTROLS = {
    'LEFT': b'a',
    'RIGHT': b'd'
}

# Player 2 usa teclas '1' a '9' diretamente no código principal

VOLUME = {
    'MUSIC': 0.5,
    'SFX': 0.5
}

# Cores: (R, G, B). Usamos cores claras para tingir a textura da comida levemente
STAR_TYPES = {
    'NORMAL': {'points': 10, 'color': (1.0, 1.0, 1.0), 'chance': 0.7}, # Branca
    'RARE':   {'points': 30, 'color': (0.5, 1.0, 0.5), 'chance': 0.2}, # Esverdeado
    'EPIC':   {'points': 50, 'color': (1.0, 0.5, 0.5), 'chance': 0.1}  # Avermelhado
}

MODES = {
    'CLASSIC': {'lives': float('inf')},
    'SURVIVAL': {'lives': 3},
    'VERSUS': {'lives': 3} 
}

DIFFICULTIES = {
    'FACIL':   {'spawn_time': 3, 'speed': 0.04},
    'MEDIO':   {'spawn_time': 2, 'speed': 0.05},
    'DIFICIL': {'spawn_time': 1, 'speed': 0.06}
}

SLOW_MO_FACTOR = 0.5
SLOW_MO_DURATION = 0.2
CAMERA_COOLDOWN = 0.3
P2_DROP_COOLDOWN = 0.75 # Cooldown entre apertar botões do P2