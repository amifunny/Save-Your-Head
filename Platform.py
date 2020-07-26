import pygame
import random
from Constants import *
from pygame.locals import *

vec = pygame.math.Vector2

class Platform(pygame.sprite.Sprite):
  
  def __init__(self):
    super().__init__()

    self.image = pygame.image.load("platform.png")

    self.width = random.randint(int(WIDTH/5),int(WIDTH/4))
    self.height = 30

    self.surf = pygame.Surface( (self.width,self.height) )
    self.surf.fill((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
    self.rect = self.surf.get_rect(center=(random.randint(0,WIDTH),
                         random.randint(0,HEIGHT-30) )
                     )

    self.point = True
    
    self.moving = True
    self.speed = -2.0

  def move(self):

    if self.moving:
      self.rect.move_ip(0,self.speed)

  def draw(self,surface):
    self.image = pygame.transform.scale( self.image,(self.width,self.height) )
    surface.blit(self.image,self.rect)
