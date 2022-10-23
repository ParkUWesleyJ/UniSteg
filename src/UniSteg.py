#########################################################
# UniSteg v0.1.1
# Wesley Jacobs
#
# Currently an exploratory program that conceals and
# extracts message to and from images.
#########################################################

import sys            # used to exit on error/quit
import os.path        # used to check if file exists

try:
    from PIL import Image # used for image processing
except:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit()

#########################################################

# Conceals a secret message into an image and saves it in current directory

#########################################################

def conceal(im, px):
    secretMessageString = input("Enter your secret message: ")

    # convert string into an array of ASCII values
    secretMessageByteArray = bytearray(secretMessageString, "ascii")
    secretMessageBinary = "" # used to store the secret message in binary format

    # loops through each ascii value
    for byte in secretMessageByteArray:
        # Adds leading zeros so each character is guaranteed to be 8 bits in length [2:] gets rid of the '0b' before the binary value
        for bit in range(8-len(str(bin(byte)[2:]))):
            secretMessageBinary += "0"
        # Adds the byte of data to the secret message binary string
        secretMessageBinary += str(bin(byte)[2:])

    # Forces the greatest significant bit of the next byte to be a one, which makes anything after the secret message not show up when extracted
    secretMessageBinary += "1"

    messagePosition = 0

    # Loops through every pixel's color values and changes the LSB to match with the binary string
    #
    # Note: THE METHODOLOGY BEHIND THIS WILL CHANGE, IT WON'T BE AS SIMPLE AS GOING LEFT TO RIGHT.
    # THERE ARE ALSO NO CHECKS TO SEE IF THE MESSAGE FITS IN THE IMAGE, BUT THAT CAN EASILY BE ADDED IN THE FUTURE.
    for col in range(0, im.size[1]):
        for row in range(0, im.size[0]):
            r = px[row, col][0]
            g = px[row, col][1]
            b = px[row, col][2]
            
            count = 0
            
            # Goes through color value and makes it even if it's supposed to be a 0 and odd if it's supposed to be a 1
            while (count < 3 and messagePosition != len(secretMessageBinary)):
                if count == 0 and int(secretMessageBinary[messagePosition]) != r % 2:
                    if (r-1 > 0):
                        r -= 1
                    else:
                        r += 1
                elif count == 1 and int(secretMessageBinary[messagePosition]) != g % 2:
                    if (g-1 > 0):
                        g -= 1
                    else:
                        g += 1
                elif count == 2 and int(secretMessageBinary[messagePosition]) != b % 2:
                    if (b-1 > 0):
                        b -= 1
                    else:
                        b += 1

                count += 1
                messagePosition += 1

            px[row, col] = (r, g, b)

    im.save('stego.png')
    print("Successfully created stegimage.")

#########################################################

# Extracts secret message from image and outputs it to console

#########################################################

def extract(im, px):
    # Note: THIS CAN BE OPTIMIZED BY TERMINATING THE READ EARLY WHEN IT HITS THE TERMINATING SET OF BINARY VALUES

    binaryMessage = ""

    # Creates a string of every least significant bit in every color of every pixel
    for col in range(0, im.size[1]):
        for row in range(0, im.size[0]):
            for color in range(0, 3):
                binaryMessage += str(px[row, col][color]%2)

    # Converts string into a format that can be decoded
    binaryMessage = int(binaryMessage, 2)
    # Converts the formatted string into ASCII values (unicode values if it doesn't fit in ASCII range)
    binaryArray = binaryMessage.to_bytes((binaryMessage.bit_length() + 7) // 8, "big")

    lastValidCharacter = 0

    # Gets the last character that can be represented using ASCII encoding, which should be the end of the message
    for element in binaryArray:
        if (element < 128):
            lastValidCharacter += 1
        else:
            break

    print("Decoded message: \"" + binaryArray[0:lastValidCharacter].decode("ascii") + "\"")

#########################################################

# DRIVER CODE

#########################################################

def main():
    # Gets the type of processing to conduct on the image
    processingType = input("[C]onceal | [E]xtract | [Q]uit\n").lower()

    while (processingType != "c" and processingType != "e" and processingType != "q"):
        processingType = input("[C]onceal | [E]xtract | [Q]uit\n").lower()

    # Gets the path of the image to process
    imagePath = input("Enter path of image: ")

    while (not os.path.isfile(imagePath) and imagePath.lower() != "q"):
        imagePath = input("Invalid path. Enter path of image: ")

    # ON QUIT
    if (processingType == "q"):
        sys.exit()

    # Attempts to open the image from the given path and get the pixel data
    try:
        with Image.open(imagePath) as im:
            px = im.load()
    except:
        print("Image not found.")
        sys.exit()

    # Conceal
    if (processingType == "c"):
        conceal(im, px)
    # Extract
    elif (processingType == "e"):
        extract(im, px)

if __name__ == "__main__":
    sys.exit(main())