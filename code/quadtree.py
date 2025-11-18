import pygame
from collections import defaultdict

class QuadTree:
    MAX_OBJECTS = 10
    MAX_LEVELS = 5
    
    def __init__(self, level, bounds):
        """
        Initialize the QuadTree.
        
        Args:
            level: Current level in the tree (0 is root).
            bounds: A pygame.Rect representing the boundaries of the node.
        """
        self.level = level
        self.bounds = bounds
        self.objects = []
        self.nodes = []  # Will hold four child nodes: [nw, ne, sw, se]
        
        # Colors for visualization
        self.colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255)]
    
    def clear(self):
        """Clear all objects and child nodes."""
        self.objects.clear()
        for node in self.nodes:
            node.clear()
        self.nodes.clear()
    
    def split(self):
        """Split the node into four child nodes."""
        sub_width = self.bounds.width // 2
        sub_height = self.bounds.height // 2
        x = self.bounds.x
        y = self.bounds.y
        
        # Create child nodes: nw, ne, sw, se
        self.nodes.append(QuadTree(self.level + 1, pygame.Rect(x, y, sub_width, sub_height)))
        self.nodes.append(QuadTree(self.level + 1, pygame.Rect(x + sub_width, y, sub_width, sub_height)))
        self.nodes.append(QuadTree(self.level + 1, pygame.Rect(x, y + sub_height, sub_width, sub_height)))
        self.nodes.append(QuadTree(self.level + 1, pygame.Rect(x + sub_width, y + sub_height, sub_width, sub_height)))
    
    def get_index(self, rect):
        """
        Determine which child node the object belongs to.
        Returns index of child node, or -1 if it doesn't fit completely in any.
        """
        index = -1
        
        # Check if the object fits completely within the child quadrants
        vertical_midpoint = self.bounds.x + (self.bounds.width // 2)
        horizontal_midpoint = self.bounds.y + (self.bounds.height // 2)
        
        # Object can fit completely within the top quadrants
        top_half = rect.y < horizontal_midpoint and rect.y + rect.height < horizontal_midpoint
        # Object can fit completely within the bottom quadrants
        bottom_half = rect.y > horizontal_midpoint
        
        # Object can fit completely within the left quadrants
        if rect.x < vertical_midpoint and rect.x + rect.width < vertical_midpoint:
            if top_half:
                index = 0  # nw
            elif bottom_half:
                index = 2  # sw
        # Object can fit completely within the right quadrants
        elif rect.x > vertical_midpoint:
            if top_half:
                index = 1  # ne
            elif bottom_half:
                index = 3  # se
        
        return index
    
    def insert(self, obj):
        """Insert an object into the QuadTree."""
        # If there are child nodes, try to insert into them
        if self.nodes:
            index = self.get_index(obj.rect)
            if index != -1:
                self.nodes[index].insert(obj)
                return
        
        # Otherwise, add to this node
        self.objects.append(obj)
        
        # If we've exceeded capacity and haven't reached max levels, split
        if len(self.objects) > self.MAX_OBJECTS and self.level < self.MAX_LEVELS:
            if not self.nodes:
                self.split()
            
            # Move objects to child nodes
            i = 0
            while i < len(self.objects):
                index = self.get_index(self.objects[i].rect)
                if index != -1:
                    self.nodes[index].insert(self.objects.pop(i))
                else:
                    i += 1
    
    def retrieve(self, return_objects, rect):
        """
        Retrieve all objects that could collide with the given rectangle.
        
        Args:
            return_objects: List to populate with objects.
            rect: The rectangle to check for potential collisions.
        """
        # Get index of the rectangle
        index = self.get_index(rect)
        
        # If we have child nodes, retrieve from the appropriate one
        if self.nodes:
            if index != -1:
                self.nodes[index].retrieve(return_objects, rect)
            else:
                # If the rectangle doesn't fit in a single child, check all children
                for node in self.nodes:
                    node.retrieve(return_objects, rect)
        
        # Add objects from this node
        return_objects.extend(self.objects)
        
        return return_objects
        
    def draw(self, surface):
        """Draw QuadTree boundaries for debugging."""
        # Choose color based on level
        color = self.colors[min(self.level, len(self.colors)-1)]
        
        # Draw boundary
        pygame.draw.rect(surface, color, self.bounds, 1)
        
        # Draw object count
        font = pygame.font.SysFont(None, 20)
        text = font.render(str(len(self.objects)), True, color)
        surface.blit(text, self.bounds.topleft)
        
        # Recursively draw child nodes
        for node in self.nodes:
            node.draw(surface)
