import random
import secrets
import math

try:
    from pathlib import Path
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding, utils
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
    from cryptography.hazmat.primitives import hashes
    from PIL import Image  # used for image processing
    import numpy as np     # used for more optimized arrays
except:
    raise ModuleNotFoundError("Missing a module. Did you run 'pip install -r modules.txt'?")


class UniSteg:
    """
    UniSteg.py | Wesley Jacobs

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
            not type(private) is not RSAPrivateKey or not type(public) is not RSAPublicKey
        ):
            raise TypeError("Keys must RSA keys made with cryptography module")

        self.__private_key = private
        self.__public_key = public

    def conceal(self, message_bytes):
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

        secret_bytes = self.__get_encrypted_seed() + message_bytes
        secret_binary = UniSteg.__bytes_to_bits(secret_bytes, True)

        im_stego = np.array(self.__image).flatten()

        # Ensures message and signature (2048 bits) can fit in image
        if len(im_stego) < len(secret_binary) + 2048:
            raise ValueError("Image has too few pixels to fit message.")

        used_indexes = []

        # Hides encrypted seed in a pattern, then the message randomly according to the seed
        for i in range(len(secret_binary)):
            if i < 2048:
                cipher_index = round(len(im_stego) / 2048) * i
                im_stego[cipher_index] = UniSteg.__fix_bit(im_stego[cipher_index], secret_binary[i])
                used_indexes.append(cipher_index)
            else:
                UniSteg.__place_random_bit(im_stego, secret_binary, used_indexes, i)

        signature_bytes = self.__get_signature_bytes(message_bytes)
        signature_binary = UniSteg.__bytes_to_bits(signature_bytes)

        # Hides signature into image randomly using seed
        for i in range(len(signature_binary)):
            UniSteg.__place_random_bit(im_stego, signature_binary, used_indexes, i)

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

        message_binary_str = ""
        binary_encrypted_seed = ""
        im_flattened = np.array(self.__image).flatten()

        num_zeros = 0  # Used to find null character

        used_indexes = []

        # Gets encrypted seed binary string from image
        for i in range(2048):
            cipher_index = round(len(im_flattened) / 2048) * i
            binary_encrypted_seed += str(im_flattened[cipher_index] % 2)

            used_indexes.append(cipher_index)

        try:
            self.__decrypt_seed(binary_encrypted_seed)
        except:
            raise ValueError("Private key is not compatible with this image")

        # Creates a string of the least significant bits in the image that correlate to a secret message
        while num_zeros < 8 or len(message_binary_str) % 8 != 0:
            message_binary, num_zeros = UniSteg.__extract_random_bit(
                im_flattened,
                message_binary_str,
                used_indexes,
                num_zeros
            )

        message_binary = int(message_binary_str[:-8], 2)
        message_bytes = message_binary.to_bytes((message_binary.bit_length() + 7) // 8, "big")
        message_decoded = message_bytes.decode("utf-8")

        signature_binary = ""

        # Gets signature binary string from image
        for i in range(2048):
            signature_binary = UniSteg.__extract_random_bit(im_flattened, signature_binary, used_indexes)[0]

        signature_binary = int(signature_binary, 2)
        signature_bytes = signature_binary.to_bytes((signature_binary.bit_length() + 7) // 8, "big")

        try:
            self.__verify_signature(message_bytes, signature_bytes)
        except:
            raise ValueError(f"The message \"{message_decoded}\" was not sent from the intended sender")

        return message_decoded

    def __get_encrypted_seed(self):
        """
        Set the random seed and return the encrypted version of it using public key

        :return: Encrypted seed
        :rtype: bytearray
        """
        random_seed = secrets.randbelow(10 ** 21)
        random.seed(random_seed)

        return self.__public_key.encrypt(
            random_seed.to_bytes((random_seed.bit_length() + 7) // 8, "big"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def __decrypt_seed(self, binary_encrypted_seed):
        """
        Get the encrypted seed bits, decrypt them using private key, then set
        the random seed to that seed

        :param binary_encrypted_seed: The binary to decrypt
        :type binary_encrypted_seed: str
        :return:
        """
        binary_encrypted_seed = int(binary_encrypted_seed, 2)
        encrypted_seed = binary_encrypted_seed.to_bytes((binary_encrypted_seed.bit_length() + 7) // 8, "big")

        seed_bytes = self.__private_key.decrypt(
                encrypted_seed,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

        random_seed = int.from_bytes(seed_bytes, "big")
        random.seed(random_seed)

    def __get_signature_bytes(self, message_bytes):
        """
        Hashes the secret message and returns the signature in bytes

        :param message_bytes:
        :type message_bytes: bytes
        :return: Digital signature
        :rtype: bytes
        """
        hasher = hashes.Hash(hashes.SHA256())
        hasher.update(message_bytes)
        digest = hasher.finalize()

        return self.__private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256())
        )

    def __verify_signature(self, message_bytes, signature_bytes):
        """
        Verifies the signature using the hash of the secret message

        :param message_bytes:
        :type message_bytes: bytes
        :param signature_bytes:
        :type signature_bytes: bytes
        :raises InvalidSignature: When the signature doesn't match the intended sender's signature
        """
        hasher = hashes.Hash(hashes.SHA256())
        hasher.update(message_bytes)
        digest = hasher.finalize()

        self.__public_key.verify(
            signature_bytes,
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256())
        )

    @staticmethod
    def __fix_bit(to_fix, should_be):
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

    @staticmethod
    def __bytes_to_bits(bytes_to_convert, null_end=False):
        """
        Converts a bytearray to an array of bits

        :param bytes_to_convert: The bytearray to convert
        :type bytes_to_convert: bytes
        :param null_end: Whether the array should end with a null character
        :type null_end: bool
        :return:
        :rtype: list[int]
        """
        bit_array = np.array([], dtype=int)

        for byte in bytes_to_convert:
            bits = bin(byte)[2:]

            # Adds leading zeros to ensure each byte is eight bits
            for bit in range(8-len(bits)):
                bit_array = np.append(bit_array, 0)

            # Adds the byte in binary form to array of bits
            bit_array = np.concatenate(
                (bit_array, [int(bit) for bit in list(bits)])
            )

        if null_end:
            bit_array = np.append(bit_array, [0] * 8)

        return bit_array

    @staticmethod
    def __place_random_bit(im, bit_array, used_indexes, i):
        """
        Places a bit randomly in an image array using the seed

        :param im: ndarray of image
        :type im: :class:`numpy.core._multiarray_umath.ndarray`
        :param bit_array:
        :type bit_array: list[int]
        :param used_indexes:
        :type used_indexes: list[int]
        :param i:
        :type i: int
        :return: Modified image array with newly placed bit
        """
        while True:
            random_index = math.floor(random.random() * len(im))

            if random_index not in used_indexes:
                break

        used_indexes.append(random_index)
        im[random_index] = UniSteg.__fix_bit(im[random_index], bit_array[i])

    @staticmethod
    def __extract_random_bit(im, bits_string, used_indexes, num_zeros=-1):
        """
        Extracts a bit using random seed from image

        :param im: ndarray of image
        :type im: :class:`numpy.core._multiarray_umath.ndarray`
        :param bits_string:
        :type bits_string: str
        :param used_indexes:
        :type used_indexes: list[int]
        :param num_zeros:
        :type num_zeros: int
        :return:
        """
        random_index = math.floor(random.random() * len(im))

        while random_index in used_indexes:
            random_index = math.floor(random.random() * len(im))

        used_indexes.append(random_index)

        if num_zeros >= 0:
            if im[random_index] % 2 == 0:
                num_zeros += 1
            else:
                num_zeros = 0

        bits_string = str(bits_string) + str(im[random_index] % 2)

        return bits_string, num_zeros
