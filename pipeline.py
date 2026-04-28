import pandas as pd
from data_extract import load_raw_data
from data_transform import clean_data
from data_metrics import compute_metrics


def run_pipeline():

    df = load_raw_data()
    df_clean = clean_data(df)

    df_clean.to_parquet("data/staging/clean.parquet")

    #df_clean = pd.read_parquet("data/staging/clean.parquet")

    #metrics = compute_metrics(df_clean)
    # Deberia usar metricas si ya quiero sacar algunas tablas anexas sin tener que usar ORM, estas tendrian ya que ser CSV.

if __name__ == "__main__":
    run_pipeline()