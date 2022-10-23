#########################################################
# StegEval v0.6
# Wesley Jacobs
#
# A tool used to compare an original image and its
# stegimage counterpart to detect differences in
# distortion and pixel values.
#########################################################

import sys                        # used to exit on error/quit
from json.encoder import INFINITY # used for case where PSNR is undefined
import math                       # used for log10
import os.path                    # used to check if file exists

try:
    import numpy as np                # used to calculate averages and sums of Image pixels more efficiently
    from PIL import Image             # used for image processing
    import matplotlib.pyplot as plt   # used to visually represent histograms
except:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit()

#########################################################

# Calculates Mean Square Error (MSE)

#########################################################

def calc_mse(img_original, img_stego):
    # Get the squared difference between all pixels then get the average
    mse = np.mean(np.square(np.subtract(img_original, img_stego, dtype=np.int32)))

    return round(mse, 10)

#########################################################

# Calculates Peak Signal-to-Noise Ratio (PSNR)

#########################################################

def calc_psnr(mse):
    if (mse == 0):
        psnr = INFINITY
    else:
        psnr = 10 * math.log10((255 ** 2) / mse)

    return round(psnr, 10)

#########################################################

# Calculates Quality Index (QI)

#########################################################

def calc_qi(img_original, img_stego):
    # Average pixel values
    avg_original = np.mean(img_original)
    avg_stego = np.mean(img_stego)

    # Standard deviation of pixel values
    std_original = np.sum(np.subtract(img_original, avg_original) ** 2) / (3*img_original.size[0]*img_original.size[1]-1)
    std_stego = np.sum(np.subtract(img_stego, avg_stego) ** 2) / (3*img_stego.size[0]*img_stego.size[1]-1)

    # Covariance of both original and stego image pixel values
    covariance = np.sum(np.subtract(img_original, avg_original) * np.subtract(img_stego, avg_stego)) / (3*img_original.size[0]*img_original.size[1]-1)

    if (std_original == 0 and std_stego == 0):
        qi = INFINITY
    else:
        qi = (4 * covariance * avg_original * avg_stego) / ((std_original + std_stego) * ((avg_original ** 2) + (avg_stego ** 2)))

    return round(qi, 10)

#########################################################

# Gets Pixel Value Difference Histogram

#########################################################

def show_hist(img_original, img_stego):
    # Gets an array of individual pixel average values
    avg_pix_array_original = np.mean(np.array(img_original, dtype=np.int32).reshape(np.array(img_original).size // 3, 3), axis=1)
    avg_pix_array_stego = np.mean(np.array(img_stego, dtype=np.int32).reshape(np.array(img_stego).size // 3, 3), axis=1)

    # Create histograms
    y, x, _ = plt.hist(x=avg_pix_array_original, bins=range(0, 256), color="#000000", alpha=0.5, histtype="step", label="Original")
    plt.hist(x=avg_pix_array_stego, bins=range(0, 256), color="#ff0000", alpha=0.5, histtype="step", label="Stego")

    # Several values that can be used to see differences between images
    avg_original = np.mean(avg_pix_array_original)
    avg_stego = np.mean(avg_pix_array_stego)
    std_original = np.std(avg_pix_array_original)
    std_stego = np.std(avg_pix_array_stego)
    minmax_original = (np.max(avg_pix_array_original), np.min(avg_pix_array_original))
    minmax_stego = (np.max(avg_pix_array_stego), np.min(avg_pix_array_stego))

    # Histogram formatting
    plt.ylim([0, y.max()+1])
    plt.xlabel("Pixel values")
    plt.ylabel("Occurences")
    plt.title("Pixel Value Histogram")
    plt.legend()
    plt.tight_layout()

    plt.show()

    return [avg_original, avg_stego, std_original, std_stego, minmax_original, minmax_stego]

#########################################################

# DRIVER CODE

#########################################################

def main ():
    # Gets original image
    original_path = input("Enter path of original image (Q to quit): ")

    while (not os.path.isfile(original_path) and original_path.lower() != "q"):
        original_path = input("Invalid path. Enter path of original image (Q to quit): ")

    if (original_path.lower() == "q"):
        sys.exit()

    # Tries to open image into RGB mode
    try:
        with Image.open(original_path).convert("RGB") as img_original:
            pixels_original = img_original.load()
            print("Image dimensions: " + str(img_original.size[0]) + "x" + str(img_original.size[1]))
    except:
        print("Unable to get image into correct format. (Only works with RGB images)")
        sys.exit()

    # Gets stego image
    stego_path = input("Enter path of stego image (Q to quit): ")

    while (not os.path.isfile(stego_path) and stego_path.lower() != "q"):
        stego_path = input("Invalid path. Enter path of stego image (Q to quit): ")

    if (stego_path.lower() == "q"):
        sys.exit()

    # Tries to open image into RGB mode
    try:
        with Image.open(stego_path).convert("RGB") as img_stego:
            img_stego.load()
            print("Image dimensions: " + str(img_stego.size[0]) + "x" + str(img_stego.size[1]))
    except:
        print("Unable to get image into correct format. (Only works with RGB images)")
        sys.exit()

    # Stops program if the images aren't the same size
    if (img_original.size != img_stego.size):
        print("The two provided images are not the same size!")
        sys.exit()

    # Calculates MSE, PSNR, and QI
    mse = calc_mse(img_original, img_stego)
    psnr = calc_psnr(mse)
    qi = calc_qi(img_original, img_stego)

    print("\n--==DISTORTION MEASUREMENTS==--")
    print("{:<5} | {:<20} | Lower = Better".format("MSE", mse))
    print("{:<5} | {:<20} | Higher = Better".format("PSNR", psnr))
    print("{:<5} | {:<20} | Higher = Better".format("QI", "INVALID (STDDEV=0)" if qi == INFINITY else qi))

    # Shows histogram and gets statistics of each image
    hist_info = show_hist(img_original, img_stego)

    print("\n--==HISTOGRAM INFORMATION==--")
    print("{:<20} | {:<20}".format("Mean Original", hist_info[0]))
    print("{:<20} | {:<20}".format("Mean Stego", hist_info[1]))
    print("{:<20} | {:<20}".format("StdDev Original", hist_info[2]))
    print("{:<20} | {:<20}".format("StdDev Stego", hist_info[3]))
    print("{:<20} | {:<20}".format("MinMax Original", str(hist_info[4])))
    print("{:<20} | {:<20}".format("MinMax Stego", str(hist_info[5])))

if __name__ == "__main__":
    sys.exit(main())