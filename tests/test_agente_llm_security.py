
import pytest

from src.agente_llm import (
    ARGUMENTOS,
    NOMBRES,
    LlamadaInvalida,
    validar_llamada,
    validar_sql,
)


# ============================================================
# 1. WHITELIST: HERRAMIENTAS AUTORIZADAS
# ============================================================

class TestHerramientasPermitidas:

    def test_acepta_herramienta_status(self):
        assert validar_llamada(NOMBRES["status"], {}) == {}

    def test_acepta_herramienta_listar(self):
        assert validar_llamada(NOMBRES["listar"], {}) == {}

    def test_rechaza_herramienta_inexistente(self):
        with pytest.raises(LlamadaInvalida):
            validar_llamada("delete_database", {})

    def test_rechaza_nombre_similar(self):
        with pytest.raises(LlamadaInvalida):
            validar_llamada("get_system_status_fake", {})

    def test_rechaza_herramienta_vacia(self):
        with pytest.raises(LlamadaInvalida):
            validar_llamada("", {})


# ============================================================
# 2. VALIDACIÓN DE ARGUMENTOS
# ============================================================

class TestArgumentosSeguros:

    def test_rechaza_argumentos_no_dict(self):
        with pytest.raises(LlamadaInvalida):
            validar_llamada(
                NOMBRES["consultar"],
                "argumentos"
            )

    def test_rechaza_argumento_obligatorio_faltante(self):
        with pytest.raises(LlamadaInvalida):
            validar_llamada(
                NOMBRES["consultar"],
                {"dataset_id": "geo/archivo.parquet"}
            )

    def test_rechaza_argumento_adicional(self):
        with pytest.raises(LlamadaInvalida):
            validar_llamada(
                NOMBRES["describir"],
                {
                    "dataset_id": "geo/archivo.parquet",
                    "admin": True
                }
            )

    def test_descarta_argumentos_en_herramienta_sin_parametros(self):
        # El modelo pequeno manda argumentos de mas: se descartan y no llegan al MCP.
        assert validar_llamada(NOMBRES["status"], {"admin": True}) == {}

    def test_rechaza_argumentos_no_dict_en_herramienta_sin_parametros(self):
        with pytest.raises(LlamadaInvalida):
            validar_llamada(
                NOMBRES["status"],
                ["admin"]
            )

    def test_acepta_argumentos_correctos(self):
        resultado = validar_llamada(
            NOMBRES["describir"],
            {"dataset_id": "geo/archivo.parquet"}
        )

        assert resultado == {
            "dataset_id": "geo/archivo.parquet"
        }


# ============================================================
# 3. VALIDACIÓN DE IDENTIFICADORES DE DATASETS
# ============================================================

class TestDatasetId:

    @pytest.mark.parametrize("dataset_id", [
        "",
        "../secreto.parquet",
        "../../etc/passwd",
        "/etc/passwd",
        r"geo\..\secreto.parquet",
        "geo/../../secreto.parquet",
        "geo archivo.parquet",
        "geo/archivo.parquet/../../secreto",
        "a" * 129,
        None,
        123,
    ])
    def test_rechaza_dataset_id_malicioso(self, dataset_id):
        with pytest.raises(LlamadaInvalida):
            validar_llamada(
                NOMBRES["describir"],
                {"dataset_id": dataset_id}
            )

    @pytest.mark.parametrize("dataset_id", [
        "geo/archivo.parquet",
        "ingresos/datos.csv",
        "metadatos/catalogo.json",
        "dataset_01",
    ])
    def test_acepta_dataset_id_valido(self, dataset_id):
        resultado = validar_llamada(
            NOMBRES["describir"],
            {"dataset_id": dataset_id}
        )

        assert resultado["dataset_id"] == dataset_id


# ============================================================
# 4. SQL: CONSULTAS LEGÍTIMAS
# ============================================================

class TestSQLPermitido:

    @pytest.mark.parametrize("sql", [
        "SELECT * FROM dataset",
        "SELECT COUNT(*) FROM dataset",
        "SELECT * FROM dataset WHERE id = 1",
        "SELECT nombre FROM dataset ORDER BY nombre",
        "SELECT * FROM dataset;",
    ])
    def test_acepta_select_legitimo(self, sql):
        resultado = validar_sql(sql)

        assert resultado.upper().startswith("SELECT")
        assert ";" not in resultado

    def test_acepta_consulta_con_alias(self):
        resultado = validar_sql(
            "SELECT d.nombre FROM dataset AS d"
        )

        assert resultado.upper().startswith("SELECT")


