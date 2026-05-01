import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Rutas de mis archivos de dump y BD
PARQUET_PATH = "data/staging/clean.parquet"
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/postgres"

# Nombres de mis tablas en la base de datos postgresql
APP_LABEL = "base"
TABLE_REGION   = f"{APP_LABEL}_region"
TABLE_PRODUCTO = f"{APP_LABEL}_producto"
TABLE_MERCADO  = f"{APP_LABEL}_mercado"
TABLE_SNAPSHOT = f"{APP_LABEL}_snapshot"

def _insert_ignore(table, conn, keys, data_iter):
    """
    Versión genérica usando el nombre de tabla dinámico desde el objeto `table`.
    Compatible con pandas >= 1.3 y SQLAlchemy >= 1.4
    """
    from sqlalchemy import Table, MetaData
    meta = MetaData()
    meta.reflect(bind=conn, only=[table.name])
    tbl = meta.tables[table.name]
    stmt = pg_insert(tbl).values([dict(zip(keys, row)) for row in data_iter])
    stmt = stmt.on_conflict_do_nothing()
    conn.execute(stmt)

def _add_timestamps(df: pd.DataFrame) -> pd.DataFrame: # Las tablas guardan la fecha de creacion y update, es necesario tambien mandarlas cuando se llenan 
    now = datetime.now(timezone.utc)
    df = df.copy()
    df["created_at"] = now
    df["updated_at"] = now
    return df

def load_region(df: pd.DataFrame, engine) -> None:
    df_region = (
        df[["ID region", "Region"]]
        .drop_duplicates() # Solo es necesario guardar las regiones y su id, sin duplicados
        .rename(columns={"ID region": "id_region", "Region": "nombre"}) # Es necesario cambiar los indices a aquellos que tiene la base de datos
    )
    df_region = _add_timestamps(df_region)

    df_region.to_sql(
        TABLE_REGION,
        engine,
        if_exists="append",
        index=False,
        method=_insert_ignore,
    )
    print(f"  [Region]   {len(df_region):,} filas procesadas")

def load_producto(df: pd.DataFrame, engine) -> None:
    df_producto = (
        df[["Producto", "Variedad / Tipo", 
            "Calidad", "Unidad de comercializacion", 
            "Origen"]]
        .drop_duplicates() # Solo es necesario guardar las regiones y su id, sin duplicados
        .rename(columns={"Producto": "nombre", "Variedad / Tipo": "variedad", 
                         "Calidad": "calidad", "Unidad de comercializacion": "unidad_comercio", 
                         "Origen" : "origen"})
    )

    # Normaliza cadenas vacías a NULL para respetar la unique constraint
    df_producto["variedad"] = df_producto["variedad"].where(df_producto["variedad"].notna(), None)
    df_producto["calidad"]  = df_producto["calidad"].where(df_producto["calidad"].notna(), None)
    df_producto = _add_timestamps(df_producto)

    df_producto.to_sql(
        TABLE_PRODUCTO,
        engine,
        if_exists="append",
        index=False,
        method=_insert_ignore,
    )
    print(f"  [Producto]   {len(df_producto):,} filas procesadas")

# ── Main ───────────────────────────────────────────────────────────────────────

def run():
    print(f"Leyendo {PARQUET_PATH} …")
    df = pd.read_parquet(PARQUET_PATH) # Donde se localizan los datos obtenidos de la pipeline
    print(f"  → {len(df):,} filas\n")

    engine = create_engine(DATABASE_URL) # Conectarse a DB postgres

    print("Cargando tablas (orden: Region → Producto → Mercado → Snapshot)")
    load_region(df, engine)
    load_producto(df, engine)
    #load_mercado(df, engine)
    #load_snapshot(df, engine)

    print("\n✓ Carga completada.")


if __name__ == "__main__":
    run()
