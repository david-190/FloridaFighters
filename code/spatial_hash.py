"""
Spatial Hash Grid - Optimized Collision Detection Algorithm

Purpose: Reduce collision checks from O(n²) to O(n) by dividing the world
into a grid and only checking entities in nearby cells.

Algorithm: Hash-based spatial partitioning
- Divides world space into uniform grid cells
- Each entity is placed in one or more cells based on its bounding box
- Collision queries only check entities in relevant cells
- Time complexity: O(n) for uniform distribution
- Space complexity: O(n + c) where c is number of cells

Usage in game loop:
1. Clear grid each frame
2. Insert all obstacles/entities
3. Query nearby entities when needed (movement, combat, etc.)
"""

import pygame
from settings import TILESIZE


class SpatialHashGrid:
    """
    Spatial Hash Grid for efficient collision detection.
    
    Algorithm Implementation:
    1. World is divided into cells of size cell_size x cell_size
    2. Each sprite is hashed to one or more cells based on its hitbox
    3. Queries only check sprites in the same or adjacent cells
    4. Reduces average collision checks from O(n²) to O(n)
    
    Example:
        If you have 100 obstacles and check all of them every frame:
        - Without spatial hash: 100 checks per query = O(n²) total
        - With spatial hash: ~5-10 checks per query = O(n) total
    """
    
    def __init__(self, cell_size=TILESIZE * 2):
        """
        Initialize spatial hash grid.
        
        Args:
            cell_size: Size of each grid cell in pixels (default: 3 tiles = 192px)
                      Larger cells = fewer cells but more entities per cell
                      Smaller cells = more cells but fewer entities per cell
                      
        Design choice: 3 tiles is optimal for typical enemy/player sizes
        - Too small: entities span many cells, overhead increases
        - Too large: too many entities per cell, less optimization
        """
        self.cell_size = cell_size
        self.grid = {}  # Dictionary mapping (cell_x, cell_y) -> [sprite list]
        
        # Statistics for debugging/optimization
        self.stats = {
            'total_sprites': 0,
            'total_cells': 0,
            'max_sprites_per_cell': 0,
            'queries_this_frame': 0
        }
    
    def _hash(self, x, y):
        """
        Hash world coordinates to grid cell coordinates.
        
        Algorithm: Integer division to map continuous space to discrete cells
        
        Example:
            cell_size = 192
            position (100, 250) -> cell (0, 1)
            position (400, 100) -> cell (2, 0)
            
        Returns: Tuple of (cell_x, cell_y)
        """
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def _get_cells_for_rect(self, rect):
        """
        Get all grid cells that a rectangle overlaps.
        
        Algorithm: 
        1. Find top-left cell from rect.left, rect.top
        2. Find bottom-right cell from rect.right, rect.bottom
        3. Return all cells in that rectangular range
        
        Handles sprites that span multiple cells (large objects, long hitboxes).
        
        Example:
            A sprite at (180, 180) with size 50x50
            - Overlaps cells (0,0), (1,0), (0,1), (1,1) if cell_size=192
            - Ensures sprite is found no matter which cell you query from
        """
        # Get corner cells
        min_cell = self._hash(rect.left, rect.top)
        max_cell = self._hash(rect.right - 1, rect.bottom - 1)  # -1 to handle exact boundaries
        
        # Collect all cells in range
        cells = []
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                cells.append((x, y))
        
        return cells
    
    def clear(self):
        """
        Clear all sprites from the grid. 
        
        IMPORTANT: Call this at the start of each frame before rebuilding.
        The grid is rebuilt every frame because sprites move.
        """
        self.grid.clear()
        self.stats['queries_this_frame'] = 0
    
    def insert(self, sprite):
        """
        Insert a sprite into the spatial hash grid.
        
        Algorithm:
        1. Calculate which cells the sprite's hitbox overlaps
        2. Add sprite reference to each overlapping cell
        3. Update statistics
        
        Time Complexity: O(k) where k = cells sprite spans (usually 1-4)
        
        Args:
            sprite: Any sprite with a 'hitbox' attribute (Rect)
        """
        # Skip sprites without hitbox
        if not hasattr(sprite, 'hitbox'):
            return
        
        # Get all cells this sprite overlaps
        cells = self._get_cells_for_rect(sprite.hitbox)
        
        # Add sprite to each cell
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append(sprite)
        
        # Update statistics
        self.stats['total_sprites'] += 1
        self.stats['total_cells'] = len(self.grid)
        
        # Track max sprites per cell for optimization analysis
        for cell_sprites in self.grid.values():
            if len(cell_sprites) > self.stats['max_sprites_per_cell']:
                self.stats['max_sprites_per_cell'] = len(cell_sprites)
    
    def query(self, rect):
        """
        Query sprites that could collide with the given rectangle.
        
        Algorithm:
        1. Find all cells the query rectangle overlaps
        2. Collect all sprites from those cells
        3. Remove duplicates (sprite may be in multiple cells)
        4. Return set of potential collision candidates
        
        Time Complexity: O(k * m) where:
            k = cells queried (usually 1-4)
            m = average sprites per cell (should be ~5-10 with good cell_size)
        
        IMPORTANT: This returns POTENTIAL collisions. You still need to do
        actual hitbox.colliderect() checks on the returned sprites!
        
        Args:
            rect: pygame.Rect representing query area (usually entity's hitbox)
            
        Returns: 
            Set of sprites that could collide (still need AABB check)
            
        Example:
            # Check collision during movement
            predicted_hitbox = self.hitbox.copy()
            predicted_hitbox.x += self.direction.x * speed
            
            nearby = spatial_grid.query(predicted_hitbox)
            for sprite in nearby:
                if sprite.hitbox.colliderect(predicted_hitbox):
                    # Handle collision
        """
        cells = self._get_cells_for_rect(rect)
        candidates = set()
        
        # Collect sprites from all relevant cells
        for cell in cells:
            if cell in self.grid:
                candidates.update(self.grid[cell])
        
        # Update statistics
        self.stats['queries_this_frame'] += 1
        
        return candidates
    
    def query_point(self, x, y):
        """
        Query sprites at a specific point.
        
        Useful for click detection, projectile hits, etc.
        
        Args:
            x, y: World coordinates
            
        Returns:
            List of sprites in the cell containing this point
        """
        cell = self._hash(x, y)
        return self.grid.get(cell, [])
    
    def query_radius(self, center, radius):
        """
        Query sprites within a circular radius.
        
        Algorithm:
        1. Calculate bounding box of circle
        2. Query all cells in bounding box
        3. Filter by actual distance check
        
        Useful for: Area attacks, proximity detection, explosions
        
        Args:
            center: (x, y) tuple for center point
            radius: Radius in pixels
            
        Returns:
            Set of sprites within radius
        """
        # Create bounding rect for circle
        rect = pygame.Rect(
            center[0] - radius,
            center[1] - radius,
            radius * 2,
            radius * 2
        )
        
        # Get candidates from spatial hash
        candidates = self.query(rect)
        
        # Filter by actual circular distance
        center_vec = pygame.math.Vector2(center)
        in_radius = set()
        
        for sprite in candidates:
            if hasattr(sprite, 'hitbox'):
                sprite_center = pygame.math.Vector2(sprite.hitbox.center)
                if center_vec.distance_to(sprite_center) <= radius:
                    in_radius.add(sprite)
        
        return in_radius
    
    def get_stats(self):
        """
        Get performance statistics for debugging/optimization.
        
        Returns:
            Dictionary with performance metrics
        """
        return self.stats.copy()
    
    def visualize_debug(self, surface, camera_offset):
        """
        Draw grid cells for debugging (enable with DEBUG_MODE).
        
        Args:
            surface: pygame.Surface to draw on
            camera_offset: Vector2 camera offset for positioning
        """
        # Draw grid lines
        for cell_coord, sprites in self.grid.items():
            if len(sprites) > 0:
                # Calculate screen position
                world_x = cell_coord[0] * self.cell_size
                world_y = cell_coord[1] * self.cell_size
                screen_x = world_x - camera_offset.x
                screen_y = world_y - camera_offset.y
                
                # Draw cell outline
                rect = pygame.Rect(screen_x, screen_y, self.cell_size, self.cell_size)
                
                # Color intensity based on sprite count
                sprite_count = len(sprites)
                intensity = min(255, sprite_count * 30)
                color = (0, intensity, 0, 100)  # Green, more intense = more sprites
                
                pygame.draw.rect(surface, color, rect, 2)
                
                # Draw sprite count
                from debug import debug
                debug(str(sprite_count), screen_y + 5, screen_x + 5)