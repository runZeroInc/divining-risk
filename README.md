# Divining Risk

Materials created and used in support of [Divining Risk: Deciphering Signals From Vulnerability Scores](https://www.runzero.com/resources/deciphering-signals-from-vulnerability-scores/)
a research paper by runZero first published in May, 2025.

## Scripts provided

- `build-epss-matrix.py` : Builds a time series matrix of EPSS scores from a series of downloaded EPSS CSV files.
- `check-kev.sh` : Checks a list of CVEs (nominally, the top-20 biggest movers in an EPSS time series) for KEV inclusion.
- `collect-epss-scores.sh` : Downloads a series of EPSS CSV data files, based on a date range.
- `detect-significant-changes.py` : Analyzes a Parquet-formatted set of EPSS scores and looks for those that move "a lot" over a number of days. By default, "a lot" is 50 points, and the period is one day.
- `find-cisa-ssvc-pocs.sh` : Inspect a local clone of the [cvelistV5](https://github.com/CVEProject/cvelistV5/) set, looking for those marked with proof-of-concept exploits available.
- `monte-carlo-epss.py` : Takes a list of EPSS scores, and figures out how many scored vulnerabilities "should" be "exploited" in the next 30 days.

## Data files provided

For convenience, a number of data files are provided for reference. See [data/README](data/README.md) for details on how to recreate these.

## Steps to Reproduce

You might be interested in re-running these experiments with fresh data. Here's how!

```bash
# Start fresh
rm data/parquet/*
rm data/epss-csv/*
# Set start and end dates and collect EPSS scores.
START_DATE=2025-05-11 END_DATE=2025-06-09 ./collect-epss-scores.sh
# Generate Parquet files
python3 build-epss-matrix.py
# Check for significant changes
python3 detect-significant-changes.py --magnitude 0.50 --days 1
# Check if any are already in CISA's KEV
curl -s https://raw.githubusercontent.com/cisagov/kev-data/refs/heads/develop/known_exploited_vulnerabilities.csv | cut -d, -f1 | tail -n +2 > data/CISA-KEV.txt
./check-kev.sh
```

## Security Warning

These scripts should not be used in, or linked to, any production environment.

They take untrusted user-provided input, often by relative directory reference,
and are certainly exploitable with directory traversal, SQL injection, deserialization,
and probably other techniques, if you provide weird enough inputs.

Don't do it.

(I imagine someone will troll me by assigning CVEs for these vulnerabilities anyway.)
