---
description: How the game should look like
auto_execution_mode: 1
---

# Aetherbound
## A Zelda-inspired Action RPG in Python

![Aetherbound](graphics/menu/portrait.jpg)

Aetherbound is an engaging top-down action RPG that combines fluid combat mechanics with magical abilities, creating an immersive gaming experience inspired by classic Legend of Zelda games.

## 🎮 Game Features

- **Dynamic Combat System**: 
  - Multiple weapon types with unique attack patterns and cooldowns
  - Magical abilities system with flame and heal spells
  - Strategic combat with invulnerability frames and knockback mechanics
  - Four distinct enemy types with unique AI behaviors

- **Character Progression**:
  - Upgradeable stats (Health, Energy, Attack, Magic, Speed)
  - Experience system with exponential cost scaling
  - Five different weapons to master
  - Interactive upgrade menu system

- **Rich World Design**:
  - Beautiful pixel art graphics with Y-sorting for depth
  - Particle effects for magic, combat, and environmental interactions
  - CSV-based tile map system for level design
  - Camera system that follows the player
  - Atmospheric sound design with positional audio

## 🎯 Controls

- **Movement**: 
  - W: Move up
  - S: Move down
  - A: Move left
  - D: Move right
- **Combat**:
  - H: Use weapon
  - J: Cast magic
  - K: Switch weapon
  - L: Switch magic
- **Menu**: ESC key to access upgrade menu
- **Start/Restart**: Space bar at title screen or death screen

## 🛠 Technical Implementation

### Core Technologies
- **Python 3.x**: Core programming language
- **Pygame**: Game development library for rendering, input, and audio
- **CSV Module**: For tile-based map data parsing
- **Math Module**: For trigonometric calculations in visual effects

### Advanced Systems Implementation

#### 🧠 **Advanced AI State Machines** 
*Location: `enemy.py` - Lines 63-175*
- Enemies use a sophisticated three-state AI system (idle, move, attack)
- State transitions based on distance calculations using `notice_radius` and `attack_radius`
- AI makes decisions based on player proximity and attack cooldowns
- Dynamic behavior patterns unique to each enemy type (squid, raccoon, spirit, bamboo)

#### 🎯 **Sophisticated Collision System**
*Location: `entity.py` - Lines 21-46*
- Axis-separated collision detection preventing sprite teleportation bugs
- Hitbox inflation system for precise collision boundaries (`settings.py` - HITBOX_OFFSET)
- Separate collision handling for horizontal and vertical movement
- Obstacle sprite groups for efficient collision queries
- Rectangle-based collision resolution with pixel-perfect positioning

#### 🔄 **Advanced Pattern Recognition**
*Location: `player.py` - Lines 69-212 & `enemy.py` - Lines 63-125*
- Player status string parsing to determine animation states and weapon positioning
- Pattern matching for attack directions and animation transitions
- Enemy behavior pattern recognition based on distance thresholds
- Status management with idle, move, and attack pattern detection
- Frame-perfect animation state transitions

#### ⚡ **Complex Physics Simulations**
*Location: `entity.py` - Lines 13-25 -*
- Vector-based movement with magnitude normalization for consistent diagonal speed
- Knockback physics with resistance multipliers for enemy hit reactions
- Invulnerability frames with sine wave opacity modulation (`entity.py` - Lines 48-55)
- Direction-based force application for attack reactions
- Frame-rate independent movement calculations

#### 🗺️ **Navigation System**
*Location: `enemy.py` - Lines 63-74*
- Vector-based pathfinding calculating direction to player
- Distance-based navigation with magnitude calculations
- Real-time path updates following player movement
- Normalized direction vectors for smooth enemy tracking
- Multi-radius detection zones (notice vs. attack ranges)

### Game Architecture

**Entity Component System**: 
- Base `Entity` class (`entity.py`) provides shared functionality
- Player and Enemy inherit movement, collision, and animation systems
- Sprite groups organize entities by rendering and collision needs

**Tile-based Map System**: 
- CSV files define map layouts (`level.py` - Lines 53-95)
- Dynamic tile instantiation from map data
- Object layer system for different tile types (boundary, grass, objects, entities)

**Particle System**: 
- Animation player manages particle effects (`particles.py`)
- Dynamic particle spawning for combat feedback
- Leaf particles with horizontal reflection for variety

**Camera System**:
- Y-sort sprite rendering for depth illusion (`level.py` - Lines 183-219)
- Camera offset following player position
- Centered viewport with smooth scrolling

## 💡 Inspiration & Credits

This project was developed with guidance from the [Clear Code Tutorial](https://www.youtube.com/watch?v=QU1pPzEGrqw&list=PLH3CJ3zIUwuVAPJQJM56p3TzK2inMwhBh&index=3&t=1s), which provides a foundation for creating a Zelda-style game in Python with Dark Souls elements.

### Original Tutorial Content:
- Base game mechanics and combat system
- Entity and player movement framework
- UI and upgrade menu systems
- Particle effects implementation

### Custom Modifications & Additions:
- **Enhanced Map Design**: Working on expanded custom map layouts with new tile arrangements
- **Additional Enemy Types**: Planning to implement new enemy variants with unique behaviors
- **Extended Combat Mechanics**: Refined weapon and magic balance
- **Improved Visual Feedback**: Enhanced particle effects and animations

### Game Design Inspiration:
- **The Legend of Zelda**: Top-down perspective and action-adventure elements
- **Dark Souls**: Combat mechanics and character progression concepts

### Assets:
- Visual assets and music from [Pixel Boy's Ninja Adventure Asset Pack](https://pixel-boy.itch.io/ninja-adventure-asset-pack)

## 🚀 Getting Started

### Prerequisites
```bash
pip install pygame
```

### Running the Game
1. Ensure Python 3.x is installed on your system
2. Install Pygame: `pip install pygame`
3. Navigate to the game directory
4. Run: `python main.py`
5. Press Space at the title screen to begin your adventure

## 📝 Code Structure
```
├── main.py              # Game initialization and main loop
├── level.py             # Level management and sprite groups
├── player.py            # Player entity with input handling
├── enemy.py             # Enemy AI and behavior
├── entity.py            # Base entity class with physics
├── weapon.py            # Weapon sprite positioning
├── magic.py             # Magic spell implementation
├── particles.py         # Particle effect system
├── ui.py                # User interface rendering
├── upgrade.py           # Stat upgrade menu
├── settings.py          # Game constants and configuration
├── support.py           # Helper functions for asset loading
└── tile.py              # Tile sprite class
```

## 🎓 Educational Value

This project demonstrates:
- Object-oriented programming principles
- Game loop architecture
- Sprite management and rendering
- Collision detection algorithms
- State machine implementation
- Vector mathematics in game development
- Event handling and input processing
- Audio/visual feedback systems

---

**Note**: This is a project based on tutorial content with custom expansions. All original tutorial credit goes to Clear Code, with asset credit to Pixel Boy.