import os
import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id=os.environ["MINIO_ROOT_USER"],
    aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
    region_name="us-east-1",
    config=Config(s3={"addressing_style": "path"}),
)
bucket = "datos-confidenciales"
s3.create_bucket(Bucket=bucket)
s3.upload_file("ingresos_sinteticos.parquet", bucket, "ingresos/ingresos_sinteticos.parquet")
print("Subido. Objetos en el bucket:")
for o in s3.list_objects_v2(Bucket=bucket)["Contents"]:
    print(" -", o["Key"], o["Size"], "bytes")
