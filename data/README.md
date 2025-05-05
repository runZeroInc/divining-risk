Collect CISA KEVs:

```
curl -s https://raw.githubusercontent.com/cisagov/kev-data/refs/heads/develop/known_exploited_vulnerabilities.csv | cut -d, -f1 | tail -n +2 > CISA-KEV.txt
```

Collect VulnCheck KEV:
- Sign up for a community account.
- Go to https://docs.vulncheck.com/indices/vulncheck-intelligence#vulncheck-kev
- Click Browse the Vulncheck KEV index.
- Click Download Vulncheck KEV backup.
- Expand the ZIP
- `jq -r '.[].cve[]' ~/Downloads/vulncheck_known_exploited_vulnerabilities.json > VulnCheck-KEV.txt`

Collect all the KEVs from:

```

```
