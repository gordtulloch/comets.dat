#!/bin/bash

# Modern replacement for the old JPL comet data wget command
# The old command no longer works:
# wget -O comets.dat --post-data="..." http://ssd.jpl.nasa.gov/sbdb_query.cgi

echo "=== JPL SBDB Comet Data Download ==="
echo "Modern API replacement for the old CGI interface"
echo

# Base URL for the new SBDB Query API
BASE_URL="https://ssd-api.jpl.nasa.gov/sbdb_query.api"

# Build the query parameters
# sb-kind=c : comets only
# sb-xfrag=1 : exclude comet fragments (similar to the old filters)
# fields= : specify which data fields to include
PARAMS="sb-kind=c&sb-xfrag=1&full-prec=1"
FIELDS="full_name,pdes,name,prefix,class,epoch,e,a,q,i,om,w,tp,per,moid,t_jup,H,first_obs,last_obs,data_arc,n_obs_used"
PARAMS="${PARAMS}&fields=${FIELDS}"

# Full URL
FULL_URL="${BASE_URL}?${PARAMS}"

echo "Fetching comet data from JPL SBDB API..."
echo "URL: $BASE_URL"
echo

# Method 1: Get JSON data
echo "=== Downloading JSON format ==="
if command -v curl >/dev/null 2>&1; then
    echo "Using curl..."
    curl -s "$FULL_URL" | python3 -m json.tool > comets.json
    if [ $? -eq 0 ]; then
        echo "✓ JSON data saved to comets.json"
        # Count records
        RECORD_COUNT=$(python3 -c "import json; data=json.load(open('comets.json')); print(len(data.get('data', [])))" 2>/dev/null)
        if [ ! -z "$RECORD_COUNT" ]; then
            echo "  Records found: $RECORD_COUNT"
        fi
    else
        echo "✗ Failed to download JSON data"
    fi
elif command -v wget >/dev/null 2>&1; then
    echo "Using wget..."
    wget -q -O comets.json "$FULL_URL"
    if [ $? -eq 0 ]; then
        echo "✓ JSON data saved to comets.json"
        # Pretty print the JSON
        python3 -m json.tool comets.json > comets_formatted.json && mv comets_formatted.json comets.json
        # Count records
        RECORD_COUNT=$(python3 -c "import json; data=json.load(open('comets.json')); print(len(data.get('data', [])))" 2>/dev/null)
        if [ ! -z "$RECORD_COUNT" ]; then
            echo "  Records found: $RECORD_COUNT"
        fi
    else
        echo "✗ Failed to download JSON data"
    fi
else
    echo "✗ Neither curl nor wget is available"
fi

echo

# Method 2: Convert to CSV if jq is available
if command -v jq >/dev/null 2>&1 && [ -f comets.json ]; then
    echo "=== Converting to CSV format ==="
    echo "Converting JSON to CSV using jq..."
    
    # Extract CSV header from fields array
    jq -r '.fields | @csv' comets.json > comets.csv 2>/dev/null
    
    # Extract data rows
    jq -r '.data[] | @csv' comets.json >> comets.csv 2>/dev/null
    
    if [ $? -eq 0 ] && [ -s comets.csv ]; then
        echo "✓ CSV data saved to comets.csv"
        LINE_COUNT=$(wc -l < comets.csv)
        echo "  CSV lines: $LINE_COUNT (including header)"
    else
        echo "✗ Failed to convert to CSV"
    fi
elif [ -f comets.json ]; then
    echo "=== jq not available for CSV conversion ==="
    echo "Install jq for automatic CSV conversion, or use the Python script:"
    echo "  python3 get_comet_data.py --format csv"
else
    echo "=== No JSON file to convert ==="
fi

echo

# Show sample of the data
if [ -f comets.json ]; then
    echo "=== Sample of downloaded data ==="
    echo "First comet record:"
    python3 -c "
import json
try:
    with open('comets.json', 'r') as f:
        data = json.load(f)
    if 'data' in data and 'fields' in data and len(data['data']) > 0:
        fields = data['fields']
        first_record = data['data'][0]
        for i, field in enumerate(fields):
            if i < len(first_record) and first_record[i] is not None:
                print(f'  {field}: {first_record[i]}')
    else:
        print('  No data records found')
except Exception as e:
    print(f'  Error reading data: {e}')
" 2>/dev/null
fi

echo
echo "=== Summary ==="
echo "The old JPL CGI interface has been replaced with a modern REST API."
echo "Files created:"
if [ -f comets.json ]; then
    echo "  ✓ comets.json - Full data in JSON format"
fi
if [ -f comets.csv ]; then
    echo "  ✓ comets.csv - Data in CSV format"
fi
echo
echo "For more advanced usage, use the Python script:"
echo "  python3 get_comet_data.py --help"
echo
echo "API Documentation: https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html"