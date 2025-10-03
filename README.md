# JPL Comet Data Download - Modern API Solution

## Overview

The old JPL command for downloading comet data no longer works:

```bash
wget -O comets.dat --post-data="obj_group=all&obj_kind=com&..." http://ssd.jpl.nasa.gov/sbdb_query.cgi
```

JPL has replaced their old CGI interface with a modern REST API. This repository provides alternative methods to download comet data using the new **SBDB (Small-Body Database) Query API**.

## Quick Start

### Option 1: Shell Script (Simple)
```bash
chmod +x download_comets.sh
./download_comets.sh
```

This downloads **3,868 comet records** and saves as both JSON and CSV files. Requires `curl` (or `wget`) and optionally `jq` for CSV conversion.

### Option 2: Python Script (Advanced)
```bash
# Download all comets as CSV (recommended)
python3 get_comet_data.py

# Download with specific options
python3 get_comet_data.py --format json --output my_comets --numbered-only

# Generate KStars-compatible format
python3 get_comet_data.py --format kstars --output kstars_comets

# Limit results for testing
python3 get_comet_data.py --limit 100 --format csv

# See all options
python3 get_comet_data.py --help
```

### Option 3: Direct API Call
```bash
# Basic comet data (using curl)
curl "https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name,e,a,q,i,per&sb-xfrag=1" > comets.json

# Convert to CSV with jq
curl "https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name,e,a,q&sb-xfrag=1" | jq -r '.fields | @csv' > comets.csv
curl "https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name,e,a,q&sb-xfrag=1" | jq -r '.data[] | @csv' >> comets.csv

# Using wget
wget -O comets.json "https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name,e,a,q,i&full-prec=1&sb-xfrag=1"
```

### Option 4: API Examples
```bash
chmod +x api_examples.sh
./api_examples.sh
```

Shows various API query examples with different filters and demonstrates usage patterns.

## What Changed?

| Old Method | New Method |
|------------|------------|
| `http://ssd.jpl.nasa.gov/sbdb_query.cgi` | `https://ssd-api.jpl.nasa.gov/sbdb_query.api` |
| POST requests with form data | GET requests with query parameters |
| Custom field codes | Named field parameters |
| Limited format options | JSON output (easily convertible to CSV) |
| Complex URL-encoded form data | Clean, readable query parameters |
| Unreliable CGI interface | Modern REST API with versioning |

## Current Data Available

As of October 2025, the JPL SBDB contains:
- **3,868 comet records** (excluding fragments)
- **4,315+ total comet records** (including fragments)
- Data from observations spanning 1835-2025
- Records updated regularly with new observations

## Available Data Fields

The new API provides extensive data fields for comets:

### Object Information
- `full_name` - Full designation and name
- `pdes` - Primary designation
- `name` - IAU name (if any)
- `prefix` - Comet prefix (P, C, D, A)
- `class` - Orbit classification

### Orbital Elements
- `e` - Eccentricity
- `a` - Semi-major axis (au)
- `q` - Perihelion distance (au)
- `i` - Inclination (deg)
- `om` - Longitude of ascending node (deg)
- `w` - Argument of perihelion (deg)
- `tp` - Time of perihelion passage (TDB)
- `per` - Orbital period (days)

### Additional Parameters
- `moid` - Minimum orbit intersection distance with Earth
- `t_jup` - Jupiter Tisserand parameter
- `H` - Absolute magnitude
- `first_obs` - First observation date
- `last_obs` - Last observation date
- `data_arc` - Data arc span (days)
- `n_obs_used` - Number of observations used

## Filtering Options

### Comet Types
```bash
# All comets (including fragments)
sb-kind=c

# Exclude comet fragments
sb-kind=c&sb-xfrag=1

# Numbered comets only
sb-kind=c&sb-ns=n

# Unnumbered comets only
sb-kind=c&sb-ns=u
```

### Orbital Classes
```bash
# Jupiter-family comets
sb-kind=c&sb-class=JFc

# Halley-type comets
sb-kind=c&sb-class=HTC

# Parabolic comets
sb-kind=c&sb-class=PAR
```

## Python Script Options

```bash
python3 get_comet_data.py [options]

Options:
  --format {json,csv}     Output format (default: csv)
  --output OUTPUT         Output filename without extension (default: comets)
  --include-fragments     Include comet fragments in results
  --numbered-only         Include only numbered comets
  --limit LIMIT           Limit number of results
```

### Examples

