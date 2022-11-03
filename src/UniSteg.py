#########################################################
# UniSteg v0.2
# Wesley Jacobs
#
# Currently an exploratory program that conceals and
# extracts message to and from images.
#########################################################

import sys            # used to exit on error/quit

try:
    from PIL import Image # used for image processing
    import numpy as np    # used for more optimized arrays
except:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit()

class UniSteg:

    def __init__(self, image=None):
        if (type(image) == type(None)):
            self._image = image
        else:
            try:
                fmt = image.format
            except:
                raise TypeError("Image must be of Image type.")
            if (fmt != "JPEG" and fmt != "PNG"):
                raise TypeError("Image must be be of PNG or JPEG file format.")
            self._image = image

    def setImage(self, image):
        try:
            fmt = image.format
        except:
            raise TypeError("Image must be of Image type.")
        if (fmt != "JPEG" and fmt != "PNG"):
            raise TypeError("Image must be be of PNG or JPEG file format.")
        self._image = image

    # Conceals a secret message into an image and saves it in current directory

    def conceal(self, im):
        secretMessageString = input("Enter your secret message: ")

        # convert string into an array of ASCII values
        secretMessageByteArray = bytearray(secretMessageString, "ascii")
        secretMessageBinary = np.array([], dtype=int) # used to store the secret message in binary format

        # loops through each ascii value
        for byte in secretMessageByteArray:
            # Adds leading zeros so each character is guaranteed to be 8 bits in length [2:] gets rid of the '0b' before the binary value
            for bit in range(8-len(str(bin(byte)[2:]))):
                secretMessageBinary = np.append(secretMessageBinary, 0)
            # Adds the byte of data to the secret message binary string
            secretMessageBinary = np.concatenate((secretMessageBinary, [int(ch) for ch in list(bin(byte)[2:])]))

        # Add null character to signify the ending
        secretMessageBinary = np.append(secretMessageBinary, [0,0,0,0,0,0,0,0])

        # Stores the subtraction mask, which is what turns the original pixel's bits into secret message bits
        subtractMask = np.array(im).flatten()[:len(secretMessageBinary)]

        # Create subtraction mask based on the secret message
        for i in range(len(subtractMask)):
            if (subtractMask[i] % 2 != secretMessageBinary[i]):
                if (subtractMask[i]-1 > 0):
                    subtractMask[i] = 1
                else:
                    subtractMask[i] = -1
            else:
                subtractMask[i] = 0

        # Create the new image from the subtraction mask
        imFlattened = np.array(im).flatten()
        imStego = np.append(np.subtract(imFlattened[:len(secretMessageBinary)], subtractMask), imFlattened[len(secretMessageBinary):]).reshape(np.array(im).shape)

        Image.fromarray(imStego).save('stego.png')
        print("Successfully created stegimage.")

    # Extracts secret message from image and outputs it to console

    def extract(self, im):
        binaryMessage = ""
        imFlattened = np.array(im).flatten()

        # Stores how many zeros in a row to find null character
        numZeros = 0

        # Creates a string of least significant bits in the image that correlate to a secret message
        for i in range(len(imFlattened)):
            binaryMessage += str(imFlattened[i] % 2)

            if (imFlattened[i] % 2 == 0):
                numZeros += 1
            else:
                numZeros = 0

            # If the end of a byte and found 8 or more zeros (accounting for 0s at the end of previous byte), end the search
            if numZeros >= 8 and (i + 1) % 8 == 0:
                break

        # Convert to decimal ASCII values
        binaryMessage = int(binaryMessage, 2)
        # Converts the formatted string into readable bytes
        byteArray = binaryMessage.to_bytes((binaryMessage.bit_length() + 7) // 8, "big")

        print("Decoded message: \"" + byteArray.decode("ascii") + "\"")