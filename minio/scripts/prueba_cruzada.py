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


def resultado(accion):
    try:
        accion()
        return "PERMITIDO"
    except ClientError as e:
        return "RECHAZADO (" + e.response["Error"]["Code"] + ")"


usuarios = {
    "lector-publico": cliente("lector-publico", os.environ["LECTOR_PASSWORD"]),
    "lector-confidencial": cliente("lector-confidencial", os.environ["CONF_PASSWORD"]),
}

for nombre, c in usuarios.items():
    print("==", nombre)
    print("  leer datos-publicos        :", resultado(lambda: c.get_object(Bucket="datos-publicos", Key="aviso.txt")))
    print("  leer datos-confidenciales  :", resultado(lambda: c.get_object(Bucket="datos-confidenciales", Key="ingresos/ingresos_sinteticos.parquet")))
    print("  escribir datos-confidenc.  :", resultado(lambda: c.put_object(Bucket="datos-confidenciales", Key="intruso.txt", Body=b"x")))
