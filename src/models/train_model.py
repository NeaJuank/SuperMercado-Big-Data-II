import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor


def prepare_data_for_model(df):
    y = df["cantidad_vendida"]
    drop_cols = ["cantidad_vendida", "fecha_venta", "fecha", "producto_id", "producto", "categoria", "marca", "promocion", "dia_semana", "ciudad", "sucursal"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
    X = pd.get_dummies(X, drop_first=True)
    return X, y


def train_model(df, config):
    print("\nEntrenando modelo XGBoost...")
    X, y = prepare_data_for_model(df)
    test_size = config["model"]["test_size"]
    random_state = config["model"]["random_state"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=random_state)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5

    print("MAE:", round(mae, 2))
    print("RMSE:", round(rmse, 2))

    os.makedirs("models", exist_ok=True)
    model_path = "models/demand_forecasting_model.pkl"
    columns_path = "models/model_columns.pkl"
    joblib.dump(model, model_path)
    joblib.dump(X.columns.tolist(), columns_path)

    print(f"Modelo guardado en: {model_path}")
    print(f"Columnas de entrenamiento guardadas en: {columns_path}")
    return model
