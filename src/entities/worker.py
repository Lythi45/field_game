"""
Worker AI system for autonomous characters
"""

from enum import Enum
import random
from typing import Optional, Tuple, List
from src.utils.math_utils import IsometricMath

class WorkerType(Enum):
    """Different types of workers"""
    FARMER = "farmer"
    BUILDER = "builder"
    CRAFTER = "crafter"
    LABORER = "laborer"

class WorkerState(Enum):
    """Worker AI states"""
    IDLE = "idle"
    MOVING = "moving"
    WORKING = "working"
    RESTING = "resting"
    SEEKING_WORK = "seeking_work"

class Task:
    """Represents a task that can be assigned to workers"""
    
    def __init__(self, task_type: str, target_pos: Tuple[int, int], priority: int = 1):
        self.type = task_type
        self.target_pos = target_pos
        self.priority = priority
        self.duration = 0.0
        self.progress = 0.0
        self.completed = False

class Worker:
    """Represents a worker character with AI"""
    
    def __init__(self, worker_type: WorkerType, x: int, y: int, name: str = None):
        self.type = worker_type
        self.x = x
        self.y = y
        self.name = name or f"{worker_type.value}_{random.randint(1000, 9999)}"
        
        # AI State
        self.state = WorkerState.IDLE
        self.current_task: Optional[Task] = None
        self.path: List[Tuple[int, int]] = []
        self.path_index = 0
        
        # Worker properties
        self.properties = self._get_worker_properties()
        
        # Stats
        self.energy = 100.0
        self.happiness = 75.0
        self.efficiency = 1.0
        self.experience = 0
        
        # Movement
        self.move_speed = 2.0  # tiles per second
        self.move_progress = 0.0
        
        # Work
        self.assigned_building = None
        self.inventory = {}
        self.carrying_capacity = self.properties["carrying_capacity"]
        
        # Timing
        self.work_timer = 0.0
        self.rest_timer = 0.0
        self.last_rest = 0.0
    
    def _get_worker_properties(self) -> dict:
        """Get properties for this worker type"""
        properties = {
            WorkerType.FARMER: {
                "skills": ["planting", "harvesting", "watering"],
                "carrying_capacity": 20,
                "work_efficiency": 1.0,
                "preferred_tasks": ["plant_crop", "harvest_crop", "water_crop"]
            },
            WorkerType.BUILDER: {
                "skills": ["construction", "repair"],
                "carrying_capacity": 30,
                "work_efficiency": 1.2,
                "preferred_tasks": ["build", "repair", "demolish"]
            },
            WorkerType.CRAFTER: {
                "skills": ["crafting", "processing"],
                "carrying_capacity": 15,
                "work_efficiency": 1.1,
                "preferred_tasks": ["craft_item", "process_material"]
            },
            WorkerType.LABORER: {
                "skills": ["transport", "general"],
                "carrying_capacity": 25,
                "work_efficiency": 0.9,
                "preferred_tasks": ["transport", "cleanup", "general_work"]
            }
        }
        return properties.get(self.type, properties[WorkerType.LABORER])
    
    def update(self, dt: float, world):
        """Update worker AI and state"""
        # Update energy and happiness
        self._update_stats(dt)
        
        # State machine
        if self.state == WorkerState.IDLE:
            self._update_idle(dt, world)
        elif self.state == WorkerState.SEEKING_WORK:
            self._update_seeking_work(dt, world)
        elif self.state == WorkerState.MOVING:
            self._update_moving(dt, world)
        elif self.state == WorkerState.WORKING:
            self._update_working(dt, world)
        elif self.state == WorkerState.RESTING:
            self._update_resting(dt, world)
    
    def _update_stats(self, dt: float):
        """Update worker stats over time"""
        # Energy decreases while working
        if self.state == WorkerState.WORKING:
            self.energy -= 10.0 * dt  # 10 energy per second while working
        elif self.state == WorkerState.RESTING:
            self.energy += 20.0 * dt  # 20 energy per second while resting
        
        # Clamp energy
        self.energy = IsometricMath.clamp(self.energy, 0.0, 100.0)
        
        # Happiness affected by various factors
        if self.energy < 20:
            self.happiness -= 5.0 * dt  # Unhappy when tired
        elif self.state == WorkerState.WORKING:
            self.happiness += 1.0 * dt  # Happy when productive
        
        # Clamp happiness
        self.happiness = IsometricMath.clamp(self.happiness, 0.0, 100.0)
        
        # Efficiency based on energy and happiness
        self.efficiency = (self.energy / 100.0) * (self.happiness / 100.0)
    
    def _update_idle(self, dt: float, world):
        """Update idle state"""
        # Check if we need rest
        if self.energy < 30:
            self.state = WorkerState.RESTING
            return
        
        # Look for work
        if not self.current_task:
            self.state = WorkerState.SEEKING_WORK
    
    def _update_seeking_work(self, dt: float, world):
        """Update work-seeking state"""
        # Simple work finding - look for nearby farmable tiles
        if self.type == WorkerType.FARMER:
            task = self._find_farming_task(world)
            if task:
                self.assign_task(task)
                return
        
        # If no work found, go idle
        self.state = WorkerState.IDLE
    
    def _update_moving(self, dt: float, world):
        """Update movement along path"""
        if not self.path or self.path_index >= len(self.path):
            # Reached destination
            self.state = WorkerState.WORKING if self.current_task else WorkerState.IDLE
            return
        
        # Move towards next waypoint
        target_x, target_y = self.path[self.path_index]
        
        # Calculate movement
        dx = target_x - self.x
        dy = target_y - self.y
        distance = IsometricMath.distance(self.x, self.y, target_x, target_y)
        
        if distance < 0.1:  # Close enough to waypoint
            self.x, self.y = target_x, target_y
            self.path_index += 1
        else:
            # Move towards waypoint
            move_distance = self.move_speed * dt
            if move_distance >= distance:
                self.x, self.y = target_x, target_y
                self.path_index += 1
            else:
                self.x += (dx / distance) * move_distance
                self.y += (dy / distance) * move_distance
    
    def _update_working(self, dt: float, world):
        """Update working state"""
        if not self.current_task:
            self.state = WorkerState.IDLE
            return
        
        # Work on current task
        work_rate = self.efficiency * self.properties["work_efficiency"]
        self.current_task.progress += work_rate * dt
        self.work_timer += dt
        
        # Check if task is complete
        if self.current_task.progress >= self.current_task.duration:
            self._complete_task(world)
            self.state = WorkerState.IDLE
    
    def _update_resting(self, dt: float, world):
        """Update resting state"""
        self.rest_timer += dt
        
        # Rest for at least 10 seconds or until energy is above 80
        if self.rest_timer >= 10.0 and self.energy > 80:
            self.rest_timer = 0.0
            self.state = WorkerState.IDLE
    
    def _find_farming_task(self, world) -> Optional[Task]:
        """Find a farming task near the worker"""
        # Look for farmable tiles within range
        search_radius = 10
        
        for dy in range(-search_radius, search_radius + 1):
            for dx in range(-search_radius, search_radius + 1):
                check_x = int(self.x) + dx
                check_y = int(self.y) + dy
                
                if world.is_farmable(check_x, check_y):
                    tile = world.get_tile(check_x, check_y)
                    if tile and not tile.crop:
                        # Found empty farmable tile
                        task = Task("plant_crop", (check_x, check_y), priority=2)
                        task.duration = 5.0  # 5 seconds to plant
                        return task
                    elif tile and tile.crop and tile.crop.is_ready():
                        # Found ready crop to harvest
                        task = Task("harvest_crop", (check_x, check_y), priority=3)
                        task.duration = 3.0  # 3 seconds to harvest
                        return task
        
        return None
    
    def assign_task(self, task: Task):
        """Assign a task to this worker"""
        self.current_task = task
        
        # Create path to task location
        self.path = [task.target_pos]  # Simple direct path for now
        self.path_index = 0
        
        self.state = WorkerState.MOVING
        print(f"{self.name} assigned task: {task.type} at {task.target_pos}")
    
    def _complete_task(self, world):
        """Complete the current task"""
        if not self.current_task:
            return
        
        task = self.current_task
        
        if task.type == "plant_crop":
            self._complete_plant_task(world, task)
        elif task.type == "harvest_crop":
            self._complete_harvest_task(world, task)
        
        # Gain experience
        self.experience += 1
        
        # Clear task
        self.current_task = None
        print(f"{self.name} completed task: {task.type}")
    
    def _complete_plant_task(self, world, task):
        """Complete a planting task"""
        from src.entities.crop import Crop, CropType
        
        x, y = task.target_pos
        if world.is_farmable(x, y):
            # Plant a random crop
            crop_type = random.choice(list(CropType))
            crop = Crop(crop_type)
            world.plant_crop(x, y, crop)
    
    def _complete_harvest_task(self, world, task):
        """Complete a harvesting task"""
        x, y = task.target_pos
        harvest_result = world.harvest_crop(x, y)
        
        if harvest_result:
            # Add to inventory
            crop_type = harvest_result["type"].value
            amount = harvest_result["amount"]
            
            if crop_type in self.inventory:
                self.inventory[crop_type] += amount
            else:
                self.inventory[crop_type] = amount
            
            print(f"{self.name} harvested {amount} {crop_type}")
    
    def can_work(self) -> bool:
        """Check if worker can work"""
        return self.energy > 20 and self.state != WorkerState.RESTING
    
    def get_position(self) -> Tuple[float, float]:
        """Get worker position"""
        return (self.x, self.y)
    
    def __str__(self):
        return f"Worker({self.name}, {self.type.value}, {self.state.name})"