"""Carga privada de configuración para WSGI; no inicia un servidor de desarrollo."""
import os
from pathlib import Path
import tomllib


def create_hosted_app(config_path):
    with Path(config_path).open("rb") as archivo:
        configuracion = tomllib.load(archivo)["environment"]
    permitidas = {"FLASK_SECRET_KEY", "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER",
                  "DB_PASSWORD", "DB_SSL_CA", "DB_UNIX_SOCKET"}
    if set(configuracion) - permitidas or any(not isinstance(v, str) for v in configuracion.values()):
        raise ValueError("Configuración de alojamiento inválida.")
    # No heredar configuración de otra base/entorno accidentalmente.
    for nombre in permitidas:
        os.environ.pop(nombre, None)
    os.environ.update(configuracion)
    os.environ["TECNOSTORE_PRODUCTION"] = "1"
    from api import create_app
    app = create_app()
    app.config.update(DEBUG=False, TESTING=False)
    return app
