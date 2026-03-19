from src.data.load_data import load_config
from src.etl.etl_pipeline import run_etl
from src.features.feature_engineering import create_features
from src.models.train_model import train_model
from src.models.predict_model import load_model, predict_demand, predict_future
from src.reports.generate_kpis import calculate_kpis
from src.reports.generate_report import save_reports


def main():
    print("\n==============================")
    print("SISTEMA ANALÍTICO Y PREDICCIÓN DEMANDA")
    print("==============================\n")

    config = load_config()

    df_clean, df_rejects = run_etl(config)

    df_features = create_features(df_clean)
    df_features.to_csv(config["paths"]["features_data"], index=False)

    model = train_model(df_features, config)
    loaded_model = load_model()

    historical_pred = predict_demand(loaded_model, df_features, config)
    future_pred = predict_future(loaded_model, df_features, config)

    kpis = calculate_kpis(df_features, config)
    save_reports(kpis, historical_pred, future_pred, config)

    print("\nPipeline completado correctamente. Revisa los reportes en:")
    print(f"- {config['reports']['reports_path']}")
    print(f"- {config['warehouse']['db_path']}")


if __name__ == "__main__":
    main()