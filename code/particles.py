import pygame
from random import choice
from support import import_folder

class AnimationPlayer:
    
    def __init__(self):
        """Load all particle animation frames into memory."""
        self.frames = {
            # Magic effects
            'flame': import_folder('graphics/particles/flame/frames'),
            'aura': import_folder('graphics/particles/aura'),
            'heal': import_folder('graphics/particles/heal/frames'),
            
            # Attack effects
            'claw': import_folder('graphics/particles/claw'),
            'slash': import_folder('graphics/particles/slash'),
            'sparkle': import_folder('graphics/particles/sparkle'),
            'leaf_attack': import_folder('graphics/particles/leaf_attack'),
            'thunder': import_folder('graphics/particles/thunder'),
 
            # Enemy death effects
            'squid': import_folder('graphics/particles/smoke_orange'),
            'raccoon': import_folder('graphics/particles/raccoon'),
            'spirit': import_folder('graphics/particles/nova'),
            'bamboo': import_folder('graphics/particles/bamboo'),
            
            # Leaf particles with mirrored variations
            'leaf': (
                import_folder('graphics/particles/leaf1'),
                import_folder('graphics/particles/leaf2'),
                import_folder('graphics/particles/leaf3'),
                import_folder('graphics/particles/leaf4'),
                import_folder('graphics/particles/leaf5'),
                import_folder('graphics/particles/leaf6'),
                self.reflect_images(import_folder('graphics/particles/leaf1')),
                self.reflect_images(import_folder('graphics/particles/leaf2')),
                self.reflect_images(import_folder('graphics/particles/leaf3')),
                self.reflect_images(import_folder('graphics/particles/leaf4')),
                self.reflect_images(import_folder('graphics/particles/leaf5')),
                self.reflect_images(import_folder('graphics/particles/leaf6'))
                )
            }
    
    def reflect_images(self, frames):
        """Create horizontally flipped versions of animation frames."""
        new_frames = []
        
        for frame in frames:
            flipped_frame = pygame.transform.flip(frame, True, False)
            new_frames.append(flipped_frame)
            
            return new_frames
        
    def create_grass_particles(self, pos, groups):
        """Spawn random leaf particle effect at position."""
        animation_frames = choice(self.frames['leaf'])
        ParticleEffect(pos, animation_frames, groups)
        
    def create_particles(self, animation_type, pos, groups):
        """Spawn specified particle effect at position."""
        animation_frames = self.frames[animation_type]
        ParticleEffect(pos, animation_frames, groups)
        

class ParticleEffect(pygame.sprite.Sprite):
    
    def __init__(self, pos, animation_frames, groups):
        super().__init__(groups)
        
        self.sprite_type = 'magic'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = animation_frames
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center = pos) 
        
    def animate(self):
        """Advance animation frame and destroy sprite when complete."""
        self.frame_index += self.animation_speed
        
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
            
    def update(self):
        self.animate()