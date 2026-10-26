import json
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
doc = {"dataset": "ingresos_sinteticos", "formato": "parquet", "filas": 5, "sintetico": True}
s3.put_object(
    Bucket="datos-confidenciales",
    Key="metadatos/ingresos_sinteticos.json",
    Body=json.dumps(doc, ensure_ascii=False).encode("utf-8"),
    ContentType="application/json",
)
obj = s3.get_object(Bucket="datos-confidenciales", Key="metadatos/ingresos_sinteticos.json")
print(json.loads(obj["Body"].read().decode("utf-8")))
print("Contenido del bucket:")
for o in s3.list_objects_v2(Bucket="datos-confidenciales")["Contents"]:
    print(" -", o["Key"], o["Size"], "bytes")
