"""
Input handling system for the game
"""

import pygame
from src.config import Config

class InputHandler:
    """Handles all user input (keyboard, mouse)"""
    
    def __init__(self, renderer, world):
        self.renderer = renderer
        self.world = world
        
        # Input state
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False, False, False]  # Left, Middle, Right
        
        # Camera movement
        self.camera_speed = Config.CAMERA_SPEED
    
    def handle_event(self, event):
        """Handle a single pygame event"""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            self._handle_key_press(event.key)
        
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons[event.button - 1] = True
            self._handle_mouse_press(event.button, event.pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons[event.button - 1] = False
        
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        
        elif event.type == pygame.MOUSEWHEEL:
            self._handle_mouse_wheel(event.y)
    
    def _handle_key_press(self, key):
        """Handle single key press events"""
        if key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        
        elif key == pygame.K_SPACE:
            # Toggle pause (if we add pause functionality)
            pass
        
        elif key == pygame.K_g:
            # Toggle grid display
            Config.SHOW_GRID = not Config.SHOW_GRID
            print(f"Grid display: {'ON' if Config.SHOW_GRID else 'OFF'}")
        
        elif key == pygame.K_d:
            # Toggle debug mode
            Config.DEBUG_MODE = not Config.DEBUG_MODE
            print(f"Debug mode: {'ON' if Config.DEBUG_MODE else 'OFF'}")
        
        elif key == pygame.K_r:
            # Reset camera position
            self.renderer.get_camera().set_position(0, 0)
            print("Camera reset to origin")
    
    def _handle_mouse_press(self, button, pos):
        """Handle mouse button press events"""
        if button == 1:  # Left click
            self.renderer.handle_mouse_click(pos, self.world)
            
            # Get selected tile for debugging
            selected = self.renderer.get_selected_tile()
            if selected:
                print(f"Selected tile: {selected}")
        
        elif button == 3:  # Right click
            # Could be used for context menus or other actions
            pass
    
    def _handle_mouse_wheel(self, direction):
        """Handle mouse wheel events for zooming"""
        camera = self.renderer.get_camera()
        if direction > 0:
            camera.zoom_in()
        else:
            camera.zoom_out()
    
    def update(self, dt: float):
        """Update input state (for continuous input like movement)"""
        self._handle_camera_movement(dt)
    
    def _handle_camera_movement(self, dt: float):
        """Handle continuous camera movement"""
        camera = self.renderer.get_camera()
        
        # Calculate movement based on pressed keys
        dx = dy = 0
        
        if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
            dx -= self.camera_speed
        if pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
            dx += self.camera_speed
        if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
            dy -= self.camera_speed
        if pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed:
            dy += self.camera_speed
        
        # Apply movement
        if dx != 0 or dy != 0:
            # Scale by delta time and zoom for consistent movement
            scale = dt * 60 * camera.zoom  # 60 for frame-rate independence
            camera.move(dx * scale, dy * scale)