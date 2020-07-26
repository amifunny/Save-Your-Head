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

    if self.vel.y >= 0:
      for hit in hits:
        if self.pos.y<hit.rect.bottom:
          self.jumping = False
          self.pos.y = hit.rect.top+1
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
player1 = Player(vec(100,HEIGHT/2))
player2 = Player(vec(WIDTH-100,HEIGHT/2))
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
    
    if player1.rect.bottom<=player2.rect.top+2:
      player1.score += 1
      return 1
    if player2.rect.bottom<=player2.rect.top+2:
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

  return False

def CheckIfGameOver():  

  print(player1.score)
  print(math.ceil(ROUNDS/2))

  if player1.score>=math.ceil(ROUNDS/2):
    return 1
  if player2.score>=math.ceil(ROUNDS/2):
    return 2
  
  return False


def PlayBackMusic():
  pass


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

    round_result = CheckIfRoundOver()
    if not isinstance( round_result , bool ):
        print("ROUND OVER" ) 
        return

main()



























