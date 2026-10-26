import io
import os
import boto3
import geopandas as gpd
from shapely.geometry import Point
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id=os.environ["MINIO_ROOT_USER"],
    aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
    region_name="us-east-1",
    config=Config(s3={"addressing_style": "path"}),
)
datos = gpd.GeoDataFrame(
    {"folio": [1, 2, 3], "entidad": ["Aguascalientes", "Jalisco", "Zacatecas"]},
    geometry=[Point(-102.29, 21.88), Point(-103.35, 20.67), Point(-102.57, 22.77)],
    crs="EPSG:4326",
)
datos.to_parquet("puntos_sinteticos.parquet")
s3.upload_file("puntos_sinteticos.parquet", "datos-confidenciales", "geo/puntos_sinteticos.parquet")
obj = s3.get_object(Bucket="datos-confidenciales", Key="geo/puntos_sinteticos.parquet")
leido = gpd.read_parquet(io.BytesIO(obj["Body"].read()))
print(leido)
print("CRS:", leido.crs)
