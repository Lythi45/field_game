"""
Main Game class that manages the game loop and coordinates all systems
"""

import pygame
import sys
from src.config import Config
from src.graphics.renderer import Renderer
from src.world.world import World
from src.input.input_handler import InputHandler

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
        
        # Create renderer
        self.renderer = Renderer(self.screen)
        
        # Create input handler
        self.input_handler = InputHandler(self.renderer, self.world)
        
        # Game state
        self.paused = False
        self.game_speed = Config.GAME_SPEED
        
        print(f"Game initialized: {Config.WORLD_WIDTH}x{Config.WORLD_HEIGHT} world")
    
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
        
        # Update input handler (for continuous input like camera movement)
        self.input_handler.update(scaled_dt)
    
    def render(self):
        """Render the game"""
        self.renderer.render_world(self.world)
    
    def toggle_pause(self):
        """Toggle game pause state"""
        self.paused = not self.paused
        print(f"Game {'paused' if self.paused else 'unpaused'}")
    
    def quit(self):
        """Quit the game"""
        self.running = False