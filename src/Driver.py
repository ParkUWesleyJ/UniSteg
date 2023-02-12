#########################################################
# Driver.py v0.1
# Wesley Jacobs
#
# Drives the UniSteg and StegEval algorithms to provide
# a pleasant user experience. Can be altered as the
# UniSteg and StegEval classes validate image inputs.
#########################################################

from UniSteg import UniSteg
from StegEval import StegEval
from stegencrypt import *
from enums import Colors

import os.path
from json.encoder import INFINITY  # used for case where PSNR is undefined
import sys

try:
    from PIL import Image  # used for image processing
except ModuleNotFoundError:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit()


# The main code to drive the two algorithms
def main():
    set_private_key()

    # Gets the algorithm type user wants to use
    algorithm_type = input(
        "\n---------------------------------------\n" +
        "Enter one of the following commands:\n" +
        " /evaluate\n /conceal_extract\n /quit\n" +
        "---------------------------------------\n\n" +
        "> "
    ).lower()

    # Input validation for algorithm type
    while algorithm_type != "/evaluate" and algorithm_type != "/conceal_extract" and algorithm_type != "/quit":
        algorithm_type = input(
            Colors.RED + "Invalid command.\n" + Colors.WHITE +
            "\n---------------------------------------\n" +
            "Enter one of the following commands:\n" +
            " /evaluate\n /conceal_extract\n /quit\n" +
            "---------------------------------------\n\n" +
            "> "
        ).lower()

    # Handling and setting algorithm type
    if algorithm_type == "/conceal_extract":
        algorithm = UniSteg()
    elif algorithm_type == "/evaluate":
        algorithm = StegEval()
    else:
        print("Quitting...")
        return

    # Handles when user wants to conceal/decode
    if isinstance(algorithm, UniSteg):
        # Gets one image from user input
        image = input_image(1, [])

        # Handles when user quits
        if image is None:
            return

        # Sets the image for the UniSteg object
        algorithm.set_image(image[0])

        # Gets the type of processing to conduct on the image
        processing_type = input(
            "\n--------------------------------------\n" +
            "Enter one of the following commands:\n" +
            " /conceal\n /extract\n /home\n /quit\n" +
            "---------------------------------------\n\n" +
            "> "
        ).lower()

        # Input validation for processing method
        while processing_type != "/conceal" and processing_type != "/extract" \
                and processing_type != "/home" and processing_type != "/quit":
            processing_type = input(
                Colors.RED + "Invalid command.\n" + Colors.WHITE +
                "\n---------------------------------------\n" +
                "Enter one of the following commands:\n" +
                " /conceal\n /extract\n /home\n /quit\n" +
                "---------------------------------------\n\n" +
                "> "
            ).lower()

        # Handles processing type, quitting, and going back to home
        if processing_type == "/conceal":
            if algorithm.conceal() == -1:
                main()
            print("Steg-image created.")
        elif processing_type == "/extract":
            print("Extracted message:", algorithm.extract())
        elif processing_type == "/home":
            print("Returning to home.\n")
            main()
        elif processing_type == "/quit":
            print("Quitting...")
            return
    # Handles when user wants to evaluate
    elif isinstance(algorithm, StegEval):
        # Gets two images from user input
        images = input_image(2, [])

        # Handles when user quits
        if images is None or images[0] is None or images[1] is None:
            return

        # Sets the images for the StegEval object
        algorithm.set_images(images)

        # Gets the method of evaluation to run on the images
        eval_type = input(
            "\n--------------------------------------\n" +
            "Enter one of the following commands:\n" +
            " /mse\n /psnr\n /qi\n /hist\n /all_evals\n /home\n /quit\n" +
            "---------------------------------------\n\n" +
            "> "
        ).lower()

        # Input validation for method of evaluation
        while eval_type != "/mse" and eval_type != "/psnr" and eval_type != "/qi" \
                and eval_type != "/hist" and eval_type != "/all_evals" and eval_type != "/home" \
                and eval_type != "/quit":
            eval_type = input(
                Colors.RED + "Invalid input.\n" + Colors.WHITE +
                "\n--------------------------------------\n" +
                "Enter one of the following commands:\n" +
                " /mse\n /psnr\n /qi\n /hist\n /all_evals\n /quit\n" +
                "---------------------------------------\n\n" +
                "> "
            ).lower()

        # Handles method of evaluation, quitting, and going back to home
        if eval_type == "/mse":
            print("{:<5} | {:<20} | Lower = Better".format("MSE", algorithm.calc_mse()))
        elif eval_type == "/psnr":
            print("{:<5} | {:<20} | Higher = Better".format("PSNR", algorithm.calc_psnr()))
        elif eval_type == "/qi":
            qi = algorithm.calc_qi()
            print("{:<5} | {:<20} | Higher = Better".format("QI", "INVALID (STDDEV=0)" if qi == INFINITY else qi))
        elif eval_type == "/hist":
            hist_info = algorithm.show_hist()
            print("{:<20} | {:<20}".format("Mean Original", hist_info[0]))
            print("{:<20} | {:<20}".format("Mean Stego", hist_info[1]))
            print("{:<20} | {:<20}".format("StdDev Original", hist_info[2]))
            print("{:<20} | {:<20}".format("StdDev Stego", hist_info[3]))
            print("{:<20} | {:<20}".format("MinMax Original", str(hist_info[4])))
            print("{:<20} | {:<20}".format("MinMax Stego", str(hist_info[5])))
        elif eval_type == "/all_evals":
            print("\n--==DISTORTION MEASUREMENTS==--")
            print("{:<5} | {:<20} | Lower = Better".format("MSE", algorithm.calc_mse()))
            print("{:<5} | {:<20} | Higher = Better".format("PSNR", algorithm.calc_psnr()))
            qi = algorithm.calc_qi()
            print("{:<5} | {:<20} | Higher = Better".format("QI", "INVALID (STDDEV=0)" if qi == INFINITY else qi))

            print("\n--==HISTOGRAM INFORMATION==--")
            hist_info = algorithm.show_hist()
            print("{:<20} | {:<20}".format("Mean Original", hist_info[0]))
            print("{:<20} | {:<20}".format("Mean Stego", hist_info[1]))
            print("{:<20} | {:<20}".format("StdDev Original", hist_info[2]))
            print("{:<20} | {:<20}".format("StdDev Stego", hist_info[3]))
            print("{:<20} | {:<20}".format("MinMax Original", str(hist_info[4])))
            print("{:<20} | {:<20}".format("MinMax Stego", str(hist_info[5])))
        elif eval_type == "/home":
            print("Returning to home.\n")
            main()
        elif eval_type == "/quit":
            print("Quitting...")
            return

    main()  # Brings user back to the beginning to do it again


