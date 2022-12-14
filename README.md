# UniSteg and StegEval
**This repo contains two separate programs.**

UniSteg: An program used to conceal and extract messages to and from images
StegEval: A program with several algorithms used to determine how well a message is hidden in a stegimage

## UniSteg v0.3
**A Steganographic program that hides and extracts Unicode from images.**

- Conceals UTF-8 encoded messages inside images through the manipulation of LSBs in pixel color values.
- Extracts UTF-8 encoded messages from images by getting the LSB of each pixel color value.

## StegEval v0.6
**A program that uses several analysis algorithms to determine how well a message is hidden inside an image. Does not yield results that show how resistant an image is to steganalysis attacks.**

- Calculates Mean Square Error (MSE), which is the averaged pixel-by-pixel squared difference between the original image and stegimage. (How similar the images are)
- Calculates Peak Signal-to-Noise Ratio (PSNR), which expresses the ratio between the maximum possible value of a signal and the power of distorting noise that affects the quality of its representation. (How much noise an image has)
- Calculates Quality Index (QI), which simply measures stegimage quality in comparison to the original.
- Creates a Pixel Value Histogram to give a visual representation of the distribution of pixel values. Along with this comes averages, standard deviations, minimums, and maximums of the histograms.
- *NOTE: Only supports images that can be converted into RGB mode. If you'd like to test it, see the TestImages file.*

> WARNING: Both of these versions are not stable nor secure. Do not use these programs in their current state if you expect them to yield good results. They are functional but they are not secure.
