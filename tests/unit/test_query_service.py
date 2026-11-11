import io

import pytest
import pyarrow as pa
import pyarrow.parquet as pq

from src.mcp.services.query_service import QueryService


class FakeBody:
    def __init__(self, payload):
        self.payload = payload

    def read(self, limit):
        return self.payload[:limit]

    def close(self):
        pass


class FakeS3Client:
    def __init__(self, payload):
        self.payload = payload

    def get_object(self, **kwargs):
        return {"ContentLength": len(self.payload), "Body": FakeBody(self.payload)}


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM dataset",
        "SELECT departamento, SUM(ingreso) FROM dataset GROUP BY departamento",
        "SELECT 1",
    ],
)
def test_validate_query_accepts_selects_over_dataset(sql):
    QueryService._validate_query(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM dataset",
        "SELECT * FROM dataset; DELETE FROM dataset",
        "SELECT * FROM read_parquet('s3://otro-bucket/secreto.parquet')",
        "SELECT * FROM otro_dataset",
        "WITH x AS (SELECT * FROM dataset) SELECT * FROM x",
        "SELECT * FROM dataset JOIN otro_dataset USING (id)",
    ],
)
def test_validate_query_rejects_writes_multiple_statements_and_other_sources(sql):
    with pytest.raises(ValueError):
        QueryService._validate_query(sql)


def test_invalid_sql_has_a_stable_tool_error_shape(monkeypatch):
    service = QueryService()
    result = service.query_dataset("datos.parquet", "DELETE FROM dataset")

    assert result == {
        "ok": False,
        "error": {
            "code": "INVALID_QUERY",
            "message": "Solo se permite una sentencia SELECT.",
        },
    }


@pytest.mark.parametrize("operation", ["describe_dataset", "query_dataset"])
def test_query_service_rejects_invalid_keys_before_requesting_s3(operation):
    service = QueryService()
    service._client = lambda: pytest.fail("No debe llamarse a S3 para una clave inválida")

    if operation == "describe_dataset":
        result = service.describe_dataset("../private.parquet")
    else:
        result = service.query_dataset("../private.parquet", "SELECT * FROM dataset")

    assert result["ok"] is False
    assert result["error"]["code"] == "INVALID_OBJECT_KEY"


def test_query_dataset_returns_structured_rows_and_enforces_row_limit():
    table = pa.table({"id": [1, 2, 3]})
    buffer = io.BytesIO()
    pq.write_table(table, buffer)

    service = QueryService()
    service._client = lambda: FakeS3Client(buffer.getvalue())
    service.max_rows = 2

    result = service.query_dataset(
        "ingresos.parquet",
        "SELECT id FROM dataset ORDER BY id",
    )

    assert result["ok"] is True
    assert result["data"]["columns"] == ["id"]
    assert result["data"]["rows"] == [{"id": 1}, {"id": 2}]
    assert result["data"]["row_count"] == 2
    assert result["data"]["truncated"] is True
