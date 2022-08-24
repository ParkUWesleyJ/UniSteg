from PIL import Image # used for image processing
import sys            # used to exit on error/quit

processingType = input("[C]onceal | [E]xtract | [Q]uit\n").lower()
while (processingType != "c" and processingType != "e" and processingType != "q"):
    processingType = input("[C]onceal | [E]xtract | [Q]uit\n").lower()

# ON QUIT
if (processingType == "q"):
    sys.exit()
# ON CONCEAL
elif (processingType == "c"):
    imagePath = input("Enter path of image: ")

    try:
        with Image.open(imagePath) as im:
            px = im.load()
    except:
        print("Image not found.")
        sys.exit()

    secretMessageString = input("Enter your secret message: ")

    secretMessageByteArray = bytearray(secretMessageString, "ascii")
    secretMessageBinary = ""

    for byte in secretMessageByteArray:
        # Adds leading zeros
        for bit in range(8-len(str(bin(byte)[2:]))):
            secretMessageBinary += "0"
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
# ON EXTRACT
elif (processingType == "e"):
    imagePath = input("Enter path of image: ")
    binaryMessage = ""
    curBit = 0

    try:
        with Image.open(imagePath) as im:
            px = im.load()
    except:
        print("Image not found.")
        sys.exit()

    # Creates a string of every least significant bit in every color of every pixel
    for col in range(0, im.size[1]):
        for row in range(0, im.size[0]):
            for color in range(0, 3):
                binaryMessage += str(px[row, col][color]%2)

    # Converts string into a format that python can decode
    binaryMessage = int(binaryMessage, 2)
    binaryArray = binaryMessage.to_bytes((binaryMessage.bit_length() + 7) // 8, "big")

    lastValidCharacter = 0

    # Gets the last character that can be represented using ASCII encoding
    for element in binaryArray:
        if (element < 128):
            lastValidCharacter += 1
        else:
            break

    print("Decoded message: \"" + binaryArray[0:lastValidCharacter].decode("ascii") + "\"")

# END
