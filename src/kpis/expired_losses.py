import pandas as pd


def calculate_total_expired_losses(df):
    """
    Calcula el total de pérdidas por productos vencidos
    """

    print("\nCalculando KPI: Pérdidas por vencimiento")

    total_losses = df["perdida_vencimiento"].sum()

    print(f"Pérdidas totales por vencimiento: ${round(total_losses,2)}")

    return total_losses


def expired_losses_by_product(df):
    """
    Calcula pérdidas por vencimiento por producto
    """

    print("\nCalculando pérdidas por producto")

    losses_product = (
        df.groupby("producto")["perdida_vencimiento"]
        .sum()
        .sort_values(ascending=False)
    )

    print(losses_product.head(10))

    return losses_product


def expired_losses_by_city(df):
    """
    Calcula pérdidas por vencimiento por ciudad
    """

    print("\nCalculando pérdidas por ciudad")

    losses_city = (
        df.groupby("ciudad")["perdida_vencimiento"]
        .sum()
        .sort_values(ascending=False)
    )

    print(losses_city)

    return losses_city