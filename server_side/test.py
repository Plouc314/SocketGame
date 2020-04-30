import pandas as pd

df = pd.read_csv('user_data.csv')

print(df)
print(df['username']=='alex')

index = df[df['username'] == 'alex']

print(index)