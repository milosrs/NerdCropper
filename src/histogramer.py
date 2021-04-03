import cv2
import numpy as np
import json
import random
import math
import enum
import matplotlib.pyplot as plt
from Equation import Expression
from noises import PerlinNoise, SimplexNoise, normalize

# ---------------------- CLASSES AND ENUMS -------------- #
class Configuration:
    def __init__(self):
        self.__readConfigFile()

    def __readConfigFile(self):
        with open('config.json', 'r') as configFile:
            self.data = configFile.read()

        self.configObj = json.loads(self.data)
        return self.configObj

    def readKey(self, key):
        return self.configObj[key]

class Position(enum.Enum):
    ABOVE = 1
    UNDER = 2

class Band:
    def __init__(self, bandDefs):
        self.bandDefinition = {}

        for key in bandDefs.keys():
            func = Expression(bandDefs[key][0], ["x", "y"])
            pos = bandDefs[key][1]
            self.bandDefinition[key] = (self.__solveKernelDefinition(func), self.__convertPositionStringToEnum(pos), func)

    #Generates X axis dots and solves an expression which defines a band
    #Coordinate system is moved to the center of the image
    def __solveKernelDefinition(self, f):
        xAxis = range(-kernelSize, kernelSize)
        dots = []

        for x in xAxis:
            sol = f(x, kernelSize) / (kernelSize / 2)
            dots.append(sol)

        print(dots)
        return dots

    def __convertPositionStringToEnum(self, positionString):
        return Position.ABOVE if positionString == "ABOVE" else Position.UNDER

    def __functionData(self):
        data = []

        for key in self.bandDefinition:
            data.append(self.bandDefinition[key][0])

        return data

    def plotFunction(self):
        funcData = self.__functionData()

        for data in funcData:
            plt.plot(data)

        plt.show()


configObject = Configuration()
# ---------------Read data from configuration----------------- #
# Config constants
leftEdgeMargin = configObject.readKey('leftEdgeMargin')
rightEdgeMargin = configObject.readKey('rightEdgeMargin')
topEdgeMargin = configObject.readKey('topEdgeMargin')
bottomEdgeMargin = configObject.readKey('bottomEdgeMargin')
laneOffset = configObject.readKey('laneOffset')
xAxisMaxJitter = configObject.readKey('xAxisMaxJitter')
minPrintOffset = configObject.readKey('minPrintOffset')
maxPrintOffset = configObject.readKey('maxPrintOffset')
minPrintStrength = configObject.readKey('minPrintStrength')
maxPrintStrength = configObject.readKey('maxPrintStrength')
laneNumber = configObject.readKey('lanesNumber')
# Kernel = Band
kernelSize = configObject.readKey('bandSize')
# Kernel function = Band Definition
kernelFunctions = configObject.readKey('bandDefinitions')

def createImage(width, height, color):
    blank_image = np.zeros((height, width), np.uint8)
    blank_image[:, :] = color
    return blank_image

def kernelNoise(kernelSize, num_octaves, persistence, currentBand, dimensions=2):
    simplex = SimplexNoise(num_octaves, persistence, dimensions)
    data = []

    for i in range(kernelSize):
        data.append([])
        i1 = i - int(kernelSize / 2)

        for j in range(kernelSize):
            j1 = j - int(kernelSize / 2)
            if(shouldPixelGetNoise(i1, j1, i, currentBand)):
                noise = normalize(simplex.fractal(i, j, hgrid=kernelSize))
                data[i].append(noise * 255)
            else:
                data[i].append(0)

    data = np.array(data).astype(np.uint8)
    return data

def shouldPixelGetNoise(y, x, i, currentBand):
    shouldGetNoise = True

    for bandKey in currentBand.bandDefinition.keys():
        if shouldGetNoise:
            pixelSol = currentBand.bandDefinition[bandKey][2](x, y)
            renderPos = currentBand.bandDefinition[bandKey][1]
            bandSol = currentBand.bandDefinition[bandKey][0]
            shouldGetNoise = shouldGetNoise and pixelSol <= bandSol[i] if renderPos == Position.UNDER else pixelSol >= bandSol[i]
        else:
            break

    return shouldGetNoise

def grayKernel(kernel, kernelWidth, kernelHeight):
    printStrength = random.randint(minPrintStrength, maxPrintStrength) / 100
    return kernel[0:kernelHeight, 0:kernelWidth] * printStrength

