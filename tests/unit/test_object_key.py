import pytest

from src.mcp.services.object_key import InvalidObjectKey, validate_object_key
from src.mcp.services.minio_service import MinIOService


@pytest.mark.parametrize(
    "object_key,suffixes",
    [
        ("metadatos/ingresos.json", (".json",)),
        ("datos/área/ingresos.PARQUET", (".parquet",)),
        ("geo/.hidden.geoparquet", (".geoparquet",)),
        ("folder//valid.parquet", (".parquet",)),
        ("folder/%2e%2e/report.json", (".json",)),
    ],
)
def test_validate_object_key_accepts_s3_keys_without_rewriting(object_key, suffixes):
    assert validate_object_key(object_key, suffixes) == object_key


@pytest.mark.parametrize(
    "object_key,suffixes",
    [
        ("", (".json",)),
        ("/metadatos/datos.json", (".json",)),
        ("folder/../datos.json", (".json",)),
        ("folder/./datos.json", (".json",)),
        ("folder\\datos.json", (".json",)),
        ("folder/da\x00tos.json", (".json",)),
        ("datos.parquet", (".json",)),
        ("á" * 1021 + ".json", (".json",)),
    ],
)
def test_validate_object_key_rejects_invalid_keys(object_key, suffixes):
    with pytest.raises(InvalidObjectKey):
        validate_object_key(object_key, suffixes)


@pytest.mark.parametrize(
    "method,object_key",
    [
        ("read_json", "../datos.json"),
        ("read_parquet", "../datos.parquet"),
        ("read_geoparquet", "../datos.parquet"),
    ],
)
def test_minio_reads_reject_invalid_keys_before_requesting_s3(method, object_key):
    service = object.__new__(MinIOService)
    service._get_client = lambda: pytest.fail("No debe llamarse a S3 para una clave inválida")

    with pytest.raises(InvalidObjectKey):
        getattr(service, method)(object_key)