# Gets user input of images. Number of images depends on algorithm being used
def input_image(num_images, image_array):
    # Since only two images can be used at max, throw an error if it tries to use more
    if num_images > 2:
        raise ValueError("Number of images cannot exceed two.")

    # Loops through each image that needs to be added
    for i in range(0, num_images):
        # Gets the path of the image to process
        image_path = input(
            "\n---------------------------------------------------------\n" +
            "Enter path of image or enter one of the following commands " +
            "(Image " + str(len(image_array) + 1) + "):\n" +
            " /home\n /quit\n" +
            "---------------------------------------------------------\n\n" +
            "> "
        )

        # Input validation for image path
        while not os.path.isfile(image_path) and image_path.lower() != "/quit" and image_path.lower() != "/home":
            image_path = input(
                Colors.RED + "Invalid command/path.\n" + Colors.WHITE +
                "\n---------------------------------------------------------\n" +
                "Enter path of image or enter one of the following commands " +
                "(Image " + str(len(image_array) + 1) + "):\n" +
                " /home\n /quit\n" +
                "---------------------------------------------------------\n\n" +
                "> "
            )

        # Handles quitting and going back to home
        if image_path.lower() == "/quit":
            print("Quitting...")
            return
        elif image_path.lower() == "/home":
            main()

        # Attempts to open the image from the given path
        # Retries image path input on exception
        try:
            if num_images > 1 or len(image_array) > 0:
                with Image.open(image_path).convert("RGB") as im:
                    im.load()
            else:
                with Image.open(image_path) as im:
                    im.load()

            if len(image_array) > 0 and (im.size[0] != image_array[0].size[0] or im.size[1] != image_array[0].size[1]):
                raise ValueError

            image_array.append(im)
            num_images -= 1
        except:
            print(Colors.RED + "An error occurred. Was the file a PNG/JPEG image?" +
                  "If inputting more than one image, were they the same size?" + Colors.WHITE)
            input_image(num_images, image_array)

    return image_array


if __name__ == "__main__":
    main()
