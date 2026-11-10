#!/usr/bin/python3.14
"""Adaptador CGI para Flask en Tommy; no contiene credenciales."""
import os
from pathlib import Path
import sys
from wsgiref.handlers import CGIHandler
from tempfile import SpooledTemporaryFile

private = Path(__file__).resolve().parent.parent / "tecnostore-private"
sys.path.insert(0, str(private / "app"))
from hosting import create_hosted_app

application = create_hosted_app(private / "config.toml")
# Conservar URLs públicas y Location sin el nombre interno del adaptador.
os.environ["SCRIPT_NAME"] = ""
os.environ["PATH_INFO"] = os.environ.get("PATH_INFO") or "/"
# Consumir el cuerpo aunque Flask rechace la solicitud antes de leer JSON.
# Evita que Apache reciba un cierre de tubería con datos pendientes (AH00574).
with SpooledTemporaryFile(max_size=1024 * 1024) as body:
    remaining = int(os.environ.get("CONTENT_LENGTH") or 0)
    while remaining > 0:
        block = sys.stdin.buffer.read(min(65536, remaining))
        if not block:
            break
        body.write(block)
        remaining -= len(block)
    body.seek(0)
    handler = CGIHandler()
    handler.stdin = body
    handler.run(application)
