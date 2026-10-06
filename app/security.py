import os
from cryptography.fernet import Fernet


KEY_FILE = "secret.key"


def get_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()

        with open(KEY_FILE, "wb") as f:
            f.write(key)

        return key

    with open(KEY_FILE, "rb") as f:
        return f.read()


fernet = Fernet(get_key())


def encrypt_file(input_path, output_path):
    with open(input_path, "rb") as f:
        data = f.read()

    encrypted_data = fernet.encrypt(data)

    with open(output_path, "wb") as f:
        f.write(encrypted_data)


def decrypt_file(file_path):
    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    return fernet.decrypt(encrypted_data)