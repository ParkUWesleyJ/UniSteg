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
import sys      # used to exit on error/quit
import math

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


def fix_bit(to_fix, should_be):
    if to_fix % 2 == should_be:
        return to_fix

    if to_fix - 1 > 0:
        to_fix -= 1
    else:
        to_fix += 1

    return to_fix


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
        else:
            with open("encrypt_info/" + uuid_input + "/public.pem", "rb") as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read()
                )

        random_seed = secrets.randbelow(10 ** 21)
        random.seed(random_seed)

        print(random_seed)

        secret_message = public_key.encrypt(
            random_seed.to_bytes((random_seed.bit_length() + 7) // 8, "big"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        secret_message += bytes(input("Enter your secret message: "), "utf-8")

        # stores all secret data, including message and encrypted seed
        secret_binary = np.array([], dtype=int)

        # Loops through each utf-8 byte in message
        for byte in secret_message:
            bits = bin(byte)[2:]

            # Adds leading zeros to ensure each byte is eight bits
            for bit in range(8-len(bits)):
                secret_binary = np.append(secret_binary, 0)

            # Adds the byte in binary form to array of bits
            secret_binary = np.concatenate(
                (secret_binary, [int(bit) for bit in list(bits)])
            )

        # Add null character to signify the ending
        secret_binary = np.append(secret_binary, [0] * 8)

        # A flattened for of the image for secret bits to be placed
        im_stego = np.array(self._image).flatten()

        # Throws error if message cannot fit in image
        if len(im_stego) < len(secret_binary):
            raise ValueError("Image has too few pixels to fit message.")

        used_indexes = []

        for i in range(len(secret_binary)):
            if i < 2048:
                cipher_index = round(len(im_stego) / 2048) * i
                im_stego[cipher_index] = fix_bit(im_stego[cipher_index], secret_binary[i])
                used_indexes.append(cipher_index)
            else:
                random_index = math.floor(random.random() * len(im_stego))

                while random_index in used_indexes:
                    random_index = math.floor(random.random() * len(im_stego))

                im_stego[random_index] = fix_bit(im_stego[random_index], secret_binary[i])

                used_indexes.append(random_index)

        im_stego = im_stego.reshape(np.array(self._image).shape)
        Image.fromarray(im_stego).save('other/stego.png')

    # Extracts secret message from image and outputs it to console
    def extract(self):
        if self._image is None:
            raise TypeError("Image is of None type.")

        with open("encrypt_info/private.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )

        binary_message = ""
        binary_encrypted_seed = ""
        im_flattened = np.array(self._image).flatten()

        # Stores how many zeros in a row to find null character
        num_zeros = 0

        used_indexes = []

        for i in range(2048):
            cipher_index = round(len(im_flattened) / 2048) * i
            binary_encrypted_seed += str(im_flattened[cipher_index] % 2)

            used_indexes.append(cipher_index)

        binary_encrypted_seed = int(binary_encrypted_seed, 2)
        bytes_encrypted_seed = binary_encrypted_seed.to_bytes((binary_encrypted_seed.bit_length() + 7) // 8, "big")

        random_seed_bytes = private_key.decrypt(
            bytes_encrypted_seed,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        random_seed = int.from_bytes(random_seed_bytes, "big")
        random.seed(random_seed)

        # Creates a string of the least significant bits in the image that correlate to a secret message
        while num_zeros < 8 or len(binary_message) % 8 != 0:
            random_index = math.floor(random.random() * len(im_flattened))

            while random_index in used_indexes:
                random_index = math.floor(random.random() * len(im_flattened))

            binary_message += str(im_flattened[random_index] % 2)

            if im_flattened[random_index] % 2 == 0:
                num_zeros += 1
            else:
                num_zeros = 0

        # Convert to decimal UTF-8 values
        binary_message = int(binary_message[:-8], 2)
        # Converts the formatted string into readable bytes
        byte_array = binary_message.to_bytes((binary_message.bit_length() + 7) // 8, "big")

        return byte_array.decode("utf-8")
