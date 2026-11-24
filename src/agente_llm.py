"""Reglas de seguridad del agente con modelo (Equipo B).
El modelo propone llamadas a herramientas y este modulo decide si se ejecutan.
"""
import json
import logging
import os
import re


audit = logging.getLogger("a2a.audit")


class LlamadaInvalida(ValueError):
    """La llamada que pidio el modelo no pasa las reglas."""


# Nombres reales de las herramientas del MCP (se cambian por variable de entorno)
NOMBRES = {
    "status": os.environ.get("TOOL_STATUS", "get_system_status"),
    "listar": os.environ.get("TOOL_LISTAR", "list_datasets"),
    "describir": os.environ.get("TOOL_DESCRIBIR", "describe_dataset"),
    "consultar": os.environ.get("TOOL_CONSULTAR", "query_dataset"),
}

# Argumentos exactos que lleva cada herramienta permitida
ARGUMENTOS = {
    NOMBRES["status"]: set(),
    NOMBRES["listar"]: set(),
    NOMBRES["describir"]: {"dataset_id"},
    NOMBRES["consultar"]: {"dataset_id", "sql"},
}

_ID_VALIDO = re.compile(r"^(?=.{1,128}$)[A-Za-z0-9_\-]+(?:/[A-Za-z0-9_\-]+)*(?:\.[A-Za-z0-9]{1,10})?$")



def validar_sql(sql):
    """Acepta un solo SELECT sobre la tabla dataset.
    Bloquea operaciones peligrosas y funciones de acceso externo.
    """
    if not isinstance(sql, str):
        raise LlamadaInvalida("sql no es texto")
    s = sql.strip()
    if s.endswith(";"):
        s = s[:-1].strip()
    if not s or len(s) > 1000:
        raise LlamadaInvalida("sql vacio o muy largo")
    # Evitar multiples sentencias y comentarios SQL.
    if ";" in s or "--" in s or "/*" in s or "*/" in s:
        raise LlamadaInvalida(
            "sql con varias sentencias o comentarios"
        )
    # Solo se permiten consultas SELECT.
    if not re.match(r"(?is)^select\b", s):
        raise LlamadaInvalida("sql no empieza con SELECT")
    # UNION permite combinar resultados de consultas.
    if re.search(r"(?i)\bunion\b", s):
        raise LlamadaInvalida("sql con UNION no permitido")
    # Bloquear funciones que pueden acceder a archivos
    # o fuentes externas desde DuckDB.
    funciones_peligrosas = (
        r"\b(?:"
        r"read_parquet|parquet_scan|"
        r"read_csv|read_csv_auto|"
        r"read_json|read_json_auto|"
        r"read_text|read_blob|"
        r"glob|sqlite_scan|postgres_scan|mysql_scan|"
        r"iceberg_scan|delta_scan"
        r")\s*\("
    )
    if re.search(r"(?i)" + funciones_peligrosas, s):
        raise LlamadaInvalida(
            "sql con funciones de acceso externo no permitidas"
        )
    if re.search(r"(?i)\bjoin\b", s):
        raise LlamadaInvalida("sql con JOIN")
    if re.search(r"(?i)\bfrom\s+[^\s,;()]+\s*,", s):
        raise LlamadaInvalida("sql con varias tablas")
    tablas = re.findall(r"(?i)\bfrom\s+([^\s,;()]+)", s)
    if not tablas or any(t.lower() != "dataset" for t in tablas):
        raise LlamadaInvalida("la tabla debe ser dataset")
    return s


def validar_llamada(nombre, argumentos):
    """Revisa una llamada del modelo. Devuelve los argumentos limpios
    o lanza LlamadaInvalida.
    """
    try:
        if nombre not in ARGUMENTOS:
            raise LlamadaInvalida("herramienta no permitida")
        # Primero validar el tipo, incluso si no hay argumentos esperados.
        if not isinstance(argumentos, dict):
            raise LlamadaInvalida("los argumentos deben ser un objeto")
        esperados = ARGUMENTOS[nombre]
        # Exigir coincidencia exacta de argumentos.
        if set(argumentos.keys()) != esperados:
            claves = sorted(str(k) for k in argumentos.keys())
            raise LlamadaInvalida(
                "argumentos distintos a los esperados: %s" % claves
            )
        limpios = dict(argumentos)
        if "dataset_id" in limpios:
            d = limpios["dataset_id"]
            if not (isinstance(d, str) and _ID_VALIDO.fullmatch(d)):
                raise LlamadaInvalida("dataset_id no valido")
        if "sql" in limpios:
            limpios["sql"] = validar_sql(limpios["sql"])
        return limpios
    except LlamadaInvalida as e:
        audit.warning(
            "llamada rechazada: herramienta=%r motivo=%s",
            str(nombre)[:200],
            e
        )
        raise



