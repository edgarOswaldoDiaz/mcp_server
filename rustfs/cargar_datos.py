"""Carga los 3 datos SINTETICOS de ejemplo en el bucket confidencial (con la cuenta admin) y los vuelve a leer.

Mismos objetos que en minio/ (asi el MCP y el agente funcionan igual con cualquiera de los dos):
  metadatos/ingresos_sinteticos.json, ingresos/ingresos_sinteticos.parquet, geo/puntos_sinteticos.parquet

Uso (contenedor con boto3, pandas y geopandas, en la misma red que el almacenamiento):
  docker exec -i --env-file rustfs/.env mcp-server python - < rustfs/cargar_datos.py
Variables: RUSTFS_ROOT_USER, RUSTFS_ROOT_PASSWORD, ENDPOINT (def. http://rustfs:9000)
"""
import io
import json
import os

import boto3
import geopandas as gpd
import pandas as pd
from botocore.config import Config
from shapely.geometry import Point

BUCKET = "datos-confidenciales"
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("ENDPOINT", "http://rustfs:9000"),
    aws_access_key_id=os.environ["RUSTFS_ROOT_USER"],
    aws_secret_access_key=os.environ["RUSTFS_ROOT_PASSWORD"],
    region_name="us-east-1",
    config=Config(s3={"addressing_style": "path"}),
)

ingresos = pd.DataFrame({
    "folio": [1, 2, 3, 4, 5],
    "entidad": ["Aguascalientes", "Jalisco", "Zacatecas", "Jalisco", "Aguascalientes"],
    "ingreso_mensual": [8500, 12000, 7300, 15400, 9100],
})
puntos = gpd.GeoDataFrame(
    {"folio": [1, 2, 3], "entidad": ["Aguascalientes", "Jalisco", "Zacatecas"]},
    geometry=[Point(-102.29, 21.88), Point(-103.35, 20.67), Point(-102.57, 22.77)],
    crs="EPSG:4326",
)
meta = {"dataset": "ingresos_sinteticos", "formato": "parquet", "filas": 5, "sintetico": True}

buf1, buf2 = io.BytesIO(), io.BytesIO()
ingresos.to_parquet(buf1, index=False)
puntos.to_parquet(buf2)

s3.put_object(Bucket=BUCKET, Key="metadatos/ingresos_sinteticos.json",
              Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"), ContentType="application/json")
s3.put_object(Bucket=BUCKET, Key="ingresos/ingresos_sinteticos.parquet", Body=buf1.getvalue())
s3.put_object(Bucket=BUCKET, Key="geo/puntos_sinteticos.parquet", Body=buf2.getvalue())

print("Objetos en", BUCKET)
for o in s3.list_objects_v2(Bucket=BUCKET)["Contents"]:
    print(" -", o["Key"], o["Size"], "bytes")
leido = s3.get_object(Bucket=BUCKET, Key="metadatos/ingresos_sinteticos.json")["Body"].read()
print("Relectura del JSON:", json.loads(leido))
