import pandas as pd


def create_features(df):
    """
    Crea nuevas variables (features) para el modelo de Machine Learning
    """

    print("\nIniciando feature engineering...")

    # ==============================
    # FEATURES TEMPORALES
    # ==============================

    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["dia"] = df["fecha"].dt.day
    df["dia_semana_num"] = df["fecha"].dt.weekday

    # fin de semana
    df["es_fin_semana"] = df["dia_semana_num"].isin([5, 6]).astype(int)

    # ==============================
    # FEATURES DE INVENTARIO
    # ==============================

    df["stock_vendido"] = df["stock_inicial"] - df["stock_final"]

    # ratio de venta vs stock
    df["ratio_venta_stock"] = df["cantidad_vendida"] / (df["stock_inicial"] + 1)

    # ==============================
    # FEATURES DE PROMOCIONES
    # ==============================

    df["tiene_promocion"] = df["promocion"].apply(
        lambda x: 0 if x == "Sin promoción" else 1
    )

    # descuento en porcentaje real
    df["descuento_real"] = df["precio_unitario_cop"] - df["precio_final_cop"]

    # ==============================
    # FEATURES FINANCIERAS
    # ==============================

    df["margen_por_producto"] = df["margen_ganancia"] / (df["cantidad_vendida"] + 1)

    print("Feature engineering completado")

    return df


def save_features(df, config):
    """
    Guarda el dataset con features creadas
    """

    output_path = config["paths"]["features_data"]

    df.to_csv(output_path, index=False)

    print(f"\nDataset con features guardado en: {output_path}")