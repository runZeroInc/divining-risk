#!/bin/bash

# Create this with detect_significant_changes.py, in this repo
significant_changes_file="./data/significant-changes.csv"

# KEV files, collected per the instructions in ./data
cisa_kev_file="./data/CISA-KEV.txt"
vulncheck_kev_file="./data/Vulncheck-KEV.txt"

echo "# Checking significant changes against KEV lists..."
echo "cve,change,date,marker"
while IFS=, read -r cve change date; do
    # Skip the header line from the file
    if [[ "$cve" == "cve" ]]; then
        continue
    fi

    in_cisa=$(grep -Fxq "$cve" "$cisa_kev_file" && echo "c" || echo "")
    in_vulncheck=$(grep -Fxq "$cve" "$vulncheck_kev_file" && echo "v" || echo "")

    # Assign marker based on presence in KEV lists
    marker="${in_cisa}${in_vulncheck}"

    # Output the result in CSV
    echo "$cve,$change,$date,$marker"
done < "$significant_changes_file"
