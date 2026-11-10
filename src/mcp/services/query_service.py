"""Consulta datasets Parquet del bucket confidencial mediante DuckDB."""

from __future__ import annotations

import io
import json
import logging
import os
import threading
import time
from typing import Any

import boto3
import duckdb
import pyarrow.parquet as pq
import sqlglot
from botocore.exceptions import ClientError
from botocore.config import Config
from sqlglot import exp
from src.mcp.services.object_key import InvalidObjectKey, validate_object_key

logger = logging.getLogger(__name__)


class QueryService:
    """Expone un catálogo acotado y consultas SQL de solo lectura."""

    def __init__(self) -> None:
        self.endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY")
        self.secret_key = os.getenv("MINIO_SECRET_KEY")
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "datos-confidenciales")
        if self.bucket_name != "datos-confidenciales":
            raise ValueError("MINIO_BUCKET_NAME debe ser datos-confidenciales.")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.max_file_bytes = int(os.getenv("QUERY_MAX_FILE_BYTES", str(256 * 1024 * 1024)))
        self.max_rows = int(os.getenv("QUERY_MAX_ROWS", "500"))
        self.timeout_seconds = float(os.getenv("QUERY_TIMEOUT_SECONDS", "10"))

    def _client(self):
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=Config(
                connect_timeout=5,
                read_timeout=10,
                retries={"max_attempts": 2, "mode": "standard"},
            ),
        )

    @staticmethod
    def _ok(data: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "data": data}

    @staticmethod
    def _error(code: str, message: str) -> dict[str, Any]:
        return {"ok": False, "error": {"code": code, "message": message}}

    def list_datasets(self) -> dict[str, Any]:
        """Lista objetos Parquet del bucket configurado, sin revelar credenciales."""
        try:
            paginator = self._client().get_paginator("list_objects_v2")
            datasets = []
            for page in paginator.paginate(Bucket=self.bucket_name):
                for item in page.get("Contents", []):
                    key = item["Key"]
                    if key.lower().endswith(".parquet"):
                        datasets.append({
                            "dataset_id": key,
                            "format": "parquet",
                            "size_bytes": item["Size"],
                        })
            return self._ok({"datasets": datasets, "count": len(datasets)})
        except Exception:
            logger.exception("No se pudo listar el bucket confidencial")
            return self._error("STORAGE_ERROR", "No se pudo listar el bucket de datos.")

    def _read_dataset(self, dataset_id: str) -> bytes:
        dataset_id = validate_object_key(dataset_id, (".parquet",))
        response = self._client().get_object(Bucket=self.bucket_name, Key=dataset_id)
        body = response["Body"]
        size = response.get("ContentLength", 0)
        try:
            if size > self.max_file_bytes:
                raise OverflowError("El dataset supera el tamaño máximo permitido.")
            payload = body.read(self.max_file_bytes + 1)
            if len(payload) > self.max_file_bytes:
                raise OverflowError("El dataset supera el tamaño máximo permitido.")
            return payload
        finally:
            body.close()

    def describe_dataset(self, dataset_id: str) -> dict[str, Any]:
        """Devuelve las columnas y tipos de un dataset Parquet permitido."""
        try:
            table = pq.read_schema(io.BytesIO(self._read_dataset(dataset_id)))
            return self._ok({
                "dataset_id": dataset_id,
                "columns": [{"name": field.name, "type": str(field.type)} for field in table],
            })
        except InvalidObjectKey as exc:
            return self._error("INVALID_OBJECT_KEY", str(exc))
        except ValueError as exc:
            return self._error("INVALID_DATASET", str(exc))
        except OverflowError as exc:
            return self._error("DATASET_TOO_LARGE", str(exc))
        except ClientError as exc:
            logger.warning("Error S3 al describir el dataset (%s)", exc.response.get("Error", {}).get("Code"))
            code = exc.response.get("Error", {}).get("Code")
            if code in {"NoSuchKey", "404", "NotFound"}:
                return self._error("DATASET_NOT_FOUND", "El dataset solicitado no existe.")
            if code in {"AccessDenied", "403"}:
                return self._error("ACCESS_DENIED", "No hay permiso para leer el dataset.")
            return self._error("STORAGE_ERROR", "No se pudo leer el dataset.")
        except Exception:
            logger.exception("No se pudo describir el dataset Parquet")
            return self._error("INVALID_PARQUET", "El objeto no contiene un Parquet válido.")

    @staticmethod
    def _validate_query(sql: str) -> str:
        """Acepta una consulta SELECT y limita las fuentes a la tabla registrada."""
        if not sql or len(sql) > 20_000:
            raise ValueError("La consulta está vacía o supera el tamaño permitido.")
        try:
            statements = sqlglot.parse(sql, read="duckdb")
        except sqlglot.errors.ParseError as exc:
            raise ValueError("La consulta SQL no es válida.") from exc
        if len(statements) != 1 or not isinstance(statements[0], exp.Select):
            raise ValueError("Solo se permite una sentencia SELECT.")
        if statements[0].args.get("with"):
            raise ValueError("No se permiten expresiones WITH.")
        for select in statements[0].find_all(exp.Select):
            if select.args.get("with"):
                raise ValueError("No se permiten expresiones WITH.")
            from_clause = select.args.get("from_")
            if from_clause and not (
                isinstance(from_clause.this, exp.Table)
                and from_clause.this.name.lower() == "dataset"
                and not from_clause.this.db
                and not from_clause.this.catalog
            ):
                raise ValueError("La consulta solo puede usar la tabla dataset.")
            for join in select.args.get("joins") or []:
                if not (
                    isinstance(join.this, exp.Table)
                    and join.this.name.lower() == "dataset"
                    and not join.this.db
                    and not join.this.catalog
                ):
                    raise ValueError("La consulta solo puede usar la tabla dataset.")
        for table in statements[0].find_all(exp.Table):
            if table.name.lower() != "dataset" or table.db or table.catalog:
                raise ValueError("La consulta solo puede usar la tabla dataset.")
        return statements[0].sql(dialect="duckdb")

    def query_dataset(self, dataset_id: str, sql: str) -> dict[str, Any]:
        """Ejecuta un SELECT sobre la tabla llamada dataset y limita sus resultados."""
        connection = None
        timer = None
        started = time.monotonic()
        try:
            sql = self._validate_query(sql)
            payload = self._read_dataset(dataset_id)
            arrow_table = pq.read_table(io.BytesIO(payload))
            connection = duckdb.connect(
                database=":memory:",
                config={
                    "enable_external_access": "false",
                    "autoinstall_known_extensions": "false",
                    "autoload_known_extensions": "false",
                },
            )
            connection.register("dataset", arrow_table)
            timer = threading.Timer(self.timeout_seconds, connection.interrupt)
            timer.daemon = True
            timer.start()
            cursor = connection.execute(sql)
            columns = [item[0] for item in cursor.description or []]
            rows = cursor.fetchmany(self.max_rows + 1)
            truncated = len(rows) > self.max_rows
            rows = rows[:self.max_rows]
            return self._ok({
                "dataset_id": dataset_id,
                "columns": columns,
                "rows": [
                    json.loads(json.dumps(dict(zip(columns, row)), default=str))
                    for row in rows
                ],
                "row_count": len(rows),
                "truncated": truncated,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
            })
        except InvalidObjectKey as exc:
            return self._error("INVALID_OBJECT_KEY", str(exc))
        except ValueError as exc:
            return self._error("INVALID_QUERY", str(exc))
        except OverflowError as exc:
            return self._error("DATASET_TOO_LARGE", str(exc))
        except ClientError as exc:
            logger.warning("Error S3 al consultar el dataset (%s)", exc.response.get("Error", {}).get("Code"))
            code = exc.response.get("Error", {}).get("Code")
            if code in {"NoSuchKey", "404", "NotFound"}:
                return self._error("DATASET_NOT_FOUND", "El dataset solicitado no existe.")
            if code in {"AccessDenied", "403"}:
                return self._error("ACCESS_DENIED", "No hay permiso para leer el dataset.")
            return self._error("STORAGE_ERROR", "No se pudo leer el dataset.")
        except Exception as exc:
            if "interrupt" in str(exc).lower():
                return self._error("QUERY_TIMEOUT", "La consulta superó el tiempo máximo permitido.")
            logger.exception("No se pudo ejecutar la consulta sobre el dataset")
            return self._error("QUERY_ERROR", "No se pudo ejecutar la consulta.")
        finally:
            if timer:
                timer.cancel()
            if connection:
                connection.close()
