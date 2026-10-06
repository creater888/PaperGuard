import os
import uuid


UPLOAD_FOLDER = "uploads"
ENCRYPTED_FOLDER = "encrypted_papers"


def create_folders():

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("database", exist_ok=True)


def generate_filename(original_filename):

    extension = os.path.splitext(original_filename)[1]

    return str(uuid.uuid4()) + extension