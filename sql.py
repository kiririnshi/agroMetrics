"""

Script para abastecer la base de datos de la app base con los datos ya procesados.

Orden de carga (respeta dependencias FK):
    1. Region
    2. Producto   (sin FK)
    3. Mercado    (FK → Region)
    4. Snapshot   (FK → Producto, Mercado)

Ejecución:
    python sql.py run

"""

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

# Load functions

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

def load_mercado(df: pd.DataFrame, engine) -> None:
    df_mercado_raw = (
        df[["Mercado", "ID region", "Subsector"]]
        .drop_duplicates()
        .rename(columns={
            "Mercado":    "nombre",
            "Subsector":  "sub_sector",
        })
    )

    # Necesitamos el PK (id) de Region, no el id_region del negocio
    with engine.connect() as conn:
        regiones_db = pd.read_sql(
            text(f"SELECT id, id_region FROM {TABLE_REGION}"),
            conn,
        )

    df_mercado = df_mercado_raw.merge(
        regiones_db,
        left_on="ID region",
        right_on="id_region",
        how="left",
    ).rename(columns={"id": "region_id"}).drop(columns=["ID region", "id_region"])

    df_mercado = _add_timestamps(df_mercado)

    df_mercado.to_sql(
        TABLE_MERCADO,
        engine,
        if_exists="append",
        index=False,
        method=_insert_ignore,
    )
    print(f"  [Mercado]  {len(df_mercado):,} filas procesadas")

def load_snapshot(df: pd.DataFrame, engine) -> None:
    # Leer pk de producto y mercado
    with engine.connect() as conn:
        productos_db = pd.read_sql(
            text(f"SELECT id, nombre, variedad, calidad FROM {TABLE_PRODUCTO}"),
            conn,
        )
        mercados_db = pd.read_sql(
            text(f"SELECT m.id, m.nombre, m.region_id, r.id_region "
                 f"FROM {TABLE_MERCADO} m "
                 f"JOIN {TABLE_REGION} r ON m.region_id = r.id"),
            conn,
        )
    

    df_snap = df.rename(columns={
        "Fecha":          "fecha",
        "Producto":       "nombre_producto",
        "Variedad / Tipo":"variedad",
        "Calidad":        "calidad",
        "Mercado":        "nombre_mercado",
        "ID region":      "id_region",
        "Volumen":        "volumen",
        "Precio minimo":  "precio_minimo",
        "Precio maximo":  "precio_maximo",
        "Precio promedio":"precio_promedio",
    }).copy()

    # Normaliza nulos para el merge con productos
    df_snap["variedad"] = df_snap["variedad"].where(df_snap["variedad"].notna(), None)
    df_snap["calidad"]  = df_snap["calidad"].where(df_snap["calidad"].notna(), None)

    # Merge → producto_id
    df_snap = df_snap.merge(
        productos_db.rename(columns={"id": "producto_id", "nombre": "nombre_producto"}),
        on=["nombre_producto", "variedad", "calidad"],
        how="left",
    )

    # Merge → mercado_id
    df_snap = df_snap.merge(
        mercados_db.rename(columns={"id": "mercado_id", "nombre": "nombre_mercado"}),
        on=["nombre_mercado", "id_region"],
        how="left",
    )

    # Columnas finales para la tabla
    df_final = df_snap[[
        "fecha", "producto_id", "mercado_id",
        "precio_minimo", "precio_maximo", "precio_promedio", "volumen",
    ]]
    df_final = _add_timestamps(df_final)

    df_final.to_sql(
        TABLE_SNAPSHOT,
        engine,
        if_exists="append",
        index=False,
        method=_insert_ignore,
    )
    print(f"  [Snapshot] {len(df_final):,} filas procesadas")

# Main

def run():
    print(f"Leyendo {PARQUET_PATH} …")
    df = pd.read_parquet(PARQUET_PATH) # Donde se localizan los datos obtenidos de la pipeline
    print(f"  → {len(df):,} filas\n")

    engine = create_engine(DATABASE_URL) # Conectarse a DB postgres

    print("Cargando tablas (orden: Region → Producto → Mercado → Snapshot)")
    load_region(df, engine)
    load_producto(df, engine)
    load_mercado(df, engine)
    load_snapshot(df, engine)

    print("\n✓ Carga completada.")


if __name__ == "__main__":
    run()
