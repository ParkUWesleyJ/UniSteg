from UniSteg import UniSteg
from StegEval import StegEval

import os.path
import sys

try:
    from PIL import Image # used for image processing
except:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit()

def main():
    # Gets the algorithm type user wants to use
    algorithmType = input(
        "\n---------------------------------------\n" +
        "Enter one of the following values:\n" +
        "[E]valuate | [C]onceal/Extract | [Q]uit\n" +
        "---------------------------------------\n\n" +
        "> "
    )[0].lower()

    # Input validation for algorithm type
    while (algorithmType != "e" and algorithmType != "c" and algorithmType != "q"):
        algorithmType = input(
            "Invalid input.\n" +
            "\n---------------------------------------\n" +
            "Enter one of the following values:\n" +
            "[E]valuate | [C]onceal/Extract | [Q]uit\n" +
            "---------------------------------------\n\n" +
            "> "
        )[0].lower()
    
    # Handling and setting algorithm type
    if (algorithmType == "c"):
        algorithm = UniSteg()
    elif (algorithmType == "e"):
        algorithm = StegEval()
    else:
        print("Quitting...")
        return

    # Handles when user wants to conceal/decode
    if (type(algorithm) == UniSteg):
        image = inputImage()

        if (type(image) != type(None)):
            algorithm.setImage(image)
        else:
            return

        # Gets the type of processing to conduct on the image
        processingType = input(     
            "\n--------------------------------------\n" +       
            "Enter one of the following values:\n" +
            "[C]onceal | [E]xtract | [H]ome | [Q]uit\n" +
            "---------------------------------------\n\n" +
            "> "
        )[0].lower()

        # Input validation for processing method
        while (processingType != "c" and processingType != "e" and processingType != "h" and processingType != "q"):
            processingType = input(    
                "Invalid input.\n" + 
                "\n---------------------------------------\n" +       
                "Enter one of the following values:\n" +
                "[C]onceal | [E]xtract | [H]ome | [Q]uit\n" +
                "---------------------------------------\n\n" +
                "> "
            )[0].lower()

        # Handles processing type, quitting, and going back to home
        if (processingType == "c"):
            algorithm.conceal(image)
        if (processingType == "e"):
            algorithm.extract(image)
        if (processingType == "b"):
            main()
        if (processingType == "q"):
            return

    elif (type(algorithm) == StegEval):
        pass

def inputImage():
    # Gets the path of the image to process
    imagePath = input(
        "\n---------------------------------------------------------\n" +
        "Enter path of image or enter one of the following values:\n" +
        "[H]ome | [Q]uit\n" +
        "---------------------------------------------------------\n\n" +
        "> "
    )

    # Input validation for image path
    while (not os.path.isfile(imagePath) and imagePath.lower() != "q" and imagePath.lower() != "h"):
        imagePath = input(
            "Invalid input.\n" +
            "\n---------------------------------------------------------\n" +
            "Enter path of image or enter one of the following values:\n" +
            "[H]ome | [Q]uit\n" +
            "---------------------------------------------------------\n\n" +
            "> "
        )

    # Handles quitting and going back to home
    if (imagePath.lower() == "q"):
        print("Quitting...")
        return
    if (imagePath.lower() == "h"):
        main()

    # Attempts to open the image from the given path
    # Retries image path input on exception
    try:
        with Image.open(imagePath) as im:
            im.load()
        return im
    except:
        print("An error occurred. Was the file an image? (.png, .jpg)")
        inputImage()

if __name__ == "__main__":
    main()