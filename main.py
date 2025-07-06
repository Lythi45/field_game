#!/usr/bin/env python3
"""
Isometric Farming Game - Main Entry Point
"""

import pygame
import sys
from src.game import Game
from src.config import Config

def main():
    """Main game entry point"""
    # Initialize Pygame
    pygame.init()
    
    # Create game instance
    game = Game()
    
    # Main game loop
    try:
        game.run()
    except KeyboardInterrupt:
        print("Game interrupted by user")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()