# ============================================================
# 5. SQL INJECTION Y OPERACIONES DESTRUCTIVAS
# ============================================================

class TestSQLInjection:

    @pytest.mark.parametrize("sql", [
        "DELETE FROM dataset",
        "DROP TABLE dataset",
        "UPDATE dataset SET nombre = 'hack'",
        "INSERT INTO dataset VALUES (1)",
        "TRUNCATE TABLE dataset",
        "ALTER TABLE dataset ADD COLUMN admin INT",
        "CREATE TABLE usuarios (id INT)",
        "SELECT * FROM dataset; DROP TABLE dataset",
        "SELECT * FROM dataset -- comentario",
        "SELECT * FROM dataset /* comentario */",
        "SELECT * FROM dataset JOIN usuarios ON 1=1",
        "SELECT * FROM dataset, usuarios",
        "SELECT * FROM usuarios",
    ])
    def test_rechaza_sql_peligroso(self, sql):
        with pytest.raises(LlamadaInvalida):
            validar_sql(sql)

    @pytest.mark.parametrize("sql", [
        None,
        123,
        "",
        "   ",
        "SELECT " + ("a" * 1001),
    ])
    def test_rechaza_sql_invalido(self, sql):
        with pytest.raises(LlamadaInvalida):
            validar_sql(sql)

    def test_rechaza_union_select(self):
        sql = (
            "SELECT * FROM dataset "
            "UNION SELECT * FROM dataset"
        )

        with pytest.raises(LlamadaInvalida):
            validar_sql(sql)

    def test_rechaza_lectura_parquet(self):
        sql = (
            "SELECT read_parquet('secreto.parquet') "
            "FROM dataset"
        )

        with pytest.raises(LlamadaInvalida):
            validar_sql(sql)

    def test_rechaza_lectura_csv(self):
        sql = (
            "SELECT read_csv_auto('/etc/passwd') "
            "FROM dataset"
        )

        with pytest.raises(LlamadaInvalida):
            validar_sql(sql)


# ============================================================
# 6. VALIDACIÓN DE LA HERRAMIENTA query_dataset
# ============================================================

class TestConsultaDataset:

    def test_acepta_consulta_completa(self):
        argumentos = {
            "dataset_id": "geo/archivo.parquet",
            "sql": "SELECT * FROM dataset"
        }

        resultado = validar_llamada(
            NOMBRES["consultar"],
            argumentos
        )

        assert resultado["dataset_id"] == "geo/archivo.parquet"
        assert resultado["sql"] == "SELECT * FROM dataset"

    def test_rechaza_sql_malicioso_en_herramienta(self):
        argumentos = {
            "dataset_id": "geo/archivo.parquet",
            "sql": "DROP TABLE dataset"
        }

        with pytest.raises(LlamadaInvalida):
            validar_llamada(
                NOMBRES["consultar"],
                argumentos
            )

    def test_rechaza_dataset_malicioso_en_consulta(self):
        argumentos = {
            "dataset_id": "../../secreto.parquet",
            "sql": "SELECT * FROM dataset"
        }

        with pytest.raises(LlamadaInvalida):
            validar_llamada(
                NOMBRES["consultar"],
                argumentos
            )

    def test_rechaza_argumentos_extra_en_consulta(self):
        argumentos = {
            "dataset_id": "geo/archivo.parquet",
            "sql": "SELECT * FROM dataset",
            "admin": True
        }

        with pytest.raises(LlamadaInvalida):
            validar_llamada(
                NOMBRES["consultar"],
                argumentos
            )


# ============================================================
# 7. CONFIGURACIÓN DE SEGURIDAD
# ============================================================

class TestConfiguracionSegura:

    def test_existen_cuatro_herramientas_autorizadas(self):
        assert len(ARGUMENTOS) == 4

    def test_status_no_requiere_argumentos(self):
        assert ARGUMENTOS[NOMBRES["status"]] == set()

    def test_listar_no_requiere_argumentos(self):
        assert ARGUMENTOS[NOMBRES["listar"]] == set()

    def test_describir_requiere_dataset_id(self):
        assert ARGUMENTOS[NOMBRES["describir"]] == {
            "dataset_id"
        }

    def test_consultar_requiere_dataset_y_sql(self):
        assert ARGUMENTOS[NOMBRES["consultar"]] == {
            "dataset_id",
            "sql"
        }
