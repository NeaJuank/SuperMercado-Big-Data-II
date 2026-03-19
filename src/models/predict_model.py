import os
import joblib
import pandas as pd


def load_model(model_path="models/demand_forecasting_model.pkl"):
    try:
        model = joblib.load(model_path)
        print("Modelo cargado correctamente")
        return model
    except Exception as e:
        print("Error cargando modelo:", e)
        return None


def _align_features(X, model_columns):
    for col in model_columns:
        if col not in X.columns:
            X[col] = 0
    for col in X.columns:
        if col not in model_columns:
            X = X.drop(columns=[col])
    X = X[model_columns]
    return X


def prepare_prediction_data(df, model_columns):
    df = df.copy()
    drop_cols = ["cantidad_vendida", "fecha_venta", "fecha", "producto_id", "producto", "categoria", "marca", "promocion", "dia_semana", "sucursal"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
    X = pd.get_dummies(X, drop_first=True)
    X = _align_features(X, model_columns)
    return X


def predict_demand(model, df, config=None):
    print("\nGenerando predicciones de demanda...")
    columns = joblib.load("models/model_columns.pkl")
    X = prepare_prediction_data(df, columns)
    predictions = model.predict(X)
    df["prediccion_demanda"] = predictions
    print("Predicciones generadas correctamente")
    return df


def predict_future(model, df, config, days=30):
    print("\nGenerando predicciones futuras...")
    last_date = pd.to_datetime(df["fecha_venta"]).max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=days)

    combos = df[["producto", "ciudad"]].drop_duplicates()
    base = df.groupby(["producto", "ciudad"]).agg({
        "precio_venta": "mean",
        "descuento_pct": "mean",
        "stock_disponible": "mean",
        "margen_ganancia": "mean",
    }).reset_index()

    rows = []
    for _, combo in combos.iterrows():
        values = base[(base["producto"] == combo["producto"]) & (base["ciudad"] == combo["ciudad"])].head(1)
        if values.empty:
            continue
        values = values.iloc[0]
        for date in future_dates:
            rows.append({
                "producto": combo["producto"],
                "ciudad": combo["ciudad"],
                "fecha_venta": date,
                "cantidad_vendida": 0,
                "precio_venta": values["precio_venta"],
                "descuento_pct": values["descuento_pct"],
                "stock_disponible": values["stock_disponible"],
                "margen_ganancia": values["margen_ganancia"],
                "promocion": "Sin promoción",
                "dias_hasta_vencimiento": 30,
                "tiene_promocion": 0,
                "ratio_venta_stock": 0,
                "es_fin_semana": 1 if date.weekday() in [5, 6] else 0,
                "anio": date.year,
                "mes": date.month,
                "dia": date.day,
                "dia_semana": date.weekday(),
                "trimestre": (date.month - 1) // 3 + 1,
            })

    future_df = pd.DataFrame(rows)
    model_columns = joblib.load("models/model_columns.pkl")
    X_future = prepare_prediction_data(future_df, model_columns)
    future_values = model.predict(X_future)
    future_df["prediccion_demanda"] = future_values

    print("Predicciones futuras generadas")
    return future_df


def save_predictions(df, output_path="reports/generated/predicciones_demanda.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Predicciones guardadas en: {output_path}")
