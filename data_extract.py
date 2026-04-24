import pandas as pd
import glob

files = glob.glob('data/*.csv')
dfs = [pd.read_csv(f) for f in files]
df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

df.to_csv("final.csv", index=False)

