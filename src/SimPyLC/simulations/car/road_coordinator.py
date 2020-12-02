import math
import numpy as np
import cv2 
class RoadCoordinator:

    # set height and color of the road in image 
    # minRoadHeight = number of pixel up from the bottom of the image
    # maxRoadHeight = number of pixel down from the top of the image
    # colorformat = [255,255,255]
    def __init__(self, minRoadHeight, maxRoadHeight, lowRoadColor, highRoadColor):
        self.minRoadHeight = minRoadHeight
        self.maxRoadHeight = maxRoadHeight
        self.lowRoadColor = lowRoadColor
        self.highRoadColor = highRoadColor

    # image should opencv2 image
    # returns (leftborderline, rightborderline, middleRoadline)
    # line consists of 2 coordinates for top and bottom
    def getRoadBorderCoordinates(self, image):
        self.image = image
        threshold = self._convertImage(image)
        roadCenterCoordinates = self._calculateRoadBorderCoordinates(threshold)
        self._visualize(image, roadCenterCoordinates)
        return roadCenterCoordinates

    def _convertImage(self, image):
        height = image.shape[0]
        width = image.shape[1]
        image = image[self.minRoadHeight: height - self.maxRoadHeight,0:width]
        blur = cv2.blur(image,(5,5))
        blur0=cv2.medianBlur(blur,5)
        blur1= cv2.GaussianBlur(blur0,(5,5),0)
        blur2= cv2.bilateralFilter(blur1,9,75,75)
        maskRed = cv2.inRange(blur2, np.array([0, 0, 0]), np.array([155, 55, 255]))
        image[maskRed>0]=(255,72,0)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lowRoadColor = np.array(self.lowRoadColor)
        highRoadColor = np.array(self.highRoadColor)
        mask = cv2.inRange(hsv, lowRoadColor, highRoadColor)
        threshold = cv2.threshold(mask, 145, 255, cv2.THRESH_BINARY_INV)[1]
        return threshold

    # 1 calculates and sort contours by size
    # 2 calculates road border lines
    # 3 calculates center road lines
    def _calculateRoadBorderCoordinates(self, threshold):
        cnts = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        s = sorted(cnts,key=cv2.contourArea,  reverse=True )
        first = s[0]
        second = s[1]
        # Obtain road border coordinates
        bottomFirst = tuple(first[first[:, :, 1].argmax()][0])
        bottomSecond = tuple(second[second[:, :, 1].argmax()][0])
        topFirst = tuple(first[first[:, :, 0].argmax()][0])
        topSecond = tuple(second[second[:, :, 0].argmin()][0])
        leftRoadBorder = (bottomFirst, topFirst)
        rightRoadBorder = (bottomSecond, topSecond)

        if(bottomFirst[0] > bottomSecond[0]):
            topFirst = tuple(first[first[:, :, 0].argmin()][0])
            topSecond = tuple(second[second[:, :, 0].argmax()][0])
            leftRoadBorder = (bottomSecond, topSecond)
            rightRoadBorder = (bottomFirst, topFirst)
        
        # calculate center top & bottom of road
        bottomMiddle = (int((bottomFirst[0] + bottomSecond[0]) / 2),int((bottomFirst[1] + bottomSecond[1]) / 2))
        topMiddle = (int((topFirst[0] + topSecond[0]) / 2),int((topFirst[1] + topSecond[1]) / 2))
        middleRoad = (bottomMiddle, topMiddle)
        self.middleX = (topFirst[0] + topSecond[0])/2
        self.middleY = (topFirst[1] + topSecond[1])/2
        return(leftRoadBorder, rightRoadBorder, middleRoad)
    
    def _visualize(self, image ,result):
        height = image.shape[0]
        width = image.shape[1]
        image = image[self.minRoadHeight: height - self.maxRoadHeight,0:width]
        for line in result:
            cv2.line(image, line[0], line[1], (255, 255, 255), thickness=2)
            for point in line:
                cv2.circle(image, point, 8, (255, 255, 255), -1)
