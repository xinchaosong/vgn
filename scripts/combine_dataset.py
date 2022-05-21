import pandas as pd

df_pile = pd.read_csv("/media/DATACENTER2/HiLo_other_approaches/vgn_data/raw/pile/grasps.csv")
df_packed = pd.read_csv("/media/DATACENTER2/HiLo_other_approaches/vgn_data/raw/packed/grasps.csv")

print(df_pile.shape)
print(df_packed.shape)

df_all = pd.concat([df_pile, df_packed])
print(df_all.shape)
print(df_all.head(5))

df_all = df_all.sample(frac=1)
print(df_all.head(5))

df_all.to_csv("/media/DATACENTER2/HiLo_other_approaches/vgn_data/raw/foo/grasps.csv", index=False)
