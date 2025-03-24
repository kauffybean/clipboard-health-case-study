import pandas as pd
import numpy as np
import base64
import io
from datetime import datetime

def load_and_clean_data(file_path):
    """
    Load and clean the marketplace data from CSV file
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned DataFrame with proper data types
    """
    # Load data from CSV
    df = pd.read_csv(file_path)
    
    # Convert date columns to datetime
    date_columns = ['created_at', 'shift_date', 'viewed_at', 'claimed_at', 'canceled_at']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Calculate lead time in hours
    if 'created_at' in df.columns and 'shift_date' in df.columns:
        df['lead_time_hours'] = (df['shift_date'] - df['created_at']).dt.total_seconds() / 3600
    
    # Convert boolean columns
    bool_columns = ['is_ncns', 'is_verified']
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].astype(bool)
    
    return df

def create_download_link(df, filename="data.csv", text="Download CSV"):
    """
    Creates a download link for a DataFrame
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame to be downloaded
    filename : str
        Name of the file to be downloaded
    text : str
        Text to display for the download link
        
    Returns:
    --------
    str
        HTML link for downloading the DataFrame
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href