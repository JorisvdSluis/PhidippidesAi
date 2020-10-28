class segmentator: 
    def __init__ (self, speed, minimalRadius, minimalHeight, maximumHeight):
         self.speed = speed
         self.minimalRadius = minimalRadius
         self.minimalHeight = minimalHeight
         self.maximumHeight = maximumHeight
         self.radius = self.minimalRadius + (self.speed/2) 
         self.segmentatedPoints = []

    def segmentate(self, data):
        for points in data:
            x =  points.get('x')
            y =  points.get('y')
            z = points.get('z') 
            if(self.isWithinMinimalDistance(x,y,z)):
                self.segmentatedPoints.append(points)
        return self.segmentatedPoints

    def isWithinMinimalDistance(self, x, y, z):
        if(z > self.minimalHeight and z < self.maximumHeight):
            if(x > -self.radius and x < self.radius):
                if(y > -self.radius and y < self.radius):
                    return True
        return False

# for testing purposes only
from read_json import read_json
import json as json
pointcloud = read_json()
seg = segmentator(11.1111111, 4,-1,1.5)
points = seg.segmentate(pointcloud)

file = open("segmentation.txt", "a")
for point in points:    
    file.write(str(point.get('x')) +" "+str(point.get('y'))+" "+str(point.get('z')) + "\n")
file.close()