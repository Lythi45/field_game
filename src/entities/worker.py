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
        
        # Global energy check - force rest if critically low (safety net)
        if self.energy <= 10 and self.state != WorkerState.RESTING:
            print(f"{self.name} EMERGENCY REST - critically low energy ({self.energy:.0f}) - preserving task")
            self.state = WorkerState.RESTING
            self.rest_timer = 0.0
            # Don't clear current_task - preserve it for resumption
            # Don't clear path - we'll need it to resume movement
            return
        
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
        # Energy decreases while working or moving
        if self.state == WorkerState.WORKING:
            self.energy -= 8.0 * dt  # 8 energy per second while working
        elif self.state == WorkerState.MOVING:
            self.energy -= 3.0 * dt  # 3 energy per second while moving
        elif self.state == WorkerState.RESTING:
            self.energy += 25.0 * dt  # 25 energy per second while resting
        elif self.state == WorkerState.SEEKING_WORK:
            self.energy -= 1.0 * dt  # 1 energy per second while seeking work
        
        # Clamp energy
        self.energy = IsometricMath.clamp(self.energy, 0.0, 100.0)
        
        # Happiness affected by various factors
        if self.energy < 20:
            self.happiness -= 5.0 * dt  # Unhappy when tired
        elif self.state == WorkerState.WORKING:
            self.happiness += 1.0 * dt  # Happy when productive
        elif self.state == WorkerState.RESTING:
            self.happiness += 2.0 * dt  # Happy when resting
        
        # Clamp happiness
        self.happiness = IsometricMath.clamp(self.happiness, 0.0, 100.0)
        
        # Efficiency based on energy and happiness
        self.efficiency = max(0.1, (self.energy / 100.0) * (self.happiness / 100.0))
    
    def _update_idle(self, dt: float, world):
        """Update idle state"""
        # Check if we need rest
        if self.energy < 30:
            print(f"{self.name} going to rest from idle state (energy: {self.energy:.0f})")
            self.state = WorkerState.RESTING
            self.rest_timer = 0.0  # Reset rest timer
            return
        
        # Look for work
        if not self.current_task:
            self.state = WorkerState.SEEKING_WORK
    
    def _update_seeking_work(self, dt: float, world):
        """Update work-seeking state"""
        # Check if worker needs rest before seeking work
        if self.energy < 30:
            print(f"{self.name} needs rest before seeking work (energy: {self.energy:.0f})")
            self.state = WorkerState.RESTING
            return
        
        # Find work based on worker type
        if self.type == WorkerType.FARMER:
            task = self._find_farming_task(world)
            if task:
                self.assign_task(task)
                return
        elif self.type == WorkerType.BUILDER:
            # Look for construction tasks
            task = self._find_building_task(world)
            if task:
                self.assign_task(task)
                return
            # If no construction work, occasionally wander (but only if they have energy)
            elif self.energy > 50 and random.random() < 0.05:  # 5% chance to move randomly
                self._wander_randomly(world)
                return
        
        # If no work found, go idle
        self.state = WorkerState.IDLE
    
    def _update_moving(self, dt: float, world):
        """Update movement along path"""
        # Check if worker needs rest (interrupt movement if energy too low)
        if self.energy < 20:
            print(f"{self.name} pausing movement due to low energy ({self.energy:.0f}) - will resume after rest")
            # Don't abandon task, just pause movement
            self.state = WorkerState.RESTING
            return
        
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
        
        # Check if worker needs rest (interrupt work if energy too low)
        if self.energy < 20:
            print(f"{self.name} pausing work due to low energy ({self.energy:.0f}) - will resume after rest")
            # Don't abandon task, just pause it
            self.state = WorkerState.RESTING
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
        
        # Rest until energy is sufficiently recovered
        if self.energy >= 70:  # Rest until 70% energy
            print(f"{self.name} finished resting (energy: {self.energy:.0f})")
            self.rest_timer = 0.0
            self._resume_after_rest()
        elif self.rest_timer >= 15.0:  # Or rest for max 15 seconds
            print(f"{self.name} finished resting after 15 seconds (energy: {self.energy:.0f})")
            self.rest_timer = 0.0
            self._resume_after_rest()
    
    def _find_farming_task(self, world) -> Optional[Task]:
        """Find a farming task near the worker with priority-based selection"""
        search_radius = 15
        
        # Collect all potential tasks with their priorities and distances
        potential_tasks = []
        
        for dy in range(-search_radius, search_radius + 1):
            for dx in range(-search_radius, search_radius + 1):
                check_x = int(self.x) + dx
                check_y = int(self.y) + dy
                
                if world.is_valid_position(check_x, check_y):
                    tile = world.get_tile(check_x, check_y)
                    # Check if tile is farmable OR has crops (for harvesting/watering)
                    if tile and (world.is_farmable(check_x, check_y) or tile.crop):
                        distance = abs(dx) + abs(dy)  # Manhattan distance
                        
                        # Priority 1: Harvest ready crops (highest priority)
                        if tile.crop and tile.crop.is_ready():
                            task = Task("harvest_crop", (check_x, check_y), priority=3)
                            task.duration = 3.0
                            potential_tasks.append((3, distance, task))  # (priority, distance, task)
                        
                        # Priority 2: Water crops that need watering
                        elif tile.crop and not tile.crop.watered and tile.crop.stage.name != "READY":
                            task = Task("water_crop", (check_x, check_y), priority=2)
                            task.duration = 2.0
                            potential_tasks.append((2, distance, task))
                        
                        # Priority 3: Plant on empty farmable tiles (lowest priority)
                        elif not tile.crop:
                            # Check if there are already enough crops nearby
                            nearby_crops = self._count_nearby_crops(world, check_x, check_y, radius=3)
                            if nearby_crops < 2:  # Don't overcrowd
                                task = Task("plant_crop", (check_x, check_y), priority=1)
                                task.duration = 5.0
                                potential_tasks.append((1, distance, task))
        
        if not potential_tasks:
            return None
        
        # Sort by priority first (highest first), then by distance (closest first)
        # This ensures harvesting at distance 5 beats planting at distance 1
        potential_tasks.sort(key=lambda x: (-x[0], x[1]))
        
        # Return the highest priority task (closest among same priority)
        return potential_tasks[0][2]
    
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
        elif task.type == "water_crop":
            self._complete_water_task(world, task)
        elif task.type == "build_structure":
            self._complete_build_task(world, task)
        
        # Gain experience
        self.experience += 1
        
        # Clear task
        self.current_task = None
        print(f"{self.name} completed task: {task.type}")
    
    def _complete_plant_task(self, world, task):
        """Complete a planting task"""
        from src.entities.crop import Crop, CropType
        
        x, y = task.target_pos
        tile = world.get_tile(x, y)
        
        # Only plant if tile is still empty and farmable
        if tile and world.is_farmable(x, y) and not tile.crop:
            # Plant a random crop
            crop_type = random.choice(list(CropType))
            crop = Crop(crop_type)
            if world.plant_crop(x, y, crop):
                print(f"{self.name} planted {crop_type.value} at ({x}, {y})")
            else:
                print(f"{self.name} failed to plant at ({x}, {y}) - tile occupied")
    
    def _complete_harvest_task(self, world, task):
        """Complete a harvesting task"""
        x, y = task.target_pos
        harvest_result = world.harvest_crop(x, y)
        
        if harvest_result:
            # harvest_result is a Crop object, not a dictionary
            crop_type = harvest_result.type.value
            # Get yield from the crop's harvest method
            yield_info = harvest_result.harvest()
            amount = yield_info["amount"]
            
            if crop_type in self.inventory:
                self.inventory[crop_type] += amount
            else:
                self.inventory[crop_type] = amount
            
            print(f"{self.name} harvested {amount} {crop_type}")
    
    def _complete_water_task(self, world, task):
        """Complete a watering task"""
        x, y = task.target_pos
        tile = world.get_tile(x, y)
        
        if tile and tile.crop and not tile.crop.watered:
            tile.crop.water()
            print(f"{self.name} watered {tile.crop.type.value} at ({x}, {y})")
    
    def _count_nearby_crops(self, world, center_x: int, center_y: int, radius: int = 3) -> int:
        """Count crops within radius of a position"""
        count = 0
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                check_x = center_x + dx
                check_y = center_y + dy
                
                if world.is_valid_position(check_x, check_y):
                    tile = world.get_tile(check_x, check_y)
                    if tile and tile.crop:
                        count += 1
        
        return count
    
    def _wander_randomly(self, world):
        """Make worker wander to a random nearby location"""
        # Pick a random direction
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        dx, dy = random.choice(directions)
        
        # Move 3-5 tiles in that direction
        distance = random.randint(3, 5)
        target_x = int(self.x + dx * distance)
        target_y = int(self.y + dy * distance)
        
        # Find nearest walkable position
        walkable_pos = world.find_nearest_walkable(target_x, target_y, max_distance=5)
        if walkable_pos:
            # Create a simple movement task
            task = Task("wander", walkable_pos, priority=0)
            task.duration = 1.0  # Quick task
            self.assign_task(task)
            print(f"{self.name} wandering to {walkable_pos}")
    
    def _resume_after_rest(self):
        """Resume appropriate state after resting"""
        if self.current_task:
            # Resume task - check if we need to move to location first
            if self.path and self.path_index < len(self.path):
                print(f"{self.name} resuming movement to {self.current_task.type}")
                self.state = WorkerState.MOVING
            else:
                # Check if we're at the task location
                task_x, task_y = self.current_task.target_pos
                distance = abs(self.x - task_x) + abs(self.y - task_y)
                if distance <= 1.0:  # Close enough to work
                    print(f"{self.name} resuming {self.current_task.type}")
                    self.state = WorkerState.WORKING
                else:
                    # Need to move to task location
                    self.path = [self.current_task.target_pos]
                    self.path_index = 0
                    print(f"{self.name} moving to resume {self.current_task.type}")
                    self.state = WorkerState.MOVING
        else:
            # No task to resume, go idle
            self.state = WorkerState.IDLE
    
    def _find_building_task(self, world) -> Optional[Task]:
        """Find a building construction task near the worker"""
        # Look for suitable building locations within range
        search_radius = 20
        
        # Create list of positions sorted by distance
        positions = []
        for dy in range(-search_radius, search_radius + 1):
            for dx in range(-search_radius, search_radius + 1):
                check_x = int(self.x) + dx
                check_y = int(self.y) + dy
                
                if world.is_valid_position(check_x, check_y):
                    distance = abs(dx) + abs(dy)  # Manhattan distance
                    positions.append((distance, check_x, check_y))
        
        # Sort by distance (closest first)
        positions.sort()
        
        # Check positions for building opportunities
        for distance, check_x, check_y in positions:
            if world.is_buildable(check_x, check_y):
                tile = world.get_tile(check_x, check_y)
                if tile and not tile.building:
                    # Decide what to build based on nearby needs
                    building_type = self._decide_building_type(world, check_x, check_y)
                    if building_type:
                        task = Task("build_structure", (check_x, check_y), priority=2)
                        task.duration = self._get_building_duration(building_type)
                        task.building_type = building_type  # Store what to build
                        return task
        
        return None
    
    def _decide_building_type(self, world, x: int, y: int):
        """Decide what type of building to construct based on needs"""
        from src.entities.building import BuildingType
        
        # Count existing buildings in the area
        nearby_radius = 10
        building_counts = {}
        
        for dy in range(-nearby_radius, nearby_radius + 1):
            for dx in range(-nearby_radius, nearby_radius + 1):
                check_x = x + dx
                check_y = y + dy
                
                if world.is_valid_position(check_x, check_y):
                    tile = world.get_tile(check_x, check_y)
                    if tile and tile.building:
                        building_type = tile.building.type.value
                        building_counts[building_type] = building_counts.get(building_type, 0) + 1
        
        # Building priority based on needs
        total_buildings = sum(building_counts.values())
        
        # Always need at least one house
        if building_counts.get("house", 0) == 0:
            return BuildingType.HOUSE
        
        # Need storage for farming operations
        if building_counts.get("warehouse", 0) == 0 and total_buildings >= 1:
            return BuildingType.WAREHOUSE
        
        # Build more houses for growing population
        if building_counts.get("house", 0) < 3:
            return BuildingType.HOUSE
        
        # Build farm buildings near farmland
        nearby_farmland = self._count_nearby_farmland(world, x, y, radius=5)
        if nearby_farmland > 3 and building_counts.get("farm", 0) == 0:
            return BuildingType.FARM
        
        # Build workshops for production
        if building_counts.get("workshop", 0) == 0 and total_buildings >= 3:
            return BuildingType.WORKSHOP
        
        # Build wells for water access
        if building_counts.get("well", 0) == 0 and total_buildings >= 2:
            return BuildingType.WELL
        
        return None  # No building needed right now
    
    def _count_nearby_farmland(self, world, center_x: int, center_y: int, radius: int = 5) -> int:
        """Count farmland tiles within radius"""
        from src.world.tile import TileType
        count = 0
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                check_x = center_x + dx
                check_y = center_y + dy
                
                if world.is_valid_position(check_x, check_y):
                    tile = world.get_tile(check_x, check_y)
                    if tile and tile.type == TileType.FARMLAND:
                        count += 1
        
        return count
    
    def _get_building_duration(self, building_type) -> float:
        """Get construction time for different building types"""
        from src.entities.building import BuildingType
        
        durations = {
            BuildingType.HOUSE: 15.0,      # 15 seconds
            BuildingType.WAREHOUSE: 20.0,  # 20 seconds
            BuildingType.FARM: 12.0,       # 12 seconds
            BuildingType.WORKSHOP: 25.0,   # 25 seconds
            BuildingType.WELL: 10.0,       # 10 seconds
        }
        
        return durations.get(building_type, 15.0)
    
    def _complete_build_task(self, world, task):
        """Complete a building construction task"""
        from src.entities.building import Building
        
        x, y = task.target_pos
        building_type = getattr(task, 'building_type', None)
        
        if building_type and world.is_buildable(x, y):
            tile = world.get_tile(x, y)
            if tile and not tile.building:
                # Create and place the building
                building = Building(building_type, x, y)
                building.start_construction()
                building.construction_progress = 1.0  # Complete immediately
                building.state = building.state.COMPLETED
                
                if world.place_building(x, y, building):
                    print(f"{self.name} built {building_type.value} at ({x}, {y})")
                    
                    # Add building to inventory as "built structures"
                    built_type = building_type.value
                    if built_type in self.inventory:
                        self.inventory[built_type] += 1
                    else:
                        self.inventory[built_type] = 1
                else:
                    print(f"{self.name} failed to place {building_type.value} at ({x}, {y})")
    
    def can_work(self) -> bool:
        """Check if worker can work"""
        return self.energy > 20 and self.state != WorkerState.RESTING
    
    def get_position(self) -> Tuple[float, float]:
        """Get worker position"""
        return (self.x, self.y)
    
    def __str__(self):
        return f"Worker({self.name}, {self.type.value}, {self.state.name})"