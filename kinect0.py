'''
Created on 2018 M11 10

@author: Tina
'''
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
                        
            self.handState -= self.delta*30
            self.bodyState -= self.deltaJump *30
            # cycle previous and current heights for next time
            self.prevRightHandHeight = self.curRightHandHeight
            self.prevHeight = self.curHeight
            #print("hand:",self.handState,end = "") # debug: printing handState
            print("body:",self.bodyState)
            if self.handState >= 6:
                self.flag = True
            else: self.flag = False

            
            hToW = float(self.frameSurface.get_height()) / self.frameSurface.get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface, (self.screen.get_width(), targetHeight))
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None
            pygame.display.update()

            # --- Limit to 60 frames per second
            self.clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()

game = GameRuntime()
game.run()





