# -- Game created by Amifunny

import pygame
from pygame.locals import *
import sys
import random
import time
import math
import os

pygame.init()
vec = pygame.math.Vector2

# Control Variables
HEIGHT = 650
WIDTH = 700
# Height at bottom not accessible to players
PREV_HEIGHT = 200
# Acc. used for both x and y axes
G = 1.0
FRIC = -0.10
FPS = 45
# Number of Game Rounds
ROUNDS = 3

# Colors
screen_bg = (52,120,195)
screen_dark_bg = (28,71,119)
screen_color = (255,255,255)
GREEN = (29,141,102)
dash_color = (246,155,73)
# dash_color = (245,122,34)

# Time controllers for platform generation
newPlatGenTime = 1000

newPlatGenElapse = 3000
MAX_newPlatGenElapse = 3000
MIN_newPlatGenElapse = 2000

# Change Speed of platforms
newSpeedTime = 30000
newSpeedElapse = 30000

PLATSPEED = -2.0
MIN_PLATSPEED = -2.0
MAX_PLATSPEED = -3.0

PLAYER_NAMES = ['RED','BLUE']
PLAYER_IMG = [
  "image_assets/players/parrot.png",
  "image_assets/players/penguin.png",
]

FramePerSec = pygame.time.Clock()

# Set Attributes of popup game window
display_surface = pygame.display.set_mode( (WIDTH,HEIGHT) )
pygame.display.set_caption("SAVE YOUR HEAD")

game_icon = pygame.image.load("icons/game_icon_small.png")
pygame.display.set_icon( game_icon )


# -------------------------------------------------------------------------

# -- Main playable Player's Class

class Player(pygame.sprite.Sprite):
  
  def __init__(self,init_pos_vec,player_image,name,dash_pos):
    super().__init__()

    # h (height) and w (width) of player
    self.h = 50
    self.w = 50
    
    # Image for player avatar
    self.image = pygame.image.load( player_image )
    self.image = pygame.transform.scale( self.image,(self.w,self.h) )
    
    # Create the body surface of avatar
    self.surf = pygame.Surface((self.h,self.w))
    self.rect = self.surf.get_rect()

    self.rect.width = self.w
    self.rect.height = self.h

    self.pos = init_pos_vec
    self.vel = vec(0,0)
    self.acc = vec(0,G)

    self.power = vec(G,G)

    self.alive = True

    self.jumping = False
    self.score = 0

    # Dash store utility powerups info
    self.dash = PlayerDash(name,dash_pos)

  def move_WASD(self):

    # At evey move self.power.y i.e gravity is
    # acting on player
    self.acc = vec(0,self.power.y)

    pressed_key = pygame.key.get_pressed()

    # Key function
    # A - Move left
    # D - Move Right
    # E - Shoot Bullet

    # `dash.direction` store -1 for left and
    # +1 for right for shoooting direction
    if pressed_key[K_a]:
      self.acc.x = -self.power.x
      self.dash.direction = -1
    
    if pressed_key[K_d]:
      self.acc.x = self.power.x
      self.dash.direction = 1
    
    if pressed_key[K_e]:
      if self.dash.can_shoot:
        # To Avoid Shooting all bullets in one press
        self.dash.can_shoot = False  
        self.shoot_bullet()
    else:
      # When key is up again allow shooting
      self.dash.can_shoot = True  

    self.apply_physics()

  def move_arrows(self):
    
    self.acc = vec(0,self.power.y)

    # Key function
    # ARROW_LEFT : Move left
    # ARROW_RIGHT : Move right
    # Right CTRL : Shoot Bullet

    pressed_key = pygame.key.get_pressed()
   
    if pressed_key[K_LEFT]:
      self.acc.x = -self.power.x
      self.dash.direction = -1
   
    if pressed_key[K_RIGHT]:
      self.acc.x = self.power.x
      self.dash.direction = 1
   
    if pressed_key[K_RCTRL]:
      if self.dash.can_shoot:
        self.dash.can_shoot = False  
        self.shoot_bullet()
    else:
      self.dash.can_shoot = True  

    self.apply_physics()  

  def apply_physics(self):

    # Decreasing acc due to friction
    self.acc.x += self.vel.x * FRIC
    # Velocity due to acc in both directions
    self.vel += self.acc
    # New position of player due to velocity
    self.pos += self.vel + 0.5*self.acc

    self.pos.y = min( self.pos.y , HEIGHT-PREV_HEIGHT )

    # This allow player to go into one end of screen
    # and appear out of another end
    if self.pos.x-self.w/2 > WIDTH:
      self.pos.x = 0
    if self.pos.x+self.w/2 < 0:
      self.pos.x = WIDTH
       
    self.rect.midbottom = self.pos

  def shoot_bullet(self): 

    # Create a bullet at position ajdacent to player,
    # moving in stored `dash.direction`

    if self.dash.bullets>0:
      self.dash.bullets -= 1      
      all_sprites.add( Bullet(self.dash.direction,vec(self.rect.centerx,self.rect.centery)) )

  def update(self):

    # To handle collision with plaforms and
    # and utility powerups

    hits = pygame.sprite.spritecollide( self , platforms , False )

    if self.vel.y >= 0:
      for hit in hits:
        if self.pos.y<hit.rect.bottom:

          self.jumping = False
          self.pos.y = hit.rect.top+1
          self.vel.y = 0

    for util in pygame.sprite.spritecollide(self,util_group,True):
      # If its a bomb, player dies
      if util.utility_type==BOMB_U:
        # Set Explosion
        make_explosion( util.rect.centerx , util.rect.centery )
        self.alive = False
      else:
        self.dash.update( util.utility_type,self )

  def jump(self):
    if not self.jumping:

      MAX_JUMP = -15
      self.jumping = True
      self.vel.y = MAX_JUMP

  def cancel_jump(self):

    # If jump button is released,
    # slow down the upward velocity
    self.jumping = False
    if self.vel.y<-3:
      self.vel.y = -3

  def draw(self,surface):
    surface.blit( self.image,self.rect )
    self.dash.draw(surface,self)

