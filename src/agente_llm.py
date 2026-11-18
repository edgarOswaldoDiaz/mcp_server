"""Reglas de seguridad del agente con modelo (Equipo B).
El modelo propone llamadas a herramientas y este modulo decide si se ejecutan.
"""
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

_ID_VALIDO = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")


def validar_sql(sql):
    """Acepta un solo SELECT sobre la tabla dataset. Es una segunda capa:
    la revision principal la hace el MCP."""
    if not isinstance(sql, str):
        raise LlamadaInvalida("sql no es texto")
    s = sql.strip()
    if s.endswith(";"):
        s = s[:-1].strip()
    if not s or len(s) > 1000:
        raise LlamadaInvalida("sql vacio o muy largo")
    if ";" in s or "--" in s or "/*" in s:
        raise LlamadaInvalida("sql con varias sentencias o comentarios")
    if not re.match(r"(?is)^select\b", s):
        raise LlamadaInvalida("sql no empieza con SELECT")
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
    o lanza LlamadaInvalida."""
    try:
        if nombre not in ARGUMENTOS:
            raise LlamadaInvalida("herramienta no permitida")
        if not isinstance(argumentos, dict) or set(argumentos) != ARGUMENTOS[nombre]:
            raise LlamadaInvalida("argumentos distintos a los esperados")
        limpios = dict(argumentos)
        if "dataset_id" in limpios:
            d = limpios["dataset_id"]
            if not (isinstance(d, str) and _ID_VALIDO.match(d)):
                raise LlamadaInvalida("dataset_id no valido")
        if "sql" in limpios:
            limpios["sql"] = validar_sql(limpios["sql"])
        return limpios
    except LlamadaInvalida as e:
        audit.warning("llamada rechazada: herramienta=%r motivo=%s", str(nombre)[:200], e)
        raise
