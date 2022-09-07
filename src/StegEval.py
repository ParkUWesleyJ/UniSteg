#########################################################
# StegEval v0.3
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
np.set_printoptions(threshold=sys.maxsize)

#########################################################

# Calculates Mean Square Error (MSE)
def calcMSE(imO, imS):
    # get the squared difference between all pixels then get the average
    mse = np.mean(np.square(np.subtract(imO, imS)))

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
    # average pixel value in original image
    avgO = np.mean(imO)
    # average pixel value in stego-image
    avgS = np.mean(imS)
    # standard deviation of pixel values in original image
    stdDevO = np.sum(np.subtract(imS, avgS) ** 2) / (3*imO.size[0]*imO.size[1]-1)
    # standard deviation of pixel values in stego image
    stdDevS = np.sum(np.subtract(imO, avgO) ** 2) / (3*imO.size[0]*imO.size[1]-1)
    # covariance of both original and stego image pixel values
    covariance = np.sum(np.subtract(imO, avgO) * np.subtract(imS, avgS)) / (3*imO.size[0]*imO.size[1]-1)

    if (stdDevO == 0 and stdDevS == 0):
        qi = 1.0
    else:
        qi = (4 * covariance * avgO * avgS) / ((stdDevO + stdDevS) * ((avgO ** 2) + (avgS ** 2)))

    return round(qi, 10)

#########################################################

# Calculates Structural Similary Index Measure (SSIM)
# WARNING: Will likely yield poor results as it's better suited for grayscale images
def calcSSIM(imO, imS):
    # average pixel value in original image
    avgO = np.mean(imO)
    # average pixel value in stego-image
    avgS = np.mean(imS)
    # standard deviation of pixel values in original image
    stdDevO = np.sum(np.subtract(imS, avgS) ** 2) / (3*imO.size[0]*imO.size[1]-1)
    # standard deviation of pixel values in stego image
    stdDevS = np.sum(np.subtract(imO, avgO) ** 2) / (3*imO.size[0]*imO.size[1]-1)
    # covariance of both original and stego image pixel values
    covariance = np.sum(np.subtract(imO, avgO) * np.subtract(imS, avgS)) / (3*imO.size[0]*imO.size[1]-1)
    # first stablizier, takes a constant (.01 in this case) then multiplies it by 2^(bits per pixel), subtracts one, then squares it
    stabilizer1 = (.01 * (2 ** (8 * 3) - 1)) ** 2
    # first stablizier, takes a constant (.03 in this case) then multiplies it by 2^(bits per pixel), subtracts one, then squares it
    stabilizer2 = (.03 * (2 ** (8 * 3) - 1)) ** 2

    ssim = ((2 * avgO * avgS + stabilizer1) * (2 * covariance + stabilizer2)) / ((avgO ** 2 + avgS ** 2 + stabilizer1) * (stdDevO + stdDevS + stabilizer2))
    print(ssim)

    return round(ssim, 10)

#########################################################

# DRIVER CODE
imagePathOriginal = input("Enter path of original image: ")
imagePathStego = input("Enter path of stego image: ")

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
ssim = calcSSIM(imO, imS)


print("\n--==DISTORTION MEASUREMENTS==--")
print("{:<5} | {:<20} | Lower = Better".format("MSE", mse))
print("{:<5} | {:<20} | Higher = Better".format("PSNR", psnr))
print("{:<5} | {:<20} | Higher = Better".format("QI", qi))
print("{:<5} | {:<20} | Higher = Better".format("SSIM", ssim))

print("\n--==SECURITY MEASUREMENTS==--")

# END
