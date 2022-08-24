from json.encoder import INFINITY # used for case where PSNR is undefined
import math                       # used for log10
from PIL import Image             # used for image processing
import sys                        # used to exit on error/quit

#########################################################

# Calculates Mean Square Error (MSE)
def calcMSE(imO, imS, pxO, pxS):
    totalRed = 0.0
    totalGreen = 0.0
    totalBlue = 0.0
    curLoop = 1
    lastPrinted = 0

    for col in range(0, imO.size[1]):
        for row in range(0, imO.size[0]):
            totalRed += (pxO[row, col][0] - pxS[row, col][0]) ** 2
            totalGreen += (pxO[row, col][1] - pxS[row, col][1]) ** 2
            totalGreen += (pxO[row, col][2] - pxS[row, col][2]) ** 2

            curLoop += 1
            curVal = round(curLoop / (imO.size[0]*imO.size[1]) * 100)
            if ((curVal * 10) != lastPrinted and (curVal * 10) % 10 == 0):
                lastPrinted = (curVal * 10)
                print("MSE | Progress: " + (str) (curVal) + "%", end='\r')
                
    
    mse = (totalRed+totalGreen+totalBlue) / (3*imO.size[1]*imO.size[0])

    print(end="\x1b[2K")
    print("MSE |", mse, "(Lower = Better)")

    return mse

#########################################################

# Calculates Peak Signal-to-Noise Ratio (PSNR)
def calcPSNR(mse):
    if (mse == 0):
        psnr = INFINITY
    else:
        psnr = 10 * math.log10((255 ** 2) / mse)

    print("PSNR |", psnr, "(Higher = Better)")
    return psnr

#########################################################

# DRIVER CODE
imagePathOriginal = input("Enter path of original image: ")
imagePathStego = input("Enter path of stego image: ")

mse = 0
psnr = 0

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

print("\n--==RESULTS==--")
mse = calcMSE(imO, imS, pxO, pxS)
psnr = calcPSNR(mse)

# END