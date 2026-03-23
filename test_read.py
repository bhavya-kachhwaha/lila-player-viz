import pyarrow.parquet as pq
import os

# Pick the first file from February_10
folder = "player_data/February_10"
files = os.listdir(folder)
first_file = os.path.join(folder, files[0])

print("Reading file:", first_file)

table = pq.read_table(first_file)
df = table.to_pandas()

# Decode event column from bytes to string
df['event'] = df['event'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)

print("\n--- First 5 rows ---")
print(df.head())

print("\n--- Column names ---")
print(df.columns.tolist())

print("\n--- Event types in this file ---")
print(df['event'].unique())

print("\n--- Map ---")
print(df['map_id'].unique())

print("\n--- User ID (UUID = human, number = bot) ---")
print(df['user_id'].iloc[0])

print("\n--- Total rows ---")
print(len(df))