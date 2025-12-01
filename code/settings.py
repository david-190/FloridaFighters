# Display settings
WIDTH = 1280
HEIGTH = 720
FPS = 60
TILESIZE = 64

# Hitbox adjustments for different sprite types
HITBOX_OFFSET = {
    'player': -26,
    'object': -40,
    'grass': -10,
    'invisible': 0
}

# UI dimensions
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = 'graphics/font/joystix.ttf'
UI_FONT_SIZE = 18
UI_FONT_SIZE_LARGE = 32

# Color palette
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'
HEALTH_COLOR = 'red'
ENERGY_COLOR = 'blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# Upgrade menu colors
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
UPGRADE_BG_COLOR_SELECTED = '#EEEEEE'

# Debug mode
DEBUG_MODE = False 

# Weapon statistics
weapon_data = {
    'pickaxe': {'cooldown': 100, 'damage': 15, 'graphic': 'graphics/weapons/pickaxe/full.png'},
    'staff': {'cooldown': 400, 'damage': 30, 'graphic': 'graphics/weapons/staff/full.png'},
    'axe': {'cooldown': 300, 'damage': 20, 'graphic': 'graphics/weapons/axe/full.png'},
    'ninjaku': {'cooldown': 50, 'damage': 8, 'graphic': 'graphics/weapons/ninjaku/full.png'},
    'mace': {'cooldown': 80, 'damage': 10, 'graphic': 'graphics/weapons/mace/full.png'}
}

# Magic abilities
magic_data = {
    'flame': {'strength': 15, 'cost': 20, 'graphic': 'graphics/particles/flame/fire.png'},
    'heal': {'strength': 20, 'cost': 10, 'graphic': 'graphics/particles/heal/heal.png'}
}

# Enemy attributes
monster_data = {
    'eye': {'health': 200, 'exp': 100, 'damage': 20, 'attack_type': 'slash', 'attack_sound': 'audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 90, 'notice_radius': 460},
    'raccoon': {'health': 300, 'exp': 250, 'damage': 40, 'attack_type': 'claw', 'attack_sound': 'audio/attack/claw.wav', 'speed': 2, 'resistance': 3, 'attack_radius': 140, 'notice_radius': 500},
    'squirrel': {'health': 150, 'exp': 110, 'damage': 10, 'attack_type': 'thunder', 'attack_sound': 'audio/attack/fireball.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 70, 'notice_radius': 400},
    'owl': {'health': 120, 'exp': 120, 'damage': 12, 'attack_type': 'leaf_attack', 'attack_sound': 'audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 60, 'notice_radius': 450}
}