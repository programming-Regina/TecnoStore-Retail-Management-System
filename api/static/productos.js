"use strict";
const $ = (id) => document.getElementById(id);
const money = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" });
function message(id, text, type = "") {
  $(id).textContent = text;
  $(id).className = type;
}
// fetch envía la petición HTTP. Si hay datos, los convertimos a JSON para el POST.
async function request(url, data) {
  let response;
  try {
    response = await fetch(url, data === undefined ? { credentials: "same-origin" } : {
      method: "POST", credentials: "same-origin",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify(data)
    });
  } catch {
    throw new Error("No se pudo conectar con el servidor. Verificá que Flask esté iniciado y volvé a intentar.");
  }
  let result;
  try { result = await response.json(); }
  catch { throw new Error("El servidor devolvió una respuesta inesperada. Volvé a intentar."); }
  // El estado HTTP indica si la operación tuvo éxito. El JSON aporta el detalle.
  if (!response.ok) {
    const error = new Error(result.error || "No se pudo completar la operación.");
    error.status = response.status;
    throw error;
  }
  return result;
}
function busy(form, value) {
  form.setAttribute("aria-busy", String(value));
  form.querySelectorAll("button").forEach((button) => { button.disabled = value; });
}
function render(products) {
  $("productos").replaceChildren();
  for (const product of products) {
    const row = document.createElement("tr");
    for (const value of [product.id_producto, product.descripcion, product.marca,
      money.format(Number(product.precio_venta)), product.stock]) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    }
    $("productos").append(row);
  }
}
async function loadProducts(text = "", mode = "nombre") {
  text = text.trim();
  const byId = mode === "id";
  if (byId && (!/^[0-9]+$/.test(text) || Number(text) < 1 || Number(text) > 2147483647)) {
    message("catalogo-estado", "Ingresá un ID entero entre 1 y 2147483647.", "error");
    return false;
  }
  busy($("consulta"), true);
  render([]);
  message("catalogo-estado", "Consultando productos…");
  try {
    const url = byId ? `/api/productos/${Number(text)}` :
      (text ? `/api/productos?nombre=${encodeURIComponent(text)}` : "/api/productos");
    const result = await request(url);
    const products = byId ? [result.producto] : result.productos;
    render(products);
    message("catalogo-estado", byId ? "Producto encontrado." : (products.length ? (text ? `${products.length} coincidencias.` : `${products.length} productos activos.`) : (text ? "No se encontraron productos con ese nombre." : "No hay productos activos.")));
    return true;
  } catch (error) {
    if (byId && error.status === 404) {
      message("catalogo-estado", "No se encontró un producto con ese ID.");
    } else {
      message("catalogo-estado", error.message, "error");
    }
    return false;
  } finally { busy($("consulta"), false); }
}
async function loadCategories() {
  const select = $("id_categoria");
  select.disabled = true;
  $("reintentar-categorias").hidden = true;
  select.replaceChildren(new Option("Cargando categorías…", ""));
  message("categoria-estado", "Consultando categorías…");
  try {
    const { categorias } = await request("/api/categorias");
    select.replaceChildren(new Option(categorias.length ? "Seleccioná una categoría" : "Sin categorías disponibles", ""));
    for (const category of categorias) {
      select.add(new Option(category.categoria, String(category.id_categoria)));
    }
    select.disabled = !categorias.length;
    message("categoria-estado", categorias.length ? "" : "No hay categorías disponibles para registrar productos.");
    $("reintentar-categorias").hidden = Boolean(categorias.length);
  } catch (error) {
    select.replaceChildren(new Option("Categorías no disponibles", ""));
    message("categoria-estado", error.message, "error");
    $("reintentar-categorias").hidden = false;
  }
}
$("reintentar-categorias").addEventListener("click", loadCategories);
function changeSearchMode() {
  const input = $("producto-busqueda");
  const byId = $("modo-id").checked;
  input.value = "";
  input.type = byId ? "number" : "search";
  input.required = byId;
  input.placeholder = byId ? "Ej. 14" : "Ej. mouse";
  for (const [attribute, value] of [["min", "1"], ["max", "2147483647"], ["step", "1"]]) {
    if (byId) input.setAttribute(attribute, value);
    else input.removeAttribute(attribute);
  }
  $("busqueda-etiqueta").textContent = byId ? "ID del producto" : "Nombre del producto";
  input.focus();
}
$("modo-nombre").addEventListener("change", changeSearchMode);
$("modo-id").addEventListener("change", changeSearchMode);
$("consulta").addEventListener("submit", (event) => {
  event.preventDefault();
  loadProducts($("producto-busqueda").value, $("modo-id").checked ? "id" : "nombre");
});
$("ver-todos").addEventListener("click", () => {
  $("producto-busqueda").value = "";
  loadProducts();
});
$("login").addEventListener("submit", async (event) => {
  event.preventDefault();
  busy(event.currentTarget, true);
  message("sesion-estado", "Iniciando sesión…");
  try {
    const result = await request("/api/login", { username: $("username").value, clave: $("clave").value });
    $("login").hidden = true;
    $("logout").hidden = false;
    // El rol orienta el mensaje de la pantalla. Flask verifica el permiso en cada alta.
    const allowed = ["administrador", "depositero"].includes(result.usuario.rol);
    message("sesion-estado", `${result.usuario.nombre} · ${result.usuario.rol}. ${allowed ? "Podés registrar productos." : "Tu rol no tiene permiso para registrar productos."}`, allowed ? "success" : "error");
  } catch (error) {
    message("sesion-estado", error.message, "error");
    $("login").hidden = false;
    $("logout").hidden = true;
  } finally {
    $("clave").value = "";
    busy($("login"), false);
  }
});
$("logout").addEventListener("click", async () => {
  $("logout").disabled = true;
  message("sesion-estado", "Cerrando sesión…");
  try {
    const result = await request("/api/logout", {});
    $("login").hidden = false;
    $("logout").hidden = true;
    message("sesion-estado", result.mensaje);
  } catch (error) { message("sesion-estado", error.message, "error"); }
  finally { $("logout").disabled = false; }
});
$("alta").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form));
  // La revisión en el formulario da una respuesta inmediata. El servidor valida los datos recibidos.
  if (!data.descripcion.trim() || !data.marca.trim()) {
    message("alta-estado", "Completá la descripción y la marca.", "error");
    return;
  }
  if (Number(data.precio_venta) <= Number(data.precio_compra)) {
    message("alta-estado", "El precio de venta debe superar al precio de compra.", "error");
    return;
  }
  if ($("id_categoria").disabled || !data.id_categoria) {
    message("alta-estado", "Seleccioná una categoría disponible antes de registrar el producto.", "error");
    return;
  }
  data.id_categoria = Number(data.id_categoria);
  busy(form, true);
  message("alta-estado", "Registrando producto…");
  try {
    const result = await request("/api/productos", data);
    form.reset();
    message("alta-estado", `${result.mensaje} ID asignado: ${result.id_producto}.`, "success");
    // El alta ya se confirmó. La consulta posterior solo actualiza el catálogo de la pantalla.
    if (!$("ver-todos").disabled) {
      $("producto-busqueda").value = "";
      await loadProducts();
    }
  } catch (error) { message("alta-estado", error.message, "error"); }
  finally { busy(form, false); }
});
loadProducts();

loadCategories();
