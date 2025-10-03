#!/usr/bin/env python3
"""
Modern JPL SBDB API client for downloading comet data.

This script replaces the old wget command that no longer works:
wget -O comets.dat --post-data="..." http://ssd.jpl.nasa.gov/sbdb_query.cgi

The old CGI interface has been replaced with a modern REST API.
"""

import requests
import json
import csv
import sys
from urllib.parse import urlencode

def get_comet_data(output_format='json', include_fragments=False, numbered_only=False):
    """
    Fetch comet data from JPL's SBDB Query API.
    
    Args:
        output_format (str): 'json' or 'csv'
        include_fragments (bool): Whether to include comet fragments
        numbered_only (bool): Whether to limit to numbered comets only
    
    Returns:
        dict: API response data
    """
    
    # Base URL for the SBDB Query API
    base_url = "https://ssd-api.jpl.nasa.gov/sbdb_query.api"
    
    # Parameters for the API call
    params = {
        'sb-kind': 'c',  # Comets only
        'fields': ','.join([
            'full_name',     # Full designation and name
            'pdes',          # Primary designation
            'name',          # IAU name (if any)
            'prefix',        # Comet prefix (P, C, D)
            'class',         # Orbit classification
            'epoch',         # Epoch of osculation
            'e',             # Eccentricity
            'a',             # Semi-major axis (au)
            'q',             # Perihelion distance (au)
            'i',             # Inclination (deg)
            'om',            # Longitude of ascending node (deg)
            'w',             # Argument of perihelion (deg)
            'tp',            # Time of perihelion passage (TDB)
            'per',           # Orbital period (days)
            'moid',          # Minimum orbit intersection distance with Earth
            't_jup',         # Jupiter Tisserand parameter
            'H',             # Absolute magnitude
            'first_obs',     # First observation date
            'last_obs',      # Last observation date
            'data_arc',      # Data arc span (days)
            'n_obs_used'     # Number of observations used
        ]),
        'full-prec': '1'  # Full precision output
    }
    
    # Optional filters
    if not include_fragments:
        params['sb-xfrag'] = '1'  # Exclude fragments
    
    if numbered_only:
        params['sb-ns'] = 'n'  # Numbered objects only
    
    try:
        print(f"Fetching comet data from JPL SBDB API...")
        print(f"URL: {base_url}")
        print(f"Parameters: {params}")
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' in data:
            print(f"Successfully retrieved {len(data['data'])} comet records.")
            return data
        else:
            print("Warning: No data field in response")
            print("Response:", json.dumps(data, indent=2)[:500] + "...")
            return data
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None

def save_as_csv(data, filename='comets.csv'):
    """Save the comet data as CSV file."""
    if not data or 'data' not in data or 'fields' not in data:
        print("No data to save")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if not data['data']:
                print("No comet records found")
                return False
                
            # Get field names from the API response
            fieldnames = data['fields']
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(fieldnames)
            
            # Write data rows
            writer.writerows(data['data'])
            
        print(f"Data saved to {filename}")
        return True
        
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def save_as_json(data, filename='comets.json'):
    """Save the comet data as JSON file."""
    if not data:
        print("No data to save")
        return False
    
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2)
        
        print(f"Data saved to {filename}")
        return True
        
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def convert_to_kstars_format(data):
    """
    Convert JPL SBDB data to KStars format.
    
    KStars expects these fields in order:
    ["full_name", "epoch.mjd", "q", "e", "i", "w", "om", "tp", "orbit_id", "neo",
     "M1", "M2", "diameter", "extent", "albedo", "rot_per", "per.y", "moid", "H", "G", "class"]
    """
    if not data or 'data' not in data or 'fields' not in data:
        return None
    
    # Map JPL fields to KStars fields
    jpl_fields = data['fields']
    kstars_fields = [
        "full_name", "epoch.mjd", "q", "e", "i", "w", "om", "tp", "orbit_id", "neo",
        "M1", "M2", "diameter", "extent", "albedo", "rot_per", "per.y", "moid", "H", "G", "class"
    ]
    
    # Create field mapping (JPL index -> KStars value)
    field_map = {}
    for i, field in enumerate(jpl_fields):
        if field in ['full_name']:
            field_map['full_name'] = i
        elif field in ['epoch']:
            field_map['epoch.mjd'] = i
        elif field in ['q']:
            field_map['q'] = i
        elif field in ['e']:
            field_map['e'] = i
        elif field in ['i']:
            field_map['i'] = i
        elif field in ['w']:
            field_map['w'] = i
        elif field in ['om']:
            field_map['om'] = i
        elif field in ['tp']:
            field_map['tp'] = i
        elif field in ['moid']:
            field_map['moid'] = i
        elif field in ['H']:
            field_map['H'] = i
        elif field in ['class']:
            field_map['class'] = i
        elif field in ['per']:  # Convert days to years
            field_map['per.y'] = i
    
    # Convert data rows
    kstars_data = []
    for row in data['data']:
        kstars_row = []
        for field in kstars_fields:
            if field in field_map:
                value = row[field_map[field]]
                # Special conversions
                if field == 'per.y' and value is not None:
                    # Convert period from days to years
                    try:
                        value = float(value) / 365.25
                    except (ValueError, TypeError):
                        value = None
                elif field == 'epoch.mjd' and value is not None:
                    # Epoch might need conversion from JD to MJD
                    try:
                        # If it's already MJD, keep it; if JD, convert
                        epoch_val = float(value)
                        if epoch_val > 2400000:  # Likely Julian Date
                            value = epoch_val - 2400000.5  # Convert JD to MJD
                        else:
                            value = epoch_val  # Already MJD
                    except (ValueError, TypeError):
                        value = None
                kstars_row.append(value)
            else:
                # Field not available in JPL data, use null
                kstars_row.append(None)
        
        kstars_data.append(kstars_row)
    
    # Create KStars format structure
    kstars_format = {
        "signature": f"KStars comet data converted from JPL SBDB API",
        "fields": kstars_fields,
        "data": kstars_data,
        "count": len(kstars_data)
    }
    
    return kstars_format

