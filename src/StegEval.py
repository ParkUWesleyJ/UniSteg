#########################################################
# StegEval v0.2
# Wesley Jacobs
#
# A program consisting of several algorithms used to
# guage distortion levels and security of images before
# and after image hiding.
#########################################################

from json.encoder import INFINITY # used for case where PSNR is undefined
import math                       # used for log10
import numpy as np                # used to calculate averages and sums of Image pixels more efficiently
from PIL import Image             # used for image processing
import sys                        # used to exit on error/quit

#########################################################

# Calculates Mean Square Error (MSE)
def calcMSE(imO, imS):
    mse = np.square(np.subtract(imO, imS)).mean()

    return round(mse, 10)

#########################################################

# Calculates Peak Signal-to-Noise Ratio (PSNR)
def calcPSNR(mse):
    if (mse == 0):
        psnr = INFINITY
    else:
        psnr = 10 * math.log10((255 ** 2) / mse)

    return round(psnr, 10)

#########################################################

# Calculates Quality Index (QI)
def calcQI(imO, imS):
    avgO = np.mean(imO)
    avgS = np.mean(imS)
    stdDevO = np.sum(np.subtract(imS, avgS) ** 2) / (3*imO.size[0]*imO.size[1]-1)
    stdDevS = np.sum(np.subtract(imO, avgO) ** 2) / (3*imO.size[0]*imO.size[1]-1)
    covariance = np.sum(np.subtract(imO, avgO) * np.subtract(imS, avgS)) / (3*imO.size[0]*imO.size[1]-1)

    if (stdDevO == 0 and stdDevS == 0):
        qi = 1
    else:
        qi = (4 * covariance * avgO * avgS) / ((stdDevO + stdDevS) * ((avgO ** 2) + (avgS ** 2)))

    return round(qi, 10)

#########################################################

# DRIVER CODE
imagePathOriginal = input("Enter path of original image: ")
imagePathStego = input("Enter path of stego image: ")

mse = 0
psnr = 0
qi = 0

try:
    with Image.open(imagePathOriginal) as imO:
        pxO = imO.load()
    with Image.open(imagePathStego) as imS:
        pxS = imS.load()
except:
    print("One or more images not found.")
    sys.exit()

if (imO.size != imS.size):
    print("The two provided images are not the same size.")
    sys.exit()

mse = calcMSE(imO, imS)
psnr = calcPSNR(mse)
qi = calcQI(imO, imS)

print("\n--==DISTORTION MEASUREMENTS==--")
print("{:<5} | {:<20} | Lower = Better".format("MSE", mse))
print("{:<5} | {:<20} | Higher = Better".format("PSNR", psnr))
print("{:<5} | {:<20} | Higher = Better".format("QI", qi))

print("\n--==SECURITY MEASUREMENTS==--")

# END
