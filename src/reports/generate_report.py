import os
import pandas as pd


def save_reports(kpis, historical_preds, future_preds, config):
    print("\nGuardando reportes...")
    os.makedirs(config["reports"]["reports_path"], exist_ok=True)

    kpi_rows = []
    for name, values in kpis.items():
        kpi_rows.append({
            "kpi": name,
            "valor": values["valor"],
            "meta": values["meta"],
            "cumple": values["cumple"],
            "brecha": values["brecha"],
            "recomendacion": values["recomendacion"]
        })

    kpi_df = pd.DataFrame(kpi_rows)
    kpi_csv_path = config["reports"]["kpis_csv"]
    os.makedirs(os.path.dirname(kpi_csv_path), exist_ok=True)
    kpi_df.to_csv(kpi_csv_path, index=False)

    pred_history_path = os.path.join(config["reports"]["reports_path"], "predicciones_historicas.csv")
    historical_preds.to_csv(pred_history_path, index=False)

    pred_future_path = config["reports"]["predictions_csv"]
    os.makedirs(os.path.dirname(pred_future_path), exist_ok=True)
    future_preds.to_csv(pred_future_path, index=False)

    natural_path = config["reports"]["natural_report_path"]
    with open(natural_path, "w", encoding="utf-8") as f:
        f.write("Reporte de resultados - Sistema de Predicción de Demanda\n")
        f.write("===============================================\n\n")
        f.write(f"Registros procesados: {len(historical_preds)}\n")
        f.write("\nResumen de KPIs:\n")
        for name, values in kpis.items():
            status = "CUMPLE" if values["cumple"] else "NO CUMPLE"
            f.write(f"- {name}: {values['valor']:.4f} (Meta: {values['meta']:.2f}) -> {status}\n")
            f.write(f"  Recomendación: {values['recomendacion']}\n")

        f.write("\nPrimeras predicciones futuras:\n")
        for _, row in future_preds.head(5).iterrows():
            f.write(f"  {row['fecha_venta']} - {row['producto']} en {row['ciudad']}: {row['prediccion_demanda']:.2f} unidades\n")

    print(f"Reportes guardados en: {config['reports']['reports_path']}")
    print(f"Reporte natural guardado en: {config['reports']['natural_report_path']}")
