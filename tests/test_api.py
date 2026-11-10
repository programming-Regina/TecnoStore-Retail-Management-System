"""Contrato HTTP y compatibilidad de la consulta, sin modificar MySQL."""
import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from api import create_app
from db.dao import obtener_productos_activos_ordenados


class ProductosTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_listado_reutiliza_capas_y_oculta_costo(self):
        conn = MagicMock()
        conn.cursor.return_value.fetchall.return_value = [{
            "id_producto": 1, "descripcion": "Mouse", "marca": "Tecno",
            "precio_venta": Decimal("1500.50"), "stock": 3,
            "precio_compra": Decimal("1000"), "activo": 1,
        }]
        with patch("db.connection.conectar_bd", return_value=conn):
            response = self.client.get("/api/productos")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["productos"], [{
            "id_producto": 1, "descripcion": "Mouse", "marca": "Tecno",
            "precio_venta": "1500.50", "stock": 3,
        }])
        sql = conn.cursor.return_value.execute.call_args.args[0]
        self.assertIn("activo = 1", sql)
        self.assertIn("ORDER BY descripcion", sql)
        conn.close.assert_called_once()

    def test_busqueda_nombre_parametrizada_y_solo_activos(self):
        conn = MagicMock()
        conn.cursor.return_value.fetchall.return_value = [dict(
            id_producto=2, descripcion="Mouse", marca="Tecno",
            precio_venta=Decimal("100"), stock=4, precio_compra=Decimal("50"))]
        with patch("db.connection.conectar_bd", return_value=conn):
            r = self.client.get("/api/productos", query_string={"nombre": "  MoU  "})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json["productos"]), 1)
        self.assertNotIn("precio_compra", r.json["productos"][0])
        sql, params = conn.cursor.return_value.execute.call_args.args
        self.assertIn("activo = 1", sql)
        self.assertIn("LOCATE(LOWER(%s), LOWER(descripcion))", sql)
        self.assertIn("ORDER BY descripcion", sql)
        self.assertEqual(params, ("MoU",))
        conn.close.assert_called_once()

    def test_busqueda_sin_resultados_y_texto_literal(self):
        for nombre in ("inexistente", "%_", "' OR 1=1 --"):
            with self.subTest(nombre=nombre):
                conn = MagicMock()
                conn.cursor.return_value.fetchall.return_value = []
                with patch("db.connection.conectar_bd", return_value=conn):
                    r = self.client.get("/api/productos", query_string={"nombre": nombre})
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.json, {"productos": []})
                self.assertEqual(conn.cursor.return_value.execute.call_args.args[1], (nombre,))

    def test_nombre_vacio_lista_todos_y_error_busqueda(self):
        conn = MagicMock()
        conn.cursor.return_value.fetchall.return_value = []
        with patch("db.connection.conectar_bd", return_value=conn):
            self.assertEqual(self.client.get("/api/productos?nombre=%20").status_code, 200)
        self.assertNotIn("LOCATE", conn.cursor.return_value.execute.call_args.args[0])
        with patch("db.connection.conectar_bd", return_value=None):
            self.assertEqual(self.client.get("/api/productos?nombre=mouse").status_code, 503)

    def test_catalogo_vacio(self):
        conn = MagicMock()
        conn.cursor.return_value.fetchall.return_value = []
        with patch("db.connection.conectar_bd", return_value=conn):
            response = self.client.get("/api/productos")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"productos": []})

    def test_sin_conexion_api_503_escritorio_lista_vacia(self):
        with patch("db.connection.conectar_bd", return_value=None):
            self.assertEqual(obtener_productos_activos_ordenados(), [])
            response = self.client.get("/api/productos")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {"error": "No se pudieron consultar los productos."})

    def test_error_sql_cierra_recursos_y_devuelve_503(self):
        from mysql.connector import Error
        conn = MagicMock()
        conn.cursor.return_value.execute.side_effect = Error("detalle privado")
        with patch("db.connection.conectar_bd", return_value=conn):
            response = self.client.get("/api/productos")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("detalle privado", response.get_data(as_text=True))
        conn.cursor.return_value.close.assert_called_once()
        conn.close.assert_called_once()

    def test_post_sin_sesion(self):
        self.assertEqual(self.client.post("/api/productos").status_code, 401)


class ProductoIndividualTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()
        self.conn = MagicMock()
        self.producto = dict(id_producto=1, descripcion="Mouse", marca="Tecno",
                             precio_venta=Decimal("1500.50"), stock=3,
                             activo=1, precio_compra=Decimal("1000"))

    def consultar(self, producto, ruta="/api/productos/1"):
        self.conn.cursor.return_value.fetchone.return_value = producto
        with patch("db.dao.conectar_bd", return_value=self.conn):
            return self.client.get(ruta)

    def test_existente_y_consulta_parametrizada(self):
        response = self.consultar(self.producto)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"producto": dict(
            id_producto=1, descripcion="Mouse", marca="Tecno",
            precio_venta="1500.50", stock=3)})
        self.assertEqual(self.conn.cursor.return_value.execute.call_args.args[1], (1,))
        self.conn.cursor.return_value.close.assert_called_once()
        self.conn.close.assert_called_once()

    def test_inexistente(self):
        response = self.consultar(None)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Producto no encontrado."})

    def test_inactivo(self):
        self.producto["activo"] = 0
        self.assertEqual(self.consultar(self.producto).status_code, 404)

    def test_id_cero_no_consulta_bd(self):
        self.assertEqual(self.consultar(None, "/api/productos/0").status_code, 404)
        self.conn.cursor.assert_not_called()

    def test_sin_conexion(self):
        with patch("db.dao.conectar_bd", return_value=None):
            response = self.client.get("/api/productos/1")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {"error": "No se pudo consultar el producto."})

    def test_error_sql_cierra_recursos(self):
        from mysql.connector import Error
        self.conn.cursor.return_value.execute.side_effect = Error("detalle privado")
        response = self.consultar(None)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("detalle privado", response.get_data(as_text=True))
        self.conn.cursor.return_value.close.assert_called_once()
        self.conn.close.assert_called_once()

    def test_id_no_numerico(self):
        self.assertEqual(self.client.get("/api/productos/abc").status_code, 404)


class AltaProductoTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()
        with self.client.session_transaction() as sesion:
            sesion["username"] = "AdminPepe"
        permisos = patch("api.consultar_rol_api", return_value="administrador")
        permisos.start()
        self.addCleanup(permisos.stop)
        self.datos = dict(descripcion="Mouse prueba", marca="Tecno", precio_compra="100.00",
                          precio_venta="150.00", id_categoria=5)
        self.conn = MagicMock()
        self.conn.cursor.return_value.lastrowid = 90
        self.conn.cursor.return_value.rowcount = 1

    def enviar(self):
        with patch("db.connection.conectar_bd", return_value=self.conn):
            return self.client.post("/api/productos", json=self.datos)

    def test_alta_transaccion_y_location(self):
        r = self.enviar()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json["id_producto"], 90)
        self.assertEqual(r.headers["Location"], "/api/productos/90")
        self.conn.commit.assert_called_once()
        self.conn.rollback.assert_not_called()
        cursor = self.conn.cursor.return_value
        sql, parametros = cursor.execute.call_args.args
        self.assertIn("0, 1", sql)
        self.assertEqual(parametros, ("Mouse prueba", "Tecno", Decimal("100.00"), Decimal("150.00"), 5))
        cursor.close.assert_called_once()
        self.conn.close.assert_called_once()

    def test_validaciones_no_escriben(self):
        casos = [("descripcion", " "), ("marca", "x" * 51), ("precio_venta", "50"),
                 ("precio_compra", "NaN"), ("precio_venta", "Infinity"),
                 ("precio_compra", None), ("precio_compra", True),
                 ("precio_compra", []), ("precio_venta", "150.001"),
                 ("precio_venta", "100000000"), ("precio_compra", "0"),
                 ("id_categoria", 1.5), ("id_categoria", 0), ("id_categoria", True)]
        for campo, valor in casos:
            with self.subTest(campo=campo, valor=valor):
                datos = dict(self.datos, **{campo: valor})
                with patch("logic.inventario.insertar_producto") as insertar:
                    r = self.client.post("/api/productos", json=datos)
                self.assertEqual(r.status_code, 400)
                insertar.assert_not_called()

    def test_json_invalido_y_campos(self):
        for cuerpo in ([], None, {}, dict(self.datos, stock=10)):
            with self.subTest(cuerpo=cuerpo):
                r = self.client.post("/api/productos", json=cuerpo, content_type="application/json")
                self.assertEqual(r.status_code, 400)
        r = self.client.post("/api/productos", data="{", content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_categoria_inexistente_rollback(self):
        from mysql.connector import IntegrityError
        self.conn.cursor.return_value.execute.side_effect = IntegrityError("privado", errno=1452)
        r = self.enviar()
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json, {"error": "La categoría indicada no existe."})
        self.conn.rollback.assert_called_once()
        self.conn.commit.assert_not_called()
        self.conn.close.assert_called_once()

    def test_fallo_sql_rollback(self):
        from mysql.connector import Error
        self.conn.cursor.return_value.execute.side_effect = Error("privado")
        r = self.enviar()
        self.assertEqual(r.status_code, 503)
        self.assertNotIn("privado", r.get_data(as_text=True))
        self.conn.rollback.assert_called_once()
        self.conn.cursor.return_value.close.assert_called_once()
        self.conn.close.assert_called_once()

    def test_sin_conexion(self):
        with patch("db.connection.conectar_bd", return_value=None):
            r = self.client.post("/api/productos", json=self.datos)
        self.assertEqual(r.status_code, 503)

    def test_compatibilidad_escritorio(self):
        from logic.inventario import gestionar_alta_producto
        with patch("db.connection.conectar_bd", return_value=self.conn):
            exito, mensaje = gestionar_alta_producto("Mouse", "Tecno", "100", "150", "5")
        self.assertTrue(exito)
        self.assertIn("Stock inicial: 0", mensaje)
        self.assertEqual(gestionar_alta_producto("Mouse", "Tecno", "150", "100", "5")[0], False)


class LoginTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.usuario = dict(id_usuario=1, nombre="Admin", apellido="Pepe", clave="clave", activo=1, rol="Admin")

    def login(self, clave="clave"):
        with patch("logic.auth.obtener_usuario_por_username", return_value=self.usuario):
            return self.client.post("/api/login", json=dict(username="AdminPepe", clave=clave))

    def test_login_no_modifica_global_y_no_expone_clave(self):
        from logic import auth
        anterior = auth.USUARIO_ID
        r = self.login()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["usuario"]["rol"], "administrador")
        self.assertNotIn("clave", r.json["usuario"])
        self.assertEqual(auth.USUARIO_ID, anterior)
        self.assertIn("HttpOnly", r.headers["Set-Cookie"])

    def test_credenciales_y_usuario_inactivo(self):
        self.assertEqual(self.login("incorrecta").status_code, 401)
        self.usuario["activo"] = 0
        self.assertEqual(self.login().status_code, 401)
        self.usuario = None
        self.assertEqual(self.login().status_code, 401)

    def test_entrada_invalida(self):
        for datos in (None, [], {}, dict(username=1, clave="clave")):
            self.assertEqual(self.client.post("/api/login", json=datos, content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post("/api/login").status_code, 415)

    def test_fallo_bd(self):
        with patch("logic.auth.obtener_usuario_por_username", side_effect=ConnectionError):
            self.assertEqual(self.client.post("/api/login", json=dict(username="AdminPepe", clave="clave")).status_code, 503)

    def test_roles_y_baja_revalidada_sin_escritura(self):
        self.login()
        for rol, estado in (("vendedor", 403), ("gerente", 403), (None, 401)):
            with self.subTest(rol=rol):
                with patch("api.consultar_rol_api", return_value=rol), patch("api.gestionar_alta_producto") as alta:
                    self.assertEqual(self.client.post("/api/productos", json={}).status_code, estado)
                    alta.assert_not_called()
        self.assertEqual(self.client.post("/api/productos", json={}).status_code, 401)

    def test_depositero_autorizado(self):
        self.login()
        datos=dict(descripcion="Mouse", marca="Tecno", precio_compra="10", precio_venta="20", id_categoria=5)
        with patch("api.consultar_rol_api", return_value="depositero"), patch("api.gestionar_alta_producto", return_value=90):
            self.assertEqual(self.client.post("/api/productos", json=datos).status_code, 201)

    def test_logout_y_clientes_independientes(self):
        self.login()
        otro = self.app.test_client()
        self.assertEqual(otro.post("/api/productos", json={}).status_code, 401)
        self.assertEqual(self.client.post("/api/logout").status_code, 200)
        self.assertEqual(self.client.post("/api/productos", json={}).status_code, 401)

    def test_cookie_manipulada(self):
        self.client.set_cookie("session", "firma-invalida")
        self.assertEqual(self.client.post("/api/productos", json={}).status_code, 401)


class CategoriasTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()
        self.conn = MagicMock()

    def test_listado_publico_solo_lectura(self):
        self.conn.cursor.return_value.fetchall.return_value = [
            dict(id_categoria=5, categoria="Periféricos", interno="privado")]
        with patch("db.connection.conectar_bd", return_value=self.conn):
            r = self.client.get("/api/categorias")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json, {"categorias": [dict(id_categoria=5, categoria="Periféricos")]})
        self.conn.cursor.return_value.execute.assert_called_once_with(
            "SELECT id_categoria, categoria FROM Categoria ORDER BY categoria")
        self.conn.commit.assert_not_called()
        self.conn.cursor.return_value.close.assert_called_once()
        self.conn.close.assert_called_once()
        self.assertEqual(self.client.post("/api/categorias", json={}).status_code, 405)

    def test_vacio(self):
        self.conn.cursor.return_value.fetchall.return_value = []
        with patch("db.connection.conectar_bd", return_value=self.conn):
            self.assertEqual(self.client.get("/api/categorias").json, {"categorias": []})

    def test_sin_conexion_compatibilidad_escritorio(self):
        from db.dao import obtener_categorias
        with patch("db.connection.conectar_bd", return_value=None):
            self.assertEqual(obtener_categorias(), [])
            r = self.client.get("/api/categorias")
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json, {"error": "No se pudieron consultar las categorías."})

    def test_error_sql_y_creacion_cursor_cierra_recursos(self):
        from mysql.connector import Error
        for fallo_cursor in (False, True):
            with self.subTest(fallo_cursor=fallo_cursor):
                conn = MagicMock()
                if fallo_cursor:
                    conn.cursor.side_effect = Error("detalle privado")
                else:
                    conn.cursor.return_value.execute.side_effect = Error("detalle privado")
                with patch("db.connection.conectar_bd", return_value=conn):
                    r = self.client.get("/api/categorias")
                self.assertEqual(r.status_code, 503)
                self.assertNotIn("detalle privado", r.get_data(as_text=True))
                conn.close.assert_called_once()
                if not fallo_cursor:
                    conn.cursor.return_value.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
