# UniSteg v0.1
A Steganographic program that hides and extracts Unicode from images.

Conceals ASCII messages inside images through the manipulation of LSBs in pixel color values.
Extracts ASCII messages from images by getting the LSB of each pixel color value.

WARNING: This version is not stable nor secure. Do not use this program in its current state to hide sensitive information as it will almost certainly be cracked if someone knows the image is a stegimage.
