import pygame
from pygame.locals import *
import sys
import random
import time
import math

pygame.init()
vec = pygame.math.Vector2

# Control Variables
HEIGHT = 650
WIDTH = 700
PREV_HEIGHT = 200
G = 1.0
FRIC = -0.12
FPS = 45
ROUNDS = 3

# Colors
screen_bg = (52,120,195)
screen_color = (255,255,255)
GREEN = (29,141,102)

newPlatGenTime = 1000
newPlatGenElapse = 2000

newSpeedTime = 15000
newSpeedElapse = 15000

PLATSPEED = -3.0

FramePerSec = pygame.time.Clock()

display_surface = pygame.display.set_mode( (WIDTH,HEIGHT) )
pygame.display.set_caption("SAVE YOUR HEAD")

class Player(pygame.sprite.Sprite):
  
  def __init__(self,init_pos_vec,name,dash_pos):
    super().__init__()

    # h (height) and w (width) of player
    self.h = 50
    self.w = 50
    
    # Image for player avatar
    self.image = pygame.image.load("penguin.png")
    self.image = pygame.transform.scale( self.image,(self.w,self.h) )
    
    # Create the body surface of avatar
    self.surf = pygame.Surface((self.h,self.w))
    self.rect = self.surf.get_rect()

    self.rect.width = self.w
    self.rect.height = self.h

    self.pos = init_pos_vec
    self.vel = vec(0,0)
    self.acc = vec(0,G)

    self.power = G

    self.alive = True

    self.jumping = False
    self.score = 0

    self.dash = PlayerDash(name,dash_pos)

  def move_WASD(self):
    
    self.acc = vec(0,self.power)

    pressed_key = pygame.key.get_pressed()
    if pressed_key[K_a]:
      self.acc.x = -self.power
    if pressed_key[K_d]:
      self.acc.x = self.power
    if pressed_key[K_e]:
      shoot_bullet()

    self.apply_physics()

  def move_arrows(self):
    
    self.acc = vec(0,self.power)

    pressed_key = pygame.key.get_pressed()
    if pressed_key[K_LEFT]:
      self.acc.x = -self.power
    if pressed_key[K_RIGHT]:
      self.acc.x = self.power
    if pressed_key[K_RCTRL]:
      shoot_bullet()
    
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

  def shoot_bullet(self):
    all_sprites.add( Bullet() )

  def update(self):

    hits = pygame.sprite.spritecollide( self , platforms , False )

    if self.vel.y >= 0:
      for hit in hits:
        if self.pos.y<hit.rect.bottom:
          self.jumping = False
          self.pos.y = hit.rect.top+1
          self.vel.y = 0

    for util in pygame.sprite.spritecollide(self,util_group,True):
      if util.utility_type!=1:
        self.dash.update( util.utility_type )
      else:
        self.alive = False

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
    surface.blit( self.image,self.rect )
    self.dash.draw(surface,self)

bullet_group = pygame.sprite.Group()
class Bullet(pygame.sprite.Sprite):
  
  def __init__(self,direction):
    super().__init__()
    self.speed = direction*2.0
    self.image = "shot.png"
  
    self.w = 50
    self.h = 10

    self.surface = pygame.Surface( (self.w,self.h) )
    self.rect = self.surface.get_rect()

  def move(self):
    self.rect.move_ip( self.speed , 0 )

  def check_hit():

    for hit_player in pygame.sprite.spritecollide(self,players,False):
      hit_player.alive = False
      self.kill()

    for plat_hit in pygame.sprite.spritecollide(self,platforms,False)
      self.kill()

  def draw(self,surface):
    surface.blit( self.image,self.rect )
    check_hit()
    self.move()

