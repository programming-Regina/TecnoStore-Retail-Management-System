"use strict";
const $ = (id) => document.getElementById(id);
const money = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" });
function message(id, text, type = "") {
  $(id).textContent = text;
  $(id).className = type;
}
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
  if (!response.ok) throw new Error(result.error || "No se pudo completar la operación.");
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
async function loadProducts(nombre = "") {
  nombre = nombre.trim();
  busy($("consulta"), true);
  render([]);
  message("catalogo-estado", "Consultando productos…");
  try {
    const result = await request(nombre ? `/api/productos?nombre=${encodeURIComponent(nombre)}` : "/api/productos");
    const products = result.productos;
    render(products);
    message("catalogo-estado", products.length ? (nombre ? `${products.length} coincidencias.` : `${products.length} productos activos.`) : (nombre ? "No se encontraron productos con ese nombre." : "No hay productos activos."));
    return true;
  } catch (error) {
    message("catalogo-estado", error.message, "error");
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
$("consulta").addEventListener("submit", (event) => {
  event.preventDefault();
  loadProducts($("producto-nombre").value);
});
$("ver-todos").addEventListener("click", () => {
  $("producto-nombre").value = "";
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
    // No repetir el alta si la actualización del catálogo falla.
    if (!$("ver-todos").disabled) {
      $("producto-nombre").value = "";
      await loadProducts();
    }
  } catch (error) { message("alta-estado", error.message, "error"); }
  finally { busy(form, false); }
});
loadProducts();

loadCategories();
