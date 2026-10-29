#!/usr/bin/env bash
# Prueba de punta a punta del agente A2A -> MCP (OAuth+DPoP) -> almacenamiento S3 (RustFS o MinIO).
# Uso:  ./scripts/probar_agente.sh [URL_DEL_AGENTE]        (por defecto http://localhost:8002)
# Variable opcional: API_KEY (la clave Bearer de ENTRADA del agente; por defecto la de .env.example).
URL="${1:-http://localhost:8002}"
KEY="${API_KEY:-secret-a2a-token-123}"
fallos=0

# Manda "texto" al agente, espera a que la tarea termine (max. 20 s) y devuelve el JSON de la tarea.
preguntar() {
  local cuerpo id res i
  cuerpo=$(printf '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"role":"user","parts":[{"kind":"text","text":"%s"}],"messageId":"m1"}}}' "$1")
  id=$(curl -s -X POST "$URL/a2a/rpc" -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
        -d "$cuerpo" | grep -o '"id":"task-[0-9a-f]*"' | head -1 | cut -d'"' -f4)
  [ -z "$id" ] && { echo "SIN_TAREA"; return; }
  for i in $(seq 1 20); do
    res=$(curl -s "$URL/a2a/tasks/$id" -H "Authorization: Bearer $KEY")
    case "$res" in *TASK_STATE_SUBMITTED*|*TASK_STATE_WORKING*) sleep 1 ;; *) break ;; esac
  done
  echo "$res"
}

# comprobar "descripcion" ESTADO_ESPERADO "texto que debe aparecer (opcional)" "mensaje a enviar"
comprobar() {
  local desc="$1" esperado="$2" contiene="$3" msg="$4" res estado
  res=$(preguntar "$msg")
  estado=$(echo "$res" | grep -o 'TASK_STATE_[A-Z_]*' | head -1)
  if [ "$estado" = "$esperado" ] && { [ -z "$contiene" ] || echo "$res" | grep -q "$contiene"; }; then
    echo "[PASA ] $desc  ->  $estado"
  else
    echo "[FALLA] $desc  ->  esperado $esperado, obtenido ${estado:-nada}"
    echo "        respuesta: $(echo "$res" | cut -c1-300)"
    fallos=$((fallos+1))
  fi
}

codigo() { curl -s -o /dev/null -w "%{http_code}" "$@"; }

echo "Agente: $URL"
comprobar "Leer JSON confidencial"        TASK_STATE_COMPLETED '"filas":5'   "leer metadatos/ingresos_sinteticos.json"
comprobar "Leer Parquet confidencial"     TASK_STATE_COMPLETED 'folio'       "leer ingresos/ingresos_sinteticos.parquet"
comprobar "Leer GeoParquet confidencial"  TASK_STATE_COMPLETED 'geometry'    "leer geo/puntos_sinteticos.parquet"
comprobar "Archivo inexistente (debe fallar)" TASK_STATE_FAILED 'no existe'  "leer no/existe.json"

c=$(codigo "$URL/a2a/tasks/task-inexistente")
[ "$c" = "401" ] && echo "[PASA ] Consultar tarea SIN token  ->  401" || { echo "[FALLA] Consultar tarea SIN token -> $c (esperado 401)"; fallos=$((fallos+1)); }
c=$(codigo -X POST "$URL/a2a/rpc" -H "Content-Type: application/json" -d '{}')
[ "$c" = "401" ] && echo "[PASA ] Enviar tarea SIN token  ->  401" || { echo "[FALLA] Enviar tarea SIN token -> $c (esperado 401)"; fallos=$((fallos+1)); }

[ "$fallos" -eq 0 ] && echo "RESULTADO: TODO CORRECTO" || echo "RESULTADO: $fallos PRUEBA(S) FALLARON"
exit $((fallos>0))
