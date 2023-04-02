from enum import Enum
import requests
import sys
import os.path
from json.encoder import INFINITY  # used for case where PSNR is undefined

try:
    from UniSteg import UniSteg
    from StegEval import StegEval
    from UserKeys import *
    from PIL import Image  # used for image processing
    from cryptography.hazmat.primitives import serialization
except ModuleNotFoundError:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit(-1)


class Colors(str, Enum):
    """
    Stores color constants
    """
    RED = "\033[91m",
    WHITE = "\033[0m"


class Driver:
    """
    Driver.py | Wesley Jacobs

    Drives the two algorithms that come with this module
    """
    @staticmethod
    def main():
        """
        The main function for guiding a user through using UniSteg and StegEval
        """
        algorithm_type = Driver.get_algorithm_type()

        # Sets algorithm to proceed with (or quits)
        if algorithm_type.startswith('c'):
            algorithm = UniSteg()
        elif algorithm_type.startswith('e'):
            algorithm = StegEval()
        else:
            print("Quitting...")
            sys.exit(0)

        if isinstance(algorithm, UniSteg):
            Driver.handle_unisteg_algorithm(algorithm)

        if isinstance(algorithm, StegEval):
            Driver.handle_stegeval_algorithm(algorithm)

        Driver.main()

    ########################################################################

    @staticmethod
    def handle_unisteg_algorithm(algorithm):
        """
        Handles the process of setting up and running the UniSteg algorithm

        :param algorithm: UniSteg algorithm instance
        :type algorithm: :class:`UniSteg`
        """
        image = Driver.get_image('for concealing/extracting')
        algorithm.set_image(image)

        processing_type = Driver.get_processing_type()

        # Navigation handling
        if processing_type.startswith('h'):
            print("Returning to home.")
        if processing_type.startswith('q'):
            print("Quitting...")
            sys.exit(0)

        private_key = Driver.get_private_key()
        public_key = Driver.get_public_key(processing_type)

        if type(public_key) is str and public_key.startswith('h'):
            print("Returning to home.")
            Driver.main()
        if type(public_key) is str and public_key.startswith('q'):
            print("Quitting...")
            sys.exit(0)

        algorithm.set_keys(private_key, public_key)

        # Processing handling
        if processing_type.startswith('c'):
            message_to_conceal = bytes(input("Enter your secret message: "), "utf-8")
            algorithm.conceal(message_to_conceal)
            print("Steg-image created.")
        if processing_type.startswith('e'):
            try:
                extracted_message = algorithm.extract()
                print("Extracted message:", extracted_message)
            except ValueError as err:
                print(Colors.RED + str(err) + Colors.WHITE)

    ########################################################################

    @staticmethod
    def handle_stegeval_algorithm(algorithm):
        """
        Handles the process of setting up and running the StegEval algorithm

        :param algorithm: StegEval algorithm instance
        :type algorithm: :class:`StegEval`
        """
        original_image, steg_image = Driver.verify_image_sizes()
        algorithm.set_images(original_image, steg_image)

        eval_type = Driver.get_eval_type()

        # Evaluation handling
        if eval_type.startswith('m') or eval_type.startswith('a'):
            print("{:<5} | {:<20} | Lower = Better".format("MSE", algorithm.calc_mse()))
        if eval_type.startswith('p') or eval_type.startswith('a'):
            print("{:<5} | {:<20} | Higher = Better".format("PSNR", algorithm.calc_psnr()))
        if eval_type.startswith('qi') or eval_type.startswith('a'):
            qi = algorithm.calc_qi()
            print("{:<5} | {:<20} | Higher = Better".format(
                "QI", "INVALID (Avg/Stddev=0)" if qi == INFINITY else qi
            ))
        if eval_type.startswith('hi') or eval_type.startswith('a'):
            hist_info = algorithm.show_hist()
            print(("\n{:<20} | {:<20}" * 6).format(
                "Mean Original", hist_info[0],
                "Mean Stego", hist_info[1],
                "StdDev Original", hist_info[2],
                "StdDev Stego", hist_info[3],
                "MinMax Original", str(hist_info[4]),
                "MinMax Stego", str(hist_info[5])
            ))

        # Navigation handling
        if eval_type.startswith('h') and not eval_type.startswith('ho'):
            print("Returning to home.")
        if eval_type.startswith('q') and not eval_type.startswith('qi'):
            print("Quitting...")
            sys.exit(0)

    ########################################################################

    @staticmethod
    # Gets user input of images. Number of images depends on algorithm being used
    def get_image(image_context):
        """
        Gets and loads an image from an input path

        :param image_context: The context of the image that should be grabbed
        :type image_context: str
        :return: An Image object
        :rtype: :class:`PIL.Image.Image`
        """
        image_path = Driver.get_image_path(image_context)

        # Navigation handling
        if image_path.lower().startswith('q'):
            print("Quitting...")
            sys.exit(0)
        if image_path.lower().startswith('h'):
            print("Returning to home.")
            Driver.main()

        # Attempts to open the image from the given path
        # Retries image path input on exception
        try:
            with Image.open(image_path).convert("RGB") as im:
                im.load()
                return im
        except:
            print(
                Colors.RED + "Invalid file! Ensure the file is an image and can be converted into RGB mode." +
                Colors.WHITE
            )
            return Driver.get_image(image_context)

    ########################################################################

    @staticmethod
    def get_algorithm_type():
        """
        Gets the algorithm type through user input

        :return: A string containing the chosen algorithm
        :rtype: str
        """
        while True:
            algorithm_type = input(
                "\n---------------------------------------\n" +
                " What would you like to do?\n" +
                " [E]VALUATE\n [C]ONCEAL/EXTRACT\n [Q]UIT\n" +
                "---------------------------------------\n\n" +
                "> "
            ).lower()

            if algorithm_type.startswith('e') or algorithm_type.startswith('c') or algorithm_type.startswith('q'):
                return algorithm_type

            print(Colors.RED + "Invalid input.\n" + Colors.WHITE)

    ########################################################################

    @staticmethod
    def get_processing_type():
        """
        Gets the processing type for UniSteg through user input

        :return: A string containing the chosen processing
        :rtype: str
        """
        while True:
            processing_type = input(
                "\n--------------------------------------\n" +
                " What would you like to do?\n" +
                " [C]ONCEAL\n [E]XTRACT\n [H]OME\n [Q]UIT\n" +
                "---------------------------------------\n\n" +
                "> "
            ).lower()

            if (
                processing_type.startswith('c') or processing_type.startswith('e') or
                processing_type.startswith('h') or processing_type.startswith('q')
            ):
                return processing_type

            print(Colors.RED + "Invalid input.\n" + Colors.WHITE)

    ########################################################################

    @staticmethod
    def verify_image_sizes():
        """
        Takes in two images from input and verifies that they are the same size

        :return: A list of the two verified images
        :rtype: list[:class:`PIL.Image.Image`]
        """
        while True:
            original_image = Driver.get_image('as the original image')
            steg_image = Driver.get_image('as the steg-image')

            if original_image.size == steg_image.size:
                return [original_image, steg_image]

            print(Colors.RED + "Images not the same size. Please re-input the paths." + Colors.WHITE)

    ########################################################################

    @staticmethod
    def get_eval_type():
        """
        Gets the evaluation type through user input

        :return: A string containing the chosen evaluation method
        :rtype: str
        """
        while True:
            eval_type = input(
                "\n--------------------------------------\n" +
                " What would you like to evaluate?\n" +
                " [M]SE\n [P]SNR\n [QI]\n [HI]STOGRAM\n [A]LL\n [H]OME\n [Q]UIT\n" +
                "---------------------------------------\n\n" +
                "> "
            ).lower()

            if (
                eval_type.startswith('m') or eval_type.startswith('p') or
                eval_type.startswith('a') or eval_type.startswith('h') or
                eval_type.startswith('q')
            ):
                return eval_type

            print(Colors.RED + "Invalid input.\n" + Colors.WHITE)

    ########################################################################

    @staticmethod
    def get_image_path(image_context):
        """
        Gets the image path through user input

        :param image_context: The context of the image that should be found
        :type image_context: str
        :return: A string containing the path of the image
        :rtype: str
        """
        while True:
            image_path = input(
                "\n---------------------------------------------------------\n" +
                " Enter path of image to use " + image_context + "\n" +
                " [H]ome\n [Q]uit\n" +
                "---------------------------------------------------------\n\n" +
                "> "
            )

            if (
                os.path.isfile(image_path) or image_path.lower().startswith('q') or
                image_path.lower().startswith('h')
            ):
                return image_path

            print(Colors.RED + "Invalid path/command.\n" + Colors.WHITE)

    @staticmethod
    def get_private_key():
        """
        Gets the private key. If UUID/private key not found, reinitialize user information

        :return: RSA Private key
        :rtype: :class:`cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey`
        """
        Path("encrypt_info/").mkdir(parents=True, exist_ok=True)

        private_key_file = Path("encrypt_info/private.pem")
        uuid_file = Path("encrypt_info/uuid.UUID")

        if not private_key_file.is_file() or not uuid_file.is_file():
            keys = UserKeys()

            user_data = {
                "uuid": str(keys.get_uuid()),
                "public_key": keys.get_public_bytes()
            }

            response = requests.post("https://api-unisteg.glitch.me/users", user_data)

            if response.status_code != 200:
                print(Colors.RED + response.json()["response"] + Colors.WHITE)
                Driver.main()
            else:
                private_key_file.open("w").write(keys.get_private_bytes().decode("ascii"))
                uuid_file.open("w").write(str(keys.get_uuid()))
        else:
            response = requests.get("https://api-unisteg.glitch.me/user?uuid=" + uuid_file.open("r").read())

            if response.status_code != 200:
                print(Colors.RED + response.json()["response"] + Colors.WHITE)
                Driver.main()

            # Gets private key tied to user for signing and decryption
            with open(private_key_file, "rb") as key_file:
                return serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )

    @staticmethod
    def get_public_key(processing_type):
        """
        Gets the public key based on UUID input

        :param processing_type: How the image is going to be processed
        :type processing_type: str
        :return: RSA Public key
        :rtype: :class:`cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey` | str
        """
        while True:
            public_key_context = 'receiver'

            if processing_type.startswith("e"):
                public_key_context = 'sender'

            uuid_input = input(
                f"\n---------------------------------------------------------\n" +
                f" Enter UUID of {public_key_context}\n" +
                " [H]ome\n [Q]uit\n" +
                "---------------------------------------------------------\n\n" +
                "> "
            ).lower()

            response = requests.get("https://api-unisteg.glitch.me/user?uuid=" + uuid_input)

            if response.status_code != 200:
                print(Colors.RED + response.json()["response"] + Colors.WHITE)
            else:
                return serialization.load_pem_public_key(
                    bytes(response.json()["response"][uuid_input]["public_key"].encode("ascii"))
                )

            if uuid_input.startswith('h') or uuid_input.startswith('q'):
                return uuid_input


if __name__ == "__main__":
    Driver.main()
