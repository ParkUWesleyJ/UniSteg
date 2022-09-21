#########################################################
# StegEval v0.5
# Wesley Jacobs
#
# A tool used to compare an original image and its
# stegimage counterpart to detect differences in
# distortion and pixel values.
#########################################################

import sys                            # used to exit on error/quit

try:
    from json.encoder import INFINITY # used for case where PSNR is undefined
except:
    print("Missing json.encode module")
    sys.exit()

try:
    import math                       # used for log10
except:
    print("Missing math module")
    sys.exit()

try:
    import numpy as np                # used to calculate averages and sums of Image pixels more efficiently
except:
    print("Missing NumPy module")
    sys.exit()

try:
    from PIL import Image             # used for image processing
except:
    print("Missing Pillow module")
    sys.exit()

try:
    import matplotlib.pyplot as plt   # used to visually represent histograms
except:
    print("Missing matplotlib module")
    sys.exit()

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

# Gets Pixel Value Difference Histogram
def showHist(imO, imS):
    # gets an array of individual pixel average values for original image
    avgPixelO = np.mean(np.array(imO, dtype=np.int16).reshape(np.array(imO).size // 3, 3), axis=1)
    # gets an array of individual pixel average values for stego image
    avgPixelS = np.mean(np.array(imS, dtype=np.int16).reshape(np.array(imS).size // 3, 3), axis=1)

    plt.hist(x=avgPixelO, bins=range(int(avgPixelO.min()), int(avgPixelO.max()) + 1), color="#000000", alpha=0.5, histtype="step", label="Original")
    plt.hist(x=avgPixelS, bins=range(int(avgPixelS.min()), int(avgPixelS.max()) + 1), color="#ff0000", alpha=0.5, histtype="step", label="Stego")

    # several values that can be used to see differences between images
    avgO = np.mean(avgPixelO)
    avgS = np.mean(avgPixelS)
    stdO = np.std(avgPixelO)
    stdS = np.std(avgPixelS)
    minmaxO = (np.max(avgPixelO), np.min(avgPixelO))
    minmaxS = (np.max(avgPixelS), np.min(avgPixelS))

    plt.xlabel("Pixel values")
    plt.ylabel("Occurences")
    plt.title("Pixel Value Histogram")
    plt.legend()

    plt.tight_layout()

    plt.show()

    return [avgO, avgS, stdO, stdS, minmaxO, minmaxS]

# DRIVER CODE
imagePathOriginal = input("Enter path of original image: ")
imagePathStego = input("Enter path of stego image: ")

try:
    with Image.open(imagePathOriginal) as imO:
        pxO = imO.load()
except:
    print("Original image doesn't exist")
    sys.exit()
try:
    with Image.open(imagePathStego) as imS:
        pxS = imS.load()
except:
    print("Stego image doesn't exist.")
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

histInfo = showHist(imO, imS)

print("\n--==HISTOGRAM INFORMATION==--")
print("{:<20} | {:<20}".format("Mean Original", histInfo[0]))
print("{:<20} | {:<20}".format("Mean Stego", histInfo[1]))
print("{:<20} | {:<20}".format("StdDev Original", histInfo[2]))
print("{:<20} | {:<20}".format("StdDev Stego", histInfo[3]))
print("{:<20} | {:<20}".format("MinMax Original", str(histInfo[4])))
print("{:<20} | {:<20}".format("MinMax Stego", str(histInfo[5])))