# -- Dash Board at top of each player's side,
#    stores all powerups data and also renponsible for rendering
#    info on screen

class PlayerDash():
  
  def __init__(self,player_name,init_pos):
    
    self.bullets = 3
    self.direction = 1
    self.can_shoot = True

    self.name = player_name
    self.pos_topleft = init_pos
    
    self.double_power_end = 0
    self.double_power = False

  def update(self,util_type,player):
    
    # When Ammo utility is taken,
    # Increse number of bullets.
    if util_type==AMMO_U:
      pygame.mixer.Sound('sound/ammo_util.wav').play()
      self.bullets += 3
    
    elif util_type==DOUBLE_U:

      # SOUND
      pygame.mixer.Sound('sound/util_taken.ogg').play()
      
      # Double the power of player,
      # i.e its x-axis accerleration increases
      player.power.x = 2*G
      self.double_power = True
      if pygame.time.get_ticks()>self.double_power_end:
        self.double_power_end = pygame.time.get_ticks() + 15000
      else:
        self.double_power_end += 15000

  def draw(self,surface,player):

    # Also check if 2X is over
    if pygame.time.get_ticks()>self.double_power_end:
      self.double_power = False
      player.power.x = G

    # Render info of Players' utilities

    font = pygame.font.Font("fonts/EvilEmpire.ttf",20)

    y_pos = self.pos_topleft.y
    sys_text = font.render( "Player {}".format(self.name),True,dash_color )
    display_surface.blit( sys_text , (self.pos_topleft.x,y_pos) )

    if self.bullets>0:
      y_pos += 30
      sys_text = font.render( "{} x Shots".format(self.bullets),True,dash_color )
      display_surface.blit( sys_text , (self.pos_topleft.x,y_pos ) )

    if self.double_power:
      y_pos += 30
      sys_text = font.render( "2X Power",True,dash_color )
      display_surface.blit( sys_text , (self.pos_topleft.x,y_pos ) )


# -- Bullet class render from adjacent of player
#    and move it in horizontal direction

