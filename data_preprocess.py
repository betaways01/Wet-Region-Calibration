import pandas as pd

def clean_and_format_data(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path, sheet_name=None)
    
    # Dictionary to hold cleaned data
    cleaned_data = {}
    
    for sheet_name, sheet_data in df.items():
        # Extract relevant data starting from row 5
        relevant_data = sheet_data.iloc[4:].dropna(axis=1, how='all').dropna(axis=0, how='all')
        # Reset the index
        relevant_data.reset_index(drop=True, inplace=True)
        
        # Add cleaned data to dictionary
        cleaned_data[sheet_name] = relevant_data
    
    # Save cleaned data to a new Excel file
    output_path = file_path.replace('.xlsx', '_cleaned.xlsx')
    with pd.ExcelWriter(output_path) as writer:
        for sheet_name, data in cleaned_data.items():
            data.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return output_path

# File paths
input_file_path = 'Distribution_Uniformity.xlsx'
cleaned_file_path = clean_and_format_data(input_file_path)
