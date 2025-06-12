# Set start date to March 17, 2025, the first day of EPSSv4.
START_DATE=2025-03-17 ./collect-epss-scores.sh
# Generate Parquet files
python3 build-epss-matrix.py
# Check for significant changes
python3 detect-significant-changes.py --magnitude 0.50 --days 1
# Check if any are already in CISA's KEV
# Experiment with pinning the cert.
#    curl -s https://raw.githubusercontent.com/cisagov/kev-data/refs/heads/develop/known_exploited_vulnerabilities.csv \
#    --pinnedpubkey "sha256//1FtgkXeU53bUTaObUogizKNIqs/ZGaEo1k2AwG30xts=" \
#        | cut -d, -f1 | tail -n +2 > data/CISA-KEV.txt
# ./check-kev.sh
