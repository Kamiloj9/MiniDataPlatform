import os
import boto3
import pandas as pd

# === Configuration ===
S3_ENDPOINT = "http://localhost:9000"
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin123")
S3_BUCKET = os.getenv("MINIO_BUCKET", "datalake")
PARQUET_PREFIX = "output/mydatabase.public.orders/"

# === Setup S3 client ===
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

# === Discover Parquet files ===
response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=PARQUET_PREFIX)
parquet_files = [
    obj for obj in response.get("Contents", [])
    if obj["Key"].endswith(".parquet")
]

if not parquet_files:
    print("⚠️ No Parquet files found.")
    exit(0)

# === Sort files by LastModified (latest first) ===
parquet_files.sort(key=lambda x: x["LastModified"], reverse=True)

# === Read first non-empty file ===
os.environ["AWS_ACCESS_KEY_ID"] = S3_ACCESS_KEY
os.environ["AWS_SECRET_ACCESS_KEY"] = S3_SECRET_KEY
storage_options = {"client_kwargs": {"endpoint_url": S3_ENDPOINT}}

for obj in parquet_files:
    key = obj["Key"]
    s3_url = f"s3://{S3_BUCKET}/{key}"
    print(f"📂 Trying file: {key} ({obj['LastModified']})")

    try:
        df = pd.read_parquet(s3_url, storage_options=storage_options)
        if not df.empty:
            print("✅ DataFrame loaded:")
            print(df.head())
            break
        else:
            print("ℹ️ File is empty.")
    except Exception as e:
        print(f"❌ Error reading {key}: {e}")
else:
    print("⚠️ All Parquet files are empty or unreadable.")