```bash
# Download all comets as CSV (recommended for most users)
python3 get_comet_data.py

# Download numbered comets only as JSON with custom filename
python3 get_comet_data.py --format json --numbered-only --output numbered_comets

# Download first 100 comets including fragments for testing
python3 get_comet_data.py --limit 100 --include-fragments --output sample_comets

# Get only Jupiter-family comets (requires custom filtering)
# Use the shell script or direct API call for orbital class filtering
```

## Files in This Repository

| File | Purpose | Usage |
|------|---------|-------|
| `download_comets.sh` | Simple automated download | `./download_comets.sh` |
| `get_comet_data.py` | Advanced Python client | `python3 get_comet_data.py [options]` |
| `api_examples.sh` | API usage examples | `./api_examples.sh` |
| `README.md` | This documentation | Read for instructions |
| `comets.csv` | Downloaded comet data (CSV) | Generated by scripts |
| `comets.json` | Downloaded comet data (JSON) | Generated by scripts |

## KStars Integration

The Python script now supports generating data in **KStars-compatible format**, allowing you to update the comet database in the KStars astronomy software.

### Generate KStars Format Data
```bash
# Download all comets in KStars format
python3 get_comet_data.py --format kstars --output kstars_comets

# This creates kstars_comets.dat with current JPL data
```

### Install in KStars
```bash
# Backup original KStars comet data
sudo cp /usr/share/kstars/comets.dat /usr/share/kstars/comets.dat.backup

# Install updated comet data
sudo cp kstars_comets.dat /usr/share/kstars/comets.dat

# Restart KStars to use the updated data
```

### What You Get
- **Current JPL data**: Latest orbital elements and observations
- **3,868 comet records**: Updated from JPL's live database
- **Compatible format**: Matches KStars' exact JSON structure
- **Regular updates**: Run the script periodically for fresh data

### KStars Data Fields
The generated file includes all fields that KStars expects:
- Orbital elements (q, e, i, w, om, tp)
- Object classification and magnitude data
- Period and distance information
- Compatible with KStars Solar System viewer

**Note**: The original KStars comet data contains 3,768 records. The JPL database now has 3,868 records, so you'll get 100+ additional comets with current orbital data.

## API Endpoints

### Primary API
- **SBDB Query API**: `https://ssd-api.jpl.nasa.gov/sbdb_query.api`
  - Purpose: Bulk queries for multiple objects
  - Best for: Downloading comet catalogs

### Individual Object API
- **SBDB API**: `https://ssd-api.jpl.nasa.gov/sbdb.api`
  - Purpose: Detailed data for specific objects
  - Best for: Getting comprehensive data for known comets

## Requirements

### For Shell Script (`download_comets.sh`)
- `curl` or `wget` - for downloading data
- `python3` - for JSON formatting and data parsing
- `jq` (optional) - for automatic CSV conversion
  ```bash
  # Install jq on Ubuntu/Debian
  sudo apt install jq
  
  # Install jq on macOS
  brew install jq
  ```

### For Python Script (`get_comet_data.py`)
- Python 3.6+
- `requests` library

Install Python dependencies:
```bash
pip3 install requests
```

### For Direct API Access
- Any HTTP client (`curl`, `wget`, browser, etc.)
- Optional: `jq` for JSON-to-CSV conversion

## Output Formats

### JSON Format (Raw API Response)
```json
{
  "signature": {
    "source": "NASA/JPL SBDB (Small-Body DataBase) Query API",
    "version": "1.0"
  },
  "count": 3868,
  "fields": [
    "full_name", "pdes", "name", "prefix", "class",
    "epoch", "e", "a", "q", "i", "om", "w", "tp", "per",
    "moid", "t_jup", "H", "first_obs", "last_obs", "data_arc", "n_obs_used"
  ],
  "data": [
    [
      "    1P/Halley", "1P", "Halley", "P", "HTC",
      "2439907.5", ".9679221169240834", "17.93003431157555", ".575157544193894",
      "162.1951462980701", "59.07198712310091", "112.2128395742619",
      "2446469.698337207711", "27731.29225689917", ".0744805", "-0.598", null,
      "1835-08-21", "1994-01-11", "57852", 8518
    ]
    // ... more comets
  ]
}
```

### CSV Format (Converted)
```csv
full_name,pdes,name,prefix,class,epoch,e,a,q,i,om,w,tp,per,moid,t_jup,H,first_obs,last_obs,data_arc,n_obs_used
    1P/Halley,1P,Halley,P,HTC,2439907.5,.9679221169240834,17.93003431157555,.575157544193894,162.1951462980701,59.07198712310091,112.2128395742619,2446469.698337207711,27731.29225689917,.0744805,-0.598,,1835-08-21,1994-01-11,57852,8518
    2P/Encke,2P,Encke,P,ETc,2459824.5,.8479045643066414,2.21967917165898,.3376030707129459,11.42908482022491,334.2193343019926,187.1096554650546,2460239.543731008880,1207.907664979198,.167197,3.023,,2018-11-05,2025-09-24,2515,622
...
```

