#!/bin/bash

# Simple direct API call examples for JPL comet data
# These replace the old wget command that no longer works

echo "=== Direct JPL SBDB API Examples ==="
echo

# Example 1: Basic comet query - all comets with essential fields
echo "Example 1: All comets with basic orbital elements"
BASIC_URL="https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name,e,a,q,i,per&sb-xfrag=1"
echo "URL: $BASIC_URL"
echo

# Example 2: Named comets only with more details
echo "Example 2: Named comets only with detailed information"
NAMED_URL="https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&sb-ns=n&fields=full_name,name,class,e,a,q,i,per,t_jup,first_obs,last_obs"
echo "URL: $NAMED_URL"
echo

# Example 3: Jupiter-family comets only
echo "Example 3: Jupiter-family comets only"
JFC_URL="https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&sb-class=JFc&fields=full_name,e,a,q,per,t_jup"
echo "URL: $JFC_URL"
echo

# Example 4: Comets with perihelion distance < 1 AU (sun-grazers and close approaches)
echo "Example 4: Comets with perihelion distance < 1 AU"
CLOSE_URL="https://ssd-api.jpl.nasa.gov/sbdb_query.api?sb-kind=c&fields=full_name,e,a,q,per&sb-cdata=%7B%22AND%22%3A%5B%22q%7CLT%7C1.0%22%5D%7D"
echo "URL: $CLOSE_URL"
echo "Note: sb-cdata contains URL-encoded JSON: {\"AND\":[\"q|LT|1.0\"]}"
echo

# Test one of the examples
echo "=== Testing Example 1 (first 3 results) ==="
if command -v curl >/dev/null 2>&1; then
    curl -s "$BASIC_URL" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'Total comets found: {data.get(\"count\", 0)}')
    if 'data' in data and data['data']:
        print('First 3 comets:')
        fields = data.get('fields', [])
        for i, record in enumerate(data['data'][:3]):
            print(f'  {i+1}. {record[0] if record else \"N/A\"}')
    else:
        print('No data found')
except Exception as e:
    print(f'Error: {e}')
"
else
    echo "curl not available - install curl to test the API calls"
fi

echo
echo "=== Usage Instructions ==="
echo "To download data:"
echo "  curl \"[URL]\" > comets.json"
echo "  wget -O comets.json \"[URL]\""
echo
echo "For CSV conversion:"
echo "  curl \"[URL]\" | jq -r '.fields | @csv' > comets.csv"
echo "  curl \"[URL]\" | jq -r '.data[] | @csv' >> comets.csv"
echo
echo "Field reference: https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html"