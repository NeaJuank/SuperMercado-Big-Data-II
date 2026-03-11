import pandas as pd


def calculate_inventory_rotation(df):
    """
    Calcula el KPI de rotación de inventario
    """

    print("\nCalculando KPI: Rotación de Inventario")

    ventas_totales = df["cantidad_vendida"].sum()

    inventario_promedio = (
        df["stock_inicial"].mean() + df["stock_final"].mean()
    ) / 2

    if inventario_promedio == 0:
        rotation = 0
    else:
        rotation = ventas_totales / inventario_promedio

    print(f"Ventas Totales: {ventas_totales}")
    print(f"Inventario Promedio: {round(inventario_promedio,2)}")
    print(f"Rotación de Inventario: {round(rotation,2)}")

    return rotation


def inventory_rotation_by_product(df):
    """
    Calcula la rotación de inventario por producto
    """

    print("\nCalculando rotación por producto")

    grouped = df.groupby("producto").agg({
        "cantidad_vendida": "sum",
        "stock_inicial": "mean",
        "stock_final": "mean"
    })

    grouped["inventario_promedio"] = (
        grouped["stock_inicial"] + grouped["stock_final"]
    ) / 2

    grouped["rotacion_inventario"] = (
        grouped["cantidad_vendida"] /
        (grouped["inventario_promedio"] + 1)
    )

    return grouped.sort_values("rotacion_inventario", ascending=False)