def save_as_kstars(data, filename='comets.dat'):
    """Save the comet data in KStars JSON format."""
    if not data:
        print("No data to save")
        return False
    
    try:
        kstars_data = convert_to_kstars_format(data)
        if not kstars_data:
            print("Error converting to KStars format")
            return False
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(kstars_data, jsonfile, separators=(',', ':'))  # Compact JSON like KStars
        
        print(f"Data saved to {filename} in KStars format")
        print(f"Compatible with KStars - can replace /usr/share/kstars/comets.dat")
        return True
        
    except Exception as e:
        print(f"Error saving KStars format: {e}")
        return False

def main():
    """Main function to demonstrate usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download comet data from JPL SBDB API')
    parser.add_argument('--format', choices=['json', 'csv', 'kstars'], default='csv',
                        help='Output format: csv, json, or kstars (for KStars astronomy software)')
    parser.add_argument('--output', '-o', default='comets',
                        help='Output filename (without extension)')
    parser.add_argument('--include-fragments', action='store_true',
                        help='Include comet fragments in results')
    parser.add_argument('--numbered-only', action='store_true',
                        help='Include only numbered comets')
    parser.add_argument('--limit', type=int,
                        help='Limit number of results')
    
    args = parser.parse_args()
    
    # Fetch the data
    data = get_comet_data(
        output_format=args.format,
        include_fragments=args.include_fragments,
        numbered_only=args.numbered_only
    )
    
    if not data:
        sys.exit(1)
    
    # Apply limit if specified
    if args.limit and 'data' in data:
        data['data'] = data['data'][:args.limit]
        print(f"Limited results to first {args.limit} records")
    
    # Save in requested format
    if args.format == 'csv':
        filename = f"{args.output}.csv"
        success = save_as_csv(data, filename)
    elif args.format == 'kstars':
        filename = f"{args.output}.dat"
        success = save_as_kstars(data, filename)
    else:
        filename = f"{args.output}.json"
        success = save_as_json(data, filename)
    
    if success:
        print(f"\nComet data successfully downloaded and saved to {filename}")
        if 'data' in data:
            print(f"Total records: {len(data['data'])}")
        if args.format == 'kstars':
            print("\nTo use with KStars:")
            print(f"sudo cp {filename} /usr/share/kstars/comets.dat")
            print("Then restart KStars to use the updated comet data.")
    else:
        sys.exit(1)

# Example usage for direct import
def get_all_comets_csv():
    """Simple function to get all comet data and save as CSV."""
    data = get_comet_data()
    if data:
        save_as_csv(data, 'comets.csv')
        return True
    return False

if __name__ == '__main__':
    main()