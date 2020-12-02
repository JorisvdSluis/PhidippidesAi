# ====== Legal notices
#
# Copyright (C) 2013 - 2020 GEATEC engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.
#
# The QQuickLicense can be accessed at: http://www.geatec.com/qqLicence.html
#
# __________________________________________________________________________
#
#
#  THIS PROGRAM IS FUNDAMENTALLY UNSUITABLE FOR CONTROLLING REAL SYSTEMS !!
#
# __________________________________________________________________________
#
# It is meant for training purposes only.
#
# Removing this header ends your licence.
#

import time as tm
import traceback as tb
import math
import simpylc as sp
import pid as pid
import road_coordinator as rd
import cv2 

class CameraPilot:
    def __init__ (self):
        print ('Use up arrow to start, down arrow to stop')
        
        self.driveEnabled = False
        sp.world.physics.proportional.set(0.40)
        sp.world.physics.intergral.set(20)
        sp.world.physics.differential.set(15)
        self.steeringPID = pid.Pid(sp.world.physics.proportional,sp.world.physics.intergral, sp.world.physics.differential)
        self.driveEnabled = True
        self.targetVelocity = 0.7
        self.steeringAngle = 0

        coordinator = rd.RoadCoordinator(200,0,[100,150,0],[140,255,255])
        cap = cv2.VideoCapture('test.mp4')
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                coordinator.getRoadBorderCoordinates(frame)
                soughtAfterAngle = math.degrees(math.atan((coordinator.middleY / coordinator.middleX)))
                
                cv2.imshow('frame',frame)
                self.sweep (soughtAfterAngle * -10)
                self.output ()
                tm.sleep (0.01)

                
                if cv2.waitKey(25) & 0xFF == ord('q'):    
                    break
            else:
                break

        cap.release()
        cv2.destroyAllWindows()

        
        
        
    def sweep (self,angle):   # Control algorithm to be tested
  
        
        #set steering angle
        self.steeringAngle = sp.world.physics.steeringAngle
        self.controlSteeringAngle(angle)
        #set velocity
        # self.targetVelocity = (90 - sp.abs (self.steeringAngle))/75 if self.driveEnabled else 0



    def controlSteeringAngle(self, soughtAfterAngle): 
        currentAngle = sp.world.physics.steeringAngle
        self.steeringAngle =self.steeringPID.control(currentAngle, soughtAfterAngle, 0.02)

    def output (self):  # Output to simulator
        sp.world.physics.steeringAngle.set (self.steeringAngle)
        sp.world.physics.targetVelocity.set (self.targetVelocity)
        
