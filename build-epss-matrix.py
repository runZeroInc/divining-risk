import os
import glob
import pandas as pd
import duckdb
import re
import time

def log(msg):
    timestamp = time.strftime("[%a %b %d %H:%M:%S %Z %Y]")
    print(f"{timestamp} {msg}")

# Configuration details
csv_folder = './data/epss-csv/'         # Folder where your CSV files live
parquet_folder = './data/parquet/'      # Folder to store Parquet files
output_parquet = './data/epss_matrix.parquet'  # Output file
output_csv = './data/epss_matrix.csv'  # Output file

# Create parquet folder if needed
os.makedirs(parquet_folder, exist_ok=True)

# Convert compressed CSVs to Parquet
log("Converting CSVs to Parquet...")

for csv_path in sorted(glob.glob(os.path.join(csv_folder, '*.csv.gz'))):

    filename = os.path.basename(csv_path)
    # Extract date from filename
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if not match:
        log("Skipping {filename}, no valid date found.")
        continue
    date = match.group(1)
    parquet_path = os.path.join(parquet_folder, f"{date}.parquet")

    # Skip if we've done this already
    if os.path.exists(parquet_path):
        log(f"Skipping {filename}, Parquet already exists.")
        continue

    # Read the CSV, handling the comment lines and missing values, and only keep the 'epss' column. Skip any we've done.
    log(f"Converting {filename} to Parquet...")
    df = pd.read_csv(
        csv_path,
        compression='infer',
        comment='#',
        dtype={'cve': str, 'epss': float}  # No 'percentile' column for this exercise
    )
    df['date'] = date
    df = df[['cve', 'epss', 'date']]
    df.to_parquet(parquet_path, index=False)

log("Building wide matrix using DuckDB...")

all_dates = sorted([
    os.path.basename(p).replace('.parquet', '')
    for p in glob.glob(os.path.join(parquet_folder, '*.parquet'))
])

pivot_columns = ',\n        '.join([f"'{d}'" for d in all_dates])

# SQL query for DuckDB
query = f"""
WITH all_data AS (
    SELECT * FROM read_parquet('{parquet_folder}/*.parquet')
),
pivoted AS (
    SELECT *
    FROM all_data
    PIVOT (
        MAX(epss) FOR date IN (
            {pivot_columns}
        )
    )
)
SELECT * FROM pivoted
"""

con = duckdb.connect(database=':memory:')
result_df = con.execute(query).fetchdf()

log(f"Saving Parquet matrix to {output_parquet}")
result_df.to_parquet(output_parquet, index=False)
log(f"Saving CSV to {output_csv}")
result_df.to_csv(output_csv, index=False)

log("Done!")
