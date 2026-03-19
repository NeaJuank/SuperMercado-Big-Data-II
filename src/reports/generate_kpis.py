import pandas as pd

def calculate_kpis(df, config):
    print("\nCalculando KPIs del negocio...")
    results = {}

    # Rotación inventario
    ventas_totales = df["cantidad_vendida"].sum()
    inventario_promedio = (df["stock_inicial"].mean() + df["stock_disponible"].mean()) / 2
    rotation = 0 if inventario_promedio == 0 else ventas_totales / inventario_promedio
    rotation_goal = config["kpis"]["goals"]["rotation_min"]
    rotation_ok = rotation >= rotation_goal
    results["rotation"] = {
        "valor": rotation,
        "meta": rotation_goal,
        "cumple": rotation_ok,
        "brecha": rotation - rotation_goal,
        "recomendacion": "Aumentar promociones en productos de baja rotación" if not rotation_ok else "Mantener ritmo de reposición actual"
    }

    # Perdidas por vencimiento
    total_losses = df["perdida_vencimiento"].sum()
    valor_inventario = (df["precio_venta"] * df["stock_disponible"]).sum()
    if valor_inventario == 0:
        loss_pct = 0
    else:
        loss_pct = total_losses / valor_inventario
    loss_goal = config["kpis"]["goals"]["expired_loss_max"]
    loss_ok = loss_pct <= loss_goal
    results["expired_loss"] = {
        "valor": loss_pct,
        "meta": loss_goal,
        "cumple": loss_ok,
        "brecha": loss_pct - loss_goal,
        "recomendacion": "Reducir stock de productos con riesgo de vencimiento y aumentar promociones" if not loss_ok else "Continuar con niveles de inventario actuales"
    }

    # Impacto promociones
    promo_sales = df[df["tiene_promocion"] == 1]["ingresos"].mean()
    normal_sales = df[df["tiene_promocion"] == 0]["ingresos"].mean()
    promo_goal = config["kpis"]["goals"]["promotion_increase_min"]
    if normal_sales == 0 or pd.isna(normal_sales):
        promo_increase = 0
    else:
        promo_increase = (promo_sales - normal_sales) / normal_sales
    promo_ok = promo_increase >= promo_goal
    results["promotion_impact"] = {
        "valor": promo_increase,
        "meta": promo_goal,
        "cumple": promo_ok,
        "brecha": promo_increase - promo_goal,
        "recomendacion": "Revisar promociones y canales si incremento es bajo" if not promo_ok else "Las promociones son efectivas"
    }

    print("KPIs calculados")
    return results
