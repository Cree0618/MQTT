import pandas as pd

# Load the CSV file
file_path = 'Neopravnena-sidla_PREHLED_LOCAL_converted.csv'
unauthorized_addresses = pd.read_csv(file_path, delimiter=';')

# Load the data from the API (assuming it's stored in a DataFrame called 'api_data')
# If it's not already in a DataFrame, we need to create it first
api_data = pd.DataFrame(all_subjects)

# Function to clean and standardize company names
def clean_name(name):
    return str(name).lower().strip()

# Clean company names in both DataFrames
unauthorized_addresses['Název_clean'] = unauthorized_addresses['Název'].apply(clean_name)
api_data['Name_clean'] = api_data['Name'].apply(clean_name)

# Find companies in the CSV file that are not in the API data
in_csv_not_in_api = unauthorized_addresses[~unauthorized_addresses['IČO'].isin(api_data['IČO'])]

# Find companies in the API data that are not in the CSV file
in_api_not_in_csv = api_data[~api_data['IČO'].isin(unauthorized_addresses['IČO'])]

# Find companies with matching IČO but different names
matching_ico_diff_name = pd.merge(unauthorized_addresses, api_data, on='IČO', how='inner')
matching_ico_diff_name = matching_ico_diff_name[matching_ico_diff_name['Název_clean'] != matching_ico_diff_name['Name_clean']]

# Save the results to CSV files
in_csv_not_in_api.to_csv('in_csv_not_in_api.csv', index=False)
in_api_not_in_csv.to_csv('in_api_not_in_csv.csv', index=False)
matching_ico_diff_name.to_csv('matching_ico_diff_name.csv', index=False)

# Print summary
print(f"Companies in CSV but not in API: {len(in_csv_not_in_api)}")
print(f"Companies in API but not in CSV: {len(in_api_not_in_csv)}")
print(f"Companies with matching IČO but different names: {len(matching_ico_diff_name)}")

# Display a few examples from each category
print("\nExamples of companies in CSV but not in API:")
print(in_csv_not_in_api[['IČO', 'Název']].head())

print("\nExamples of companies in API but not in CSV:")
print(in_api_not_in_csv[['IČO', 'Name']].head())

print("\nExamples of companies with matching IČO but different names:")
print(matching_ico_diff_name[['IČO', 'Název', 'Name']].head())