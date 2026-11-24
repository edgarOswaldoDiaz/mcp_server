from src.agente_llm import _parece_llamada


def test_detecta_llamada_escrita_como_texto():
    texto = '{"type":"function","function":{"name":"query_dataset","param":{"sql": "DROP TABLE dataset"}}}'
    assert _parece_llamada(texto) is True


def test_detecta_llamada_con_espacios_alrededor():
    assert _parece_llamada('  {"name": "query_dataset", "arguments": {}}\n') is True


def test_respuesta_normal_no_se_bloquea():
    assert _parece_llamada("Hay 2 conjuntos de datos disponibles.") is False


def test_texto_que_menciona_function_pero_no_es_bloque():
    assert _parece_llamada('Puedes usar la "function" query_dataset para eso.') is False


def test_llaves_sin_forma_de_llamada_no_se_bloquean():
    assert _parece_llamada('{"filas": 5}') is False


def test_texto_vacio():
    assert _parece_llamada("") is False
