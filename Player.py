import pygame
import random
from Constants import *
from pygame.locals import *

vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
  
  def __init__(self,init_pos_vec):
    super().__init__()

    # Image for player avatar
    self.image = pygame.image.load("penguin.png")
    # h (height) and w (width) of player
    self.h = 50
    self.w = 50

    # Create the body surface of avatar
    self.surf = pygame.Surface((self.h,self.w))
    self.rect = self.surf.get_rect()

    self.rect.width = self.w
    self.rect.height = self.h


    self.pos = init_pos_vec
    self.vel = vec(0,0)
    self.acc = vec(0,G)

    self.jumping = False
    self.score = 0

  def move_WASD(self):
    
    self.acc = vec(0,G)

    pressed_key = pygame.key.get_pressed()
    if pressed_key[K_a]:
      self.acc.x = -G
    if pressed_key[K_d]:
      self.acc.x = G
  
    self.apply_physics()

  def move_arrows(self):
    
    self.acc = vec(0,G)

    pressed_key = pygame.key.get_pressed()
    if pressed_key[K_LEFT]:
      self.acc.x = -G
    if pressed_key[K_RIGHT]:
      self.acc.x = G

    self.apply_physics()  

  def apply_physics(self):

    self.acc.x += self.vel.x * FRIC
    self.vel += self.acc
    self.pos += self.vel + 0.5*self.acc

    if self.pos.x > WIDTH:
      self.pos.x = 0
    if self.pos.x < 0:
      self.pos.x = WIDTH
       
    self.rect.midbottom = self.pos

  def update(self):

    hits = pygame.sprite.spritecollide( self , platforms , False )

    if self.vel.y > 0:
      if hits:
        if self.pos.y<hits[-1].rect.bottom:
          self.jumping = False
          self.pos.y = hits[-1].rect.top+1
          self.vel.y = 0

    # Hits between 
    p_hits = pygame.sprite.spritecollide( self , players , False )
    if len(players)==len(p_hits):

      for p in players:
        if p!=self:
          other_player = p

      if self.rect.left<=other_player.rect.right:
        self.rect.left = other_player.rect.right+1
        self.vel.x = abs(other_player.vel.x)


  def jump(self):
    # hits = pygame.sprite.spritecollide(self, platforms , False)
    if not self.jumping:
      self.jumping = True
      self.vel.y = -15

  def cancel_jump(self):
    self.jumping = False
    if self.vel.y<-3:
      self.vel.y = -3

  def draw(self,surface):
    self.image = pygame.transform.scale( self.image,(50,50) )
    surface.blit( self.image,self.rect )
