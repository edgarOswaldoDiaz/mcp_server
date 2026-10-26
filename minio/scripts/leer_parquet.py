import io
import os
import boto3
import pandas as pd
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id=os.environ["MINIO_ROOT_USER"],
    aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
    region_name="us-east-1",
    config=Config(s3={"addressing_style": "path"}),
)
obj = s3.get_object(Bucket="datos-confidenciales", Key="ingresos/ingresos_sinteticos.parquet")
tabla = pd.read_parquet(io.BytesIO(obj["Body"].read()))
print(tabla)
