from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def filler(file_path: str, passes: int = 3) -> None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    file_size = os.path.getsize(file_path)

    for pass_num in range(passes):

        random_data = os.urandom(file_size)

        with open(file_path, 'r+b') as f:
            f.write(random_data)
            f.flush()
            os.fsync(f.fileno())


def encrypt_file(file_path: str):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    key = os.urandom(32)  
    iv = os.urandom(12)   
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(file_path, 'rb') as f:
        plaintext = f.read()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    with open(file_path, 'wb') as f:
        f.write(ciphertext)


def erase_pipeline(file_path: str):
    filler(file_path, passes=10)
    encrypt_file(file_path)
    os.remove(file_path)