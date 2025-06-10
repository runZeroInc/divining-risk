#!/bin/bash

# BSD vs Linux date implementation
if command -v gdate >/dev/null 2>&1; then
    DATE_BIN="gdate"
else
    DATE_BIN="date"
fi

mkdir -p ./data/epss-csv

# Defaults are what was originally published
start_date="${START_DATE:-2025-03-17}"
end_date="${END_DATE:-2025-04-15}"

current_date="$start_date"
one_day_after_end=$($DATE_BIN -I -d "$end_date + 1 day")

while [[ "$current_date" != "$one_day_after_end" ]]; do
    file="epss_scores-$current_date.csv.gz"
    url="https://epss.cyentia.com/$file"
    output="./data/epss-csv/$file"

    echo "Downloading $file..."
    curl -L --insecure -f --retry 3 --retry-delay 5 -o "$output" "$url"

    # Advance the date using the correct date binary
    current_date=$($DATE_BIN -I -d "$current_date + 1 day")
done
