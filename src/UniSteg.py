#########################################################
# UniSteg.py v0.4
# Wesley Jacobs
#
# Currently an exploratory program that conceals and
# extracts message to and from images.
#########################################################

import random
import secrets
import sys      # used to exit on error/quit
import math

try:
    from pathlib import Path
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding, utils
    from cryptography.hazmat.primitives import hashes
    from PIL import Image  # used for image processing
    import numpy as np     # used for more optimized arrays
except:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit()


class UniSteg:
    """
    Processes images by hiding or extracting messages from them
    """
    def __init__(self, image=None):
        """
        Initializes the algorithm. Takes in an image to process if provided

        :param image: Original Image object
        :type image: :class:`PIL.Image.Image`
        """
        if image is None:
            self._image = image
        else:
            self.set_image(image)

    def set_image(self, image):
        """
        Takes in an image to process. Verifies if it works with the algorithm

        :param image: Original Image object
        :type image: :class:`PIL.Image.Image`
        :raises TypeError: When the image is not an image
        """
        try:
            image.convert('RGB')
        except:
            raise TypeError("Image must be of Image type. It must also be able to be converted to RGB mode.")
        self._image = image

    def conceal(self):
        """
        Conceals a secret message into an image using the receiver's public key for encryption and the sender's
        private key for signing

        :return: An image placed in project root directory
        :raises TypeError: When there is no image to conceal into
        """
        if self._image is None:
            raise TypeError("Image is of None type.")

        uuid_input = input("Enter UUID of intended receiver: ")
        receiver_uuid = Path("encrypt_info/your_uuid")

        # Checks if UUID exists (currently only user's UUID)
        if receiver_uuid.open("r").read() != uuid_input:
            raise ValueError("UUID doesn't exist")

        # Gets public key tied to UUID for seed encryption
        with open("encrypt_info/public.pem", "rb") as public_key_file:
            public_key = serialization.load_pem_public_key(
                public_key_file.read()
            )

        # Gets private key tied to user running program for signing
        with open("encrypt_info/private.pem", "rb") as private_key_file:
            private_key = serialization.load_pem_private_key(
                private_key_file.read(),
                password=None
            )

        random_seed = secrets.randbelow(10 ** 21)
        random.seed(random_seed)

        secret_message = public_key.encrypt(
            random_seed.to_bytes((random_seed.bit_length() + 7) // 8, "big"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        message_input = bytes(input("Enter your secret message: "), "utf-8")
        secret_message += message_input

        # Stores all secret data, including message and encrypted seed
        secret_binary = np.array([], dtype=int)

        # Converts secret message to binary format
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

        # Throws error if message (plus signature) cannot fit in image
        if len(im_stego) < len(secret_binary + 2048):
            raise ValueError("Image has too few pixels to fit message.")

        used_indexes = []

        for i in range(len(secret_binary)):
            if i < 2048:
                cipher_index = round(len(im_stego) / 2048) * i
                im_stego[cipher_index] = UniSteg.fix_bit(im_stego[cipher_index], secret_binary[i])
                used_indexes.append(cipher_index)
            else:
                random_index = math.floor(random.random() * len(im_stego))

                while random_index in used_indexes:
                    random_index = math.floor(random.random() * len(im_stego))

                im_stego[random_index] = UniSteg.fix_bit(im_stego[random_index], secret_binary[i])

                used_indexes.append(random_index)

        # Creates signature from the hash of secret message binary
        chosen_hash = hashes.SHA256()
        hasher = hashes.Hash(chosen_hash)
        hasher.update(message_input)
        digest = hasher.finalize()
        signature = private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(chosen_hash)
        )

        signature_binary = np.array([], dtype=int)

        # Converts signature to binary
        for byte in signature:
            bits = bin(byte)[2:]

            # Adds leading zeros to ensure each byte is eight bits
            for bit in range(8 - len(bits)):
                signature_binary = np.append(signature_binary, 0)

            # Adds the byte in binary form to array of bits
            signature_binary = np.concatenate(
                (signature_binary, [int(bit) for bit in list(bits)])
            )

        # Hides signature into image using seed
        for i in range(len(signature_binary)):
            random_index = math.floor(random.random() * len(im_stego))

            while random_index in used_indexes:
                random_index = math.floor(random.random() * len(im_stego))

            im_stego[random_index] = UniSteg.fix_bit(im_stego[random_index], signature_binary[i])

            used_indexes.append(random_index)

        im_stego = im_stego.reshape(np.array(self._image).shape)
        Image.fromarray(im_stego).save('other/stego.png')

    def extract(self):
        """
        Extracts a secret message from an image using the receiver's private key for decrypting and
        the sender's public key for verification

        :return: The string message hidden in the image
        :rtype: str
        :raises TypeError: When there is no image to extract from
        """
        if self._image is None:
            raise TypeError("Image is of None type.")

        uuid_input = input("Enter UUID of sender: ")
        sender_uuid = Path("encrypt_info/your_uuid")

        # Checks if UUID exists (currently only user's UUID)
        if sender_uuid.open("r").read() != uuid_input:
            raise ValueError("UUID doesn't exist")

        # Gets public key tied to UUID for verification
        with open("encrypt_info/public.pem", "rb") as public_key_file:
            public_key = serialization.load_pem_public_key(
                public_key_file.read()
            )

        # Gets private key from user running program for decryption
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

        # Gets encrypted seed binary
        for i in range(2048):
            cipher_index = round(len(im_flattened) / 2048) * i
            binary_encrypted_seed += str(im_flattened[cipher_index] % 2)

            used_indexes.append(cipher_index)

        binary_encrypted_seed = int(binary_encrypted_seed, 2)
        bytes_encrypted_seed = binary_encrypted_seed.to_bytes((binary_encrypted_seed.bit_length() + 7) // 8, "big")

        try:
            random_seed_bytes = private_key.decrypt(
                bytes_encrypted_seed,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except:
            raise ValueError("Could not read information with given private key")

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
        message_byte_array = binary_message.to_bytes((binary_message.bit_length() + 7) // 8, "big")
        message_decoded = message_byte_array.decode("utf-8")

        signature_binary = ""

        # Gets signature binary
        for i in range(2048):
            random_index = math.floor(random.random() * len(im_flattened))

            while random_index in used_indexes:
                random_index = math.floor(random.random() * len(im_flattened))

            signature_binary += str(im_flattened[random_index] % 2)

            used_indexes.append(random_index)

        signature_binary = int(signature_binary, 2)
        signature_byte_array = signature_binary.to_bytes((signature_binary.bit_length() + 7) // 8, "big")

        chosen_hash = hashes.SHA256()
        hasher = hashes.Hash(chosen_hash)
        hasher.update(message_byte_array)
        digest = hasher.finalize()

        try:
            public_key.verify(
                signature_byte_array,
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                utils.Prehashed(chosen_hash)
            )
        except:
            raise ValueError(f"The message \"${message_decoded}\" was not sent from the intended sender")

        return message_decoded

    @staticmethod
    def fix_bit(to_fix, should_be):
        """
        Changes a byte's last bit to the bit it should be

        :param to_fix: The byte to fix
        :type to_fix: int
        :param should_be: The value the last bit should be
        :type should_be: int
        :return: The fixed version of the byte
        :rtype: int
        """
        if to_fix % 2 == should_be:
            return to_fix

        if to_fix - 1 > 0:
            to_fix -= 1
        else:
            to_fix += 1

        return to_fix
