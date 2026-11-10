"""Configuración WSGI y compatibilidad de acceso, sin credenciales reales."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from api import create_app
from hosting import create_hosted_app
from logic.auth import autenticar_usuario
from db.connection import conectar_bd


class HostingTest(unittest.TestCase):
    def test_produccion_exige_secretos(self):
        with patch.dict(os.environ, {"TECNOSTORE_PRODUCTION": "1"}, clear=True):
            with self.assertRaises(RuntimeError):
                create_app()
        with patch.dict(os.environ, {"TECNOSTORE_PRODUCTION": "1", "FLASK_SECRET_KEY": "prueba"}, clear=True):
            with self.assertRaises(RuntimeError):
                create_app()

    def test_wsgi_config_privada_y_cookie_segura(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            config = Path(directory) / "config.toml"
            config.write_text('[environment]\nFLASK_SECRET_KEY="solo-prueba"\nDB_UNIX_SOCKET="/tmp/mysql.sock"\nDB_USER="prueba"\nDB_PASSWORD="solo-prueba"\nDB_NAME="prueba"\n', encoding="utf-8")
            app = create_hosted_app(config)
            self.assertTrue(app.config["SESSION_COOKIE_SECURE"])
            self.assertFalse(app.debug)
            self.assertEqual(app.test_client().get("/").status_code, 200)
            self.assertEqual(os.environ["DB_NAME"], "prueba")

    def test_socket_local_y_conector_puro(self):
        with patch.dict(os.environ, dict(DB_UNIX_SOCKET="/tmp/mysql.sock", DB_USER="prueba",
                                       DB_PASSWORD="solo-prueba", DB_NAME="prueba"), clear=True):
            with patch("db.connection.mysql.connector.connect") as connect:
                conectar_bd()
            connect.assert_called_once_with(unix_socket="/tmp/mysql.sock", user="prueba",
                password="solo-prueba", database="prueba", connection_timeout=10, use_pure=True)

    def test_mysql_externo_conserva_validacion_tls(self):
        with patch.dict(os.environ, dict(DB_HOST="db.example.test", DB_USER="prueba",
                                       DB_PASSWORD="solo-prueba", DB_NAME="prueba"), clear=True):
            with patch("db.connection.mysql.connector.connect") as connect:
                conectar_bd()
            self.assertTrue(connect.call_args.kwargs["ssl_verify_cert"])
            self.assertTrue(connect.call_args.kwargs["ssl_verify_identity"])
            self.assertTrue(connect.call_args.kwargs["use_pure"])

    def test_cgi_rutas_y_rechazo_temprano_con_cuerpo(self):
        import shutil
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / "httpdocs").mkdir()
            private = home / "tecnostore-private"
            app = private / "app"
            app.mkdir(parents=True)
            root = Path(__file__).resolve().parents[1]
            shutil.copy(root / "deploy/heliohost/tecnostore.py", home / "httpdocs/tecnostore.py")
            shutil.copy(root / "hosting.py", app / "hosting.py")
            for folder in ("api", "logic", "db"):
                shutil.copytree(root / folder, app / folder, ignore=shutil.ignore_patterns("__pycache__"))
            (private / "config.toml").write_text('[environment]\nFLASK_SECRET_KEY="solo-prueba"\nDB_UNIX_SOCKET="/tmp/falso.sock"\nDB_USER="prueba"\nDB_PASSWORD="solo-prueba"\nDB_NAME="prueba"\n', encoding="utf-8")
            for method, path, body in (("GET", "/", b""), ("POST", "/api/productos", b"x" * 70000)):
                env = dict(os.environ, GATEWAY_INTERFACE="CGI/1.1", SERVER_NAME="localhost",
                           SERVER_PORT="443", SERVER_PROTOCOL="HTTP/1.1", HTTPS="on",
                           REQUEST_METHOD=method, PATH_INFO=path, SCRIPT_NAME="/tecnostore.py",
                           CONTENT_LENGTH=str(len(body)))
                result = subprocess.run([sys.executable, str(home / "httpdocs/tecnostore.py")],
                                        input=body, capture_output=True, env=env, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                output = result.stdout.decode("utf-8")
                if method == "GET":
                    self.assertIn('<h1>Productos</h1>', output)
                    self.assertIn('href="/static/productos.css"', output)
                else:
                    self.assertIn("Status: 401", output)
                    self.assertIn("Iniciá sesión", output)

    def test_hash_y_credenciales_anteriores(self):
        from werkzeug.security import generate_password_hash
        usuario = dict(id_usuario=1, nombre="Admin", apellido="Demo", activo=1, rol="Admin")
        for guardada in ("clave-anterior", generate_password_hash("clave-anterior", method="pbkdf2:sha256:600000")):
            with self.subTest(hash=guardada.startswith("pbkdf2:")):
                with patch("logic.auth.obtener_usuario_por_username", return_value=dict(usuario, clave=guardada)):
                    self.assertTrue(autenticar_usuario("AdminDemo", "clave-anterior", sesion_escritorio=False)["success"])
                    self.assertIn("error", autenticar_usuario("AdminDemo", "incorrecta", sesion_escritorio=False))


if __name__ == "__main__":
    unittest.main()
