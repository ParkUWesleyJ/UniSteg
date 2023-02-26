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

import cryptography.hazmat.primitives.asymmetric.rsa

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
    def __init__(self, image=None, private_key=None, public_key=None):
        """
        Initializes the algorithm. Takes in an image to process if provided

        :param image: Original Image object
        :type image: :class:`PIL.Image.Image`
        :param private_key: Private key
        :type public_key: :class:`cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey`
        :param public_key: Public key
        :type public_key: :class:`cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey`
        """
        if image is None:
            self.__image = image
        else:
            self.set_image(image)

        if private_key is None:
            self.__private_key = private_key
        elif public_key is None:
            self.__public_key = public_key
        else:
            self.set_keys(private_key, public_key)

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
        self.__image = image

    def set_keys(self, private, public):
        """
        Takes in an image to process. Verifies if it works with the algorithm

        :param private: Private key
        :type private: :class:`cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey`
        :param public: Public key
        :type public: :class:`cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey`
        :raises TypeError: When a key is not an RSA Key
        """
        if (
            not type(private) is not cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
            not type(public) is not cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey
        ):
            raise TypeError("Keys must RSA keys made with cryptography module")

        self.__private_key = private
        self.__public_key = public

    def conceal(self, message_to_conceal):
        """
        Conceals a secret message into an image using the receiver's public key for encryption and the sender's
        private key for signing

        :return: An image placed in project root directory
        :raises TypeError: When there is no image to conceal into or public/private keys not set
        """
        if self.__image is None:
            raise TypeError("Image not set.")
        if self.__public_key is None or self.__private_key is None:
            raise TypeError("One or more keys not set.")

        random_seed = secrets.randbelow(10 ** 21)
        random.seed(random_seed)

        secret_content = self.__public_key.encrypt(
            random_seed.to_bytes((random_seed.bit_length() + 7) // 8, "big"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        secret_content += message_to_conceal

        # Stores all secret data, including message and encrypted seed
        secret_binary = np.array([], dtype=int)

        # Converts secret message to binary format
        for byte in secret_content:
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
        im_stego = np.array(self.__image).flatten()

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
                while True:
                    random_index = math.floor(random.random() * len(im_stego))

                    if random_index not in used_indexes:
                        break

                im_stego[random_index] = UniSteg.fix_bit(im_stego[random_index], secret_binary[i])

                used_indexes.append(random_index)

        # Creates signature from the hash of secret message binary
        chosen_hash = hashes.SHA256()
        hasher = hashes.Hash(chosen_hash)
        hasher.update(message_to_conceal)
        digest = hasher.finalize()

        signature = self.__private_key.sign(
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
            while True:
                random_index = math.floor(random.random() * len(im_stego))

                if random_index not in used_indexes:
                    break

            im_stego[random_index] = UniSteg.fix_bit(im_stego[random_index], signature_binary[i])

            used_indexes.append(random_index)

        im_stego = im_stego.reshape(np.array(self.__image).shape)
        Image.fromarray(im_stego).save('other/stego.png')

    def extract(self):
        """
        Extracts a secret message from an image using the receiver's private key for decrypting and
        the sender's public key for verification

        :return: The string message hidden in the image
        :rtype: str
        :raises TypeError: When there is no image to extract from or public/private keys not set
        """
        if self.__image is None:
            raise TypeError("Image not set.")
        if self.__public_key is None or self.__private_key is None:
            raise TypeError("One or more keys not set.")

        binary_message = ""
        binary_encrypted_seed = ""
        im_flattened = np.array(self.__image).flatten()

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
            random_seed_bytes = self.__private_key.decrypt(
                bytes_encrypted_seed,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except:
            raise ValueError("Private key is not compatible with this image")

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

            used_indexes.append(random_index)

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
            self.__public_key.verify(
                signature_byte_array,
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                utils.Prehashed(chosen_hash)
            )
        except:
            raise ValueError(f"The message \"{message_decoded}\" was not sent from the intended sender")

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
