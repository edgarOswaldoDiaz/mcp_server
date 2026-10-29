"""Prueba de permisos del almacenamiento S3 (RustFS o MinIO). Solo lectura de datos; intenta escribir con
las cuentas limitadas para comprobar que se NIEGA. Las contrasenas vienen del entorno, nunca se imprimen.

Uso (desde un contenedor con boto3 en la misma red que el almacenamiento):
  docker exec -i --env-file rustfs/.env <contenedor> python - < rustfs/probar_permisos.py
Variables: CONF_PASSWORD, LECTOR_PASSWORD, ENDPOINT (def. http://rustfs:9000), OBJETO (def. metadatos/ingresos_sinteticos.json)
"""
import os
import sys

import boto3
from botocore.exceptions import ClientError

ENDPOINT = os.environ.get("ENDPOINT", "http://rustfs:9000")
OBJETO = os.environ.get("OBJETO", "metadatos/ingresos_sinteticos.json")
CONF, PUB = "datos-confidenciales", "datos-publicos"


def cliente(usuario, clave):
    return boto3.client("s3", endpoint_url=ENDPOINT, aws_access_key_id=usuario,
                        aws_secret_access_key=clave, region_name="us-east-1")


def resultado(fn):
    """'OK' si la operacion se permite; si no, el codigo de error S3 (p. ej. AccessDenied)."""
    try:
        fn()
        return "OK"
    except ClientError as e:
        return e.response["Error"]["Code"]
    except Exception as e:  # red caida, endpoint equivocado...
        return f"ERROR_DE_CONEXION:{type(e).__name__}"


conf = cliente("lector-confidencial", os.environ["CONF_PASSWORD"])
pub = cliente("lector-publico", os.environ["LECTOR_PASSWORD"])
malo = cliente("lector-confidencial", "contrasena-incorrecta-123")

pruebas = [
    ("lector-confidencial LISTA datos-confidenciales", "OK", lambda: conf.list_objects_v2(Bucket=CONF)),
    ("lector-confidencial LISTA datos-publicos", "AccessDenied", lambda: conf.list_objects_v2(Bucket=PUB)),
    ("lector-confidencial ESCRIBE en datos-confidenciales", "AccessDenied",
     lambda: conf.put_object(Bucket=CONF, Key="prueba-escritura.txt", Body=b"x")),
    ("lector-confidencial ESCRIBE en datos-publicos", "AccessDenied",
     lambda: conf.put_object(Bucket=PUB, Key="prueba-escritura.txt", Body=b"x")),
    ("lector-publico LISTA datos-publicos", "OK", lambda: pub.list_objects_v2(Bucket=PUB)),
    ("lector-publico LISTA datos-confidenciales", "AccessDenied", lambda: pub.list_objects_v2(Bucket=CONF)),
    ("lector-publico ESCRIBE en datos-publicos", "AccessDenied",
     lambda: pub.put_object(Bucket=PUB, Key="prueba-escritura.txt", Body=b"x")),
    ("contrasena incorrecta se RECHAZA", "RECHAZADO", lambda: malo.list_objects_v2(Bucket=CONF)),
]

fallos = 0
for nombre, esperado, fn in pruebas:
    obtenido = resultado(fn)
    if esperado == "RECHAZADO":
        ok = obtenido not in ("OK",) and not obtenido.startswith("ERROR_DE_CONEXION")
    else:
        ok = obtenido == esperado
    fallos += 0 if ok else 1
    print(f"[{'PASA ' if ok else 'FALLA'}] {nombre}: esperado={esperado} obtenido={obtenido}")

# Lectura de un objeto confidencial (necesita datos cargados con la cuenta admin)
lectura = resultado(lambda: conf.get_object(Bucket=CONF, Key=OBJETO)["Body"].read())
if lectura == "OK":
    print(f"[PASA ] lector-confidencial LEE {OBJETO}")
elif lectura == "NoSuchKey":
    print(f"[AVISO] {OBJETO} no existe todavia: carga los datos de ejemplo para probar la lectura")
else:
    fallos += 1
    print(f"[FALLA] lector-confidencial LEE {OBJETO}: obtenido={lectura}")

print("RESULTADO:", "TODO CORRECTO" if fallos == 0 else f"{fallos} PRUEBA(S) FALLARON")
sys.exit(1 if fallos else 0)
