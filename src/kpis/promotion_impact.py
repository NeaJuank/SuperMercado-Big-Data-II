import pandas as pd


def promotion_sales_comparison(df):
    """
    Compara ventas con y sin promoción
    """

    print("\nCalculando KPI: Impacto de Promociones")

    ventas_promocion = df[df["tiene_promocion"] == 1]["cantidad_vendida"]
    ventas_normal = df[df["tiene_promocion"] == 0]["cantidad_vendida"]

    if len(ventas_promocion) == 0 or len(ventas_normal) == 0:
        print("No hay suficientes datos para calcular el impacto de promociones")
        return None

    promedio_promocion = ventas_promocion.mean()
    promedio_normal = ventas_normal.mean()

    impacto = promedio_promocion - promedio_normal

    print(f"Promedio ventas SIN promoción: {round(promedio_normal,2)}")
    print(f"Promedio ventas CON promoción: {round(promedio_promocion,2)}")
    print(f"Incremento promedio por promoción: {round(impacto,2)}")

    return impacto


def promotion_impact_by_product(df):
    """
    Analiza impacto de promoción por producto
    """

    print("\nImpacto de promociones por producto")

    grouped = df.groupby(["producto", "tiene_promocion"])["cantidad_vendida"].mean().unstack()

    # asegurar columnas
    grouped = grouped.fillna(0)

    grouped["impacto_promocion"] = grouped[1] - grouped[0]

    grouped = grouped.sort_values("impacto_promocion", ascending=False)

    print(grouped.head(10))

    return grouped


def promotion_effectiveness(df):
    """
    Calcula porcentaje de incremento de ventas por promoción
    """

    ventas_promocion = df[df["tiene_promocion"] == 1]["cantidad_vendida"].mean()
    ventas_normal = df[df["tiene_promocion"] == 0]["cantidad_vendida"].mean()

    if ventas_normal == 0 or pd.isna(ventas_normal):
        porcentaje = 0
    else:
        porcentaje = ((ventas_promocion - ventas_normal) / ventas_normal) * 100

    print(f"\nIncremento porcentual por promoción: {round(porcentaje,2)}%")

    return porcentaje