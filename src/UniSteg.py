#########################################################
# UniSteg.py v0.3.1
# Wesley Jacobs
#
# Currently an exploratory program that conceals and
# extracts message to and from images.
#########################################################

from enums import Colors

import random
import secrets
import sys                 # used to exit on error/quit

try:
    from pathlib import Path
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    from PIL import Image  # used for image processing
    import numpy as np     # used for more optimized arrays
except:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit()


class UniSteg:
    # Constructor that sets the image to conceal/extract if provided
    def __init__(self, image=None):
        if image is None:
            self._image = image
        else:
            self.set_image(image)

    # Sets the image to use for concealing/extracting if not set with constructor
    def set_image(self, image):
        try:
            fmt = image.format
        except:
            raise TypeError("Image must be of Image type.")
        if fmt != "JPEG" and fmt != "PNG":
            raise TypeError("Image must be a PNG or JPEG.")
        self._image = image

    # Conceals a secret message into an image and saves it in current directory
    def conceal(self):
        if self._image is None:
            raise TypeError("Image is of None type.")

        uuid_input = input("Enter UUID of intended receiver: ")

        sender_uuid = Path("encrypt_info/your_uuid")
        receiver_uuid = Path("encrypt_info/" + uuid_input + "/")

        # Checks if UUID in database or if current user's
        if sender_uuid.open("r").read() != uuid_input and not receiver_uuid.is_file():
            print(Colors.RED + "UUID not found!" + Colors.WHITE)
            return -1

        # Finds public key based on UUID input
        if sender_uuid.open("r").read() == uuid_input:
            with open("encrypt_info/public.pem", "rb") as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read()
                )
            with open("encrypt_info/private.pem", "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
        else:
            with open("encrypt_info/" + uuid_input + "/public.pem", "rb") as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read()
                )

        secret_message_string = input("Enter your secret message: ")

        # convert string into an array of UTF-8 values
        secret_message_byte_array = bytearray(secret_message_string, "utf-8")
        secret_message_binary = np.array([], dtype=int)  # used to store the secret message in binary format

        # loops through each ascii value
        for byte in secret_message_byte_array:
            # Adds leading zeros so each character is guaranteed to be 8 bits in length
            # [2:] gets rid of the '0b' before the binary value
            for bit in range(8-len(str(bin(byte)[2:]))):
                secret_message_binary = np.append(secret_message_binary, 0)
            # Adds the byte of data to the secret message binary string
            secret_message_binary = np.concatenate((secret_message_binary, [int(ch) for ch in list(bin(byte)[2:])]))

        # Add null character to signify the ending
        secret_message_binary = np.append(secret_message_binary, [0] * 8)

        # Stores the subtraction mask, which is what turns the original pixel's bits into secret message bits
        subtract_mask = np.array(self._image).flatten()[:len(secret_message_binary)]

        random_seed = secrets.randbelow(10 ** 21)
        random.seed(random_seed)

        print("\nSeed before encryption:", random_seed)

        encrypted_seed = public_key.encrypt(
            random_seed.to_bytes((random_seed.bit_length() + 7) // 8, "big"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        decrypted_seed = private_key.decrypt(
            encrypted_seed,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        print("Seed after encryption and decryption:", int.from_bytes(decrypted_seed, "big"), "\n")

        # Create subtraction mask based on the secret message
        for i in range(len(subtract_mask)):
            if subtract_mask[i] % 2 != secret_message_binary[i]:
                if subtract_mask[i]-1 > 0:
                    subtract_mask[i] = 1
                else:
                    subtract_mask[i] = -1
            else:
                subtract_mask[i] = 0

        # Create the new image from the subtraction mask
        im_flattened = np.array(self._image).flatten()
        im_stego = np.append(np.subtract(im_flattened[:len(secret_message_binary)], subtract_mask),
                             im_flattened[len(secret_message_binary):]).reshape(np.array(self._image).shape)

        Image.fromarray(im_stego).save('other/stego.png')

    # Extracts secret message from image and outputs it to console
    def extract(self):
        if self._image is None:
            raise TypeError("Image is of None type.")

        binary_message = ""
        im_flattened = np.array(self._image).flatten()

        # Stores how many zeros in a row to find null character
        num_zeros = 0

        # Creates a string of the least significant bits in the image that correlate to a secret message
        for i in range(len(im_flattened)):
            binary_message += str(im_flattened[i] % 2)

            if im_flattened[i] % 2 == 0:
                num_zeros += 1
            else:
                num_zeros = 0

            # If the end of a byte and found 8 or more zeros (accounting for 0s at the end of previous byte),
            # end the search
            if num_zeros >= 8 and (i + 1) % 8 == 0:
                break

        # Convert to decimal ASCII values
        binary_message = int(binary_message[:-8], 2)
        # Converts the formatted string into readable bytes
        byte_array = binary_message.to_bytes((binary_message.bit_length() + 7) // 8, "big")

        return byte_array.decode("utf-8")
