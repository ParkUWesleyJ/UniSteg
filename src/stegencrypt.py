#########################################################
# stegencrypt.py
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


def set_private_key():
    # creates encrypt_info directory if it doesn't exist
    Path("encrypt_info/").mkdir(parents=True, exist_ok=True)

    uuid_file = Path("encrypt_info/your_uuid")
    private_file = Path("encrypt_info/private.pem")
    public_file = Path("encrypt_info/public.pem")

    # returns if keys and uuid already made
    if uuid_file.is_file() and private_file.is_file() and public_file.is_file():
        return

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    )

    public_key = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # stores keys and UUID local files
    # FUTURE: Move public key and UUID to database
    uuid_file.open("w").write(str(uuid.uuid4()))
    private_file.open("w").write(private_key.decode("utf-8"))
    public_file.open("w").write(public_key.decode("utf-8"))
