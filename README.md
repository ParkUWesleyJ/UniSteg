# UniSteg and StegEval
**This repo contains two separate programs.**

UniSteg: An program used to conceal and extract messages to and from images
StegEval: A program with several algorithms used to determine how well a message is hidden in a stegimage

## UniSteg v0.1
**A Steganographic program that hides and extracts Unicode from images.**

- Conceals ASCII messages inside images through the manipulation of LSBs in pixel color values.
- Extracts ASCII messages from images by getting the LSB of each pixel color value.

## StegEval v0.4
**A program that uses several analysis algorithms to determine how well a message is hidden inside an image.**

- Calculates Mean Square Error (MSE), which is the averaged pixel-by-pixel squared difference between the original image and stegimage. (How similar the images are)
- Calculates Peak Signal-to-Noise Ratio (PSNR), which expresses the ratio between the maximum possible value of a signal and the power of distorting noise that affects the quality of its representation. (How much noise an image has)
- Calculates Quality Index (QI), which simply measures stegimage quality in comparison to the original
- Creates a Pixel Value Difference Histogram to detect PVD steganography methods. Calculates the mean and standard deviation of both stegimage and original image histogram plots.

> WARNING: Both of these versions are not stable nor secure. Do not use these programs in their current state if you expect them to yield good results. They are functional but they are not secure.
