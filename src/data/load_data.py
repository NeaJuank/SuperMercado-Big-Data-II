import pandas as pd
import yaml
import os


def load_config(config_path="config.yaml"):
    """
    Carga el archivo de configuración YAML
    """

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        print("Configuración cargada correctamente")
        return config

    except Exception as e:
        print("Error cargando config.yaml:", e)
        return None


def load_dataset(config):
    """
    Carga el dataset definido en config.yaml
    """

    try:
        dataset_path = config["paths"]["raw_data"]

        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"No se encontró el dataset en: {dataset_path}")

        df = pd.read_csv(dataset_path)

        print("Dataset cargado correctamente")
        print("Número de filas:", df.shape[0])
        print("Número de columnas:", df.shape[1])

        return df

    except Exception as e:
        print("Error cargando dataset:", e)
        return None


def dataset_info(df):
    """
    Muestra información básica del dataset
    """

    print("\nColumnas del dataset:")
    print(df.columns)

    print("\nTipos de datos:")
    print(df.dtypes)

    print("\nPrimeras 5 filas:")
    print(df.head())