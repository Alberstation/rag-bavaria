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
| `WEBUI_ADMIN_EMAIL` | ✅ | Email de la cuenta admin. Se crea sola en el primer arranque y se usa para dar de alta usuarios de `users.csv`. |
| `WEBUI_ADMIN_PASSWORD` | ✅ | Contraseña de esa cuenta admin. |
| `OPENAI_API_BASE_URL` | ⬜ | Por defecto `https://api.openai.com/v1`. Cámbiala para proveedores compatibles. |
| `ENABLE_SIGNUP` | ⬜ | Se cierra sola al definir `WEBUI_ADMIN_EMAIL`/`WEBUI_ADMIN_PASSWORD`. |
| `WEBUI_NAME` | ⬜ | Nombre que se muestra en la interfaz. |

> ⚠️ **No definas `PORT`.** Railway la inyecta y el contenedor ya la respeta.

## Alta automática de usuarios (`users.csv`)

Edita [`users.csv`](users.csv) en la raíz del repo para dar de alta usuarios:

```csv
name,email,password,role
Juan Perez,juan.perez@example.com,ClaveTemporal123,user
```

- `role` puede ser `admin`, `user` o `pending`.
- Las líneas que empiezan con `#` son comentarios.
- La contraseña es solo la inicial: cada usuario puede cambiarla luego desde
  **Settings → Account**.

Al hacer `git push` (o cualquier redeploy en Railway), la imagen se
reconstruye con el `users.csv` actualizado. En cada arranque del
contenedor, [`scripts/sync_users.py`](scripts/sync_users.py) espera a que
OpenWebUI esté listo, inicia sesión como admin (con `WEBUI_ADMIN_EMAIL` /
`WEBUI_ADMIN_PASSWORD`) y da de alta a los usuarios que aún no existan. Es
idempotente: los usuarios que ya existen se omiten sin error, así que
puedes dejar el archivo con el histórico completo de usuarios dados de
alta. Revisa los logs de Railway (busca las líneas `[sync_users]`) para
confirmar qué se creó en cada deploy.

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
