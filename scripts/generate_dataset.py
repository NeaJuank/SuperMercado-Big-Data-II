import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

n = 60000

productos = [
    ("LEC-000001", "Leche Entera 1L", "Lácteos", "Alquería", 3200, 4800),
    ("POL-000002", "Pollo Entero kg", "Carnes", "Mac Pollo", 9000, 14000),
    ("CAR-000003", "Carne Res kg", "Carnes", "Frigorífico", 18000, 32000),
    ("ARZ-000004", "Arroz 1kg", "Granos", "Diana", 3500, 5200),
    ("GAS-000005", "Gaseosa 1.5L", "Bebidas", "Coca-Cola", 4500, 7500),
    ("YOG-000006", "Yogurt 1L", "Lácteos", "Alpina", 5000, 9000),
    ("PAN-000007", "Pan Tajado", "Panadería", "Bimbo", 4500, 7000),
    ("CAF-000008", "Café Molido 500g", "Bebidas", "Juan Valdez", 12000, 22000),
    ("FOO-000009", "Aceite Vegetal 1L", "Despensa", "Premier", 9000, 14000),
    ("TOM-000010", "Tomate kg", "Verduras", "Genérico", 2000, 4500),
]

promociones = ["Sin promoción", "Descuento 10%", "Descuento 20%", "2x1", "Combo"]
ciudades = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga"]
sucursales = ["Centro", "Norte", "Sur", "Occidente", "Oriente"]

start = datetime(2024, 1, 1)
end = datetime(2025, 12, 31)
dias = (end - start).days

data = []

def random_dirty_row(base):
    bad = base.copy()
    error = random.choice([
        "fecha_invalida",
        "precio_invalido",
        "cantidad_invalida",
        "descuento_fuera_de_rango",
        "stock_negativo",
        "ciudad_invalida",
        "categoria_invalida",
    ])
    if error == "fecha_invalida":
        bad["fecha_venta"] = "32/13/2023"
    if error == "precio_invalido":
        bad["precio_venta"] = -100
    if error == "cantidad_invalida":
        bad["cantidad_vendida"] = 0
    if error == "descuento_fuera_de_rango":
        bad["descuento_pct"] = 150
    if error == "stock_negativo":
        bad["stock_disponible"] = -5
    if error == "ciudad_invalida":
        bad["ciudad"] = "CiudadX"
    if error == "categoria_invalida":
        bad["categoria"] = "DESCONOCIDA"
    return bad, error

for i in range(50000):
    prod = random.choice(productos)
    fecha = start + timedelta(days=random.randint(0, dias))
    precio = random.randint(prod[4], prod[5])
    cantidad = np.random.poisson(8) + 1
    promo = random.choice(promociones)
    descuento_pct = 0
    if promo == "Descuento 10%":
        descuento_pct = 10
    elif promo == "Descuento 20%":
        descuento_pct = 20
    elif promo == "2x1":
        descuento_pct = 50
    precio_venta = int(precio * (1 - (descuento_pct / 100)))
    stock_inicial = random.randint(20, 120)
    stock_disponible = max(stock_inicial - cantidad, 0)
    ingreso = cantidad * precio_venta
    margen_ganancia = ingreso * random.uniform(0.12, 0.30)
    dias_hasta_vencimiento = random.randint(1, 60)
    perdida_vencimiento = 0 if random.random() > 0.02 else random.randint(1, 5) * precio_venta
    ciudad = random.choice(ciudades)
    sucursal = random.choice(sucursales)

    row = {
        "producto_id": prod[0],
        "producto": prod[1],
        "categoria": prod[2],
        "marca": prod[3],
        "fecha_venta": fecha.strftime("%Y-%m-%d"),
        "cantidad_vendida": cantidad,
        "precio_unitario_cop": precio,
        "precio_venta": precio_venta,
        "promocion": promo,
        "descuento_pct": descuento_pct,
        "dia_semana": fecha.strftime("%A"),
        "sucursal": sucursal,
        "ciudad": ciudad,
        "stock_inicial": stock_inicial,
        "stock_disponible": stock_disponible,
        "ingresos": ingreso,
        "margen_ganancia": margen_ganancia,
        "dias_hasta_vencimiento": dias_hasta_vencimiento,
        "perdida_vencimiento": perdida_vencimiento,
        "_es_sucio": False,
        "_error_tipo": ""
    }
    data.append(row)

for i in range(10000):
    base = random.choice(data)
    row = base.copy()
    row["_es_sucio"] = True
    row["_error_tipo"] = "registro_sucio"
    dirty, err = random_dirty_row(row)
    dirty["_es_sucio"] = True
    dirty["_error_tipo"] = err
    data.append(dirty)

random.shuffle(data)

df = pd.DataFrame(data)
df.to_csv("dataset_supermercado_colombia_60000.csv", index=False)
print("Dataset generado correctamente con 60,000 registros (incluyendo sucios)")
