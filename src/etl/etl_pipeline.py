import os
import sqlite3
import json
from datetime import timedelta
import pandas as pd


def ensure_directories(config):
    paths = [
        os.path.dirname(config["paths"]["processed_data"]),
        os.path.dirname(config["paths"]["features_data"]),
        os.path.dirname(config["warehouse"]["db_path"]),
        os.path.dirname(config["reports"]["reports_path"]),
    ]
    for p in paths:
        if p and not os.path.exists(p):
            os.makedirs(p, exist_ok=True)


def extract(config):
    raw_path = config["paths"]["raw_data"]
    print(f"Extrayendo datos desde: {raw_path}")
    df = pd.read_csv(raw_path)
    print(f"Registros extraídos: {df.shape[0]}")
    return df


def _push_reject(rejects, row, reason):
    row_data = row.to_dict()
    row_data["razon_rechazo"] = reason
    rejects.append(row_data)


def transform(df, config):
    print("Transformando datos...")

    # 1) Duplicados exactos
    df = df.drop_duplicates().copy()

    # Columns normalization
    if "fecha_venta" not in df.columns and "fecha" in df.columns:
        df = df.rename(columns={"fecha": "fecha_venta"})

    if "precio_venta" not in df.columns and "precio_final_cop" in df.columns:
        df = df.rename(columns={"precio_final_cop": "precio_venta"})

    if "ingresos" not in df.columns and "ingreso_total" in df.columns:
        df = df.rename(columns={"ingreso_total": "ingresos"})

    # Ensure required helper fields
    if "stock_disponible" not in df.columns:
        if "stock_inicial" in df.columns and "stock_final" in df.columns:
            df["stock_disponible"] = df["stock_inicial"] - df["stock_final"]
        else:
            df["stock_disponible"] = 0

    if "producto_id" not in df.columns:
        df["producto_id"] = (df.get("producto", "") + df.get("categoria", "") + df.get("ciudad", "")).astype(str).str[:12]

    if "dias_hasta_vencimiento" not in df.columns:
        df["dias_hasta_vencimiento"] = 30

    if "_es_sucio" not in df.columns:
        df["_es_sucio"] = False
    if "_error_tipo" not in df.columns:
        df["_error_tipo"] = ""

    # Prepare final columns
    df["precio_venta"] = pd.to_numeric(df["precio_venta"], errors="coerce")
    df["cantidad_vendida"] = pd.to_numeric(df["cantidad_vendida"], errors="coerce")
    df["descuento_pct"] = pd.to_numeric(df["descuento_pct"], errors="coerce")
    df["stock_disponible"] = pd.to_numeric(df["stock_disponible"], errors="coerce")
    df["dias_hasta_vencimiento"] = pd.to_numeric(df["dias_hasta_vencimiento"], errors="coerce")

    # Parse dates
    df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce")

    # dirty records directly
    rejects = []
    clean_records = []

    valid_cities = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga"]
    category_map = {
        "Leche": "Lácteos",
        "Huevos": "Lácteos",
        "Yogurt": "Lácteos",
        "Pan": "Panadería",
        "Carne": "Carnes",
        "Pollo": "Carnes",
        "Gaseosa": "Bebidas",
        "Jugo": "Bebidas",
        "Arroz": "Granos",
        "Azúcar": "Despensa",
    }

    for _, row in df.iterrows():
        if row.get("_es_sucio", False):
            _push_reject(rejects, row, row.get("_error_tipo", "registro_sucio"))
            continue

        # Rule 3: producto_id not null
        if pd.isna(row["producto_id"]) or str(row["producto_id"]).strip() == "":
            _push_reject(rejects, row, "producto_id_nulo")
            continue

        # Rule 4: fecha parseable
        if pd.isna(row["fecha_venta"]):
            _push_reject(rejects, row, "fecha_invalida")
            continue

        # Rule 5: precio_venta > 0
        if pd.isna(row["precio_venta"]) or row["precio_venta"] <= 0:
            _push_reject(rejects, row, "precio_invalido")
            continue

        # Rule 6: cantidad_vendida >0
        if pd.isna(row["cantidad_vendida"]) or row["cantidad_vendida"] <= 0:
            _push_reject(rejects, row, "cantidad_invalida")
            continue

        # Rule 7: descuento_pct range [0,100]
        if pd.isna(row["descuento_pct"]) or row["descuento_pct"] < 0 or row["descuento_pct"] > 100:
            _push_reject(rejects, row, "descuento_fuera_de_rango")
            continue

        # Rule 8: stock_disponible >=0
        if pd.isna(row["stock_disponible"]) or row["stock_disponible"] < 0:
            _push_reject(rejects, row, "stock_negativo")
            continue

        # Rule 9: ciudad válida
        ciudad = str(row.get("ciudad", "")).strip()
        if ciudad not in valid_cities:
            _push_reject(rejects, row, "ciudad_invalida")
            continue

        # Rule 10: categoría válida o corrección
        categoria = str(row.get("categoria", "")).strip()
        corrected_categoria = categoria
        if categoria.upper() in ["NULL", "DESCONOCIDA", ""]:
            producto = str(row.get("producto", ""))
            for token, cat in category_map.items():
                if token.lower() in producto.lower():
                    corrected_categoria = cat
                    break
        if corrected_categoria == "":
            _push_reject(rejects, row, "categoria_invalida")
            continue

        # Recalculate ingresos
        ingresos_correcto = row["precio_venta"] * row["cantidad_vendida"]
        r = row.copy()
        r["categoria"] = corrected_categoria
        r["ingresos"] = ingresos_correcto

        # Create required computed columns
        r["tiene_promocion"] = 0 if str(r.get("promocion", "")).strip().lower() == "sin promoción" else 1
        if "dias_hasta_vencimiento" not in r or pd.isna(r["dias_hasta_vencimiento"]):
            r["dias_hasta_vencimiento"] = 30
        r["riesgo_vencimiento"] = 1 if r["dias_hasta_vencimiento"] <= 7 else 0
        r["ratio_venta_stock"] = r["cantidad_vendida"] / (r["stock_disponible"] if r["stock_disponible"] > 0 else 1)

        if pd.notna(r["fecha_venta"]):
            r["anio"] = r["fecha_venta"].year
            r["mes"] = r["fecha_venta"].month
            r["dia"] = r["fecha_venta"].day
            r["dia_semana"] = r["fecha_venta"].weekday()
            r["es_fin_semana"] = 1 if r["fecha_venta"].weekday() in [5, 6] else 0
            r["trimestre"] = (r["fecha_venta"].month - 1) // 3 + 1
        else:
            r["anio"] = r["mes"] = r["dia"] = 0
            r["dia_semana"] = 0
            r["es_fin_semana"] = 0
            r["trimestre"] = 0

        clean_records.append(r)

    df_clean = pd.DataFrame(clean_records)
    df_rejects = pd.DataFrame(rejects)

    print(f"Registros limpios: {df_clean.shape[0]}")
    print(f"Registros rechazados: {df_rejects.shape[0]}")

    return df_clean, df_rejects


