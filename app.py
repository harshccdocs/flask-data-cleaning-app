from flask import Flask, request, send_file, render_template_string
import pandas as pd
import tempfile
import os

app = Flask(__name__)

# Function to clean and process the lead data
def clean_lead_data(input_file, output_file):
    """
    This function reads a CSV file containing lead data, processes it to clean up necessary fields,
    and outputs cleaned data into a single CSV file.
    
    Parameters:
    - input_file (str): Path to the input CSV file to be cleaned.
    - output_file (str): Path to the output CSV file where cleaned data will be saved.

    Returns:
    - Path to the output file.
    """
    # Load the dataset from the CSV file, ensuring all columns are read as strings
    df = pd.read_csv(input_file, dtype=str)

    # Define a dictionary of the required columns and their corresponding names
    required_columns = {
        "property_address_line_1": "Address",  # Property Address
        "property_address_city": "City",       # City of the property
        "property_address_state": "State",     # State of the property
        "property_address_zipcode": "Zipcode", # Zipcode of the property
        "owner_1_firstname": "Firstname",      # Owner's First Name
        "owner_1_lastname": "Lastname",        # Owner's Last Name
        "contact_1_email1": "Email",           # Contact Email Address
    }

    # Extract and rename the selected columns
    df_selected = df[list(required_columns.keys())].rename(columns=required_columns)

    # Identify columns that contain phone numbers, excluding phone type columns
    phone_columns = [col for col in df.columns if "contact" in col and "phone" in col and "type" not in col]

    # Function to get the first available phone number from the identified phone columns
    def get_first_available_phone(row):
        for col in phone_columns:
            if pd.notna(row.get(col)) and str(row[col]).strip():
                return row[col]  # Return the first non-empty phone number found
        return None  # Return None if no phone number is found

    # Apply function to add a new column "Phone Number" to the dataset
    df_selected["Phone Number"] = df.apply(get_first_available_phone, axis=1)

    # Function to fill missing Firstname, Lastname, and Email using available contact information
    def fill_missing_contact_details(row):
        if pd.isna(row["Firstname"]) or pd.isna(row["Lastname"]) or pd.isna(row["Email"]):
            # If any of the required fields are missing, try to find the data in other columns
            for col in phone_columns:
                if pd.notna(row.get(col)) and str(row[col]).strip():
                    contact_num = col.split("_")[1]  # Extract contact number from column name
                    fname_col = f"contact_{contact_num}_firstname"
                    lname_col = f"contact_{contact_num}_lastname"
                    email_col = f"contact_{contact_num}_email1"

                    # Update the missing fields with available contact details
                    if fname_col in df.columns and pd.notna(df.at[row.name, fname_col]):
                        row["Firstname"] = df.at[row.name, fname_col]
                    if lname_col in df.columns and pd.notna(df.at[row.name, lname_col]):
                        row["Lastname"] = df.at[row.name, lname_col]
                    if email_col in df.columns and pd.notna(df.at[row.name, email_col]):
                        row["Email"] = df.at[row.name, email_col]
                    break  # Stop once valid contact information is found
        return row  # Return the row with updated details

    # Apply the function to fill missing contact details across the entire dataframe
    df_selected = df_selected.apply(fill_missing_contact_details, axis=1)

    # Clean up phone numbers by removing the leading "1" (common in US phone numbers)
    df_selected["Phone Number"] = df_selected["Phone Number"].astype(str).str.replace(r'^\+?1', '', regex=True)

    # Remove records where the phone number or first name is missing
    df_cleaned = df_selected.dropna(subset=["Phone Number", "Firstname"])

    # Save the cleaned data into a single CSV file
    df_cleaned.to_csv(output_file, index=False)

    return output_file  # Return the path to the cleaned file


# Route to render the home page with a file upload form (HTML file in the main folder)
@app.route('/')
def home():
    with open("index.html", "r") as file:
        return render_template_string(file.read())  # Load the HTML from the main folder


# Route to handle file upload and processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith(('.csv', '.xlsx')):
        # Save the uploaded file temporarily
        input_file = tempfile.mktemp(suffix=".csv")
        file.save(input_file)
        
        # Create a temporary file for cleaned data
        output_file = tempfile.mktemp(suffix=".csv")
        
        # Clean the data
        clean_lead_data(input_file, output_file)
        
        # Send the cleaned file for download
        return send_file(output_file, as_attachment=True, download_name="cleaned_data.csv")


if __name__ == '__main__':
    app.run(debug=True)
