#########################################################
# UserKeys.py
# Wesley Jacobs
#
# Used to create addresses, private keys, public keys,
# and to encrypt information
#########################################################

import uuid  # used to get a unique ID for the user running program
import sys   # used to exit on error/quit

try:
    from pathlib import Path
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
except:
    print("Missing a module. Did you run 'pip install -r modules.txt'?")
    sys.exit()


class UserKeys:
    def __init__(self):
        """
        Declares private and public keys along with UUID,
        then calls an initializing function
        """
        self.__private_key = None
        self.__private_key_bytes = None
        self.__public_key_bytes = None
        self.__uuid = None
        self.new_keys()

    def new_keys(self):
        """
        Generates new keys and UUID

        :return: A modified UserKeys object with new keys and UUID
        """
        self.__new_private()
        self.__new_private_bytes()
        self.__new_public_bytes()
        self.__new_uuid()

    def __new_private(self):
        """
        Generates a new private key

        :return: Modified UserKeys object with new private key
        """
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

    def __new_private_bytes(self):
        """
        Generates private key bytes from private key

        :return: Modified UserKeys object with new private key bytes
        """
        self.__private_key_bytes = self.__private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        )

    def get_private_bytes(self):
        """
        :return: Private key bytes
        :rtype: bytearray
        """
        return self.__private_key_bytes

    def __new_public_bytes(self):
        """
        Generates public key bytes from private key

        :return: Modified UserKeys object with new public key bytes
        """
        self.__public_key_bytes = self.__private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def get_public_bytes(self):
        """
        :return: Public key bytes
        :rtype: bytearray
        """
        return self.__public_key_bytes

    def __new_uuid(self):
        """
        Generates a new UUID

        :return: Modified UserKeys object with new UUID
        """
        self.__uuid = uuid.uuid4()

    def get_uuid(self):
        """
        :return: UUID object
        :rtype: :class:`uuid.UUID`
        """
        return self.__uuid
