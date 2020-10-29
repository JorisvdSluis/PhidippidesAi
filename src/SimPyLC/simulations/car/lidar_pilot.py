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
        
        self.lidarDistances = sp.world.visualisation.lidar.roadDistances
        self.obstacleDistances = sp.world.visualisation.lidar.distances
        self.lidarHalfApertureAngle = sp.world.visualisation.lidar.halfApertureAngle
        
    def sweep (self):   # Control algorithm to be tested
        self.leftRoadBorder = sp.finity
        self.leftRoadBorderAngle = 0
        
        self.nextLeftRoadBorder = sp.finity
        self.nextLeftRoadBorderAngle = 0

        self.rightRoadborder = sp.finity
        self.rightRoadBorderAngle = 0
        
        self.nextRightRoadborder = sp.finity
        self.nextRightRoadBorderAngle = 0

        for lidarAngle in range (-self.lidarHalfApertureAngle, self.lidarHalfApertureAngle):
            lidarDistance = self.lidarDistances [lidarAngle]
            obstacleDistance = self.obstacleDistances [lidarAngle]
            
            #check if encountering obstacles
            self.avoidObstacleCollision(lidarAngle, obstacleDistance)

            # Detect 4 closest points of road borders
            # discard points within 25 degrees to avoid a head on collision  
            if lidarDistance < self.leftRoadBorder and lidarAngle < -25:
                self.nextLeftRoadBorder =  self.leftRoadBorder
                self.nextLeftRoadBorderAngle = self.leftRoadBorderAngle 
                self.leftRoadBorder = lidarDistance 
                self.leftRoadBorderAngle = lidarAngle
            elif lidarDistance < self.rightRoadborder and lidarAngle > 25:
                self.nextRightRoadborder =  self.rightRoadborder
                self.nextRightRoadBorderAngle = self.rightRoadBorderAngle
                self.rightRoadborder = lidarDistance 
                self.rightRoadBorderAngle = lidarAngle
            elif lidarDistance < self.nextLeftRoadBorder and lidarAngle < -25:
                self.nextLeftRoadBorder = lidarDistance
                self.nextLeftRoadBorderAngle = lidarAngle
            elif lidarDistance < self.nextRightRoadborder and lidarAngle > 25:
                self.nextRightRoadborder = lidarDistance
                self.nextRightRoadBorderAngle = lidarAngle

        #calculate coordinates for 4 closest points 
        self.coordinatesNR = self.calculateCoordinates(self.nextRightRoadBorderAngle, self.nextRightRoadborder)
        self.coordinatesR = self.calculateCoordinates(self.rightRoadBorderAngle, self.rightRoadborder)
        self.coordinatesNL = self.calculateCoordinates(self.nextLeftRoadBorderAngle, self.nextLeftRoadBorder)
        self.coordinatesL = self.calculateCoordinates(self.leftRoadBorderAngle, self.leftRoadBorder)

        #calculate coordinates for middle point  
        self.xMiddle = self.coordinatesL[0] + self.coordinatesNL[0] + self.coordinatesR[0] + self.coordinatesNR[0]
        self.yMiddle = self.coordinatesL[1] + self.coordinatesNL[1] + self.coordinatesR[1] + self.coordinatesNR[1]

        #calculate angle and velocity from middle point
        if(math.degrees(math.atan((self.yMiddle / self.xMiddle))) > 5 or math.degrees(math.atan((self.yMiddle / self.xMiddle))) < -5):
            self.steeringAngle = (math.degrees(math.atan((self.yMiddle / self.xMiddle))) + (sp.world.physics.steeringAngle*15))/16
        else:
            self.steeringAngle = math.degrees(math.atan((self.yMiddle / self.xMiddle)))
        self.targetVelocity = (90 - sp.abs (self.steeringAngle))/80 if self.driveEnabled else 0
    
    def avoidObstacleCollision(self, lidarAngle, obstacleDistance):
        if(lidarAngle > -25 and lidarAngle < 25):
            #check if obstacle closer than road borders
            if((obstacleDistance < self.leftRoadBorder and self.leftRoadBorder < sp.finity) or  (obstacleDistance < self.rightRoadborder and self.rightRoadborder < sp.finity) ): 
                #find biggest gap to drive through
                if(sp.abs(obstacleDistance - self.leftRoadBorder) > sp.abs(obstacleDistance - self.rightRoadborder) ):
                    self.rightRoadborder = obstacleDistance
                    self.rightRoadBorderAngle = lidarAngle
                else:
                    self.leftRoadBorder = obstacleDistance
                    self.leftObstacleAngle = lidarAngle
            elif((obstacleDistance < self.nextLeftRoadBorder and self.nextLeftRoadBorder < sp.finity) or  (obstacleDistance < self.nextRightRoadborder and self.nextRightRoadborder < sp.finity)):
                if(sp.abs(obstacleDistance - self.nextLeftRoadBorder) > sp.abs(obstacleDistance - self.nextRightRoadborder) ):
                    self.nextRightRoadborder = obstacleDistance
                    self.nextRightRoadBorderAngle = lidarAngle
                else:
                    self.nextLeftRoadBorder = obstacleDistance
                    self.nextLeftRoadBorderAngle = lidarAngle

    def calculateCoordinates(self, angle, distance):
        x = math.cos(math.radians(angle)) * distance
        y = math.sin(math.radians(angle)) * distance
        return (x,y)

    def output (self):  # Output to simulator
        sp.world.physics.steeringAngle.set (self.steeringAngle)
        sp.world.physics.targetVelocity.set (self.targetVelocity)
        