class PlayerDash():
  def __init__(self,player_name,init_pos):
    
    self.bullets = 0
    self.direction = 1
    self.name = player_name
    self.pos_topleft = init_pos
    
    self.double_power_end = 0
    self.double_power = False

  def update(self,util_type,player):
    
    if util_type==2:
      self.bullets += 3
    
    elif util_type==0:

      self.power = 2*G
      self.double_power = True
      if pygame.time.get_ticks()>double_power_end:
        self.double_power_end = pygame.time.get_ticks() + 15000
      else:
        self.double_power_end += 15000

  def draw(self,surface,player):

    if pygame.time.get_ticks()>double_power_end:
      self.double_power = False
      self.power = G

    font = pygame.font.SysFont("Dashfont.ttf",20)

    y_pos = self.pos_topleft.y
    sys_text = font.render( "Player {}".format(self.name),True,screen_color )
    display_surface.blit( sys_text , (self.pos_topleft.x,y_pos) )

    if self.bullets>0:
      y_pos += 20
      sys_text = font.render( "{} x Shots".format(self.bullets),True,screen_color )
      display_surface.blit( sys_text , (self.pos_topleft.x,y_pos ) )

    if self.double_power:
      y_pos += 20
      sys_text = font.render( "2X Power",True,screen_color )
      display_surface.blit( sys_text , (self.pos_topleft.x,y_pos ) )
    

