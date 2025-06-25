#!/bin/bash

# BSD vs Linux date implementation
if command -v gdate >/dev/null 2>&1; then
    DATE_BIN="gdate"
else
    DATE_BIN="date"
fi
now=`$DATE_BIN`

# Set sensible defaults
start_date="${START_DATE:-2025-03-17}"
end_date="${END_DATE:-$($DATE_BIN +%F)}"

# Create output directory if it's not there already
mkdir -p ./data/epss-csv

current_date="$start_date"
if [[ "$DATE_BIN" == "gdate" ]]; then
    one_day_after_end=$($DATE_BIN -I -d "$end_date + 1 day")
else
    one_day_after_end=$($DATE_BIN -j -v+1d -f "%Y-%m-%d" "$end_date" "+%Y-%m-%d")
fi

while [[ "$current_date" != "$one_day_after_end" ]]; do
    file="epss_scores-$current_date.csv.gz"
    output="./data/epss-csv/$file"

    if [[ -f "$output" ]]; then
        echo "[$now] File exists: $file. Skipping."
    else
        url="https://epss.empiricalsecurity.com/$file"
        echo "[$now] Downloading $file..."
        # This experiments with public key pinning. Maybe these will survive refreshes?
        # Check back after July 28, 2025
        curl -v --retry 3 --retry-delay 5 \
        --pinnedpubkey "sha256//E6Cgac00T+woMzsm1dkWP6vOq0K7Gs7wEI7Y43/5/E4=" \
        -o "$output" "$url" || {
            echo "[$now] !! Failed to download $file. Continuing..."
        }

        # Sometimes we download too early in the day and catch an error.
        if [[ -f "$output" ]]; then
            # Validate file type
            filetype=$(file -b --mime-type "$output")
            if [[ "$filetype" != "application/gzip" ]]; then
                echo "[$now] !! Invalid file type ($filetype) for $file. Deleting..."
                rm -f "$output"
            else
                echo "[$now] File $file looks valid (gzip)."
            fi
        else
            echo "[$now] !! Failed to download $file. File not saved."
        fi
    fi

    # Advance the date
    if [[ "$DATE_BIN" == "gdate" ]]; then
        current_date=$($DATE_BIN -I -d "$current_date + 1 day")
    else
        current_date=$($DATE_BIN -j -v+1d -f "%Y-%m-%d" "$current_date" "+%Y-%m-%d")
    fi
done
