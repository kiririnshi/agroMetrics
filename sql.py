import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import create_engine

def run_sql():

    df = pd.read_parquet('data/staging/clean.parquet')

    df_region = df[["ID region", "Region"]].drop_duplicates()

    df_region = df_region.rename(columns={"ID region": "id_region", "Region": "nombre"})

    df_region["created_at"] = datetime.now(timezone.utc)
    df_region["updated_at"] = datetime.now(timezone.utc)

    # Connect to database (example: PostgreSQL)
    engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres') # db = postgres

    # Dump to database
    df_region.to_sql('base_region', engine, if_exists='append', index=False)

if __name__ == "__main__":
    run_sql()