class Bullet(pygame.sprite.Sprite):
  
  def __init__(self,direction,pos):
    super().__init__()

    self.speed = direction*4.0
    self.direction = direction

    self.w = 50
    self.h = 20

    self.image = pygame.image.load("image_assets/shot.png")
    self.image = pygame.transform.scale( self.image ,(self.w,self.h) )
    # Flip the image horizontally on basis of
    self.image = pygame.transform.flip(self.image,direction==-1,False)

    self.surface = pygame.Surface( (self.w,self.h) )
    self.rect = self.surface.get_rect(
        center = ( direction*(self.w*3/2)+pos.x , pos.y)
      )

    # SOUND
    pygame.mixer.Sound("sound/bullet_shot.wav").play()

  def move(self):
    # Moves left in left if speed is -ve,
    # else right for positive
    self.rect.move_ip( self.speed , 0 )

  def check_hit(self):

    # If Bullet touches player, 
    # player loses his life
    for hit_player in pygame.sprite.spritecollide(self,players,False):
      hit_player.alive = False
      # Explosion
      make_explosion(
        self.rect.centerx+self.direction*(self.w/2) , self.rect.centery
      )
      self.kill()

    # Bullet on touching platform just explodes
    for plat_hit in pygame.sprite.spritecollide(self,platforms,False):
      # Explosion
      make_explosion(
        self.rect.centerx+self.direction*(self.w/2) , self.rect.centery
      )
      self.kill()

    if self.rect.left>WIDTH or self.rect.right<0:
      self.kill()

  def draw(self,surface):
    # Render as well as check for hits and move
    surface.blit( self.image,self.rect )
    self.check_hit()
    self.move()

# -------------------------------------------------------------------------

# -- Handles Players' Interaction Physics

def PlayerInteract():

  p_hits = pygame.sprite.spritecollide( player1 , players , False )

  # Check if both player are collided
  if len(players)==len(p_hits):

    # Iterate through eachplayer interacting with every other player
    for player in players:
      for other_player in players:

        if player==other_player: continue

        # Distance between center points
        direction = other_player.rect.centerx - player.rect.centerx

        # Amount of distance between center is less than with of player
        # is overlapping distance
        overlap_dist = player1.w - abs(direction)

        if abs(direction)==0:
          direction = 0
        else:
          direction = (direction/abs(direction)) * overlap_dist/2
          
        other_player.pos.x = other_player.pos.x + direction * (player.power.x/other_player.power.x)
        other_player.rect.centerx = other_player.rect.centerx + direction * (player.power.x/other_player.power.x)

        player.pos.x = player.pos.x - direction * (other_player.power.x/player.power.x)
        player.rect.centerx = player.rect.centerx - direction * (other_player.power.x/player.power.x)

# -------------------------------------------------------------------------

# -- Platform Class Renders and moves it upwards

