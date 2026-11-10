"""Entrada pública WSGI. Código y secretos permanecen fuera de httpdocs."""
from pathlib import Path
import sys

private = Path(__file__).resolve().parent.parent / "tecnostore-private"
sys.path.insert(0, str(private / "app"))
from hosting import create_hosted_app

application = create_hosted_app(private / "config.toml")
