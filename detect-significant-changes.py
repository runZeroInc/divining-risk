import duckdb
import argparse

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--file', default='./data/epss_matrix.parquet', help='Input Parquet file')
parser.add_argument('--output', default='./data/significant-changes.csv', help='Output CSV file')
parser.add_argument('--magnitude', type=float, default=0.50, help='Magnitude threshold (between 0 and 1)')
parser.add_argument('--days', type=int, default=1, help='Number of days for delta window')
args = parser.parse_args()

# Load the matrix
con = duckdb.connect()
con.execute(f"CREATE TABLE epss AS SELECT * FROM read_parquet('{args.file}')")

# Get the ordered list of date columns (excluding the CVE column)
date_columns = [
    row[1] for row in con.execute("PRAGMA table_info(epss)").fetchall()
    if row[1].lower() != 'cve'
]
date_columns.sort()  # Sort alphabetically, which works for ISO date strings

# Build SQL logic for comparing deltas
checks = []
for i in range(args.days, len(date_columns)):
    newer = date_columns[i]
    older = date_columns[i - args.days]
    diff_expr = f"ABS(\"{newer}\" - \"{older}\") >= {args.magnitude}"
    sum_expr = f"(\"{newer}\" - \"{older}\")"
    checks.append(f"SELECT CVE, {sum_expr} AS change, '{newer}' AS date FROM epss WHERE {diff_expr}")

# Combine into one big union
union_query = "\nUNION\n".join(checks)

# Final query to select the most recent change per CVE
final_query = f"""
WITH changes AS (
    {union_query}
)
SELECT CVE, change, date
FROM (
    SELECT CVE, change, date, ROW_NUMBER() OVER (PARTITION BY CVE ORDER BY date DESC) AS row_num
    FROM changes
) AS ranked_changes
WHERE row_num = 1
"""

# Run and save results
result_df = con.execute(final_query).fetchdf()
result_df['change'] = result_df['change'].round(5)

# Sort: Most positive change first, most negative last
result_df = result_df.sort_values("change", ascending=False)

# Save full result CSV
result_df.to_csv(args.output, index=False)
print(f"Saved {len(result_df)} significant changes to {args.output} (sorted descending by change)")

# Show top 20 most positive changes
top_positive = result_df[result_df.iloc[:, 1] > 0].head(20)

# Pad the first column (CVE) to align cleanly
max_cve_len = top_positive.iloc[:, 0].str.len().max()
top_positive.iloc[:, 0] = top_positive.iloc[:, 0].str.ljust(max_cve_len)

print(f"Top 20 most positive changed scores of at least {args.magnitude}")
print(top_positive.to_string(index=False))

# Save top 20 most positive changes to a separate CSV
top_positive.to_csv("./data/top-20-positive-changes.csv", index=False)
print("Saved top 20 most positive changes to ./data/top-positive-changes.csv")