class Platform(pygame.sprite.Sprite):
  def __init__(self):
    super().__init__()

    self.image = pygame.image.load("platform.png")

    self.width = random.randint(int(WIDTH/4),int(WIDTH/3))
    self.height = 30

    self.surf = pygame.Surface( (self.width,self.height) )
    self.surf.fill((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
    self.rect = self.surf.get_rect(center=(random.randint(0,WIDTH),
                         random.randint(0,HEIGHT-30) )
                     )

    self.point = True
    
    self.moving = True
    self.speed = PLATSPEED

  def move(self):

    if self.moving:
      self.rect.move_ip(0,self.speed)

  def draw(self,surface):
    self.image = pygame.transform.scale( self.image,(self.width,self.height) )
    surface.blit(self.image,self.rect)


# Global Elements
player1 = Player(vec(100,HEIGHT/2),"Red",vec(50,50))
player2 = Player(vec(WIDTH-100,HEIGHT/2),"Green",vec(WIDTH-150,50))
players = pygame.sprite.Group()
base_plat = Platform()
thorn_plat = Platform()
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

def initZeroScore():
  player1.score = 0
  player2.score = 0

def initGlobalElements():

  global player1,player2
  # -- Our Box Players
  player1.pos = vec(100,HEIGHT/2)
  player2.pos = vec(WIDTH-100,HEIGHT/2)
  players.add( player1 )
  players.add( player2 )

  # -- Starting Base Platform
  base_plat.width = WIDTH
  base_plat.height = 20
  base_plat.surf = pygame.Surface((base_plat.width,base_plat.height))
  base_plat.rect = base_plat.surf.get_rect(center=(WIDTH/2,HEIGHT-PREV_HEIGHT))
  base_plat.moving = False

  # -- Top Danger Thorns
  thorn_plat.width = WIDTH
  thorn_plat.height = 30
  thorn_plat.image = pygame.image.load("thorn.png")
  thorn_plat.image = pygame.transform.flip(thorn_plat.image,False,True)
  thorn_plat.surf = pygame.Surface((thorn_plat.width,thorn_plat.height))
  for i in range(0,WIDTH,30):
    thorn_plat.surf.blit( thorn_plat.image , (i,0) )
  thorn_plat.rect = thorn_plat.surf.get_rect(center=(WIDTH/2,thorn_plat.height/2))
  thorn_plat.moving = False

  # -- Add ALL Known Sprites
  all_sprites.add( player1 )
  all_sprites.add( player2 )
  all_sprites.add( base_plat )
  all_sprites.add( thorn_plat )

  # -- Add Permanent Platforms
  platforms.add(base_plat)
  platforms.add(thorn_plat)

def ShowStartScreen():
  
  font = pygame.font.SysFont("ARIAL",50)
  welcome1 = font.render( "HEY THERE! WELCOME",True,screen_color )
  welcome2 = font.render( "Press Enter to Play",True,screen_color )
  
  display_surface.fill( screen_bg )

  display_surface.blit( welcome1 , (WIDTH/2-200,HEIGHT/2-150) )
  display_surface.blit( welcome2 , (WIDTH/2-200,HEIGHT/2) )

def ShowWinScreen(winner_num):
  
  while True:    

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        return 
      if event.type == QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
        pygame.quit()
        sys.exit()    
  

    display_surface.fill( screen_bg )
        
    # -- Display end screen
    font = pygame.font.SysFont("ARIAL",40)

    sys_text = font.render( "GAME OVER",True,screen_color )
    display_surface.blit( sys_text , (WIDTH/2-150,HEIGHT/2-100) )
    sys_text = font.render( "Player {} WINS!".format(winner_num),True,screen_color )
    display_surface.blit( sys_text , (WIDTH/2-150,HEIGHT/2-50) )
    sys_text = font.render( "Press Esc to Exit",True,screen_color )
    display_surface.blit( sys_text , (WIDTH/2-150,HEIGHT/2) )
    sys_text = font.render( "Press Enter to Play Again",True,screen_color )
    display_surface.blit( sys_text , (WIDTH/2-150,HEIGHT/2+50) )
  
    pygame.display.update()
    FramePerSec.tick(FPS)

def ScoreBoard(round_num,score_tuple):

  board_pos = (WIDTH/2-50,50)
  font = pygame.font.SysFont("ARIAL",30)
  rounds = font.render( "ROUND {}".format(round_num) ,True,GREEN )
  score_division = font.render( "{} : {}".format(score_tuple[0],score_tuple[1]),True,GREEN )
  
  display_surface.blit( rounds , board_pos )
  display_surface.blit( score_division , (board_pos[0]+25,board_pos[1]+50) )


util_group = pygame.sprite.Group()

utility_dict = {
  0 : '2x.png',
  1 : 'bomb.png',
  2 : 'ammo.png'
}

class UtilityComponent(pygame.sprite.Sprite):
  
  def  __init__(self,utility_num):
   
    super().__init__()

    self.visible = True
    self.w = 30
    self.h = 30

    self.image = pygame.image.load( utility_dict[utility_num] )
    self.image = pygame.transform.scale( self.image,(self.w,self.h) )

    self.pos = vec(0,0)

    self.utility_type = utility_num

    self.surf = pygame.Surface( (self.w,self.h) )
    self.rect = self.surf.get_rect()

    self.speed = -1.0

  def move(self):
    self.rect.move_ip(0,self.speed)

  def draw(self,surface):
    surface.blit( self.image , self.rect )


def PlatformGeneration():
  
  global newPlatGenTime
  global newSpeedTime
  global newPlatGenElapse
  global PLATSPEED

  currentTimePoint = pygame.time.get_ticks()
  if currentTimePoint>=newPlatGenTime:
      
      newPlatGenTime += newPlatGenElapse

      p  = Platform()
      p.rect.center = (
                random.randint( int(p.width/2), int(WIDTH-p.width/2) ),
                  HEIGHT+p.height/2
                )

      p.speed = PLATSPEED

      if random.choices([0,1],[0.66,0.33])[0]==0:
        util = UtilityComponent( random.choices( list(utility_dict.keys()) )[0] )
        util.speed = PLATSPEED
        util.rect.midbottom = (p.rect.centerx,p.rect.top-(5))

        util_group.add(util)
        all_sprites.add(util)
  
      platforms.add(p)
      all_sprites.add(p)

  if currentTimePoint>=newSpeedTime:
    newSpeedTime += newSpeedElapse
    PLATSPEED = max( -3.0 , PLATSPEED-0.2 )
    newPlatGenElapse = max( 1500 , newPlatGenElapse-100 )


def DestroyOutboundPlats():
  for each_plat in platforms:
    if each_plat.rect.bottom<=30 and each_plat!=thorn_plat:
      each_plat.kill()

  for each_util in util_group:
    if each_util.rect.bottom<=30:
      each_util.kill()

def check_plat_insanity(platform,group):

  if pygame.sprite.spritecollideany( platform,group ):
    return True 
  else:
    for other_plat in platforms: 
      if (abs(platform.rect.top - other_plat.rect.bottom) < 50) and (abs(platform.rect.bottom - other_plat.rect.top) < 50): 
        return True
    return False

def RoundOver():

  # -- Play Music
  pygame.mixer.Sound("end.wav").play()

  # -- Delete all components
  for ele in all_sprites:
      ele.kill()
      time.sleep(1)

def main():

  shouldStart = False

  while not shouldStart:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
          shouldStart = True
          break
        if event.type == QUIT:
          pygame.quit()
          sys.exit()    
    
    ShowStartScreen()
    pygame.display.update()
    FramePerSec.tick(FPS)

  global PLATSPEED
  while True:
    initZeroScore()
    for current_round in range(1,ROUNDS+1):
      PLATSPEED = -2.0
      initGlobalElements()
      RoundLoop( current_round )
      RoundOver()

      game_result = CheckIfGameOver()
      if not isinstance( game_result , bool ): 
        print("GAME OVER" ) 
        break
    
    ShowWinScreen(game_result)

def CheckIfRoundOver():

  # Check for player collision
  # and is one player is beneath another

  if pygame.sprite.collide_rect(player1,player2):
    
    if player1.rect.bottom<=player2.rect.top:
      player1.score += 1
      return 1
    if player2.rect.bottom<=player2.rect.top:
      player2.score += 1
      return 2

  # If top thorn platform is touched by a player
  if pygame.sprite.collide_rect(thorn_plat,player1):
    player2.score += 1
    return 2
  if pygame.sprite.collide_rect(thorn_plat,player2):
    print("Player 1 updated")
    player1.score += 1
    return 1

  if not player1.alive:
    return 1
  if not player2.alive:
    return 1
  

  return False

def CheckIfGameOver():  

  if player1.score>=math.ceil(ROUNDS/2):
    return 1
  if player2.score>=math.ceil(ROUNDS/2):
    return 2
  
  return False


def PlayBackMusic():
  pass

def PlayerInteract():

  p_hits = pygame.sprite.spritecollide( player1 , players , False )
  # Check if both player are collided
  if len(players)==len(p_hits):

    net_vel = player1.vel.x - player2.vel.x
    center_dist = player1.rect.centerx - player2.rect.centerx
    overlap_dist = player1.w - abs(center_dist)

    dist_sign = center_dist/abs(center_dist)

    if overlap_dist>0:

      overlap_dist = overlap_dist/2

      player1.pos.x += dist_sign*overlap_dist
      player2.pos.x += -dist_sign*overlap_dist

      player1.rect.centerx += dist_sign*overlap_dist
      player2.rect.centerx += -dist_sign*overlap_dist

      if player1.vel.x>player2.vel.x:

        if abs(player1.vel.x)>=abs(player2.vel.x):
          player2.vel.x = net_vel
          player1.vel.x = 0
        else:
          player1.vel.x = net_vel
          player2.vel.x = 0 


def RoundLoop(current_round):

  score1 = player1.score
  score2 = player2.score

  while True:

    for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()
        sys.exit()

      if event.type == pygame.KEYDOWN:    
        if event.key == pygame.K_w:
          player1.jump()  

        if event.key == pygame.K_UP:
          player2.jump()  

      if event.type == pygame.KEYUP:    
        if event.key == pygame.K_w:
          player1.cancel_jump()  

        if event.key == pygame.K_UP:
          player2.cancel_jump()  

    PlayBackMusic()

    # Background fill
    background_img = pygame.image.load("background.png")
    background_img = pygame.transform.scale( background_img , (WIDTH,HEIGHT) )
    display_surface.blit( background_img,(0,0) )

    ScoreBoard( current_round , (score1,score2) )

    # Displaying all entities
    for entity in all_sprites:
      if entity==thorn_plat:
        display_surface.blit(entity.surf,(0,0))        
      else:
        entity.draw( display_surface )

    # Update and count Frame
    pygame.display.update()
    FramePerSec.tick(FPS)

    PlatformGeneration()
    DestroyOutboundPlats()

    # Update player position
    player1.move_WASD()
    player2.move_arrows()

    # Check for hits 
    player1.update()
    player2.update()

    for plat in platforms:
      plat.move()
    for util in util_group:
      util.move()
    
    # round_result = CheckIfRoundOver()
    # if not isinstance( round_result , bool ):
    #     print("ROUND OVER" ) 
    #     return

    PlayerInteract()

main()



























