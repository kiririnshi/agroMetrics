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
import re
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Rutas de mis archivos de dump y BD
PARQUET_PATH = "data/staging/clean.parquet"
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/postgres"

# Nombres de mis tablas en la base de datos postgresql
APP_LABEL = "base"
TABLE_REGION   = f"{APP_LABEL}_region"
TABLE_UNIDAD   = f"{APP_LABEL}_unidad"
TABLE_PRODUCTO = f"{APP_LABEL}_producto"
TABLE_MERCADO  = f"{APP_LABEL}_mercado"
TABLE_SNAPSHOT = f"{APP_LABEL}_snapshot"

def _insert_ignore(table, conn, keys, data_iter):
    """
    Versión genérica usando el nombre de tabla dinámico desde el objeto `table`.
    Compatible con pandas >= 1.3 y SQLAlchemy >= 1.4
    """
    from sqlalchemy import MetaData
    meta = MetaData()
    meta.reflect(bind=conn, only=[table.name])
    tbl = meta.tables[table.name]
    stmt = pg_insert(tbl).values([dict(zip(keys, row)) for row in data_iter])
    stmt = stmt.on_conflict_do_nothing()
    conn.execute(stmt)

def _insert_or_update(table, conn, keys, data_iter):
    from sqlalchemy import Table, MetaData
    meta = MetaData()
    meta.reflect(bind=conn, only=[table.name])
    tbl = meta.tables[table.name]
    
    rows = [dict(zip(keys, row)) for row in data_iter]
    stmt = pg_insert(tbl).values(rows)
    
    # Columnas a actualizar cuando hay conflicto (todo excepto la PK y created_at)
    update_cols = {
        col.name: stmt.excluded[col.name]
        for col in tbl.columns
        if col.name not in ("id", "created_at")
    }
    
    stmt = stmt.on_conflict_do_update(
        index_elements=["nombre_original"],  # la columna unique
        set_=update_cols,
    )
    conn.execute(stmt)

def _add_timestamps(df: pd.DataFrame) -> pd.DataFrame: # Las tablas guardan la fecha de creacion y update, es necesario tambien mandarlas cuando se llenan 
    now = datetime.now(timezone.utc)
    df = df.copy()
    df["created_at"] = now
    df["updated_at"] = now
    return df

def normalizar_unidad(texto: str) -> dict: # Utilizado solo para la conversion de Unidades de comercializacion a un formato mas amigable para la BD.

    if pd.isna(texto):
        return {"unidad": None, "cantidad": None}

    # Aqui entran textos del tipo "caja_18_kilos"

    texto_mod = texto.replace("_", " ").strip()


    # Patrón peso: "caja 10 kg", "malla 5.5 kg", "10kg", "10 kg"
    match_kg = re.search(r'(\d+(?:\.\d+)?)\s*(kg|kilo|kilos)', texto_mod)
    if match_kg:
        return {
            "unidad": "kg",
            "cantidad": float(match_kg.group(1)),
        }

    # Patrón conteo explícito: "60 unidades", "12 unidades"
    match_unidades = re.search(r'(\d+(?:\.\d+)?)\s*unidades?', texto_mod)
    if match_unidades:
        return {
            "unidad": "unidades",
            "cantidad": float(match_unidades.group(1)),
        }

    # Patrón docena: "docena", "docena de matas"
    if "docena" in texto_mod:
        return {
            "unidad": "unidades",
            "cantidad": 12,
        }

    # Patron de kilo o unidades por si solos, estos no los toman en cuenta los bloques anteriores.
    if re.search(r'^kilo(?:gramo)?s?$|^kg$', texto_mod):
        return {
            "unidad":"kg",
            "cantidad": 1,
            }

    if re.search(r'^unidades?$', texto_mod): 
        return {
            "unidad": "unidades",
            "cantidad": 1, 
            }
    
    if texto_mod == "unidad":
        return {
            "unidad": "unidades",
            "cantidad": 1, 
            }


    return {"unidad": None, "cantidad": None}

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

def load_unidad(df: pd.DataFrame, engine) -> None: # Esto es complejo, ya que no existen unidades muy estandares en esta columna para poder llevarlas al modelo. 

    ## Este codigo sirve para dilusidar cuales son las entradas que deberia agreagar al modelo unidades y cuales ignorar.

    #unidades = (
    #df["Unidad de comercializacion"]
    #.str.strip()          # elimina espacios al inicio/fin
    #.str.lower()          # normaliza mayúsculas para no contar duplicados
    #.value_counts()       # ordena por frecuencia
    #.reset_index()
    #)
    #unidades.columns = ["unidad", "frecuencia"]

    # Solo dos tipos: kg y unidades, el resto debe ser tratado como nulls. 
    # Es necesario transformar las entradas mediante expreciones regulares (regex)


    df_unidades = (
        df[["Unidad de comercializacion"]]
            .drop_duplicates()
            .rename(columns={"Unidad de comercializacion": "nombre_original"})
        )

    normalizadas = df_unidades["nombre_original"].apply(lambda x: pd.Series(normalizar_unidad(x)))

    df_unidades = pd.concat([df_unidades, normalizadas], axis=1)

    df_unidades = _add_timestamps(df_unidades)

    df_unidades.to_sql(
        TABLE_UNIDAD,
        engine,
        if_exists="append",
        index=False,
        method=_insert_or_update,
    )
    print(f"  [Unidad]   {len(df_unidades):,} filas procesadas")

def load_producto(df: pd.DataFrame, engine) -> None:
    df_producto = (
        df[["Producto", "Variedad / Tipo", 
            "Origen"]]
        .drop_duplicates() # Solo es necesario guardar las regiones y su id, sin duplicados
        .rename(columns={"Producto": "nombre", "Variedad / Tipo": "variedad", 
                         "Calidad": "calidad", "Origen" : "origen"})
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

        unidades_db  = pd.read_sql(text(f"SELECT id, nombre_original FROM {TABLE_UNIDAD}"), conn)

    

    df_snap = df.rename(columns={
        "Fecha":          "fecha",
        "Producto":       "nombre_producto",
        "Variedad / Tipo":"variedad",
        "Calidad":        "calidad",
        "Mercado":        "nombre_mercado",
        "ID region":      "id_region",
        "Volumen":        "volumen",
        "Unidad de comercializacion": "nombre_original", 
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

    df_snap = df_snap.merge(
        unidades_db.rename(columns={"id": "unidad_id"}),
        on="nombre_original", 
        how="left",  # left → unidad_id queda null si no matchea
    )

    # Columnas finales para la tabla
    df_final = df_snap[[
        "fecha", "producto_id", "mercado_id", "unidad_id",
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
    #load_region(df, engine)
    #load_unidad(df, engine)
    #load_producto(df, engine)
    #load_mercado(df, engine)
    load_snapshot(df, engine) #### Probar esto !!!

    print("\n✓ Carga completada.")


if __name__ == "__main__":
    run()
