import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor


def prepare_data_for_model(df):
    """
    Prepara el dataset para entrenamiento del modelo
    """

    # variable objetivo
    y = df["cantidad_vendida"]

    # eliminar columnas que no ayudan al modelo
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

    # convertir variables categóricas
    X = pd.get_dummies(X, drop_first=True)

    return X, y


def train_model(df, config):
    """
    Entrena el modelo de predicción de demanda
    """

    print("\nPreparando datos para entrenamiento...")

    X, y = prepare_data_for_model(df)

    test_size = config["model"]["test_size"]
    random_state = config["model"]["random_state"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state
    )

    print("Entrenando modelo XGBoost...")

    model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=random_state
    )

    model.fit(X_train, y_train)

    print("Modelo entrenado")

    # evaluación
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions, squared=False)

    print("\nEvaluación del modelo")
    print("MAE:", round(mae, 2))
    print("RMSE:", round(rmse, 2))

    # guardar modelo
    model_path = "models/demand_forecasting_model.pkl"
    joblib.dump(model, model_path)

    print(f"\nModelo guardado en: {model_path}")

    return model