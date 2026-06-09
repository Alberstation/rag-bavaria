# OpenWebUI en Railway

Contenedor de [OpenWebUI](https://github.com/open-webui/open-webui) listo para
desplegar en [Railway](https://railway.com), conectado a la **API de OpenAI** y
con **persistencia de datos** mediante un volumen.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `Dockerfile` | Imagen basada en la oficial `open-webui:main`. |
| `railway.toml` | Configuración de build y deploy en Railway. |
| `.env.example` | Plantilla de variables de entorno. |
| `docker-compose.yml` | Solo para probar en local. |
| `.dockerignore` | Excluye archivos del build. |

## Probar en local (opcional)

```powershell
Copy-Item .env.example .env   # edita .env y pon tu OPENAI_API_KEY
docker compose up --build
```

Abre http://localhost:3000 y crea la cuenta de administrador.

## Desplegar en Railway

### Opción A — Desde GitHub (recomendada)

1. Sube esta carpeta a un repositorio de GitHub.
2. En Railway: **New Project → Deploy from GitHub repo** y elige el repo.
   Railway detectará el `Dockerfile` automáticamente.
3. Configura las **Variables** (ver abajo).
4. Añade el **Volumen** (ver abajo).
5. Genera el dominio público en **Settings → Networking → Generate Domain**.

### Opción B — Con Railway CLI

```powershell
npm i -g @railway/cli
railway login
railway init
railway up
```

## Variables de entorno (Railway → Service → Variables)

| Variable | Obligatoria | Valor |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | Tu clave de OpenAI (`sk-...`). |
| `WEBUI_SECRET_KEY` | ✅ | Cadena aleatoria larga (`openssl rand -hex 32`). Fíjala una vez y no la cambies. |
| `OPENAI_API_BASE_URL` | ⬜ | Por defecto `https://api.openai.com/v1`. Cámbiala para proveedores compatibles. |
| `ENABLE_SIGNUP` | ⬜ | `false` tras crear tu admin para cerrar el registro. |
| `WEBUI_NAME` | ⬜ | Nombre que se muestra en la interfaz. |

> ⚠️ **No definas `PORT`.** Railway la inyecta y el contenedor ya la respeta.

## Volumen (persistencia)

Sin volumen, **perderás usuarios y chats en cada redeploy**.

En Railway: selecciona el servicio → pestaña **Volumes** → **New Volume** y
monta en:

```
/app/backend/data
```

Es la ruta donde OpenWebUI guarda la base de datos SQLite, los chats, los
usuarios y la configuración.

## Notas

- La imagen `:main` es la ligera (sin Ollama ni CUDA), suficiente porque la
  inferencia ocurre en la API de OpenAI.
- Healthcheck configurado en `/health`.
- Primer arranque: el primer usuario que se registra se convierte en
  administrador.
