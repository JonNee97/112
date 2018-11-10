
import pygame
from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import sys
import math
import random

pygame.init()



class Axolotyl(object):
    def __init__(self, x, y, width, height, picture, attack):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = (self.x, self.y, self.x+self.width) 
        self.health = 10
        self.picture = picture
        self.attackPic = attack

    def draw(self,win,flag):
        if flag == False:
            win.blit(self.picture, (self.x,self.y))
        elif flag == True:
            win.blit(self.attackPic, (self.x,self.y))
        pygame.draw.rect(win, (255,0,0), (self.hitbox[0], self.hitbox[1] - 70, self.width, 20))
        pygame.draw.rect(win, (0,128,0), (self.hitbox[0], self.hitbox[1] - 70, self.width - ((self.width//10) * (10 - self.health)), 20))

    def hit(self):
        if self.health > 0:
            self.health -= 1
        else:
            return True
                
class Dog(object):
    def __init__(self, x, y, width, height, picture, attack):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = (self.x, self.y, self.x+self.width)  # Need to update to top of screen
        self.health = 10
        self.picture = picture
        self.attackPic = attack

    def draw(self,win,flag):
        if flag == False:
            win.blit(self.picture, (self.x,self.y))
        elif flag == True:
            win.blit(self.attackPic, (self.x,self.y))
        pygame.draw.rect(win, (255,0,0), (self.hitbox[0], self.hitbox[1] - 50, self.width, 20))
        pygame.draw.rect(win, (0,128,0), (self.hitbox[0], self.hitbox[1] - 50, self.width - ((self.width//10) * (10 - self.health)), 20))

    def hit(self):
        if self.health > 0:
            self.health -= 1
        else:
            return True

class projectile(object):
    def __init__(self,x,y,radius,color,speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel = 8 * speed

    def draw(self,win):
        pygame.draw.circle(win, self.color, (self.x,self.y), self.radius)

def playGame(fire):
    #mainloop
    
    
    
    
    win = pygame.display.set_mode((1000,600))

    kimcheePic = pygame.image.load('kimchee2.png')
    stellaPic = pygame.image.load('stella2.png')
    bg = pygame.image.load('bg.png')
    kimcheeAtk = pygame.image.load('kimcheeOpen2.png')
    stellaAtk = pygame.image.load('stellaOpen2.png')

    clock = pygame.time.Clock()

    kimchee = Axolotyl(100, 300, 175, 175, kimcheePic, kimcheeAtk)
    stella = Dog(700, 280, 170, 170, stellaPic, stellaAtk)
    bulletsK = []
    bulletsS = []
    run = True
    width = 1000
    height = 600
    gameOver = False
    isJump = False
    jumpCount = 10
    
    
    kimcheeFlag = False
    stellaFlag = False

    clock.tick(27)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    gameOver1 = moveBullets(bulletsK, stella)
    gameOver2 = moveBullets(bulletsS, kimchee)
    
    if gameOver1 == True or gameOver2 == True:
        run = False
        print("Game Over")  # Display game over screen

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:  ## EDIT BASED ON KINECT MAKE SURE ONLY 1 FIRED AT ONCE
        kimcheeFlag = True
        bulletsK.append(projectile(round(kimchee.x + kimchee.width //2), round(kimchee.y + kimchee.height//2 + 10), 6, (20,50,150), 1)) # EDIT BASED ON THEIR MOUTH LOCATION
    if fire:  ## EDIT BASED ON KINECT MAKE SURE ONLY 1 FIRED AT ONCE
        stellaFlag = True
        bulletsS.append(projectile(round(stella.x + stella.width //2), round(stella.y + stella.height//2 + 35), 6, (200,0,0), -1)) # EDIT BASED ON THEIR MOUTH LOCATION
   
    win.blit(bg, (0,0))
    kimchee.draw(win, kimcheeFlag)
    stella.draw(win, stellaFlag)
    for bullet in bulletsK:
        bullet.draw(win)
    for bullet in bulletsS:
        bullet.draw(win)
        
        
    if not(isJump):
        if keys[pygame.K_SPACE]:
            isJump = True
    else:
        if jumpCount >= -10:
            neg = 1
            if jumpCount < 0:
                neg = -1
            stella.y -= (jumpCount ** 2) * 0.5 * neg
            jumpCount -= 1
        else:
            isJump = False
            jumpCount = 10

    pygame.display.update()

def moveBullets(listBullets, opponent):
    gameOver = 0
    for bullet in listBullets:
            bullet.x += bullet.vel
            if bullet.x + bullet.radius > opponent.hitbox[0] and bullet.x - bullet.radius < opponent.hitbox[0] + opponent.hitbox[2]:
                gameOver = opponent.hit()
                listBullets.pop(listBullets.index(bullet))
    return gameOver


class GameRuntime(object):
    
    def __init__(self):
        pygame.init()

        self.screenWidth = 1920
        self.screenHeight = 1080

        self.delta = 0
        self.deltaJump = 0
        self.flag = False

        self.prevRightHandHeight = 0
        self.curRightHandHeight = 0
        self.preHeight = 0
        self.curHeight = 0
        self.handState = 0
        self.bodyState = 0

        self.gameover = False
        
        self.fire = 0
        self.body = 0


        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

        # Set the width and height of the window [width/2, height/2]
        self.screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

        # Loop until the user clicks the close button.
        self.done = False

        # Kinect runtime object, we want color and body frames 
        self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self.frameSurface = pygame.Surface((self.kinect.color_frame_desc.Width, self.kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data 
        self.bodies = None


    def drawColorFrame(self, frame, targetSurface):
        targetSurface.lock()
        address = self.kinect.surface_as_array(targetSurface.get_buffer())
        # replacing old frame with new one
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        targetSurface.unlock()

    def run(self):
        
        # -------- Main Program Loop -----------
        while not self.done:
            # --- Main event loop
            if self.gameover:
                font = pygame.font.Font(None, 36)
                text = font.render("Game over!", 1, (0, 0, 0))
                self.frameSurface.blit(text, (100,100))
                break
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self.done = True # Flag that we are done so we exit this loop

            # We have a color frame. Fill out back buffer surface with frame's data 
            if self.kinect.has_new_color_frame():
                frame = self.kinect.get_last_color_frame()
                self.drawColorFrame(frame, self.frameSurface)
                frame = None

            # We have a body frame, so can get skeletons
            if self.kinect.has_new_body_frame(): 
                self.bodies = self.kinect.get_last_body_frame()

                if self.bodies is not None: 
                    for i in range(0, self.kinect.max_body_count):
                        body = self.bodies.bodies[i]
                        if not body.is_tracked:
                            self.curRightHandHeight = 0
                            continue 
                    
                        joints = body.joints 
                        # save the hand positions
                        if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            
                            self.curRightHandHeight = joints[PyKinectV2.JointType_HandRight].Position.y
                            print("Called!")
                        if joints[PyKinectV2.JointType_Neck].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.curHeight = joints[PyKinectV2.JointType_Neck].Position.y
                            print(self.curHeight)
                            
          

                        # calculate delta y to see if is firing
                        self.delta = self.prevRightHandHeight - self.curRightHandHeight
                        self.deltaJump = self.prevHeight - self.curHeight
                        if math.isnan(self.delta) or self.delta > 0:
                            self.handState = 0
                            self.delta = 0
                        if math.isnan(self.deltaJump) or self.deltaJump > 0:
                            self.deltaJump = 0
                            self.bodyState = 0
                            
                tempflag = self.flag
                if self.handState >= 6:
                    self.flag = True
                    if tempflag == False:
                        self.fire = True
                else: 
                    self.flag = False
                    selffire = False
                
                playGame(self.fire)
                        
            self.handState -= self.delta*30
            self.bodyState -= self.deltaJump *30
            # cycle previous and current heights for next time
            self.prevRightHandHeight = self.curRightHandHeight
            self.prevHeight = self.curHeight
            #print("hand:",self.handState,end = "") # debug: printing handState
            print("body:",self.bodyState)
            

            
            
            pygame.display.update()
            
            
            
            # --- game logic

            # --- Limit to 60 frames per second
            self.clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()



game = GameRuntime()
game.run()
    #playGame()


