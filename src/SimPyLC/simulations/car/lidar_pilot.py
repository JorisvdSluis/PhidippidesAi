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

class LidarPilot:
    def __init__ (self):
        print ('Use up arrow to start, down arrow to stop')
        
        self.driveEnabled = False
        
        while True:
            self.input ()
            self.sweep ()
            self.output ()
            tm.sleep (0.02)
        
    def input (self):   # Input from simulator
        key = sp.getKey ()
        
        if key == 'KEY_UP':
            self.driveEnabled = True
        elif key == 'KEY_DOWN':
            self.driveEnabled = False
        
        self.lidarDistances = sp.world.visualisation.lidar.distances
        self.lidarHalfApertureAngle = sp.world.visualisation.lidar.halfApertureAngle
        
    def sweep (self):   # Control algorithm to be tested
        self.LeftObstacleDistance = sp.finity
        self.LeftObstacleAngle = 0
        
        self.nextLeftObstacleDistance = sp.finity
        self.nextLeftObstacleAngle = 0

        self.RightObstacleDistance = sp.finity
        self.RightObstacleAngle = 0
        
        self.nextRightObstacleDistance = sp.finity
        self.nextRightObstacleAngle = 0

        for lidarAngle in range (-self.lidarHalfApertureAngle, self.lidarHalfApertureAngle):
            lidarDistance = self.lidarDistances [lidarAngle]
            # Detect 4 closest points 
            # discard points within 15 degrees to avoid a head on collision  
            if lidarDistance < self.LeftObstacleDistance and lidarAngle < -15:
                self.nextLeftObstacleDistance =  self.LeftObstacleDistance
                self.nextLeftObstacleAngle = self.LeftObstacleAngle 
                self.LeftObstacleDistance = lidarDistance 
                self.LeftObstacleAngle = lidarAngle
            elif lidarDistance < self.RightObstacleDistance and lidarAngle > 15:
                self.nextRightObstacleDistance =  self.RightObstacleDistance
                self.nextRightObstacleAngle = self.RightObstacleAngle
                self.RightObstacleDistance = lidarDistance 
                self.RightObstacleAngle = lidarAngle
            elif lidarDistance < self.nextLeftObstacleDistance and lidarAngle < -15:
                self.nextLeftObstacleDistance = lidarDistance
                self.nextLeftObstacleAngle = lidarAngle
            elif lidarDistance < self.nextRightObstacleDistance and lidarAngle > 15:
                self.nextRightObstacleDistance = lidarDistance
                self.nextRightObstacleAngle = lidarAngle
                
        #calculate coordinates for 4 closest points 
        self.coordinatesNR = self.calculateCoordinates(self.nextRightObstacleAngle, self.nextRightObstacleDistance)
        self.coordinatesR = self.calculateCoordinates(self.RightObstacleAngle, self.RightObstacleDistance)
        self.coordinatesNL = self.calculateCoordinates(self.nextLeftObstacleAngle, self.nextLeftObstacleDistance)
        self.coordinatesL = self.calculateCoordinates(self.LeftObstacleAngle, self.LeftObstacleDistance)

        #calculate coordinates for middle point  
        self.xMiddle = self.coordinatesL[0] + self.coordinatesNL[0] + self.coordinatesR[0] + self.coordinatesNR[0]
        self.yMiddle = self.coordinatesL[1] + self.coordinatesNL[1] + self.coordinatesR[1] + self.coordinatesNR[1]

        #calculate angle and velocity from middle point
        self.steeringAngle = math.degrees(math.atan((self.yMiddle / self.xMiddle)))
        self.targetVelocity = (90 - sp.abs (self.steeringAngle))/80 if self.driveEnabled else 0
    
    def calculateCoordinates(self, angle, distance):
        x = math.cos(math.radians(angle)) * distance
        y = math.sin(math.radians(angle)) * distance
        return (x,y)

    def output (self):  # Output to simulator
        sp.world.physics.steeringAngle.set (self.steeringAngle)
        sp.world.physics.targetVelocity.set (self.targetVelocity)
        
