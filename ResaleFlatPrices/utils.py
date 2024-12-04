import re
import requests
import json
import time
import yaml
import pandas as pd

with open("ResaleFlatPrices\config.yaml") as file:
    try:
        config = yaml.safe_load(file)
        print(config)
    except yaml.YAMLError as exc:
        print(exc)

ACRONYM_REPLACEMENTS = {
    r"\bDR\b": "DRIVE", r"\bST\b": "STREET", r"\bRD\b": "ROAD", r"\bAVE\b": "AVENUE", r"\bNTH\b": "NORTH", r"\bSTH\b": "SOUTH",
    r"\bUPP\b": "UPPER", r"\bCRES\b": "CRESCENT", r"\bJLN\b": "JALAN", r"\bTG\b": "TANJONG", r"\bBT\b": "BUKIT", r"\bKG\b": "KAMPONG",
    r"\bCL\b": "CLOSE", r"\bPL\b": "PLACE", r"\bCTRL\b": "CENTRAL", r"\bC'WEALTH\b": "COMMONWEALTH"
}

def preprocess_street_name(street_name, block_number):
    """Preprocess the street name by replacing acronyms and prefixing with the block number."""
    # Replace all occurrences of acronyms using regular expressions
    for acronym, full_name in ACRONYM_REPLACEMENTS.items():
        print(acronym, full_name)
        street_name = re.sub(acronym, full_name, street_name)

    # Prefix the processed street name with the block number
    return f"{block_number} {street_name}"

def find_postal(lst, filename):
    '''With the block number and street name, get the full address of the HDB flat,
    including the postal code, geographical coordinates (lat/long)'''
    
    # Initialize an empty DataFrame
    file = pd.DataFrame()
    
    for index, add in enumerate(lst):
        # Do not need to change the URL
        url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={add}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
        print(index, url)
        
        # Retrieve information from website
        response = requests.get(url)
        data = json.loads(response.text)
        
        temp_df = pd.DataFrame.from_dict(data["results"])
        # The "add" is the address that was used to search on the website
        temp_df["address"] = add
        
        # Append the current DataFrame to the main DataFrame
        file = pd.concat([file, temp_df], ignore_index=True)

        # Save the DataFrame to a CSV file every 1000 iterations
        if index % 1000 == 0:
            file.to_csv(filename + '.csv', index=False)
            print(f"Saved {index} addresses")
            time.sleep(1)
            
    # Save the resulting DataFrame to a CSV file
    file.to_csv(filename + '.csv', index=False)

def save_results_to_csv(results, output_file):
    """
    Saves the results dictionary to a CSV file.
    """
    # Convert the results dictionary to a DataFrame
    df = pd.DataFrame.from_dict(results, orient='index', columns=['House', 'Nearest Amenity', 'Distance (km)'])
    # Save the DataFrame to a CSV file
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

def find_nearest(house, amenity):
    """
    this function finds the nearest locations from the 2nd table from the 1st address
    Both are dataframes with a specific format:
        1st column: any string column ie addresses taken from the "find_postal_address.py"
        2nd column: latitude (float)
        3rd column: longitude (float)
    """
    results = {}
    # first column must be address
    for index, flat in enumerate(house.iloc[:,0]):
        print(index, flat)
        # 2nd column must be latitude, 3rd column must be longitude
        flat_loc = (house.iloc[index,1],house.iloc[index,2])
        flat_amenity = ['','',100]

        for ind, eachloc in enumerate(amenity.iloc[:,0]):
            amenity_loc = (amenity.iloc[ind,1],amenity.iloc[ind,2])
            distance = geodesic(flat_loc,amenity_loc)

            if distance < flat_amenity[2]:
                flat_amenity[0] = flat
                flat_amenity[1] = eachloc
                flat_amenity[2] = distance

        results[flat] = flat_amenity
        if index % 1000 == 0:
            print(f"Saved {index} addresses")
            save_results_to_csv(results, 'ResaleFlatPrices/datasets/nearest_schools.csv')
            time.sleep(1)
    return results