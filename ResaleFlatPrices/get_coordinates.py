import re
import requests
import pandas as pd
import time

from secret import API_KEY_1, API_KEY_2_TEST, API_KEY_2_PROD

# Define the APIs and their keys
API1 = "https://geocode.maps.co/search"
API_KEY_1_SUFFIX = f"api_key={API_KEY_1}"

API2_URL = "https://api.radar.io/v1/geocode/forward"
API2_HEADERS = {
    "Authorization": f"{API_KEY_2_TEST}"
}

# Define Singapore's latitude and longitude range
SINGAPORE_LAT_RANGE = (1.1304, 1.4504)
SINGAPORE_LON_RANGE = (103.6000, 104.0000)

# Acronyms to be replaced in street names (with word boundaries)
ACRONYM_REPLACEMENTS = {
    r"\bDR\b": "DRIVE", r"\bST\b": "STREET", r"\bRD\b": "ROAD", r"\bAVE\b": "AVENUE", r"\bNTH\b": "NORTH", r"\bSTH\b": "SOUTH",
    r"\bUPP\b": "UPPER", r"\bCRES\b": "CRESCENT", r"\bJLN\b": "JALAN", r"\bTG\b": "TANJONG", r"\bBT\b": "BUKIT", r"\bKG\b": "KAMPONG",
    r"\bCL\b": "CLOSE", r"\bPL\b": "PLACE", r"\bCTRL\b": "CENTRAL", r"\bC'WEALTH\b": "COMMONWEALTH"
}

def preprocess_street_name(street_name, block_number):
    """Preprocess the street name by replacing acronyms and prefixing with the block number."""
    # Replace all occurrences of acronyms using regular expressions
    for acronym, full_name in ACRONYM_REPLACEMENTS.items():
        street_name = re.sub(acronym, full_name, street_name)

    # Prefix the processed street name with the block number
    return f"{block_number} {street_name}"

def is_within_singapore(lat, lon):
    """Check if the given latitude and longitude are within Singapore's range."""
    return SINGAPORE_LAT_RANGE[0] <= lat <= SINGAPORE_LAT_RANGE[1] and SINGAPORE_LON_RANGE[0] <= lon <= SINGAPORE_LON_RANGE[1]

def get_coordinates_from_api1(address):
    """Fetch coordinates from API 1."""
    QUERY = f"q={address}"
    API1_URL = f"{API1}?{QUERY}&{API_KEY_1_SUFFIX}"
    print(f"Calling API 1 for address: {address}")
    try:
        response = requests.get(API1_URL)
        time.sleep(1.1)  # Ensure we don't exceed the rate limit
        response.raise_for_status()
        results = response.json()
        if results:
            # Use the first result
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            return lat, lon
    except Exception as e:
        print(f"API 1 failed for {address}: {e}")
    return None, None

def get_coordinates_from_api2(address):
    """Fetch coordinates from API 2."""
    try:
        params = {"query": address, "country": "SG"}
        time.sleep(1.1)  # Ensure we don't exceed the rate limit
        response = requests.get(API2_URL, headers=API2_HEADERS, params=params)
        response.raise_for_status()
        results = response.json()
        if "addresses" in results and results["addresses"]:
            # Use the first address
            lat = results["addresses"][0]["latitude"]
            lon = results["addresses"][0]["longitude"]
            return lat, lon
    except Exception as e:
        print(f"API 2 failed for {address}: {e}")
    return None, None

def get_coordinates(address):
    """Get coordinates for an address using both APIs."""
    print(f"Processing address: {address}")
    # Try API 1
    lat, lon = get_coordinates_from_api1(address)
    
    # If API 1 fails or returns invalid coordinates
    if lat is None or lon is None or not is_within_singapore(lat, lon):
        print(f"API 1 failed or invalid for {address}, falling back to API 2.")
        # Use API 2 to fetch the street name
        api2_lat, api2_lon = None, None
        try:
            params = {"query": address, "country": "SG"}
            response = requests.get(API2_URL, headers=API2_HEADERS, params=params)
            time.sleep(1.1)  # Delay to avoid rate limiting
            response.raise_for_status()
            results = response.json()
            if "addresses" in results and results["addresses"]:
                api2_lat = results["addresses"][0]["latitude"]
                api2_lon = results["addresses"][0]["longitude"]
                street_name = results["addresses"][0].get("addressLabel")
                print(f"API 2 returned street name: {street_name}")
                
                if street_name:  # Retry API 1 with the improved street name
                    lat, lon = get_coordinates_from_api1(street_name)
        except Exception as e:
            print(f"API 2 failed for {address}: {e}")

        # If the retry with API 1 also fails, fall back to API 2's lat/lon
        if (lat is None or lon is None or not is_within_singapore(lat, lon)) and api2_lat and api2_lon:
            lat, lon = api2_lat, api2_lon

    # If no valid coordinates are found
    if lat is None or lon is None or not is_within_singapore(lat, lon):
        print(f"Address '{address}' could not be geocoded within Singapore.")

    return lat, lon

def process_addresses(csv_file):
    """Process the addresses from the CSV, remove duplicates, and geocode them."""
    # Load data from CSV
    df = pd.read_csv(csv_file)
    
    # Extract unique street names and blocks
    unique_addresses = df[['block', 'street_name']].drop_duplicates()
    
    # Dictionary to store the geocoded addresses
    geocoded_data = []

    # Process each unique street name
    counter = 0
    for _, row in unique_addresses.iterrows():
        block_number = row['block']
        street_name = row['street_name']
        
        # Preprocess street name and prefix it with the block number
        full_address = preprocess_street_name(street_name, block_number)
        
        # Get coordinates for the full address
        lat, lon = get_coordinates(full_address)
        
        if lat is not None and lon is not None:
            geocoded_data.append({'street_name': full_address, 'latitude': lat, 'longitude': lon})
        
        counter += 1
        if counter % 50 == 0:
            print(f"Processed {counter} addresses.")
            geocoded_df = pd.DataFrame(geocoded_data)
            geocoded_df.to_excel("preprocessing/geocoded_addresses.xlsx", index=False)
            print(f"Geocoded data saved to 'preprocessing/geocoded_addresses.xlsx'")
            time.sleep(1.1)

    # Convert the geocoded data to a DataFrame
    geocoded_df = pd.DataFrame(geocoded_data)
    
    # Save the geocoded data to an Excel file for future use
    geocoded_df.to_excel("preprocessing/geocoded_addresses.xlsx", index=False)
    
    print(f"Geocoded data saved to 'preprocessing/geocoded_addresses.xlsx'")

process_addresses('Resale flat prices based on registration date from Jan-2017 onwards.csv')