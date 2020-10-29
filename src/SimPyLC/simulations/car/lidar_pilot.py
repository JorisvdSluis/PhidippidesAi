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

        self.rightRoadBorder = sp.finity
        self.rightRoadBorderAngle = 0
        
        self.nextRightRoadBorder = sp.finity
        self.nextRightRoadBorderAngle = 0
        self.alternativeCoordinates = (0,0)
        self.closestObstacleDistance = sp.finity
        self.closestObstacleAngle = 0
        for lidarAngle in range (-self.lidarHalfApertureAngle, self.lidarHalfApertureAngle):
            lidarDistance = self.lidarDistances [lidarAngle]
            obstacleDistance = self.obstacleDistances [lidarAngle]
            
            # Detect 4 closest points of road borders
            self.calculateFourClosestPoints(lidarAngle,lidarDistance)
            # Detect closest obstacle
            self.calculateClosestObstacle(obstacleDistance, lidarAngle)

        #check if obstacle within current direction
        #and calculate coordinates for middle point with or without obstacle
        self.coordinatesNR = self.calculateCoordinates(self.nextRightRoadBorderAngle, self.nextRightRoadBorder)
        self.coordinatesR = self.calculateCoordinates(self.rightRoadBorderAngle, self.rightRoadBorder)
        self.coordinatesNL = self.calculateCoordinates(self.nextLeftRoadBorderAngle, self.nextLeftRoadBorder)
        self.coordinatesL = self.calculateCoordinates(self.leftRoadBorderAngle, self.leftRoadBorder)
        self.coordinatesO = self.calculateCoordinates(self.closestObstacleAngle, self.closestObstacleDistance)
         
        if(self.closestObstacleAngle > -25 and self.closestObstacleAngle < 25 and self.isObstacleWithinDirection()):
            self.avoidObstacleCollision()
       
        self.xMiddle = self.coordinatesL[0] + self.coordinatesNL[0] + self.coordinatesR[0] + self.coordinatesNR[0]
        self.yMiddle = self.coordinatesL[1] + self.coordinatesNL[1] + self.coordinatesR[1] + self.coordinatesNR[1]

        #set steering angle
        self.steeringAngle = sp.world.physics.steeringAngle
        self.controlSteeringAngle()
        #set velocity
        self.targetVelocity = (90 - sp.abs (self.steeringAngle))/75 if self.driveEnabled else 0
    
    def calculateClosestObstacle(self,distance, angle):
        if(self.closestObstacleDistance > distance):
            self.closestObstacleDistance = distance
            self.closestObstacleAngle = angle

    #check if obstacle closer than road borders
    def isObstacleWithinDirection(self):
        if(self.nextRightRoadBorder < self.closestObstacleDistance and
         self.rightRoadBorder < self.closestObstacleDistance and
         self.nextLeftRoadBorder < self.closestObstacleDistance and
         self.leftRoadBorder < self.closestObstacleDistance ):
            return False
        return True

    def avoidObstacleCollision(self):
        distanceL = math.sqrt(math.pow(sp.abs(self.coordinatesO[0] - self.coordinatesL[0]),2) +  math.pow(sp.abs(self.coordinatesO[1] - self.coordinatesL[1]),2))
        distanceR = math.sqrt(math.pow(sp.abs(self.coordinatesO[0] - self.coordinatesR[0]),2) +  math.pow(sp.abs(self.coordinatesO[1] - self.coordinatesR[1]),2))
        distanceNL = math.sqrt(math.pow(sp.abs(self.coordinatesO[0] - self.coordinatesNL[0]),2) +  math.pow(sp.abs(self.coordinatesO[1] - self.coordinatesNL[1]),2))
        distanceNR = math.sqrt(math.pow(sp.abs(self.coordinatesO[0] - self.coordinatesNR[0]),2) +  math.pow(sp.abs(self.coordinatesO[1] - self.coordinatesNR[1]),2))
        if(distanceL < distanceR and distanceL < distanceNL and distanceL < distanceNR):
            self.coordinatesL = (self.coordinatesO[0], self.coordinatesO[1] )
        elif(distanceR < distanceNL and distanceR < distanceNR):
            self.coordinatesR = (self.coordinatesO[0], self.coordinatesO[1] )
        elif(distanceNL < distanceNR):
            self.coordinatesNL = (self.coordinatesO[0], self.coordinatesO[1] )
        else:
            self.coordinatesNR = (self.coordinatesO[0], self.coordinatesO[1] )

    def calculateFourClosestPoints(self, lidarAngle, lidarDistance):
        # discard points within 25 degrees to avoid a head on collision  
        if lidarDistance < self.leftRoadBorder and lidarAngle < -25:
            self.nextLeftRoadBorder =  self.leftRoadBorder
            self.nextLeftRoadBorderAngle = self.leftRoadBorderAngle 
            self.leftRoadBorder = lidarDistance 
            self.leftRoadBorderAngle = lidarAngle
        elif lidarDistance < self.rightRoadBorder and lidarAngle > 25: 
            self.nextRightRoadBorder =  self.rightRoadBorder
            self.nextRightRoadBorderAngle = self.rightRoadBorderAngle
            self.rightRoadBorder = lidarDistance 
            self.rightRoadBorderAngle = lidarAngle
        elif lidarDistance < self.nextLeftRoadBorder and lidarAngle < -25:
            self.nextLeftRoadBorder = lidarDistance
            self.nextLeftRoadBorderAngle = lidarAngle
        elif lidarDistance < self.nextRightRoadBorder and lidarAngle > 25:
            self.nextRightRoadBorder = lidarDistance
            self.nextRightRoadBorderAngle = lidarAngle

    def calculateCoordinates(self, angle, distance):
        x = math.cos(math.radians(angle)) * distance
        y = math.sin(math.radians(angle)) * distance
        return (x,y)

    def controlSteeringAngle(self): 
        soughtAfterAngle = math.degrees(math.atan((self.yMiddle / self.xMiddle)))
        currentAngle = sp.world.physics.steeringAngle
        diffrence = soughtAfterAngle - currentAngle

        if(diffrence > 30 or diffrence < -30):
            self.steeringAngle = currentAngle + (diffrence / 40)
        if(diffrence > 25 or diffrence < -25):
            self.steeringAngle = currentAngle + (diffrence / 12.5)
        elif(diffrence > 20 or diffrence < -20):
            self.steeringAngle = currentAngle + (diffrence / 10)
        elif(diffrence > 15 or diffrence < -15):
            self.steeringAngle = currentAngle + (diffrence / 8)
        elif(diffrence > 10 or diffrence < -10):
            self.steeringAngle = currentAngle + (diffrence / 6)
        elif(diffrence > 5 or diffrence < -5):
            self.steeringAngle = currentAngle + (diffrence / 4)
        elif(diffrence > 2.5 or diffrence < -2.5):
            self.steeringAngle = currentAngle + (diffrence / 2)
        else:
             self.steeringAngle = currentAngle + diffrence

    def output (self):  # Output to simulator
        sp.world.physics.steeringAngle.set (self.steeringAngle)
        sp.world.physics.targetVelocity.set (self.targetVelocity)
        
