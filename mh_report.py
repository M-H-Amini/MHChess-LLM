import pandas as pd

df = pd.read_csv('output/results.txt', header=None, names=['White', 'Black', 'Winner', 'WhiteRnd', 'BlackRnd', 'Moves'])
print(df)