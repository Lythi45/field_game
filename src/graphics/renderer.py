"""
Main rendering system for the isometric game
"""

import pygame
from typing import Optional
from src.config import Config
from src.graphics.camera import Camera
from src.world.world import World
from src.world.tile import TileType

class Renderer:
    """Handles all rendering operations for the game"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.camera = Camera(screen.get_width(), screen.get_height())
        
        # Create basic tile surfaces (placeholder colored rectangles)
        self.tile_surfaces = self._create_tile_surfaces()
        
        # Font for debug text
        self.debug_font = pygame.font.Font(None, 24)
        
        # Selection
        self.selected_tile = None
        self.selected_worker = None
    
    def _create_tile_surfaces(self) -> dict:
        """Create colored surfaces for each tile type (placeholder graphics)"""
        surfaces = {}
        
        # Create diamond-shaped isometric tiles
        for tile_type in TileType:
            surface = self._create_isometric_tile(tile_type)
            surfaces[tile_type] = surface
        
        return surfaces
    
    def _create_isometric_tile(self, tile_type: TileType) -> pygame.Surface:
        """Create a diamond-shaped tile surface"""
        width = Config.TILE_WIDTH
        height = Config.TILE_HEIGHT
        
        # Create surface with alpha
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Get tile color
        if tile_type == TileType.GRASS:
            color = (34, 139, 34)
        elif tile_type == TileType.DIRT:
            color = (139, 69, 19)
        elif tile_type == TileType.WATER:
            color = (0, 191, 255)
        elif tile_type == TileType.STONE:
            color = (128, 128, 128)
        elif tile_type == TileType.FARMLAND:
            color = (160, 82, 45)
        elif tile_type == TileType.ROAD:
            color = (105, 105, 105)
        else:
            color = (255, 255, 255)
        
        # Draw diamond shape
        points = [
            (width // 2, 0),           # Top
            (width, height // 2),      # Right
            (width // 2, height),      # Bottom
            (0, height // 2)           # Left
        ]
        
        pygame.draw.polygon(surface, color, points)
        
        # Add border
        pygame.draw.polygon(surface, (0, 0, 0), points, 1)
        
        return surface
    
    def render_world(self, world: World, workers: list = None, buildings: list = None):
        """Render the game world"""
        # Clear screen
        self.screen.fill(Config.BACKGROUND_COLOR)
        
        # Get visible bounds to optimize rendering
        min_x, min_y, max_x, max_y = self.camera.get_visible_bounds()
        
        # Clamp to world bounds
        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(world.width - 1, max_x)
        max_y = min(world.height - 1, max_y)
        
        # Render tiles in correct order (back to front for isometric)
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                tile = world.get_tile(x, y)
                if tile:
                    self._render_tile(tile)
        
        # Render workers
        if workers:
            for worker in workers:
                self._render_worker(worker)
        
        # Render buildings from buildings list (in addition to world buildings)
        if buildings:
            for building in buildings:
                screen_x, screen_y = self.camera.world_to_screen(building.x, building.y)
                self._render_building(building, screen_x, screen_y)
        
        # Render selection
        if self.selected_tile:
            self._render_selection(self.selected_tile)
        
        # Render worker selection
        if self.selected_worker:
            self._render_worker_selection(self.selected_worker)
        
        # Render debug info
        if Config.DEBUG_MODE:
            self._render_debug_info(workers)
    
    def _render_tile(self, tile):
        """Render a single tile"""
        # Get screen position
        screen_x, screen_y = self.camera.world_to_screen(tile.x, tile.y)
        
        # Get tile surface
        surface = self.tile_surfaces.get(tile.type)
        if surface:
            # Calculate position (center the tile)
            pos_x = screen_x - Config.TILE_WIDTH // 2
            pos_y = screen_y - Config.TILE_HEIGHT // 2
            
            self.screen.blit(surface, (pos_x, pos_y))
        
        # Render building if present
        if tile.building:
            self._render_building(tile.building, screen_x, screen_y)
        
        # Render crop if present
        if tile.crop:
            self._render_crop(tile.crop, screen_x, screen_y)
    
    def _render_building(self, building, screen_x: int, screen_y: int):
        """Render a building (placeholder)"""
        # Ensure coordinates are integers
        screen_x = int(screen_x)
        screen_y = int(screen_y)
        
        # Simple colored rectangle for now
        rect = pygame.Rect(
            screen_x - 20, screen_y - 30,
            40, 40
        )
        pygame.draw.rect(self.screen, (139, 69, 19), rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
    
    def _render_crop(self, crop, screen_x: int, screen_y: int):
        """Render a crop with color-coded maturity"""
        # Ensure coordinates are integers
        screen_x = int(screen_x)
        screen_y = int(screen_y)
        
        # Color based on growth stage
        stage_colors = {
            "SEED": (139, 69, 19),      # Brown - just planted
            "SPROUT": (154, 205, 50),   # Yellow-green - sprouting
            "YOUNG": (124, 252, 0),     # Lawn green - young plant
            "MATURE": (34, 139, 34),    # Forest green - mature
            "READY": (255, 215, 0)      # Gold - ready for harvest
        }
        
        # Get color for current stage
        color = stage_colors.get(crop.stage.name, (0, 255, 0))
        
        # Size based on growth stage (larger as it grows)
        stage_sizes = {
            "SEED": 4,
            "SPROUT": 6,
            "YOUNG": 8,
            "MATURE": 10,
            "READY": 12
        }
        
        radius = stage_sizes.get(crop.stage.name, 8)
        radius = int(radius * self.camera.zoom)
        
        # Only draw if visible
        if radius >= 2:
            # Draw crop circle
            pygame.draw.circle(self.screen, color, (screen_x, screen_y - 10), radius)
            
            # Draw outline
            pygame.draw.circle(self.screen, (0, 0, 0), (screen_x, screen_y - 10), radius, 1)
            
            # Add growth progress indicator for mature crops
            if crop.stage.name in ["MATURE", "READY"] and self.camera.zoom >= 0.8:
                # Small progress bar above crop
                bar_width = int(16 * self.camera.zoom)
                bar_height = int(3 * self.camera.zoom)
                bar_x = screen_x - bar_width // 2
                bar_y = screen_y - 25
                
                # Background
                pygame.draw.rect(self.screen, (64, 64, 64), 
                               (bar_x, bar_y, bar_width, bar_height))
                
                # Progress fill
                progress = crop.get_growth_progress()
                progress_width = int(progress * bar_width)
                progress_color = (255, 215, 0) if crop.stage.name == "READY" else (0, 255, 0)
                pygame.draw.rect(self.screen, progress_color, 
                               (bar_x, bar_y, progress_width, bar_height))
            
            # Show crop type and stage when zoomed in
            if self.camera.zoom >= 1.0:
                crop_text = f"{crop.type.value}"
                if crop.stage.name == "READY":
                    crop_text += " (Ready!)"
                
                text_surface = self.debug_font.render(crop_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                text_rect.centerx = screen_x
                text_rect.bottom = screen_y - radius - 15
                
                # Background for text
                bg_rect = text_rect.inflate(4, 2)
                pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
                self.screen.blit(text_surface, text_rect)
    
    def _render_selection(self, tile):
        """Render selection highlight"""
        screen_x, screen_y = self.camera.world_to_screen(tile.x, tile.y)
        
        # Draw selection diamond
        points = [
            (screen_x, screen_y - Config.TILE_HEIGHT // 2),
            (screen_x + Config.TILE_WIDTH // 2, screen_y),
            (screen_x, screen_y + Config.TILE_HEIGHT // 2),
            (screen_x - Config.TILE_WIDTH // 2, screen_y)
        ]
        
        pygame.draw.polygon(self.screen, Config.SELECTION_COLOR, points, 3)
    
    def _render_worker(self, worker):
        """Render a worker character"""
        # Get screen position
        screen_x, screen_y = self.camera.world_to_screen(worker.x, worker.y)
        
        # Worker colors based on type
        worker_colors = {
            "farmer": (0, 255, 0),      # Green
            "builder": (255, 165, 0),   # Orange  
            "crafter": (128, 0, 128),   # Purple
            "laborer": (139, 69, 19)    # Brown
        }
        
        color = worker_colors.get(worker.type.value, (255, 255, 255))
        
        # Draw worker body (circle)
        body_radius = int(8 * self.camera.zoom)
        if body_radius >= 2:  # Only draw if visible
            pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y - 5)), body_radius)
            
            # Draw worker outline
            pygame.draw.circle(self.screen, (0, 0, 0), (int(screen_x), int(screen_y - 5)), body_radius, 2)
            
            # Draw direction indicator (small line showing movement direction)
            if hasattr(worker, 'path') and worker.path and worker.path_index < len(worker.path):
                target_x, target_y = worker.path[worker.path_index]
                target_screen_x, target_screen_y = self.camera.world_to_screen(target_x, target_y)
                
                # Draw line to target (very short, just for direction)
                dx = target_screen_x - screen_x
                dy = target_screen_y - screen_y
                length = (dx*dx + dy*dy)**0.5
                if length > 0:
                    # Normalize and scale
                    dx = (dx / length) * 12
                    dy = (dy / length) * 12
                    end_x = screen_x + dx
                    end_y = screen_y + dy - 5
                    pygame.draw.line(self.screen, (255, 255, 255), 
                                   (int(screen_x), int(screen_y - 5)), 
                                   (int(end_x), int(end_y)), 2)
        
        # Draw worker name and status (if zoomed in enough)
        if self.camera.zoom >= 0.8:
            # Worker name
            name_surface = self.debug_font.render(worker.name, True, (255, 255, 255))
            name_rect = name_surface.get_rect()
            name_rect.centerx = screen_x
            name_rect.bottom = screen_y - 15
            
            # Background for text
            bg_rect = name_rect.inflate(4, 2)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
            self.screen.blit(name_surface, name_rect)
            
            # Worker state
            state_text = f"{worker.state.name}"
            if worker.current_task:
                state_text += f" ({worker.current_task.type})"
            
            state_surface = self.debug_font.render(state_text, True, (200, 200, 200))
            state_rect = state_surface.get_rect()
            state_rect.centerx = screen_x
            state_rect.top = name_rect.bottom + 2
            
            # Background for state text
            state_bg_rect = state_rect.inflate(4, 2)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), state_bg_rect)
            self.screen.blit(state_surface, state_rect)
        
        # Draw energy bar
        if self.camera.zoom >= 0.6:
            bar_width = int(20 * self.camera.zoom)
            bar_height = int(4 * self.camera.zoom)
            bar_x = int(screen_x - bar_width // 2)
            bar_y = int(screen_y + 15)
            
            # Background
            pygame.draw.rect(self.screen, (64, 64, 64), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Energy fill
            energy_width = int((worker.energy / 100.0) * bar_width)
            energy_color = (255, 0, 0) if worker.energy < 30 else (255, 255, 0) if worker.energy < 60 else (0, 255, 0)
            pygame.draw.rect(self.screen, energy_color, 
                           (bar_x, bar_y, energy_width, bar_height))
    
    def _render_worker_selection(self, worker):
        """Render selection highlight around worker"""
        screen_x, screen_y = self.camera.world_to_screen(worker.x, worker.y)
        
        # Draw selection circle around worker
        radius = int(12 * self.camera.zoom)
        pygame.draw.circle(self.screen, Config.SELECTION_COLOR, 
                         (int(screen_x), int(screen_y - 5)), radius, 3)
    
    def _get_worker_at_mouse(self, mouse_pos: tuple, workers: list):
        """Get worker at mouse position, if any"""
        mouse_x, mouse_y = mouse_pos
        
        for worker in workers:
            screen_x, screen_y = self.camera.world_to_screen(worker.x, worker.y)
            
            # Check if mouse is within worker's click radius
            click_radius = max(12, int(12 * self.camera.zoom))
            dx = mouse_x - screen_x
            dy = mouse_y - (screen_y - 5)  # Offset for worker body position
            distance = (dx*dx + dy*dy)**0.5
            
            if distance <= click_radius:
                return worker
        
        return None
    
    def _render_debug_info(self, workers=None):
        """Render debug information"""
        debug_texts = [
            f"Camera: ({self.camera.x:.1f}, {self.camera.y:.1f})",
            f"Zoom: {self.camera.zoom:.2f}",
            f"FPS: {pygame.time.Clock().get_fps():.1f}"
        ]
        
        if workers:
            debug_texts.append(f"Workers: {len(workers)}")
        
        if self.selected_tile:
            debug_texts.append(f"Selected Tile: ({self.selected_tile.x}, {self.selected_tile.y})")
            debug_texts.append(f"Tile Type: {self.selected_tile.type.value}")
            
            # Show crop information if present
            if self.selected_tile.crop:
                crop = self.selected_tile.crop
                debug_texts.append(f"Crop: {crop.type.value}")
                debug_texts.append(f"Stage: {crop.stage.name}")
                debug_texts.append(f"Growth: {crop.get_growth_progress():.1%}")
                debug_texts.append(f"Health: {crop.health:.0f}")
                debug_texts.append(f"Watered: {'Yes' if crop.watered else 'No'}")
                if crop.is_ready():
                    debug_texts.append("READY FOR HARVEST!")
        
        if self.selected_worker:
            debug_texts.append(f"Selected Worker: {self.selected_worker.name}")
            debug_texts.append(f"Type: {self.selected_worker.type.value}")
            debug_texts.append(f"State: {self.selected_worker.state.name}")
            debug_texts.append(f"Energy: {self.selected_worker.energy:.0f}")
            debug_texts.append(f"Position: ({self.selected_worker.x:.1f}, {self.selected_worker.y:.1f})")
            if self.selected_worker.current_task:
                debug_texts.append(f"Task: {self.selected_worker.current_task.type}")
            if self.selected_worker.inventory:
                items = ", ".join(f"{k}:{v}" for k, v in self.selected_worker.inventory.items())
                debug_texts.append(f"Inventory: {items}")
        
        y_offset = 10
        for text in debug_texts:
            surface = self.debug_font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (10, y_offset))
            y_offset += 25
    
    def handle_mouse_click(self, mouse_pos: tuple, world: World, workers: list = None):
        """Handle mouse click for tile and worker selection"""
        # First check if we clicked on a worker
        if workers:
            clicked_worker = self._get_worker_at_mouse(mouse_pos, workers)
            if clicked_worker:
                self.selected_worker = clicked_worker
                self.selected_tile = None  # Clear tile selection
                return
        
        # If no worker clicked, check for tile selection
        world_x, world_y = self.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
        
        # Clamp to world bounds
        if 0 <= world_x < world.width and 0 <= world_y < world.height:
            self.selected_tile = world.get_tile(world_x, world_y)
            self.selected_worker = None  # Clear worker selection
    
    def get_camera(self) -> Camera:
        """Get the camera instance"""
        return self.camera
    
    def set_selected_tile(self, tile):
        """Set the selected tile"""
        self.selected_tile = tile
    
    def get_selected_tile(self):
        """Get the currently selected tile"""
        return self.selected_tile