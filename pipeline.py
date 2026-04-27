
from data_extract import load_raw_data
from data_transform import clean_data


def run_pipeline():

    df = load_raw_data()
    df_clean = clean_data(df)

    df_clean.to_parquet("data/staging/clean.parquet")

if __name__ == "__main__":
    run_pipeline()