**Note**: The API returns data as arrays rather than objects for efficiency. The `fields` array provides column headers, and each element in the `data` array corresponds to those fields.

## Advanced Usage

### Custom Field Selection
```bash
# Select specific fields
curl "https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name,e,q,per"

# Full precision values
curl "https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name,e,q&full-prec=1"
```

### Complex Filtering
```python
import requests

# Custom constraints using Python
params = {
    'sb-kind': 'c',
    'fields': 'full_name,e,q,per',
    'sb-cdata': '{"AND":["q|LT|1.0","per|LT|10000"]}'  # q < 1.0 AU and period < 10000 days
}

response = requests.get('https://ssd-api.jpl.nasa.gov/sbdb_query.api', params=params)
data = response.json()
```

## Troubleshooting

### Common Issues

1. **Empty Results**
   - Check your filtering parameters
   - Verify field names are correct (case-sensitive)
   - Try without filters first: `sb-kind=c` only

2. **Timeout Errors**
   - Use limit parameter for large queries: `--limit 1000`
   - The full dataset (3,868 comets) downloads in ~10-30 seconds normally
   - Implement retry logic for production use

3. **JSON Parsing Errors**
   - Check API response format with: `curl "[URL]" | head -20`
   - Verify the endpoint URL is correct
   - Check for network connectivity issues

4. **CSV Conversion Issues**
   - Ensure `jq` is installed for shell script CSV conversion
   - Use Python script for guaranteed CSV output: `python3 get_comet_data.py --format csv`
   - Manual conversion: Extract `fields` for headers, `data` arrays for rows

5. **Permission Errors**
   - Make scripts executable: `chmod +x *.sh`
   - Check write permissions in current directory

### Testing the Setup

```bash
# Test with small dataset first
python3 get_comet_data.py --limit 5 --format csv

# Test direct API access
curl "https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name&limit=3"

# Verify data format
./api_examples.sh
```

### Getting Help

- API Documentation: https://ssd-api.jpl.nasa.gov/doc/
- SBDB Query API: https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html
- Field Reference: https://ssd-api.jpl.nasa.gov/doc/sbdb_filter.html

### Contact
- JPL API Support: contact-ssd-api@jpl.nasa.gov

## Migration Guide

If you're migrating from the old command, here's a mapping:

| Old Parameter | New Equivalent | Notes |
|---------------|----------------|-------|
| `obj_kind=com` | `sb-kind=c` | Filter for comets only |
| `obj_numbered=all` | (no parameter) | Include both numbered and unnumbered by default |
| `obj_numbered=numbered` | `sb-ns=n` | Numbered objects only |
| `obj_numbered=unnumbered` | `sb-ns=u` | Unnumbered objects only |
| Custom field codes (e.g., `AcBdBiBg`) | `fields=full_name,e,a,q,i,...` | Use named fields (see Available Data Fields) |
| `format_option=full` | `full-prec=1` | Full precision output |
| `table_format=CSV` | Convert JSON to CSV | API returns JSON, convert with `jq` or Python script |
| `max_rows=10` | `limit=10` | Limit number of results |
| Complex POST form data | Clean GET parameters | Much simpler URL construction |

### Example Migration

**Old command:**
```bash
wget -O comets.dat --post-data="obj_group=all&obj_kind=com&obj_numbered=all&OBJ_field=0&OBJ_op=0&OBJ_value=&ORB_field=0&ORB_op=0&ORB_value=&combine_mode=AND&c1_group=OBJ&c1_item=Af&c1_op=!%3D&c1_value=D&c2_group=OBJ&c2_item=Ae&c2_op=!%3D&c2_value=SOHO&c_fields=AcBdBiBgBjBlBkBqBbAiAjAgAkAlApAqArAsBsBtCh&table_format=CSV&max_rows=10&format_option=full" http://ssd.jpl.nasa.gov/sbdb_query.cgi
```

**New equivalent:**
```bash
# Simple version
curl "https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name,e,a,q,i,per&full-prec=1&limit=10" > comets.json

# Or use the Python script
python3 get_comet_data.py --limit 10 --format csv
```

## License

This code is provided as-is for educational and research purposes. The JPL SBDB data is publicly available and maintained by NASA/JPL.