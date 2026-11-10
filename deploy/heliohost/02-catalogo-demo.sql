-- Catálogo ficticio público; no contiene usuarios ni contraseñas.
SET NAMES utf8mb4;
START TRANSACTION;
INSERT INTO Rol (id_rol, rol) VALUES (1, 'Admin'), (2, 'Gerente'), (3, 'Vendedor'), (4, 'Depositero');

INSERT INTO Categoria (id_categoria, categoria) VALUES (1, 'Almacenamiento'), (2, 'Procesadores'), (3, 'Memorias'), (4, 'Placas de Video'), (5, 'Periféricos');

INSERT INTO FormaPago (id_forma_pago, forma_pago) VALUES (1, 'Efectivo'), (2, 'Tarjeta de Débito'), (3, 'Tarjeta de Crédito'), (4, 'Transferencia Bancaria');

INSERT INTO Producto (id_producto, id_categoria, descripcion, marca, precio_compra, precio_venta, stock, activo) VALUES 
(1, 1, 'Disco Sólido SSD 480GB A400', 'Kingston', 25000.00, 38000.00, 80, 1),
(2, 1, 'Disco Sólido SSD 1TB NVME M.2', 'Kingston', 45000.00, 69000.00, 70, 1),
(3, 1, 'Disco Rígido Externo 2TB USB 3.0', 'Seagate', 52000.00, 78000.00, 50, 1),
(4, 1, 'Disco Sólido SSD 2TB NVME Kingston', 'Kingston', 85000.00, 125000.00, 40, 1),
(5, 1, 'Disco Rígido Interno 1TB Barracuda', 'Seagate', 35000.00, 53000.00, 65, 1),
(6, 2, 'Procesador Core i5 12400F LGA1700', 'Intel', 120000.00, 175000.00, 50, 1),
(7, 2, 'Procesador Ryzen 5 5600X AM4', 'AMD', 115000.00, 169000.00, 55, 1),
(8, 2, 'Procesador Ryzen 7 5700X AM4', 'AMD', 170000.00, 245000.00, 40, 1),
(9, 2, 'Procesador Core i3 12100F', 'Intel', 80000.00, 115000.00, 60, 1),
(10, 2, 'Procesador Core i9 14900K', 'Intel', 490000.00, 685000.00, 35, 1),
(11, 3, 'Memoria RAM 8GB DDR4 3200MHz Vengeance', 'Corsair', 18000.00, 28000.00, 100, 1),
(12, 3, 'Memoria RAM 16GB DDR5 5200MHz Dominator', 'Corsair', 38000.00, 59000.00, 80, 1),
(13, 3, 'Memoria RAM Fury 8GB DDR4 Beast', 'Kingston', 17500.00, 26500.00, 95, 1),
(14, 3, 'Memoria RAM Fury 16GB DDR4 Beast', 'Kingston', 32000.00, 48000.00, 85, 1),
(15, 3, 'Memoria RAM 32GB DDR5 Corsair Kit', 'Corsair', 75000.00, 110000.00, 45, 1),
(16, 3, 'Memoria RAM Sodimm 8GB DDR4 Notebook', 'Kingston', 19000.00, 29000.00, 70, 1),
(17, 4, 'Placa de Video RTX 4060 Ti 8GB Dual', 'ASUS', 350000.00, 499000.00, 40, 1),
(18, 4, 'Placa de Video GTX 1650 4GB Phoenix', 'ASUS', 110000.00, 165000.00, 45, 1),
(19, 4, 'Placa de Video RX 7600 XT 16GB', 'ASUS', 320000.00, 460000.00, 35, 1),
(20, 4, 'Placa de Video RX 6600 V2 8GB', 'ASUS', 210000.00, 299000.00, 38, 1),
(21, 4, 'Placa de Video RTX 3050 6GB', 'ASUS', 160000.00, 235000.00, 42, 1),
(22, 5, 'Mouse Óptico Inalámbrico G305', 'Logitech', 22000.00, 34000.00, 100, 1),
(23, 5, 'Auriculares Gamer G435 Wireless', 'Logitech', 55000.00, 85000.00, 65, 1),
(24, 5, 'Mouse Gamer Ergónomico G502 Hero', 'Logitech', 42000.00, 62000.00, 75, 1),
(25, 5, 'Teclado Mecánico Pro X Tournament', 'Logitech', 80000.00, 120000.00, 50, 1),
(26, 5, 'Cámara Web HD C920 Pro Stream', 'Logitech', 62000.00, 93000.00, 55, 1),
(27, 1, 'Disco Sólido SSD 240GB Sata3', 'Kingston', 15000.00, 23000.00, 50, 1),
(28, 2, 'Procesador Core i7 13700K Boxer', 'Intel', 280000.00, 399000.00, 50, 1),
(29, 4, 'Placa de Video RTX 4070 Super 12GB', 'ASUS', 590000.00, 820000.00, 50, 1),
(30, 5, 'Teclado Mecánico G413 Carbon RGB', 'Logitech', 45000.00, 68000.00, 50, 1);
COMMIT;
