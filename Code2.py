"""
This code generates a visualization of products that are almost identical 
based on thier name and outputs the results to a CSV file. 
After it identifies and highlights the cheapest product 
from the set of similar products.
"""

import pandas as pd
from fuzzywuzzy import fuzz, process

# Load the CSV files
coles_file_path = 'Coles.csv'
woolworths_file_path = 'Woolworths.csv'


# Read the CSV files into DataFrames
coles_df = pd.read_csv(coles_file_path)
woolworths_df = pd.read_csv(woolworths_file_path)

# Helper function to clean item names
def clean_item_name(name):
    if isinstance(name, str):
        return name.lower().strip()  # Normalize to lowercase and strip extra spaces
    return name

# Clean product names in both datasets
coles_df['Item Name'] = coles_df['Item Name'].apply(clean_item_name)
woolworths_df['Item Name'] = woolworths_df['Item Name'].apply(clean_item_name)

# Ensure the prices are numeric and remove duplicates
coles_df['Best Price'] = coles_df['Best Price'].replace('[\$,]', '', regex=True).astype(float)
woolworths_df['Best Price'] = woolworths_df['Best Price'].replace('[\$,]', '', regex=True).astype(float)
coles_df = coles_df.drop_duplicates(subset=['Item Name'])
woolworths_df = woolworths_df.drop_duplicates(subset=['Item Name'])

# Function to find the best match and compare prices
def match_products_and_prices(coles_df, woolworths_df, threshold=80):
    matched_results = []
    
    # Loop through Coles items
    for _, coles_row in coles_df.iterrows():
        coles_name = coles_row['Item Name']
        coles_price = coles_row['Best Price']
        
        # Find the best match for the Coles item in Woolworths using fuzzy matching
        match = process.extractOne(coles_name, woolworths_df['Item Name'], scorer=fuzz.token_sort_ratio)
        
        if match and match[1] >= threshold:  # Check if match score is above threshold
            woolworths_name = match[0]
            woolworths_price = woolworths_df.loc[woolworths_df['Item Name'] == woolworths_name, 'Best Price'].values[0]
            
            # Determine which store offers the cheaper price
            cheaper_store = "Coles" if coles_price < woolworths_price else "Woolworths"
            
            # Append the results
            matched_results.append({
                "Coles Item": coles_name,
                "Coles Price": coles_price,
                "Woolworths Item": woolworths_name,
                "Woolworths Price": woolworths_price,
                "Cheaper Store": cheaper_store
            })
    
    # Return the matched results as a DataFrame
    return pd.DataFrame(matched_results)

# Perform the product matching and price comparison
comparison_df = match_products_and_prices(coles_df, woolworths_df)

# Save the results to a CSV file
comparison_df.to_csv('matched_products_comparison.csv', index=False)

# Display the first few rows of the results
print(comparison_df.head())