class Platform(pygame.sprite.Sprite):

  def __init__(self):
    super().__init__()

     # Initialize random width
    self.width = random.randint(int(WIDTH/4),int(WIDTH/3))
    self.height = 30

    self.image = pygame.image.load("image_assets/platform.png")

    self.surf = pygame.Surface( (self.width,self.height) )
    self.surf.fill((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
    self.rect = self.surf.get_rect(center=(random.randint(0,WIDTH),
                         random.randint(0,HEIGHT-self.height) )
                     )

    self.moving = True
    self.speed = PLATSPEED

  def move(self):
    # Move in y-direction upwards
    if self.moving:
      self.rect.move_ip(0,self.speed)

  def draw(self,surface):
    self.image = pygame.transform.scale( self.image,(self.width,self.height) )
    surface.blit(self.image,self.rect)

# -- Generate new platform at bottom of screen
#    with random utility powerup and bomb

def PlatformGeneration():
  
  global newPlatGenTime
  global newSpeedTime
  global newPlatGenElapse
  global PLATSPEED

  # Milliseconds since start of game
  currentTimePoint = pygame.time.get_ticks()
  if currentTimePoint>=newPlatGenTime:
      
      # Set new platform genration time point
      newPlatGenTime = currentTimePoint + newPlatGenElapse

      p  = Platform()
      p.rect.center = (
                random.randint( int(p.width/2), int(WIDTH-p.width/2) ),
                  HEIGHT+p.height/2
                )

      p.speed = PLATSPEED

      # Not every platform will have some powerups,
      # Some probabilty is set to make powerups rare
      if random.choices([0,1],[0.5,0.5])[0]==1:
        # Also Laser Bomb Probability is more, than other utilities
        util = UtilityComponent( random.choices( list(utility_dict.keys()) , [0.3,0.4,0.3] )[0] )
        util.speed = PLATSPEED
        util.rect.midbottom = (p.rect.centerx,p.rect.top-(5))

        util_group.add(util)
        all_sprites.add(util)
  
      platforms.add(p)
      all_sprites.add(p)

  # After 'newSpeedElapse' time increase speed of platforms,
  # and also generation rate
  if currentTimePoint>=newSpeedTime:
    newSpeedTime = currentTimePoint + newSpeedElapse
    PLATSPEED = max( MAX_PLATSPEED , PLATSPEED - 0.2 )
    newPlatGenElapse = max( MIN_newPlatGenElapse , newPlatGenElapse-100 )

# -- Destroy Platforms and Utilities that go above the screen

def DestroyOutbounds():
  for each_plat in platforms:
    if each_plat.rect.bottom<=30 and each_plat!=thorn_plat:
      each_plat.kill()

  for each_util in util_group:
    if each_util.rect.bottom<=30:
      if each_util.utility_type==1: 
        LaserShoot(each_util.rect.left)
      each_util.kill()

# ------------------------------------------------------------

# Images dict of all utilities
utility_dict = {
  0 : 'image_assets/util/2x.png',
  1 : 'image_assets/util/bomb.png',
  2 : 'image_assets/util/ammo.png'
}

DOUBLE_U = 0
BOMB_U = 1
AMMO_U = 2

# -- Render Utilites that are powerup and laser BOMBS
#    and move with speed set by their platforms speed

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

def check_plat_insanity(platform,group):

  if pygame.sprite.spritecollideany( platform,group ):
    return True 
  else:
    for other_plat in platforms: 
      if (abs(platform.rect.top - other_plat.rect.bottom) < 50) and (abs(platform.rect.bottom - other_plat.rect.top) < 50): 
        return True
    return False

# ------------------------------------------------------

# -- Laser Object that is generated when Bomb reaches top

class Laser(pygame.sprite.Sprite):
  
  def __init__(self,offset_x):
    
    super().__init__()

    self.w = 10
    self.h = base_plat.rect.bottom

    # List all animations images in directory
    self.laser_beam_img = os.listdir('image_assets/laser/laser_beam')
    self.laser_blast_img = os.listdir('image_assets/laser/laser_blast')

    # Counter for images index 
    self.beam_ctr = 0
    self.blast_ctr = 0

    self.offset_x = offset_x
    # Time point to stop the laser
    self.end_time = pygame.time.get_ticks()+4000

    self.rect = pygame.Rect( (self.offset_x,0) , (self.w,self.h) )

    # SOUND
    pygame.mixer.Sound("sound/laser_beam.ogg").play()

  def draw(self,surface):

    laser_img = pygame.image.load( 'image_assets/laser/laser_beam/'+self.laser_beam_img[self.beam_ctr])
    laser_img = pygame.transform.scale( laser_img , (self.w,self.h) )
    surface.blit( laser_img , ( self.offset_x,0 ) )

    # Increment counter
    self.beam_ctr += 1
    self.beam_ctr = self.beam_ctr%len(self.laser_beam_img)

    laserb_img = pygame.image.load( 'image_assets/laser/laser_blast/'+self.laser_blast_img[self.blast_ctr])
    laserb_img = pygame.transform.scale( laserb_img , (2*self.w,2*self.w) )
    surface.blit( laserb_img , ( self.offset_x-self.w/2 , base_plat.rect.top-self.w ) )
    
    # Increment counter
    self.blast_ctr += 1
    self.blast_ctr = self.blast_ctr%len(self.laser_blast_img)

# -- Create Laser object that takes the offset x-coordinate to draw laser
def LaserShoot(offset_x):
  newLaser = Laser(offset_x)
  laser_group.add(newLaser)
  all_sprites.add(newLaser)

def laser_update():

  # Check if laser collide withany player,
  # that make player dead
  for player in players:
    if pygame.sprite.spritecollideany( player , laser_group , False ):
      player.alive = False

  # Remove the laser after the `end_time`
  for each_laser in laser_group:
    if each_laser.end_time<pygame.time.get_ticks():
      each_laser.kill()

# --------------------------------------------------------

# -- Explosion class that render and animate blast
class Explosion(pygame.sprite.Sprite):
  
  def __init__(self,exp_x,exp_y):
    
    super().__init__()

    self.w = 30
    self.h = 30

    # List all animations images in directory
    self.explosion_img = os.listdir('image_assets/blast')

    self.exp_ctr = 0

    self.exp_x = exp_x
    self.exp_y = exp_y

    # Time point to stop the laser
    self.end_time = pygame.time.get_ticks()+500

    # SOUND
    pygame.mixer.Sound("sound/explosion.wav").play()

  def draw(self,surface):

    exp_img = pygame.image.load( 'image_assets/blast/'+self.explosion_img[self.exp_ctr])
    exp_img = pygame.transform.scale( exp_img , (self.w,self.h) )

    image_rect = exp_img.get_rect( center=( self.exp_x,self.exp_y ) )

    surface.blit( exp_img , image_rect )

    # Increment counter
    self.exp_ctr += 1
    self.exp_ctr = self.exp_ctr%len(self.explosion_img)

def make_explosion(exp_x,exp_y):
  exp_object = Explosion(exp_x,exp_y)
  all_sprites.add( exp_object )
  explosion_group.add( exp_object )

def explosion_update():

  # Remove the blast animation after the `end_time`
  for each_explosion in explosion_group:
    if each_explosion.end_time<pygame.time.get_ticks():
      each_explosion.kill()

# -------------------------------------------------------

# Global Elements
score_tuple = ( 0 , 0 )

player1 = Player(vec(100,HEIGHT/2),PLAYER_IMG[0],PLAYER_NAMES[0],vec(50,50))
player2 = Player(vec(WIDTH-100,HEIGHT/2),PLAYER_IMG[1],PLAYER_NAMES[1],vec(WIDTH-150,50))
players = pygame.sprite.Group()

base_plat = Platform()
thorn_plat = Platform()

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
util_group = pygame.sprite.Group()
laser_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def initZeroScore():
  global score_tuple
  score_tuple = (0,0)

# -- Initialize all global elements used for every new round

def initGlobalElements():

  global player1,player2
  # -- Our Box Players
  player1 = Player(vec(100,HEIGHT/2),PLAYER_IMG[0],PLAYER_NAMES[0],vec(50,50))
  player2 = Player(vec(WIDTH-100,HEIGHT/2),PLAYER_IMG[1],PLAYER_NAMES[1],vec(WIDTH-150,50))
  player1.pos = vec(100,HEIGHT/2)
  player1.power.x = G
  player2.pos = vec(WIDTH-100,HEIGHT/2)

  player1.score = score_tuple[0]
  player2.score = score_tuple[1]

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
  thorn_image = pygame.image.load("image_assets/thorn.png")
  thorn_image = pygame.transform.flip(thorn_image,False,True)
  thorn_image = pygame.transform.scale(thorn_image,(thorn_plat.height*2,thorn_plat.height))

  thorn_plat.surf = pygame.Surface((thorn_plat.width,thorn_plat.height))
  thorn_template = pygame.Surface((thorn_plat.width,thorn_plat.height),pygame.SRCALPHA, 32)
  thorn_template = thorn_template.convert_alpha()
  
  # Repeat tile the small image on surface
  for i in range(0,WIDTH,30):
    thorn_template.blit( thorn_image , (i,0) )

  # Now this surface will be image of Platform
  thorn_plat.image = thorn_template    
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

  global PLATSPEED
  global newPlatGenElapse

  # Reset Platform Speed and generation time
  PLATSPEED = MIN_PLATSPEED
  newPlatGenElapse = MAX_newPlatGenElapse

# ---------------------------------------------------

# -- Render the welcome page shown
#    at start of game

def ShowStartScreen():

  wooden_font = pygame.font.Font("fonts/Wooden.ttf",50)
  font = pygame.font.SysFont("fonts/EvilEmpire.ttf",50)

  display_surface.fill( screen_bg )

  game_image = pygame.image.load( 'icons/game_icon_blue.png' )
  game_image = pygame.transform.scale( game_image , (200,200) )
  rect = game_image.get_rect( center=(WIDTH/2,200) )
  display_surface.blit( game_image , rect )

  welcome1 = wooden_font.render( "Save-Your-Head",True,screen_color )
  rect = welcome1.get_rect( center=(WIDTH/2,325) )
  display_surface.blit( welcome1 , rect )

  score_input_label = font.render( "Number of Rounds ",True,screen_color )
  rect = score_input_label.get_rect( center=(WIDTH/2-50,450) )
  display_surface.blit( score_input_label , rect )

  score_input = font.render( "  {}  ".format(ROUNDS) ,True,screen_color,screen_dark_bg )
  rect = score_input.get_rect( center=(rect.right+50,450) )
  rect.height = 50
  rect.width = 100

  display_surface.blit( score_input , rect )

  pygame.draw.polygon(display_surface, screen_color, (
      (rect.left,rect.top-5), (rect.left+27, rect.top-30),(rect.left+54, rect.top-5))
  )

  pygame.draw.polygon(display_surface, screen_color, (
      (rect.left,rect.top+40), (rect.left+27, rect.top+65),(rect.left+54, rect.top+40))
  )

  welcome2 = font.render( "Press Enter to Play",True,screen_color,screen_dark_bg )
  rect = score_input_label.get_rect( center=(WIDTH/2,550) )
  display_surface.blit( welcome2 , rect )

# -- Render after rounds are over,
#    show winner name and option to play again

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
    font = pygame.font.Font("fonts/EvilEmpire.ttf",30)
    wooden_font = pygame.font.Font("fonts/Wooden.ttf",50)

    sys_text = wooden_font.render( "GAME OVER",True,screen_color )
    rect = sys_text.get_rect(center=(WIDTH/2,HEIGHT/2-150))
    display_surface.blit( sys_text , rect )

    sys_text = font.render( "Player {} WINS!".format( PLAYER_NAMES[winner_num-1] ),True,screen_color )
    rect = sys_text.get_rect(center=(WIDTH/2,HEIGHT/2-50))
    display_surface.blit( sys_text , rect )

    sys_text = font.render( "Press Esc to Exit",True,screen_color )
    rect = sys_text.get_rect(center=(WIDTH/2,HEIGHT/2))
    display_surface.blit( sys_text , rect )

    sys_text = font.render( "Press Enter to Play Again",True,screen_color )
    rect = sys_text.get_rect(center=(WIDTH/2,HEIGHT/2+50))
    display_surface.blit( sys_text , rect )
  
    pygame.display.update()
    FramePerSec.tick(FPS)

# -- Score board rendering number of rounds won by 
#    each player

def ScoreBoard(round_num,score_tuple):

  board_pos = (WIDTH/2-50,50)
  font = pygame.font.SysFont("ARIAL",30)
  rounds = font.render( "ROUND {}".format(round_num) ,True,GREEN )
  score_division = font.render( "{} : {}".format(score_tuple[0],score_tuple[1]),True,GREEN )

  display_surface.blit( rounds , board_pos )
  display_surface.blit( score_division , (board_pos[0]+25,board_pos[1]+50) )

# -----------------------------------------------------------

# -- Handle when round is over and 
#    all spirites

def RoundOver():

  pygame.mixer.music.pause()

  global score_tuple
  score_tuple = (player1.score,player2.score)

  # -- Play Music
  pygame.mixer.Sound("sound/end.wav").play()

  time.sleep(1)

  # -- Delete all components
  for ele in all_sprites:
      ele.kill()


# -- Main function to handle game states
#    and handle game loop for each round

def main():

  shouldStart = False
  global ROUNDS

  # Background Music for start screen
  pygame.mixer.music.load('sound/background_start.ogg')
  pygame.mixer.music.play(-1)

  while not shouldStart:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
          shouldStart = True
          break
        if event.type == QUIT:
          pygame.quit()
          sys.exit()
        if event.type == pygame.KEYDOWN:    
          if event.key == pygame.K_UP:
            ROUNDS += 1  
          if event.key == pygame.K_DOWN:
            ROUNDS -= 1  

    if ROUNDS>10:
      ROUNDS=3
    elif ROUNDS<3:
      ROUNDS=10        
      
    ShowStartScreen()
    pygame.display.update()
    FramePerSec.tick(FPS)

  global PLATSPEED
  while True:
    
    initZeroScore()

    # Game Music
    pygame.mixer.music.load('sound/background_play.ogg')
    pygame.mixer.music.play(-1)
   
    for current_round in range(1,ROUNDS+1):
  
      pygame.mixer.music.unpause()

      # Re-Initialize all players and global elements
      initGlobalElements()
      # Start Game loop which will
      # return when either of the player losses
      RoundLoop( current_round )
      # Clearing after the round is over 
      RoundOver()

      # If a player wins majority of rounds,
      # Declare the winner
      game_result = CheckIfGameOver()
      if not isinstance( game_result , bool ): 
        print("GAME OVER" ) 
        break
    

    # End screen music
    pygame.mixer.music.load('sound/background_end.ogg')
    pygame.mixer.music.play(-1)

    ShowWinScreen(game_result)

def CheckIfRoundOver():

  # Check for player collision
  # and is one player is beneath another
  if pygame.sprite.collide_rect(player1,player2):
    
    center_dist_x = player1.rect.centerx - player2.rect.centerx
    center_dist_y = player1.rect.centery - player2.rect.centery

    # Check if x-axis overlap of players is more than 50%
    if abs(center_dist_x)<=player1.w-0.5*player1.w:
        # Check if players are overlapping along y-axis
        if abs(center_dist_y)<player1.h:

            # If distance is positive, Player2 is above Player1
            if center_dist_y>0:
                player2.score += 1
                return 2            
            if center_dist_y<0:
                player1.score += 1
                return 1            

  # If top thorn platform is touched by a player
  if pygame.sprite.collide_rect(thorn_plat,player1):
    player2.score += 1
    return 2
  if pygame.sprite.collide_rect(thorn_plat,player2):
    player1.score += 1
    return 1

  # If for any other reasons player is dead
  if not player1.alive:
    player1.score += 1
    return 1
  if not player2.alive:
    player2.score += 1
    return 2

  return False

# -- Check if one of the player wins majority
#    of rounds
def CheckIfGameOver():  

  if player1.score>=math.floor(ROUNDS/2)+1:
    return 1
  if player2.score>=math.floor(ROUNDS/2)+1:
    return 2
  
  return False


# -- Game loop where all spirites are rendered
def RoundLoop(current_round):

  # Get score before the round for score board
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
    

    # Background Image rendering
    background_img = pygame.image.load("image_assets/background.png")
    background_img = pygame.transform.scale( background_img , (WIDTH,HEIGHT) )
    display_surface.blit( background_img,(0,0) )   

    # Render score board
    ScoreBoard( current_round , (score1,score2) )

    # As we want laser to behind the other sprites
    for laser in laser_group:
      laser.draw(display_surface)

    # Displaying all entities
    for entity in all_sprites:
      
      # So we do not render lasers again
      if laser_group.has(entity): continue

      entity.draw( display_surface )

    # Update and count Frame
    pygame.display.update()
    FramePerSec.tick(FPS)

    PlatformGeneration()
    DestroyOutbounds()

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
    
    round_result = CheckIfRoundOver()
    if not isinstance( round_result , bool ):
        
        # To let the explosions render at last and not directly
        # cut to the next round
        if len(explosion_group)==0:
          pass
        else:  
          end_screen_time = pygame.time.get_ticks() + 1000
          while pygame.time.get_ticks()<end_screen_time:
            
            pygame.display.update()
            FramePerSec.tick(FPS)
            for exp in explosion_group:
              exp.draw(display_surface)
          
        return

    # Handle horizontal player interaction
    PlayerInteract()
    # Check if laser and explosion should end
    laser_update()
    explosion_update()


# -------------------------------------------------
# Just call main function that takes care of game state management

if __name__ == '__main__':
    main()



























