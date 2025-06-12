#!/bin/bash

# BSD vs Linux date implementation
if command -v gdate >/dev/null 2>&1; then
    DATE_BIN="gdate"
else
    DATE_BIN="date"
fi

# Set sensible defaults
start_date="${START_DATE:-2025-03-17}"
end_date="${END_DATE:-$($DATE_BIN +%F)}"

# Create output directory if it's not there already
mkdir -p ./data/epss-csv

current_date="$start_date"
one_day_after_end=$($DATE_BIN -I -d "$end_date + 1 day")

while [[ "$current_date" != "$one_day_after_end" ]]; do
    file="epss_scores-$current_date.csv.gz"
    output="./data/epss-csv/$file"
    now=`$DATE_BIN`

    if [[ -f "$output" ]]; then
        echo "[$now] File exists: $file. Skipping."
    else
        url="https://epss.cyentia.com/$file"
        echo "[$now] Downloading $file..."
        # This experiments with public key pinning. Maybe these will survive refreshes?
        # Check back after July 28, 2025
        curl -Ls --retry 3 --retry-delay 5 \
        --pinnedpubkey "sha256//jRUOvjFJPOPvl0fy+Q4hGlSIPs/KTsGrZMFB/TMUp7c=;sha256//E6Cgac00T+woMzsm1dkWP6vOq0K7Gs7wEI7Y43/5/E4=" \
        -o "$output" "$url" || {
            echo "[$now] !! Failed to download $file. Continuing..."
        }
    fi

    # Advance the date
    current_date=$($DATE_BIN -I -d "$current_date + 1 day")
done
