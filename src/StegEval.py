#########################################################
# StegEval v0.4
# Wesley Jacobs
#
# A program consisting of several algorithms used to
# guage distortion levels and security of images before
# and after image hiding.
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
    # reshapes original image array to subtract pairs of pixel avalues
    reshapedO = np.array(imO, dtype=np.int16).reshape(2, np.array(imO).size // 2)
    # array of difference between pairs of pixel values in original image
    pixelDiffO = np.subtract(reshapedO[0], reshapedO[1])
    # reshapes stego image array to subtract pairs of pixel avalues
    reshapedS = np.array(imS, dtype=np.int16).reshape(2, np.array(imS).size // 2)
    # array of difference between pairs of pixel values in stego image
    pixelDiffS = np.subtract(reshapedS[0], reshapedS[1])

    # average of pixel value difference in original image
    pixelDiffAvgO = np.mean(pixelDiffO)
    # standard deviation of pixel value difference in original image
    pixelDiffStdO = np.std(pixelDiffO)
    # average of pixel value difference in stego image
    pixelDiffAvgS = np.mean(pixelDiffS)
    # standard deviation of pixel value difference in stego image
    pixelDiffStdS = np.std(pixelDiffS)

    plt.hist(x=pixelDiffO, bins=range(pixelDiffO.min(), pixelDiffO.max() + 1), color="#000000", alpha=0.5, histtype="step", label="Original")
    plt.hist(x=pixelDiffS, bins=range(pixelDiffS.min(), pixelDiffS.max() + 1), color="#ff1100", alpha=0.5, histtype="step", label="Stego")

    plt.xlabel("Pixel Difference")
    plt.ylabel("Occurences")
    plt.title("Pixel Value Difference Histogram")
    plt.legend()

    plt.tight_layout()

    plt.show()

    return [pixelDiffAvgO, pixelDiffStdO, pixelDiffAvgS, pixelDiffStdS]

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

print("\n--==DISTORTION MEASUREMENTS==--")
print("{:<5} | {:<20} | Lower = Better".format("MSE", mse))
print("{:<5} | {:<20} | Higher = Better".format("PSNR", psnr))
print("{:<5} | {:<20} | Higher = Better".format("QI", qi))

histInfo = showHist(imO, imS)

print("\n--==PIXEL VALUE DIFFERENCE HISTOGRAM INFO==--")
print("{:<20} | {:<20}".format("Mean Original", histInfo[0]))
print("{:<20} | {:<20}".format("StdDev Original", histInfo[1]))
print("{:<20} | {:<20}".format("Mean Stego", histInfo[2]))
print("{:<20} | {:<20}".format("StdDev Stego", histInfo[3]))

print("\n--==RS ANALYSIS INFO==--")

# END
