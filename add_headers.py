import pandas as pd

columns = ['name', 'city', 'price', 'checkin', 'checkout', 'rating', 'plan', 'star_rating', 'check_in', 'check_out', 'rooms', 'restaurants', 'bars']

# Read the existing data from the CSV file
try:
    existing_data = pd.read_csv('deals.csv', header=None)
except pd.errors.EmptyDataError:
    existing_data = pd.DataFrame()

# Add the headers to the DataFrame
existing_data.columns = columns

# Write the DataFrame back to the CSV file with headers
existing_data.to_csv('deals.csv', index=False, header=True)