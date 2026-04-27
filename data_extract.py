import pandas as pd
import glob

def load_raw_data(path="data/raw"):

    files = glob.glob('data/raw/*.csv')
    #dfs = [pd.read_csv(f) for f in files]
    df = pd.concat((pd.read_csv(f, decimal=",") for f in files), ignore_index=True) # , decimal="," es para pasar las comas a puntos y de esa forma pandas sabe que estos son float despues

    #df.to_csv("staging/final.csv", index=False)
    return df
