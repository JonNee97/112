from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
import random


class GameRuntime(object):
    def __init__(self):
        pygame.init()

        self.screenWidth = 1920
        self.screenHeight = 1080

        self.delta = [0]*2
        self.flag = False

        self.prevx = [0]*2
        self.curx = [0]*2
        self.prevHand = [0]*2
        self.curHand = [0]*2
        self.heightState = [0]*2

        self.gameover = False


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
                            continue 
                    
                        joints = body.joints 
                        # save the hand positions
                        if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.curRightHandHeight[i] = joints[PyKinectV2.JointType_HandRight].Position.y
          

                        # calculate delta y to see if is firing
                        self.delta[i] = self.prevRightHandHeight[i] - self.curRightHandHeight[i]
                        if math.isnan(self.delta[i]) or self.delta[i] < 0:
                            self.delta[i] = 0
                            self.handState[i] = 0
                        
                        self.handState += self.delta*10

                        # cycle previous and current heights for next time
                        self.prevRightHandHeight[i] = self.curRightHandHeight[i]

                        if self.handState[i] >= 30:
                            self.flag = True
                        else: self.flag = False

            
            hToW = float(self.frameSurface.get_height()) / self.frameSurface.get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface, (self.screen.get_width(), targetHeight));
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None
            pygame.display.update()

            # --- Limit to 60 frames per second
            self.clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()

game = GameRuntime();
game.run();


class Fighter(object):
    def __init__(self, name, hp, strength,num):
        self.name = name
        self.hp = hp
        self.strength = strength

        self.prevx = 0
        self.prevy = 0
        self.curx = 0
        self.cury = 0
        self.prevHand = 0
        self.curHand = 0
        self.bodies = None

        self.num = num

    def move(self, horizontal, vertical, speed):
        if self.kinect.has_new_color_frame():
            frame = self.kinect.get_last_color_frame()
            self.drawColorFrame(frame, self.frameSurface)
            frame = None

        # We have a body frame, so can get skeletons
        if self.kinect.has_new_body_frame(): 
            self.bodies = self.kinect.get_last_body_frame()

            if self.bodies is not None: 
                body = self.bodies.bodies[self.num]
                if body.is_tracked: 
                    joints = body.joints 
                    # save the hand positions
                    if joints[PyKinectV2.JointType_Neck].TrackingState != PyKinectV2.TrackingState_NotTracked:
                        self.curx = joints[PyKinectV2.JointType_Neck].Position.x
                        self.cury = joints[PyKinectV2.JointType_Neck].Position.y

                    # cycle previous and current coefficient for next time
                    self.prevx = self.curx
                    self.prevy = self.cury


    def fire(self):
        body = self.bodies.bodies
        if body.is_tracked:
            joints = body.joints
            if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked:
                self.curRightHandHeight = joints[PyKinectV2.JointType_HandRight].Position.y

            self.curHand = joints[PyKinectV2.JointType_HandRight.TrackingState].Position.y

            self.prevHand = self.curHand
            


