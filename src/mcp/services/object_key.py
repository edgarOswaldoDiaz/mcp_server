"""Validación común de claves de objetos en almacenamiento S3."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable


class InvalidObjectKey(ValueError):
    """Indica que una clave de objeto no cumple las reglas de lectura del MCP."""


def validate_object_key(
    object_key: str,
    allowed_suffixes: Iterable[str],
) -> str:
    """Valida una clave S3 sin normalizar ni reinterpretar su valor."""
    if not isinstance(object_key, str) or not object_key:
        raise InvalidObjectKey("La clave del objeto está vacía o no es válida.")

    try:
        encoded_key = object_key.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise InvalidObjectKey("La clave del objeto no es UTF-8 válida.") from exc

    if len(encoded_key) > 1024:
        raise InvalidObjectKey("La clave del objeto supera los 1024 bytes permitidos.")
    if object_key.startswith("/") or "\\" in object_key:
        raise InvalidObjectKey("La clave del objeto tiene separadores no permitidos.")
    if any(unicodedata.category(character) == "Cc" for character in object_key):
        raise InvalidObjectKey("La clave del objeto contiene caracteres de control.")
    if any(segment in {".", ".."} for segment in object_key.split("/")):
        raise InvalidObjectKey("La clave del objeto contiene segmentos relativos.")

    suffixes = tuple(suffix.casefold() for suffix in allowed_suffixes)
    if not suffixes or not object_key.casefold().endswith(suffixes):
        raise InvalidObjectKey("La extensión del objeto no está permitida para esta herramienta.")

    return object_key
