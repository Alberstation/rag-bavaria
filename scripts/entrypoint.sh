#!/bin/bash
set -e

cd /app/backend

# Arranca OpenWebUI en segundo plano (comando original de la imagen base)
bash start.sh &
WEBUI_PID=$!

trap 'kill -TERM $WEBUI_PID 2>/dev/null' TERM INT

# Da de alta a los usuarios de users.csv. Si falla, no debe tumbar el contenedor.
python3 /app/scripts/sync_users.py || echo "[entrypoint] la sincronizacion de usuarios fallo; continuo de todas formas."

# Reenvia la señal de terminacion y mantiene vivo el proceso principal
wait "$WEBUI_PID"
