import duckdb
import argparse
import os

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--file', default='./data/epss_matrix.parquet', help='Input Parquet file')
parser.add_argument('--output', default='./data/significant-changes.csv', help='Output CSV file')
parser.add_argument('--magnitude', type=float, default=0.50, help='Magnitude threshold (between 0 and 1)')
parser.add_argument('--days', type=int, default=1, help='Number of days for delta window')
parser.add_argument('--sort', choices=['change', 'date-desc', 'date-asc'], default='change',
    help='Sort by "change" (default), "date-desc", or "date-asc"')
parser.add_argument('--positive', action='store_true', help='Only look the most recent positive changes')
parser.add_argument('--negative', action='store_true', help='Only look for most recent negative changes')
parser.add_argument('--absolute', action='store_true', help='Only look for most recent absolute changes')

args = parser.parse_args()

# Determine mode

if args.absolute:
    print("Searching for absolute changes (more recent changes mask earlier changes).")
    mode = "absolute"
elif args.positive and args.negative:
    print("Both --positive and --negative specified; defaulting to absolute mode (more recent changes mask earlier changes).")
    mode = "absolute"
elif args.positive:
    print("Searching positive changes only (more recent changes mask negative changes).")
    mode = "positive"
elif args.negative:
    print("Searching negative changes only (more recent changes mask positive changes).")
    mode = "negative"
else:
    print("Searching for absolute changes (more recent changes mask earlier changes).")
    mode = "absolute"

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
    delta_expr = f"(\"{newer}\" - \"{older}\")"
    abs_expr = f"ABS({delta_expr}) >= {args.magnitude}"

    if mode == "positive":
        where_clause = f"{abs_expr} AND {delta_expr} > 0"
    elif mode == "negative":
        where_clause = f"{abs_expr} AND {delta_expr} < 0"
    else:
        where_clause = abs_expr

    checks.append(f"SELECT CVE, {delta_expr} AS change, '{newer}' AS date FROM epss WHERE {where_clause}")

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

# Sort by argument
if args.sort == "change":
    result_df = result_df.sort_values("change", ascending=False)
elif args.sort == "date-desc":
    result_df = result_df.sort_values("date", ascending=False)
elif args.sort == "date-asc":
    result_df = result_df.sort_values("date", ascending=True)

# Save full result CSV
result_df.to_csv(args.output, index=False)
print(f"Saved {len(result_df)} {mode} changes to {args.output} (sorted by {args.sort})")

# Show top 20 most significant changes in the selected direction
if mode == "positive":
    top_20 = result_df[result_df['change'] > 0].head(20)
elif mode == "negative":
    top_20 = result_df[result_df['change'] < 0].head(20)
else:
    top_20 = result_df.head(20)

if not top_20.empty:
    # Pad the first column (CVE) to align cleanly
    max_cve_len = top_20.iloc[:, 0].str.len().max()
    top_20.iloc[:, 0] = top_20.iloc[:, 0].str.ljust(max_cve_len)

    print(f"Top 20 most {mode} changes (|delta| ≥ {args.magnitude}):")
    print(top_20.to_string(index=False))

    # Save top 20 to a separate CSV
    top20_path = f"./data/top-20-{mode}-changes.csv"
    top_20.to_csv(top20_path, index=False)
    print(f"Saved top 20 most {mode} changes to {top20_path}")
else:
    print(f"No {mode} changes found with magnitude ≥ {args.magnitude}")
