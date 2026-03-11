import joblib
import pandas as pd


def load_model(model_path="models/demand_forecasting_model.pkl"):
    """
    Carga el modelo entrenado desde disco
    """

    try:
        model = joblib.load(model_path)
        print("Modelo cargado correctamente")
        return model

    except Exception as e:
        print("Error cargando modelo:", e)
        return None


def prepare_prediction_data(df):
    """
    Prepara los datos para realizar predicciones
    """

    X = df.drop(columns=[
        "cantidad_vendida",
        "fecha",
        "producto",
        "categoria",
        "marca",
        "promocion",
        "dia_semana",
        "ciudad",
        "sucursal"
    ])

    X = pd.get_dummies(X, drop_first=True)

    return X


def predict_demand(model, df):
    """
    Genera predicciones de demanda usando el modelo entrenado
    """

    print("\nGenerando predicciones de demanda...")

    X = prepare_prediction_data(df)

    predictions = model.predict(X)

    df["prediccion_demanda"] = predictions

    print("Predicciones generadas correctamente")

    return df


def save_predictions(df, output_path="reports/generated/predicciones_demanda.csv"):
    """
    Guarda las predicciones generadas
    """

    df.to_csv(output_path, index=False)

    print(f"Predicciones guardadas en: {output_path}")