def printKernel(kernels, bg):
    newImage = bg
    bgWidth = int(bg.shape[1])
    bgHeight = int(bg.shape[0])
    kernelWidth = kernelSize
    kernelHeight = kernelSize
    kernelXPos = 0

    for i in range(kernels.__len__()):
        firstIteration = i == 0
        kernel = kernels[i]
        kernelYPos = topEdgeMargin
        kernelXPos = leftEdgeMargin if firstIteration else calcX(bgWidth, kernelWidth, kernelXPos)
        while kernelYPos < bgHeight:
            xOffset = random.randint(-xAxisMaxJitter, xAxisMaxJitter)
            xPos = kernelXPos + leftEdgeMargin + xOffset
            try:
                bgColInd = kernelHeight + kernelYPos
                bgRowInd = kernelWidth + xPos
                newImage[kernelYPos:bgColInd, xPos:bgRowInd] = grayKernel(kernel, kernelWidth, kernelHeight)
                kernelYPos = calcY(bgHeight, kernelHeight, kernelYPos)
            except Exception as e:
                break

    return newImage

def calcX(bgWidth, kernelWidth, kernelXPos):
    lastIteration = kernelWidth + laneOffset > bgWidth
    shouldUseRightOffset = lastIteration and (kernelXPos > bgWidth - rightEdgeMargin)

    if(shouldUseRightOffset):
        kernelXPos = bgWidth - rightEdgeMargin
    else:
        kernelXPos += kernelWidth + laneOffset

    return kernelXPos

def calcY(bgHeight, kernelHeight, kernelYPos):
    yOffset = random.randint(minPrintOffset, maxPrintOffset)
    lastIteration = kernelHeight + yOffset > bgHeight
    shouldUseBottomOffset = lastIteration and (kernelYPos > bgHeight - bottomEdgeMargin)

    if(shouldUseBottomOffset):
        kernelYPos = bgHeight - bottomEdgeMargin + yOffset
    else:
        kernelYPos += kernelHeight + topEdgeMargin

    return kernelYPos

def showImage(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def saltAndPepper(img):
    row , col, _ = img.shape
    number_of_pixels = random.randint(3000, 10000)

    for i in range(number_of_pixels):
        y_coord=random.randint(0, row - 1)
        x_coord=random.randint(0, col - 1)
        img[y_coord][x_coord] = 255

    number_of_pixels = random.randint(300 , 10000)

    for i in range(number_of_pixels):
        y_coord=random.randint(0, row - 1)
        x_coord=random.randint(0, col - 1)
        img[y_coord][x_coord] = 0

    return img

def dilate(image, kernelSize, elipseColor):
    halfSize = int(kernelSize/2)
    quarterSize = int(halfSize/4)
    elipse = cv2.ellipse(
        createImage(kernelSize, halfSize, elipseColor),
        (halfSize, quarterSize),
        (halfSize, quarterSize), 0, 0, 360,
        (255, 255, 255), 1, cv2.LINE_AA)
    cv2.getStructuringElement(elipse)
    return cv2.dilate(image, 10)

def createBandDefinitions():
    i = 0
    bands = []

    for defs in kernelFunctions:
        band = Band(defs)
        bands.append(band)
        i += 1

    return bands

def createKernels(bands):
    kernels = []

    for i in range(laneNumber):
        currentBand = bands[i]
        kernels.append(kernelNoise(kernelSize, num_octaves=random.randint(10, 50), persistence=random.randint(1, 100) / 100, currentBand=currentBand, dimensions=3))

    return np.array(kernels).astype(np.uint8)

def main():
    width = 1920
    height = 1080

    bg = createImage(width, height, color=0)
    bands = createBandDefinitions()
    kernels = createKernels(bands)
    printed = printKernel(kernels, bg)
    showImage(printed)

    for band in bands:
        band.plotFunction()

    for kernel in kernels:
        showImage(kernel)


if __name__ == "__main__":
    if laneNumber != len(kernelFunctions):
        print("You wanted " + laneNumber + " lanes, but defined " + len(kernelFunctions) + " band functions.")
        exit(1)
    else:
        main()


# {
#             "0": ["sin(x) * 6 - y", "ABOVE"],
#             "1": ["x^2 + 15*x + 5 + y*2", "ABOVE"]
#         }
