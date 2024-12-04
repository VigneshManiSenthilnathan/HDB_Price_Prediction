import pandas as pd
from utils import preprocess_street_name, find_postal
    

def process_addresses_resale_flats(csv_file, filename):
    df_resale = pd.read_csv(csv_file)
    df_resale["full_address"] = df_resale.apply(lambda x: preprocess_street_name(x["street_name"], x["block"]), axis=1)
    addresses = list(df_resale["full_address"])
    unique_addresses = list(set(addresses))
    print(f"Number of unique addresses: {len(unique_addresses)}")
    find_postal(unique_addresses, filename)
    
    print(f"Geocoded data saved to", filename + '.csv')

def process_addresses_schools(csv_file, filename):
    df_resale = pd.read_csv(csv_file)
    addresses = list(df_resale["address"])
    print(f"Number of unique addresses: {len(addresses)}")
    find_postal(addresses, filename)
    
    print(f"Geocoded data saved to", filename + '.csv')

# process_addresses_resale_flats('ResaleFlatPrices\datasets\Resale flat prices based on registration date from Jan-2017 onwards.csv', "ResaleFlatPrices/preprocessing/geocoded_addresses")
process_addresses_schools('ResaleFlatPrices\datasets\Generalinformationofschools.csv', "ResaleFlatPrices/preprocessing/geocoded_schools")