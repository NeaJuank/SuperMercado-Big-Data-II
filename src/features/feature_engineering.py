import pandas as pd


def create_features(df):
    """
    Crea nuevas variables (features) para el modelo de Machine Learning
    """
    print("\nIniciando feature engineering...")

    df = df.copy()

    # Fecha
    if "fecha_venta" in df.columns:
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce")
    elif "fecha" in df.columns:
        df["fecha_venta"] = pd.to_datetime(df["fecha"], errors="coerce")
    else:
        df["fecha_venta"] = pd.NaT

    df["anio"] = df["fecha_venta"].dt.year
    df["mes"] = df["fecha_venta"].dt.month
    df["dia"] = df["fecha_venta"].dt.day
    df["dia_semana"] = df["fecha_venta"].dt.weekday
    df["es_fin_semana"] = df["dia_semana"].isin([5, 6]).astype(int)
    df["trimestre"] = df["fecha_venta"].dt.quarter

    if "stock_inicial" in df.columns and "stock_final" in df.columns:
        df["stock_vendido"] = df["stock_inicial"] - df["stock_final"]
    else:
        df["stock_vendido"] = 0

    if "stock_inicial" in df.columns:
        df["ratio_venta_stock"] = df["cantidad_vendida"] / df["stock_inicial"].replace(0, 1)
    elif "stock_disponible" in df.columns:
        df["ratio_venta_stock"] = df["cantidad_vendida"] / df["stock_disponible"].replace(0, 1)
    else:
        df["ratio_venta_stock"] = 0

    if "promocion" in df.columns:
        df["promocion"] = df["promocion"].astype(str).str.strip()
        df["tiene_promocion"] = df["promocion"].apply(lambda x: 0 if x.lower() == "sin promoción" else 1)
    else:
        df["tiene_promocion"] = 0

    if "precio_unitario_cop" in df.columns and "precio_venta" in df.columns:
        df["descuento_real"] = df["precio_unitario_cop"] - df["precio_venta"]
    else:
        df["descuento_real"] = 0

    if "margen_ganancia" in df.columns:
        df["margen_por_producto"] = df["margen_ganancia"] / df["cantidad_vendida"].replace(0, 1)
    else:
        df["margen_por_producto"] = 0

    df["riesgo_vencimiento"] = df.get("dias_hasta_vencimiento", 999).apply(lambda x: 1 if pd.notna(x) and x <= 7 else 0)

    print("Feature engineering completado")

    return df


def save_features(df, config):
    """
    Guarda el dataset con features creadas
    """

    output_path = config["paths"]["features_data"]

    df.to_csv(output_path, index=False)

    print(f"\nDataset con features guardado en: {output_path}")