import pandas as pd

from geopy.distance import geodesic
from utils import save_results_to_csv, find_nearest

def import_and_prepare_data(file1, file2):
    """
    This function imports the 2 csv files and returns them as dataframes
    file1: ResaleFlatPrices\preprocessing\geocoded_addresses.csv
    file 2: ResaleFlatPrices\preprocessing\geocoded_schools.csv or ResaleFlatPrices\datasets\MRT Stations.csv
    """
    house = pd.read_csv(file1)
    amenity = pd.read_csv(file2)

    # for house find unique addresses
    house.drop_duplicates(subset=['address'], inplace=True)
    house.reset_index(drop=True, inplace=True)
    print(f"Number of unique addresses: {len(house)}")

    house = house[['address','LATITUDE','LONGITUDE']]
    amenity = amenity[['address','LATITUDE','LONGITUDE']]
    return house, amenity

flats = 'ResaleFlatPrices\preprocessing\geocoded_addresses.csv'
schools = 'ResaleFlatPrices\preprocessing\geocoded_schools.csv'
mrt = 'ResaleFlatPrices\datasets\MRT Stations.csv'

house, amenity = import_and_prepare_data(flats, schools)
results = find_nearest(house, amenity)
save_results_to_csv(results, 'ResaleFlatPrices/datasets/nearest_schools.csv')
print(results)