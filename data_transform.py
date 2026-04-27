import pandas as pd
import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_data(df):

    cols_to_normalize = ["Region", "Mercado", "Subsector", "Producto", "Variedad / Tipo", "Origen"]

    # df[cols_to_clean] = df[cols_to_clean].applymap(remove_accents)

    for column in cols_to_normalize:
        df[column] = [remove_accents(c).strip().lower().replace(" ", "_") for c in df[column]]

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    breakpoint()

    return ""