"""
Main Game class that manages the game loop and coordinates all systems
"""

import pygame
import sys
from src.config import Config
from src.graphics.renderer import Renderer
from src.world.world import World
from src.input.input_handler import InputHandler
from src.entities.worker import Worker, WorkerType
from src.entities.crop import Crop, CropType

class Game:
    """Main game class that manages the game loop"""
    
    def __init__(self):
        # Initialize display
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption(Config.TITLE)
        
        # Initialize game systems
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create world
        self.world = World()
        
        # Create workers list
        self.workers = []
        
        # Create renderer
        self.renderer = Renderer(self.screen)
        
        # Create input handler
        self.input_handler = InputHandler(self.renderer, self.world, self.workers)
        
        # Game state
        self.paused = False
        self.game_speed = Config.GAME_SPEED
        
        # Initialize game content
        self._initialize_game_content()
        
        print(f"Game initialized: {Config.WORLD_WIDTH}x{Config.WORLD_HEIGHT} world")
        print(f"Workers spawned: {len(self.workers)}")
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(Config.FPS) / 1000.0  # Delta time in seconds
            
            # Handle events
            self.handle_events()
            
            # Update game state
            if not self.paused:
                self.update(dt)
            
            # Render everything
            self.render()
            
            # Update display
            pygame.display.flip()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                # Pass event to input handler
                self.input_handler.handle_event(event)
    
    def update(self, dt: float):
        """Update game state"""
        # Apply game speed
        scaled_dt = dt * self.game_speed
        
        # Update world (crops growing, etc.)
        self.world.update(scaled_dt)
        
        # Update workers
        for worker in self.workers:
            worker.update(scaled_dt, self.world)
        
        # Update input handler (for continuous input like camera movement)
        self.input_handler.update(scaled_dt)
    
    def render(self):
        """Render the game"""
        self.renderer.render_world(self.world, self.workers)
    
    def toggle_pause(self):
        """Toggle game pause state"""
        self.paused = not self.paused
        print(f"Game {'paused' if self.paused else 'unpaused'}")
    
    def _initialize_game_content(self):
        """Initialize workers and some starting content"""
        import random
        
        # Spawn 3 workers in different locations
        worker_configs = [
            (WorkerType.FARMER, 5, 5, "Alice"),
            (WorkerType.FARMER, 8, 8, "Bob"), 
            (WorkerType.BUILDER, 12, 12, "Charlie")
        ]
        
        for worker_type, x, y, name in worker_configs:
            # Find a walkable position near the target
            spawn_pos = self.world.find_nearest_walkable(x, y, max_distance=5)
            if spawn_pos:
                worker = Worker(worker_type, spawn_pos[0], spawn_pos[1], name)
                self.workers.append(worker)
                print(f"Spawned {name} ({worker_type.value}) at {spawn_pos}")
        
        # Plant some initial crops for workers to tend
        initial_crops = [
            (10, 10, CropType.WHEAT),
            (11, 10, CropType.CORN),
            (10, 11, CropType.POTATO),
            (15, 15, CropType.CARROT),
            (16, 15, CropType.WHEAT)
        ]
        
        for x, y, crop_type in initial_crops:
            if self.world.is_farmable(x, y):
                crop = Crop(crop_type)
                if self.world.plant_crop(x, y, crop):
                    print(f"Planted {crop_type.value} at ({x}, {y})")
    
    def quit(self):
        """Quit the game"""
        self.running = False