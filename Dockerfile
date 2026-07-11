# OpenWebUI para Railway
# Imagen oficial "main": ligera, sin Ollama empaquetado ni CUDA.
# Ideal cuando solo te conectas a la API de OpenAI (o compatible).
FROM ghcr.io/open-webui/open-webui:main

# OpenWebUI escucha en el puerto definido por la variable PORT.
# Railway inyecta PORT automáticamente; este valor es solo el fallback local.
ENV PORT=8080

# Desactivamos Ollama porque solo usamos la API de OpenAI.
ENV ENABLE_OLLAMA_API=false

# Directorio donde OpenWebUI guarda BD, chats, usuarios y configuración.
# Se monta como volumen de Railway desde railway.toml

# --- Alta automática de usuarios desde users.csv ---
# Edita users.csv y haz push: en cada arranque del contenedor se sincroniza
# la lista de usuarios contra OpenWebUI (ver scripts/sync_users.py).
COPY users.csv /app/scripts/users.csv
COPY scripts/sync_users.py /app/scripts/sync_users.py
COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
RUN chmod +x /app/scripts/entrypoint.sh

EXPOSE 8080

CMD ["bash", "/app/scripts/entrypoint.sh"]
