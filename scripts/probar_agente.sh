#!/usr/bin/env bash
# Prueba de punta a punta del agente A2A -> MCP (OAuth+DPoP) -> almacenamiento S3 (RustFS o MinIO).
# Uso: ./scripts/probar_agente.sh [URL_DEL_AGENTE]
# Variable obligatoria: API_KEY (clave Bearer de entrada del agente).

set -euo pipefail

URL="${1:-http://localhost:8002}"

# No usar ninguna API key predeterminada.
: "${API_KEY:?ERROR: Debes configurar API_KEY antes de ejecutar este script}"

KEY="$API_KEY"
fallos=0

# Manda texto al agente, espera a que la tarea termine (max. 20 s) y devuelve el JSON de la tarea.
preguntar() {
    local cuerpo id res i

    cuerpo=$(printf '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"role":"user","parts":[{"kind":"text","text":"%s"}],"messageId":"m1"}}}' "$1")

    id=$(curl -s -X POST "$URL/a2a/rpc" \
        -H "Authorization: Bearer $KEY" \
        -H "Content-Type: application/json" \
        -d "$cuerpo" |
        grep -o '"id":"task-[0-9a-f]*"' |
        head -1 |
        cut -d'"' -f4 || true)

    if [ -z "$id" ]; then
        echo "SIN_TAREA"
        return
    fi

    for i in $(seq 1 20); do
        res=$(curl -s "$URL/a2a/tasks/$id" \
            -H "Authorization: Bearer $KEY")

        case "$res" in
            *TASK_STATE_SUBMITTED*|*TASK_STATE_WORKING*)
                sleep 1
                ;;
            *)
                break
                ;;
        esac
    done

    echo "$res"
}

# comprobar "descripcion" ESTADO_ESPERADO "texto que debe aparecer (opcional)" "mensaje a enviar"
comprobar() {
    local desc="$1" esperado="$2" contiene="$3" msg="$4"
    local res estado

    res=$(preguntar "$msg")
    estado=$(echo "$res" | grep -o 'TASK_STATE_[A-Z_]*' | head -1 || true)

    if [ "$estado" = "$esperado" ] &&
        { [ -z "$contiene" ] || echo "$res" | grep -q "$contiene"; }; then
        echo "[PASA ] $desc -> $estado"
    else
        echo "[FALLA] $desc -> esperado $esperado, obtenido ${estado:-nada}"
        echo "       respuesta: $(echo "$res" | cut -c1-300)"
        fallos=$((fallos+1))
    fi
}

codigo() {
    curl -s -o /dev/null -w "%{http_code}" "$@"
}

echo "Agente: $URL"

comprobar "Leer JSON confidencial" \
    TASK_STATE_COMPLETED '"filas":5' \
    "leer metadatos/ingresos_sinteticos.json"

comprobar "Leer Parquet confidencial" \
    TASK_STATE_COMPLETED 'folio' \
    "leer ingresos/ingresos_sinteticos.parquet"

comprobar "Leer GeoParquet confidencial" \
    TASK_STATE_COMPLETED 'geometry' \
    "leer geo/puntos_sinteticos.parquet"

comprobar "Archivo inexistente (debe fallar)" \
    TASK_STATE_FAILED "" \
    "leer metadatos/archivo_que_no_existe.json"

c=$(codigo "$URL/a2a/tasks/task-inexistente")

if [ "$c" = "401" ]; then
    echo "[PASA ] Consultar tarea SIN token -> 401"
else
    echo "[FALLA] Consultar tarea SIN token -> $c (esperado 401)"
    fallos=$((fallos+1))
fi

c=$(codigo -X POST "$URL/a2a/rpc" \
    -H "Content-Type: application/json" \
    -d '{}')

if [ "$c" = "401" ]; then
    echo "[PASA ] Enviar tarea SIN token -> 401"
else
    echo "[FALLA] Enviar tarea SIN token -> $c (esperado 401)"
    fallos=$((fallos+1))
fi

if [ "$fallos" -eq 0 ]; then
    echo "RESULTADO: TODO CORRECTO"
else
    echo "RESULTADO: $fallos PRUEBA(S) FALLARON"
fi

exit "$((fallos>0))"
