# Data files for Divining Risk

This subdirectory in this repo (https://github.com/runZeroInc/divining-risk/) is where data files are stored.
If you'd like to recreate the research, this repo has copies of the data files at the time of writing. Of course,
you might want to rerun things later with new data.

## Collecting EPSS scores

First off, you need to collect a set of EPSS values.

Run `collect-epss-scores.sh` and edit the date range to taste.

### Creating Parquet files

Once you have the compressed CSV files, run `build-epss-matrix.py`. This requires Python3, and having
`pip install`ed the `panda` and `duckdb` libraries. In my own environment, I used homebrew for the
initial Python3 install, and then set up a virtual environment using [venv](https://docs.python.org/3/library/venv.html).

On a reasonably modern MacBook, this should take only a minute or two for 30 days of data.

(My original attempts at all this analysis relied on shell scripts to grep through
EPSS scores, and it took days and days to build the CSVs, but at least it gave me a reference
point to make sure that Parquet and DuckDB were doing the right thing.)

## Collecting KEV lists

This is useful for running `check-kev.sh` or doing other KEV-ish things.

### Collect CISA KEVs

```
curl -s https://raw.githubusercontent.com/cisagov/kev-data/refs/heads/develop/known_exploited_vulnerabilities.csv | cut -d, -f1 | tail -n +2 > CISA-KEV.txt
```

### Collect VulnCheck KEV

Alas, there's no simple `curl` I could find to do this, but I imagine it's possible with an API key.

- Sign up for a community account.
- Go to https://docs.vulncheck.com/indices/vulncheck-intelligence#vulncheck-kev
- Click Browse the Vulncheck KEV index.
- Click Download Vulncheck KEV backup.
- Expand the ZIP with your preferred unarchiver.
- `jq -r '.[].cve[]' ~/Downloads/vulncheck_known_exploited_vulnerabilities.json > VulnCheck-KEV.txt`

## Collect a local JSON-formatted CVE list

When using `find-csa-ssvc-poc.sh`, you'll want to clone the CVE list. By default, we assume
you've cloned it "next door" to this git repo. Here's one way to do it:

`cd "$(dirname "$(git rev-parse --show-toplevel)")" && git clone https://github.com/CVEProject/cvelistV5.git`
