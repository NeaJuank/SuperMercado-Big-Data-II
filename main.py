from src.data.load_data import load_config, load_dataset
from src.data.clean_data import clean_data
from src.features.feature_engineering import create_features
from src.models.train_model import train_model
from src.models.predict_model import load_model, predict_demand
from src.kpis.inventory_rotation import calculate_inventory_rotation
from src.kpis.expired_losses import calculate_total_expired_losses
from src.kpis.promotion_impact import promotion_sales_comparison


def main():

    print("\n==============================")
    print("SISTEMA DE PREDICCION DEMANDA")
    print("==============================\n")

    # -------------------------
    # 1 Cargar configuración
    # -------------------------

    config = load_config()

    # -------------------------
    # 2 Cargar dataset
    # -------------------------

    df = load_dataset(config)

    # -------------------------
    # 3 Limpieza de datos
    # -------------------------

    df_clean = clean_data(df)

    # -------------------------
    # 4 Feature Engineering
    # -------------------------

    df_features = create_features(df_clean)

    # -------------------------
    # 5 Entrenamiento modelo
    # -------------------------

    model = train_model(df_features, config)
    # -------------------------
    # 6 Predicciones
    # -------------------------

    model = load_model()

    predictions = predict_demand(model, df_features)

    print("\nPrimeras predicciones:")
    print(predictions[:10])

    # -------------------------
    # 7 KPIs
    # -------------------------

    print("\nCALCULO DE KPIs\n")

    calculate_inventory_rotation(df_clean)

    calculate_total_expired_losses(df_clean)

    promotion_sales_comparison(df_clean)

    print("\nPipeline ejecutado correctamente\n")


if __name__ == "__main__":
    main()