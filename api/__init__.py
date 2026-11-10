"""Entrada HTTP independiente de la interfaz Tkinter."""
import os
import secrets
from datetime import timedelta

from flask import Flask, jsonify, request, url_for, session, render_template, send_from_directory
from logic.auth import autenticar_usuario, consultar_rol_api
from mysql.connector import Error, IntegrityError

from logic.inventario import procesar_consulta_stock, consultar_producto_activo, gestionar_alta_producto, consultar_categorias


def create_app():
    produccion = bool(os.environ.get("RENDER")) or os.environ.get("TECNOSTORE_PRODUCTION") == "1"
    if produccion:
        if not os.environ.get("FLASK_SECRET_KEY"):
            raise RuntimeError("Configurar FLASK_SECRET_KEY antes de iniciar en producción.")
        if (any(not os.environ.get(k) for k in ("DB_USER", "DB_PASSWORD", "DB_NAME"))
                or not (os.environ.get("DB_HOST") or os.environ.get("DB_UNIX_SOCKET"))):
            raise RuntimeError("Configurar las variables DB antes de iniciar en producción.")
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=produccion or os.environ.get("COOKIE_SECURE") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
        SESSION_REFRESH_EACH_REQUEST=False,
    )

    @app.get("/")
    def demo():
        return render_template("productos.html")

    @app.get("/assets/img/tecno_store_logo.png")
    def logo():
        return send_from_directory(os.path.join(app.root_path, "..", "assets", "img"),
                                   "tecno_store_logo.png")

    @app.post("/api/login")
    def login():
        session.clear()
        if not request.is_json:
            return jsonify(error="Se requiere Content-Type application/json."), 415
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict) or set(datos) != {"username", "clave"}:
            return jsonify(error="Enviá username y clave en un objeto JSON."), 400
        if any(not isinstance(datos[c], str) or not datos[c].strip() for c in ("username", "clave")):
            return jsonify(error="Username y clave son obligatorios y deben ser texto."), 400
        try:
            resultado = autenticar_usuario(datos["username"], datos["clave"], sesion_escritorio=False)
        except (ConnectionError, Error):
            app.logger.exception("No se pudo iniciar sesión")
            return jsonify(error="No se pudo iniciar sesión."), 503
        if "error" in resultado:
            return jsonify(error="Credenciales inválidas o usuario inhabilitado."), 401
        session["username"] = datos["username"].strip().replace(" ", "")
        session.permanent = True
        return jsonify(usuario={c: resultado[c] for c in ("nombre", "rol", "username")})

    @app.post("/api/logout")
    def logout():
        session.clear()
        return jsonify(mensaje="Sesión cerrada.")


    @app.get("/api/categorias")
    def listar_categorias():
        try:
            categorias = consultar_categorias()
        except (ConnectionError, Error):
            app.logger.exception("No se pudieron consultar las categorías")
            return jsonify(error="No se pudieron consultar las categorías."), 503
        return jsonify(categorias=[{campo: c[campo] for campo in
                                   ("id_categoria", "categoria")} for c in categorias])

    @app.get("/api/productos")
    def listar_productos():
        try:
            productos = procesar_consulta_stock(propagar_errores=True, nombre=request.args.get("nombre", "").strip())
        except (ConnectionError, Error):
            app.logger.exception("No se pudo consultar el catálogo")
            return jsonify(error="No se pudieron consultar los productos."), 503

        # Contrato público: OJO... no exponer precio de compra ni columnas internas.
        campos = ("id_producto", "descripcion", "marca", "precio_venta", "stock")
        return jsonify(productos=[{campo: p[campo] for campo in campos} for p in productos])

    @app.get("/api/productos/<int:id_producto>")
    def obtener_producto(id_producto):
        try:
            producto = consultar_producto_activo(id_producto)
        except (ConnectionError, Error):
            app.logger.exception("No se pudo consultar el producto")
            return jsonify(error="No se pudo consultar el producto."), 503
        if producto is None:
            return jsonify(error="Producto no encontrado."), 404
        campos = ("id_producto", "descripcion", "marca", "precio_venta", "stock")
        return jsonify(producto={campo: producto[campo] for campo in campos})

    @app.post("/api/productos")
    def crear_producto():
        if "username" not in session:
            return jsonify(error="Iniciá sesión para registrar productos."), 401
        try:
            rol = consultar_rol_api(session["username"])
        except (ConnectionError, Error):
            app.logger.exception("No se pudieron verificar los permisos")
            return jsonify(error="No se pudieron verificar los permisos."), 503
        if rol is None:
            session.clear()
            return jsonify(error="La sesión ya no es válida."), 401
        if rol not in {"administrador", "depositero"}:
            return jsonify(error="No tenés permiso para registrar productos."), 403
        if not request.is_json:
            return jsonify(error="Se requiere Content-Type application/json."), 415
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict):
            return jsonify(error="El cuerpo debe ser un objeto JSON válido."), 400
        campos = {"descripcion", "marca", "precio_compra", "precio_venta", "id_categoria"}
        if set(datos) != campos:
            return jsonify(error="Enviá únicamente descripcion, marca, precio_compra, precio_venta e id_categoria."), 400
        try:
            id_producto = gestionar_alta_producto(
                datos["descripcion"], datos["marca"], datos["precio_compra"],
                datos["precio_venta"], datos["id_categoria"], retornar_id=True)
        except ValueError as error:
            return jsonify(error=str(error)), 400
        except IntegrityError as error:
            if error.errno == 1452:
                return jsonify(error="La categoría indicada no existe."), 400
            app.logger.exception("Conflicto al registrar el producto")
            return jsonify(error="El producto entra en conflicto con los datos existentes."), 409
        except (ConnectionError, Error):
            app.logger.exception("No se pudo registrar el producto")
            return jsonify(error="No se pudo registrar el producto."), 503
        respuesta = jsonify(id_producto=id_producto, mensaje="Producto registrado. Stock inicial: 0.")
        respuesta.status_code = 201
        respuesta.headers["Location"] = url_for("obtener_producto", id_producto=id_producto)
        return respuesta

    return app
