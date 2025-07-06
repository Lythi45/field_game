# 🎮 Isometric Farming Game

A Python/Pygame-based isometric farming and city-building game where you can plant crops, build infrastructure, and manage workers.

## 🌟 Features

### ✅ Currently Implemented
- **Isometric Graphics System**: Full coordinate conversion and camera controls
- **Tile-based World**: Procedurally generated world with different terrain types
- **Farming System**: Plant crops, watch them grow through multiple stages, harvest when ready
- **Worker AI**: Autonomous workers that find tasks, move around, and complete work
- **Building System**: Construct buildings with construction progress and worker assignment
- **Camera Controls**: Smooth scrolling, zooming, and viewport management
- **Resource Management**: Workers carry items and manage inventory

### 🚧 Core Systems
- **Crops**: Wheat, Corn, Potato, Carrot with realistic growth cycles
- **Buildings**: Houses, Farms, Workshops, Warehouses, Wells, Roads
- **Workers**: Farmers, Builders, Crafters, Laborers with specialized skills
- **World**: 50x50 tile world with grass, dirt, water, stone terrain

## 🎯 Game Mechanics

### Farming
- Plant different crop types on farmable land
- Crops grow through 5 stages: Seed → Sprout → Young → Mature → Ready
- Watering crops increases growth speed and health
- Harvest ready crops for resources

### Workers
- **Farmers**: Plant, water, and harvest crops automatically
- **Builders**: Construct and repair buildings
- **Crafters**: Process materials in workshops
- **Laborers**: Transport goods and general tasks

### Buildings
- **Houses**: Provide housing for workers
- **Farms**: Improve nearby farming efficiency
- **Workshops**: Process raw materials into goods
- **Warehouses**: Store large quantities of resources
- **Wells**: Provide water for crops
- **Roads**: Increase movement speed

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Pygame library

### Installation

1. **Clone or download the game files**

2. **Install Pygame**:
   ```bash
   # On Ubuntu/Debian:
   sudo apt install python3-pygame
   
   # Or with pip:
   pip install pygame
   ```

3. **Test the game structure** (without pygame):
   ```bash
   python3 tmp_rovodev_test_structure.py
   ```

4. **Run the simulation demo** (without pygame):
   ```bash
   python3 tmp_rovodev_demo.py
   ```

5. **Run the full game**:
   ```bash
   python3 main.py
   ```

## 🎮 Controls

### Camera
- **WASD** or **Arrow Keys**: Move camera
- **Mouse Wheel**: Zoom in/out
- **R**: Reset camera to origin

### Interaction
- **Left Click**: Select tiles
- **Right Click**: Context actions (future feature)

### Debug
- **G**: Toggle grid display
- **D**: Toggle debug mode
- **ESC**: Quit game

## 📁 Project Structure

```
isometric-farming-game/
├── main.py                 # Game entry point
├── src/
│   ├── config.py          # Game configuration
│   ├── game.py            # Main game loop
│   ├── graphics/          # Rendering system
│   │   ├── renderer.py    # Main renderer
│   │   └── camera.py      # Camera controls
│   ├── world/             # World management
│   │   ├── world.py       # World grid and logic
│   │   └── tile.py        # Individual tiles
│   ├── entities/          # Game objects
│   │   ├── crop.py        # Crop system
│   │   ├── building.py    # Building system
│   │   └── worker.py      # Worker AI
│   ├── input/             # Input handling
│   │   └── input_handler.py
│   └── utils/             # Utilities
│       └── math_utils.py  # Isometric math
├── game_development_plan.md # Full development roadmap
└── README.md              # This file
```

## 🔧 Configuration

Edit `src/config.py` to customize:
- Screen resolution
- World size
- Tile dimensions
- Camera settings
- Debug options

## 🎯 Current Game Loop

1. **World Generation**: Creates a random world with different terrain types
2. **Worker Spawning**: Workers automatically seek and complete tasks
3. **Crop Growth**: Planted crops grow over time through multiple stages
4. **Building Construction**: Buildings can be constructed with worker assignment
5. **Resource Management**: Workers collect and transport resources

## 🚀 Next Steps

The game is fully functional as a basic farming simulation. To extend it:

1. **Add Graphics**: Replace colored rectangles with proper isometric sprites
2. **UI System**: Add menus for building placement and worker management
3. **Economy**: Implement trading and currency systems
4. **Technology Tree**: Add research and upgrades
5. **Multiplayer**: Network support for multiple players

## 🐛 Testing

Run the test suite to verify everything works:

```bash
# Test core functionality
python3 tmp_rovodev_test_structure.py

# Run simulation demo
python3 tmp_rovodev_demo.py
```

## 📝 Development Notes

- The game uses a **tile-based isometric projection**
- **Entity Component System** architecture for game objects
- **State machine** AI for workers
- **Modular design** for easy extension
- **Configuration-driven** for easy tweaking

## 🎨 Art Assets Needed

To make the game visually appealing, you'll need:
- Isometric tile sprites (64x32 pixels recommended)
- Building sprites from multiple angles
- Character walking animations
- Crop growth stage sprites
- UI elements and icons

## 🤝 Contributing

The codebase is well-structured and documented. Key areas for contribution:
- Graphics and animations
- Additional crop/building types
- Advanced AI behaviors
- Performance optimizations
- UI/UX improvements

## 📄 License

This is a learning project. Feel free to use and modify as needed!

---

**Happy Farming!** 🌾👨‍🌾🏡