def load_to_warehouse(df_clean, df_rejects, config):
    db_path = config["warehouse"]["db_path"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_producto (
        producto_key INTEGER PRIMARY KEY AUTOINCREMENT,
        producto TEXT UNIQUE,
        categoria TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_ciudad (
        ciudad_key INTEGER PRIMARY KEY AUTOINCREMENT,
        ciudad TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_tiempo (
        tiempo_key INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT UNIQUE,
        anio INTEGER,
        mes INTEGER,
        dia INTEGER,
        dia_semana INTEGER,
        es_fin_semana INTEGER,
        trimestre INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_ventas (
        venta_id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id TEXT,
        producto_key INTEGER,
        ciudad_key INTEGER,
        tiempo_key INTEGER,
        cantidad_vendida REAL,
        ingresos REAL,
        perdida_vencimiento REAL,
        ratio_venta_stock REAL,
        riesgo_vencimiento INTEGER,
        tiene_promocion INTEGER,
        FOREIGN KEY(producto_key) REFERENCES dim_producto(producto_key),
        FOREIGN KEY(ciudad_key) REFERENCES dim_ciudad(ciudad_key),
        FOREIGN KEY(tiempo_key) REFERENCES dim_tiempo(tiempo_key)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_rechazados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datos_raw TEXT,
        razon_rechazo TEXT,
        cargado_en TEXT
    )
    """)

    conn.commit()

    # Insert dimensions
    productos = df_clean[["producto", "categoria"]].drop_duplicates()
    for _, row in productos.iterrows():
        cursor.execute(
            "INSERT OR IGNORE INTO dim_producto (producto, categoria) VALUES (?, ?)",
            (row["producto"], row["categoria"])
        )

    ciudades = df_clean[["ciudad"]].drop_duplicates()
    for _, row in ciudades.iterrows():
        cursor.execute(
            "INSERT OR IGNORE INTO dim_ciudad (ciudad) VALUES (?)",
            (row["ciudad"],)
        )

    tiempos = df_clean[["fecha_venta", "anio", "mes", "dia", "dia_semana", "es_fin_semana", "trimestre"]].drop_duplicates()
    for _, row in tiempos.iterrows():
        cursor.execute(
            "INSERT OR IGNORE INTO dim_tiempo (fecha, anio, mes, dia, dia_semana, es_fin_semana, trimestre) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                row["fecha_venta"].strftime("%Y-%m-%d"),
                int(row["anio"]),
                int(row["mes"]),
                int(row["dia"]),
                int(row["dia_semana"]),
                int(row["es_fin_semana"]),
                int(row["trimestre"]),
            )
        )

    conn.commit()

    # Lookup maps
    producto_map = {row[0]: row[1] for row in cursor.execute("SELECT producto, producto_key FROM dim_producto")} 
    ciudad_map = {row[0]: row[1] for row in cursor.execute("SELECT ciudad, ciudad_key FROM dim_ciudad")} 
    tiempo_map = {row[0]: row[1] for row in cursor.execute("SELECT fecha, tiempo_key FROM dim_tiempo")} 

    # Insert facts
    for _, row in df_clean.iterrows():
        producto_key = producto_map.get(row["producto"])
        ciudad_key = ciudad_map.get(row["ciudad"])
        fecha_key = row["fecha_venta"].strftime("%Y-%m-%d")
        tiempo_key = tiempo_map.get(fecha_key)

        if not producto_key or not ciudad_key or not tiempo_key:
            continue

        cursor.execute(
            "INSERT INTO fact_ventas (producto_id, producto_key, ciudad_key, tiempo_key, cantidad_vendida, ingresos, perdida_vencimiento, ratio_venta_stock, riesgo_vencimiento, tiene_promocion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                row["producto_id"], producto_key, ciudad_key, tiempo_key,
                float(row.get("cantidad_vendida", 0)),
                float(row.get("ingresos", 0)),
                float(row.get("perdida_vencimiento", 0)),
                float(row.get("ratio_venta_stock", 0)),
                int(row.get("riesgo_vencimiento", 0)),
                int(row.get("tiene_promocion", 0)),
            )
        )

    for _, row in df_rejects.iterrows():
        cursor.execute(
            "INSERT INTO fact_rechazados (datos_raw, razon_rechazo, cargado_en) VALUES (?, ?, datetime('now'))",
            (json.dumps(row.drop(labels=["razon_rechazo"], errors="ignore")).replace("NaT", "null"), row.get("razon_rechazo", ""))
        )

    conn.commit()
    conn.close()
    print(f"Data warehouse cargado en: {db_path}")


def run_etl(config):
    ensure_directories(config)
    df = extract(config)
    df_clean, df_rejects = transform(df, config)

    df_clean.to_csv(config["paths"]["processed_data"], index=False)
    df_clean.to_csv(config["paths"]["features_data"], index=False)

    load_to_warehouse(df_clean, df_rejects, config)

    return df_clean, df_rejects
