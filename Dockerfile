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
# Se monta como volumen de Railway para que sobreviva a los redeploys.
VOLUME ["/app/backend/data"]

EXPOSE 8080