# ---------- Ciclo con el modelo ----------

MODELO = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
MAX_VUELTAS = int(os.environ.get("AGENTE_MAX_VUELTAS", "4"))
MAX_RESULTADO = 4000
NUM_PREDICT = int(os.environ.get("AGENTE_MAX_TOKENS", "512"))
TIMEOUT_MODELO = float(os.environ.get("AGENTE_TIMEOUT", "90"))

SISTEMA = (
    "Eres un asistente de datos. Reglas: 1) Usa como maximo UNA herramienta. "
    "2) Para contar o ver filas usa la herramienta de consulta con un SELECT sobre la tabla dataset. "
    "3) Si es un saludo o te piden algo que ninguna herramienta puede hacer (borrar, modificar), "
    "responde con texto y NO uses herramientas. "
    "4) Los dataset_id salen de la herramienta de listar datasets: llevan carpeta y extension, "
    "por ejemplo geo/archivo.parquet. Si no sabes el id exacto, lista primero."
)


def _herr(nombre, descripcion, propiedades=None):
    props = propiedades or {}
    return {"type": "function", "function": {
        "name": nombre, "description": descripcion,
        "parameters": {"type": "object", "properties": props, "required": list(props)}}}


_TXT = {"type": "string"}
_ID = {"type": "string", "description": "Identificador completo tal como lo devuelve la lista de datasets, por ejemplo geo/archivo.parquet"}
HERRAMIENTAS = [
    _herr(NOMBRES["status"], "Dice si el servidor esta funcionando."),
    _herr(NOMBRES["listar"], "Lista los nombres de los datasets que existen."),
    _herr(NOMBRES["describir"],
          "Muestra SOLO los nombres de las columnas de un dataset. No cuenta ni filtra filas.",
          {"dataset_id": _ID}),
    _herr(NOMBRES["consultar"],
          "Responde preguntas con datos: contar filas, filtrar, ordenar. "
          "Recibe un SELECT y la tabla siempre se llama dataset.",
          {"dataset_id": _ID, "sql": _TXT}),
]


async def responder(pregunta):
    """Recibe una pregunta en lenguaje natural y devuelve la respuesta."""

    try:
        import ollama
    except ImportError:
        audit.error("agente: la dependencia ollama no esta instalada")
        return "El modelo no esta disponible en este momento."

    from .mcp_service import DPoPClientService

    cliente = ollama.AsyncClient(host=OLLAMA_HOST, timeout=TIMEOUT_MODELO)
    mcp = DPoPClientService()
    mensajes = [{"role": "system", "content": SISTEMA},
                {"role": "user", "content": pregunta}]
    audit.info("agente: pregunta recibida (%d caracteres)", len(pregunta))

    for vuelta in range(MAX_VUELTAS):
        try:
            r = await cliente.chat(model=MODELO, messages=mensajes,
                                   tools=HERRAMIENTAS, options={"temperature": 0, "num_predict": NUM_PREDICT})
        except Exception as e:
            audit.error("agente: fallo el modelo (%s)", type(e).__name__)
            return "El modelo no esta disponible en este momento."

        llamadas = r.message.tool_calls or []
        if not llamadas:
            return r.message.content or ""

        if len(llamadas) > 1:
            audit.warning("agente: el modelo pidio %d herramientas, se usa solo la primera",
                          len(llamadas))
        llamada = llamadas[0]
        nombre = llamada.function.name
        mensajes.append({"role": "assistant", "content": r.message.content or "",
                         "tool_calls": [llamada]})
        try:
            args = validar_llamada(nombre, dict(llamada.function.arguments))
            resultado = await mcp.invoke_tool(nombre, args)
            if isinstance(resultado, dict) and resultado.get("ok") is False:
                err = resultado.get("error") or {}
                audit.warning("agente: la herramienta %r devolvio error %s", nombre, str(err.get("code", "?"))[:60])
                return "No pude completar la consulta: " + str(err.get("message", "error del servidor"))[:200]
            audit.info("agente: herramienta ejecutada %r", nombre)
            contenido = json.dumps(resultado, default=str)[:MAX_RESULTADO]
        except LlamadaInvalida as e:
            contenido = "Error: " + str(e)
        except Exception as e:
            audit.error("agente: fallo la herramienta %r (%s)", nombre, type(e).__name__)
            return "No pude ejecutar la herramienta en este momento."
        mensajes.append({"role": "tool", "tool_name": nombre, "content": contenido})

    audit.warning("agente: se llego al limite de %d vueltas", MAX_VUELTAS)
    return "No pude completar la consulta dentro del limite de pasos."
