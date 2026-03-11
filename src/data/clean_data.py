import pandas as pd


def clean_data(df):
    """
    Realiza la limpieza básica del dataset
    """

    print("\nIniciando limpieza de datos...")

    # eliminar duplicados
    df = df.drop_duplicates()

    # convertir columna fecha a datetime
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"])

    # convertir descuento a porcentaje numérico
    if "descuento_pct" in df.columns:
        df["descuento_pct"] = df["descuento_pct"].astype(float)

    # verificar valores nulos
    null_values = df.isnull().sum()

    if null_values.sum() > 0:
        print("\nValores nulos encontrados:")
        print(null_values)

        # eliminar filas con valores nulos
        df = df.dropna()

    print("Limpieza completada")
    print("Filas después de limpieza:", df.shape[0])

    return df


def save_clean_data(df, config):
    """
    Guarda el dataset limpio
    """

    output_path = config["paths"]["processed_data"]

    df.to_csv(output_path, index=False)

    print(f"\nDataset limpio guardado en: {output_path}")