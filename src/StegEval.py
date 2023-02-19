#########################################################
# StegEval.py v0.6
# Wesley Jacobs
#
# A tool used to compare an original image and its
# steg-image counterpart to detect differences in
# distortion and pixel values.
#########################################################

import sys                         # used to exit on error/quit
from json.encoder import INFINITY  # used for case where PSNR is undefined
import math                        # used for log10

try:
    import numpy as np               # used to calculate averages and sums of Image pixels more efficiently
    import matplotlib.pyplot as plt  # used to visually represent histograms
except:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit()


class StegEval:
    # Constructor that sets the images to evaluate
    def __init__(self, image1=None, image2=None):
        if image1 is None:
            self._image1 = None
        if image2 is None:
            self._image2 = None
        if image1 is not None and image2 is not None:
            self.set_images(image1, image2)

    # Sets the images to use for evaluation
    def set_images(self, image1, image2):
        try:
            image1.convert('RGB')
            image2.convert('RGB')
            size1 = image1.size
            size2 = image2.size
        except:
            raise TypeError("Images must be of Image type. It must also be able to be converted to RGB mode.")
        if size1 != size2:
            raise TypeError("Images must be the same size.")
        self._image1 = image1
        self._image2 = image2

    # Calculates Mean Square Error (MSE)
    def calc_mse(self):
        if self._image1 is None or self._image2 is None:
            raise TypeError("One or more images is of None type.")

        # Get the squared difference between all pixels then get the average
        mse = np.mean(np.square(np.subtract(self._image1, self._image2, dtype=np.int32)))

        return mse.round(10)

    # Calculates Peak Signal-to-Noise Ratio (PSNR)
    def calc_psnr(self):
        if self._image1 is None or self._image2 is None:
            raise TypeError("One or more images is of None type.")

        mse = self.calc_mse()

        if mse == 0:
            psnr = INFINITY
        else:
            psnr = 10 * math.log10((255 ** 2) / mse)

        return round(psnr, 10)

    # Calculates Quality Index (QI)
    def calc_qi(self):
        if self._image1 is None or self._image2 is None:
            raise TypeError("One or more images is of None type.")

        # Average pixel values
        avg1 = np.mean(self._image1)
        avg2 = np.mean(self._image2)

        # Standard deviation of pixel values
        std1 = np.sum(np.subtract(self._image1, avg1) ** 2) / (
                    3 * self._image1.size[0] * self._image1.size[1] - 1)
        std2 = np.sum(np.subtract(self._image2, avg2) ** 2) / (
                    3 * self._image2.size[0] * self._image2.size[1] - 1)

        # Covariance of both original and stego image pixel values
        covariance = np.sum(np.subtract(self._image1, avg1) * np.subtract(self._image2, avg2)) / (
                    3 * self._image1.size[0] * self._image1.size[1] - 1)

        if std1 == 0 and std2 == 0 or avg1 == 0 or avg2 == 0:
            qi = INFINITY
        else:
            qi = (4 * covariance * avg1 * avg2) / ((std1 + std2) * ((avg1 ** 2) + (avg2 ** 2)))

        return round(qi, 10)

    # Gets Pixel Value Difference Histogram
    def show_hist(self):
        if self._image1 is None or self._image2 is None:
            raise TypeError("One or more images is of None type.")

        # Gets an array of individual pixel average values
        avg_pix_array1 = np.mean(
            np.array(self._image1, dtype=np.int32).reshape(np.array(self._image1).size // 3, 3), axis=1)
        avg_pix_array2 = np.mean(
            np.array(self._image2, dtype=np.int32).reshape(np.array(self._image2).size // 3, 3), axis=1)

        # Create histograms
        y, x, _ = plt.hist(x=avg_pix_array1, bins=range(0, 256), color="#000000", alpha=0.5, histtype="step",
                           label="Original")
        plt.hist(x=avg_pix_array2, bins=range(0, 256), color="#ff0000", alpha=0.5, histtype="step", label="Stego")

        # Several values that can be used to see differences between images
        avg1 = np.mean(avg_pix_array1)
        avg2 = np.mean(avg_pix_array2)
        std1 = np.std(avg_pix_array1)
        std2 = np.std(avg_pix_array2)
        minmax1 = (np.max(avg_pix_array1), np.min(avg_pix_array1))
        minmax2 = (np.max(avg_pix_array2), np.min(avg_pix_array2))

        # Histogram formatting
        plt.ylim([0, y.max() + 1])
        plt.xlabel("Pixel values")
        plt.ylabel("Occurrences")
        plt.title("Pixel Value Histogram")
        plt.legend()
        plt.tight_layout()

        plt.show()

        return [avg1, avg2, std1, std2, minmax1, minmax2]
