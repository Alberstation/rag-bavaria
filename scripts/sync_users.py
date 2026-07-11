#!/usr/bin/env python3
"""Da de alta en OpenWebUI a los usuarios listados en users.csv.

Se ejecuta en cada arranque del contenedor (ver scripts/entrypoint.sh).
Inicia sesion como admin y llama a la API de OpenWebUI para crear a
cualquier usuario del CSV que todavia no exista. Es idempotente: si un
usuario ya existe, la API responde 400 y se omite sin error.
"""

import csv
import http.cookiejar
import json
import os
import time
import urllib.error
import urllib.request

PORT = os.environ.get("PORT", "8080")
BASE_URL = f"http://127.0.0.1:{PORT}"
CSV_PATH = os.environ.get("USERS_CSV_PATH", "/app/scripts/users.csv")
ADMIN_EMAIL = os.environ.get("WEBUI_ADMIN_EMAIL")
ADMIN_PASSWORD = os.environ.get("WEBUI_ADMIN_PASSWORD")
MAX_WAIT_SECONDS = int(os.environ.get("USERS_SYNC_MAX_WAIT", "120"))

VALID_ROLES = {"admin", "user", "pending"}


def log(msg):
    print(f"[sync_users] {msg}", flush=True)


def wait_for_backend():
    deadline = time.time() + MAX_WAIT_SECONDS
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health", timeout=5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


def post_json(opener, path, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with opener.open(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except ValueError:
            parsed = {"detail": body}
        return e.code, parsed


def load_users(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("email")]


def main():
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        log(
            "WEBUI_ADMIN_EMAIL / WEBUI_ADMIN_PASSWORD no estan definidas; "
            "se omite la sincronizacion de usuarios."
        )
        return

    if not os.path.exists(CSV_PATH):
        log(f"No se encontro {CSV_PATH}; nada que sincronizar.")
        return

    rows = load_users(CSV_PATH)
    if not rows:
        log("users.csv no tiene filas de usuarios; nada que hacer.")
        return

    log("Esperando a que OpenWebUI este listo...")
    if not wait_for_backend():
        log("Se agoto el tiempo de espera del backend; se omite la sincronizacion.")
        return

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    status, resp = post_json(
        opener,
        "/api/v1/auths/signin",
        {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    if status != 200:
        log(f"No se pudo iniciar sesion como admin ({status}): {resp}. Se omite la sincronizacion.")
        return

    log(f"Sesion admin iniciada. Sincronizando {len(rows)} usuario(s) desde {CSV_PATH}...")

    created, skipped, failed = 0, 0, 0
    for row in rows:
        name = (row.get("name") or "").strip()
        email = row["email"].strip()
        password = (row.get("password") or "").strip()
        role = (row.get("role") or "user").strip().lower()

        if role not in VALID_ROLES:
            log(f"  - {email}: rol '{role}' invalido, se usa 'user'.")
            role = "user"

        if not name or not password:
            log(f"  - {email}: falta name o password, se omite.")
            failed += 1
            continue

        status, resp = post_json(
            opener,
            "/api/v1/auths/add",
            {"name": name, "email": email, "password": password, "role": role},
        )

        if status == 200:
            log(f"  - {email}: creado.")
            created += 1
        elif status == 400:
            detail = resp.get("detail", resp) if isinstance(resp, dict) else resp
            log(f"  - {email}: ya existe o dato invalido, se omite ({detail}).")
            skipped += 1
        else:
            log(f"  - {email}: error inesperado ({status}): {resp}")
            failed += 1

    log(f"Listo. Creados: {created}, omitidos: {skipped}, con error: {failed}.")


if __name__ == "__main__":
    main()
