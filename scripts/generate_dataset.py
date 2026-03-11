import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Número de registros
n = 50000

# Productos con rangos de precios en COP
productos = [
("Arroz 1kg","Granos","Diana",3500,5200),
("Leche Entera 1L","Lácteos","Alquería",3200,4800),
("Huevos Docena","Huevos","Kikes",9000,14000),
("Pan Tajado","Panadería","Bimbo",4500,7000),
("Aceite Vegetal 1L","Despensa","Premier",9000,14000),
("Azúcar 1kg","Despensa","Incauca",3200,5200),
("Café Molido 500g","Bebidas","Juan Valdez",12000,22000),
("Gaseosa 1.5L","Bebidas","Coca-Cola",4500,7500),
("Pollo Entero kg","Carnes","Mac Pollo",9000,14000),
("Carne Res kg","Carnes","Frigorífico",18000,32000),
("Banano kg","Frutas","Genérico",1800,3500),
("Manzana kg","Frutas","Genérico",4500,8500),
("Papa kg","Verduras","Genérico",1500,3500),
("Tomate kg","Verduras","Genérico",2000,4500),
("Queso Campesino 500g","Lácteos","Colanta",7000,12000),
("Yogurt 1L","Lácteos","Alpina",5000,9000),
("Chocolate Mesa","Despensa","Corona",3500,6500),
("Atún Lata","Enlatados","Van Camps",4500,7500),
("Galletas","Snacks","Noel",2500,5500),
("Jugo Hit 1L","Bebidas","Postobón",3500,6000)
]

promociones = [
"Sin promoción",
"Descuento 10%",
"Descuento 20%",
"2x1",
"Combo"
]

ciudades = [
"Bogotá",
"Medellín",
"Cali",
"Barranquilla",
"Bucaramanga"
]

sucursales = [
"Centro",
"Norte",
"Sur",
"Occidente",
"Oriente"
]

start = datetime(2024,1,1)
end = datetime(2025,12,31)
dias = (end-start).days

data = []

for i in range(n):

    producto = random.choice(productos)
    fecha = start + timedelta(days=random.randint(0,dias))

    precio = random.randint(producto[3],producto[4])
    cantidad = np.random.poisson(8)+1

    promo = random.choice(promociones)

    descuento = 0
    if promo == "Descuento 10%":
        descuento = 0.10
    elif promo == "Descuento 20%":
        descuento = 0.20
    elif promo == "2x1":
        descuento = 0.50

    precio_final = int(precio*(1-descuento))

    stock_inicial = random.randint(20,120)
    stock_final = max(stock_inicial - cantidad,0)

    ingreso = cantidad * precio_final

    margen = ingreso * random.uniform(0.12,0.30)

    perdida = 0
    if random.random() < 0.02:
        perdida = random.randint(1,5)*precio_final

    ciudad = random.choice(ciudades)
    sucursal = random.choice(sucursales)

    data.append([
        producto[0],
        producto[1],
        producto[2],
        fecha,
        cantidad,
        precio,
        precio_final,
        promo,
        descuento,
        fecha.strftime("%A"),
        sucursal,
        ciudad,
        stock_inicial,
        stock_final,
        ingreso,
        margen,
        perdida
    ])

columnas = [
"producto",
"categoria",
"marca",
"fecha",
"cantidad_vendida",
"precio_unitario_cop",
"precio_final_cop",
"promocion",
"descuento_pct",
"dia_semana",
"sucursal",
"ciudad",
"stock_inicial",
"stock_final",
"ingreso_total",
"margen_ganancia",
"perdida_vencimiento"
]

df = pd.DataFrame(data, columns=columnas)

df.to_csv("dataset_supermercado_colombia_50000.csv", index=False)

print("Dataset generado correctamente")
