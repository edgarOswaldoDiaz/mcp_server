import os
import io
import json
import boto3
from botocore.exceptions import ClientError
from src.mcp.services.object_key import validate_object_key

class MinIOService:
    """Servicio encargado de la lectura de objetos desde MinIO (S3) con permisos limitados."""

    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY")
        self.secret_key = os.getenv("MINIO_SECRET_KEY")
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "datos-confidenciales")
        if self.bucket_name != "datos-confidenciales":
            raise ValueError("MINIO_BUCKET_NAME debe ser datos-confidenciales.")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    def _get_client(self):
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    def read_json(self, object_key: str) -> dict:
        try:
            object_key = validate_object_key(object_key, (".json",))
            client = self._get_client()
            response = client.get_object(Bucket=self.bucket_name, Key=object_key)
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                raise PermissionError(f"Acceso denegado al objeto '{object_key}' en MinIO.")
            elif error_code == "NoSuchKey":
                raise FileNotFoundError(f"El archivo '{object_key}' no existe en el bucket.")
            raise RuntimeError(f"Error en MinIO S3: {str(e)}")

    def read_parquet(self, object_key: str) -> list[dict]:
        try:
            object_key = validate_object_key(object_key, (".parquet",))
            import pandas as pd

            client = self._get_client()
            response = client.get_object(Bucket=self.bucket_name, Key=object_key)
            buffer = io.BytesIO(response["Body"].read())
            df = pd.read_parquet(buffer)
            return json.loads(df.to_json(orient="records"))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                raise PermissionError(f"Acceso denegado al objeto '{object_key}' en MinIO.")
            elif error_code == "NoSuchKey":
                raise FileNotFoundError(f"El archivo '{object_key}' no existe en el bucket.")
            raise RuntimeError(f"Error en MinIO S3: {str(e)}")

    def read_geoparquet(self, object_key: str) -> dict:
        try:
            object_key = validate_object_key(object_key, (".parquet", ".geoparquet"))
            import geopandas as gpd

            client = self._get_client()
            response = client.get_object(Bucket=self.bucket_name, Key=object_key)
            buffer = io.BytesIO(response["Body"].read())
            gdf = gpd.read_parquet(buffer)
            return json.loads(gdf.to_json())
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                raise PermissionError(f"Acceso denegado al objeto '{object_key}' en MinIO.")
            elif error_code == "NoSuchKey":
                raise FileNotFoundError(f"El archivo '{object_key}' no existe en el bucket.")
            raise RuntimeError(f"Error en MinIO S3: {str(e)}")
