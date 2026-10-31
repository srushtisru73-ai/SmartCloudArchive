
import hashlib
from pathlib import Path
from datetime import datetime
from supabase_client import supabase

BUCKET_NAME = "smartcloud-backups"


def calculate_hash(file_path):
    sha = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha.update(chunk)

    return sha.hexdigest()


def upload_backup(file_path):
    source = Path(file_path)

    if not source.is_file():
        raise FileNotFoundError("Selected file does not exist.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    object_name = f"{timestamp}_{source.name}"

    with open(source, "rb") as file:
        file_data = file.read()

    supabase.storage.from_(BUCKET_NAME).upload(
        path=object_name,
        file=file_data,
        file_options={"upsert": "false"}
    )

    return object_name


def list_backups():
    return supabase.storage.from_(BUCKET_NAME).list()


def restore_backup(object_name, destination_path):
    file_data = supabase.storage.from_(BUCKET_NAME).download(
        object_name
    )

    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(file_data)

    return str(destination)


if __name__ == "__main__":
    print("SmartCloud Archive cloud backup module is ready.")
