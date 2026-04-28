
def compute_metrics(df):
    resumen = (
        df.groupby(["Producto", "Region"])
        .agg(
            precio_promedio=("precio_promedio", "mean"),
            volatilidad=("precio_promedio", "std"),
        )
        .reset_index()
    )
    
    return resumen