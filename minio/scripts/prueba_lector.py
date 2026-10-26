import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


def cliente(usuario, clave):
    return boto3.client(
        "s3",
        endpoint_url="http://127.0.0.1:9000",
        aws_access_key_id=usuario,
        aws_secret_access_key=clave,
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}),
    )


admin = cliente(os.environ["MINIO_ROOT_USER"], os.environ["MINIO_ROOT_PASSWORD"])
lector = cliente("lector-publico", os.environ["LECTOR_PASSWORD"])

admin.put_object(Bucket="datos-publicos", Key="aviso.txt", Body=b"dato publico de prueba")


def probar(descripcion, accion):
    try:
        accion()
        print("PERMITIDO :", descripcion)
    except ClientError as e:
        print("RECHAZADO :", descripcion, "->", e.response["Error"]["Code"])


probar("leer datos-publicos/aviso.txt", lambda: lector.get_object(Bucket="datos-publicos", Key="aviso.txt"))
probar("listar datos-publicos", lambda: lector.list_objects_v2(Bucket="datos-publicos"))
probar("leer datos-confidenciales/ingresos/...", lambda: lector.get_object(Bucket="datos-confidenciales", Key="ingresos/ingresos_sinteticos.parquet"))
probar("listar datos-confidenciales", lambda: lector.list_objects_v2(Bucket="datos-confidenciales"))
probar("escribir en datos-publicos", lambda: lector.put_object(Bucket="datos-publicos", Key="intruso.txt", Body=b"x"))
