import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SECRET_KEY")

if not url or not key:
    raise ValueError("Supabase credentials are missing in .env")

supabase = create_client(url, key)

def test_connection():
    buckets = supabase.storage.list_buckets()

    for bucket in buckets:
        print(bucket.name)

if __name__ == "__main__":
    test_connection()