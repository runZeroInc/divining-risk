#!/bin/bash

# Pick through the CVE list repo published by the CVE Project and find all the
# CVEs that CISA has decided has an accompanying PoC or active exploitation.

# Note: Don't run this with untrusted input. This is a quick CLI tool!
# Seriously, it's super risky. Don't.

year="2025"              # Default CVE year
basedir=".."             # Where you cloned the CVE list repo (https://github.com/CVEProject/cvelistV5)
exploit="PoC"            # Default exploitation status to search for
filter_techimpact=false  # Enable to filter for Technical Impact: total

# Argument parsing
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --year)
            year="$2"
            shift 2
            ;;
        --basedir)
            basedir="$2"
            shift 2
            ;;
        --exploit)
            exploit="$2"
            shift 2
            ;;
        --techimpact)
            filter_techimpact=true
            shift 1
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--year YYYY] [--basedir PATH] [--exploit POC|Active] [--techimpact]"
            exit 1
            ;;
    esac
done

output_file="./data/cisa-ssvc-$(echo "$exploit" | tr '[:upper:]' '[:lower:]')"
if $filter_techimpact; then
    output_file="${output_file}-techimpact"
fi
output_file="${output_file}-${year}.txt"

base_dir="${basedir}/cvelistV5/cves/${year}"

# Clear the output file first
> "$output_file"

# requires jq. jq is great and completely ineffible for mortals.
base_filter='
    .containers.adp[]?.metrics[]?.other?.content
    | select(
        (.options[]? | to_entries[]
            | select(.key | ascii_downcase == "exploitation")
            | select(.value | ascii_downcase == ($exploit | ascii_downcase)))
    '
techimpact_filter='
    and (.options[]? | to_entries[]
        | select(.key | ascii_downcase == "technical impact")
        | select(.value | ascii_downcase == "total"))
    )
'

end_filter='
    )
'

if $filter_techimpact; then
    full_filter="$base_filter$techimpact_filter"
else
    full_filter="$base_filter$end_filter"
fi

find "$base_dir" -name "CVE-${year}-*.json" | while read -r file; do
    match=$(jq --arg exploit "$exploit" "$full_filter" "$file")
    if [[ -n "$match" ]]; then
        cve_id=$(basename "$file" .json)
        echo "$cve_id" | tee -a "$output_file"
    fi
done

echo "Done. Matching CVEs written to $output_file"
