import pandas as pd
import numpy as np
import base64
import io
from datetime import datetime

def load_and_clean_data(uploaded_file):
    """
    Load and clean the marketplace data from uploaded CSV file
    
    Parameters:
    -----------
    uploaded_file : UploadedFile
        The CSV file uploaded by the user
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned DataFrame with proper data types
    """
    # Load data from CSV
    df = pd.read_csv(uploaded_file)
    
    # Convert date columns to datetime
    date_columns = ['shift_start_at', 'shift_created_at', 'offer_viewed_at', 
                    'claimed_at', 'deleted_at', 'canceled_at']
    
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convert boolean columns
    bool_columns = ['is_verified', 'is_ncns']
    
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].astype(bool)
    
    # Ensure numeric columns are properly typed
    numeric_columns = ['duration', 'pay_rate', 'charge_rate']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Basic data cleaning
    
    # Remove any duplicates based on shift_id and worker_id combination
    df = df.drop_duplicates(subset=['shift_id', 'worker_id'])
    
    # Ensure logical consistency in dates
    # - claimed_at should be after offer_viewed_at
    # - canceled_at should be after claimed_at
    
    # For rows where claimed_at is before offer_viewed_at, set it to NaT
    mask = (df['claimed_at'].notna() & df['offer_viewed_at'].notna() & 
            (df['claimed_at'] < df['offer_viewed_at']))
    df.loc[mask, 'claimed_at'] = pd.NaT
    
    # For rows where canceled_at is before claimed_at, set it to NaT
    mask = (df['canceled_at'].notna() & df['claimed_at'].notna() & 
            (df['canceled_at'] < df['claimed_at']))
    df.loc[mask, 'canceled_at'] = pd.NaT
    
    # Handle edge cases
    
    # If is_verified is True but there's no claimed_at, it's likely an error
    mask = (df['is_verified'] == True) & df['claimed_at'].isna()
    df.loc[mask, 'is_verified'] = False
    
    # If is_ncns is True but there's no claimed_at, it's likely an error
    mask = (df['is_ncns'] == True) & df['claimed_at'].isna()
    df.loc[mask, 'is_ncns'] = False
    
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

def get_filtered_data(df, filters):
    """
    Filter dataframe based on provided filters
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame to filter
    filters : dict
        Dictionary of column-value pairs to filter on
        
    Returns:
    --------
    pandas.DataFrame
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if column in df.columns:
            if isinstance(value, list):
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            elif isinstance(value, tuple) and len(value) == 2:
                # Range filter
                min_val, max_val = value
                filtered_df = filtered_df[(filtered_df[column] >= min_val) & 
                                          (filtered_df[column] <= max_val)]
            else:
                # Single value filter
                filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df

def calculate_metrics(df):
    """
    Calculate key marketplace metrics
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    dict
        Dictionary with calculated metrics
    """
    metrics = {}
    
    # Volume metrics
    metrics['total_views'] = len(df)
    metrics['unique_shifts'] = df['shift_id'].nunique()
    metrics['unique_workers'] = df['worker_id'].nunique()
    metrics['unique_workplaces'] = df['workplace_id'].nunique()
    
    # Conversion metrics
    metrics['claimed_shifts'] = df['claimed_at'].notna().sum()
    metrics['conversion_rate'] = (metrics['claimed_shifts'] / metrics['total_views'] * 100).round(2)
    
    # Fulfillment metrics
    metrics['verified_shifts'] = df['is_verified'].sum()
    metrics['canceled_shifts'] = df['canceled_at'].notna().sum()
    metrics['deleted_shifts'] = df['deleted_at'].notna().sum()
    metrics['no_show_shifts'] = df['is_ncns'].sum()
    
    if metrics['claimed_shifts'] > 0:
        metrics['fulfillment_rate'] = (metrics['verified_shifts'] / metrics['claimed_shifts'] * 100).round(2)
        metrics['cancellation_rate'] = (metrics['canceled_shifts'] / metrics['claimed_shifts'] * 100).round(2)
        metrics['no_show_rate'] = (metrics['no_show_shifts'] / metrics['claimed_shifts'] * 100).round(2)
    else:
        metrics['fulfillment_rate'] = 0
        metrics['cancellation_rate'] = 0
        metrics['no_show_rate'] = 0
    
    # Rate metrics
    metrics['avg_pay_rate'] = df['pay_rate'].mean().round(2)
    metrics['avg_charge_rate'] = df['charge_rate'].mean().round(2)
    metrics['avg_markup'] = (df['charge_rate'] - df['pay_rate']).mean().round(2)
    metrics['avg_markup_pct'] = ((df['charge_rate'] - df['pay_rate']) / df['pay_rate'] * 100).mean().round(2)
    
    # Time metrics
    if 'lead_time_hours' not in df.columns:
        df['lead_time_hours'] = (df['shift_start_at'] - df['shift_created_at']).dt.total_seconds() / 3600
    
    metrics['avg_lead_time_hours'] = df['lead_time_hours'].mean().round(2)
    
    return metrics

def calculate_worker_metrics(df, worker_id=None):
    """
    Calculate metrics for a specific worker or all workers
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
    worker_id : str, optional
        Worker ID to calculate metrics for
        
    Returns:
    --------
    dict or pandas.DataFrame
        Dictionary with metrics for a specific worker or DataFrame with metrics for all workers
    """
    if worker_id is not None:
        # Filter by worker
        worker_df = df[df['worker_id'] == worker_id]
        
        # Calculate metrics
        metrics = {}
        metrics['total_views'] = len(worker_df)
        metrics['claimed_shifts'] = worker_df['claimed_at'].notna().sum()
        metrics['conversion_rate'] = (metrics['claimed_shifts'] / metrics['total_views'] * 100).round(2) if metrics['total_views'] > 0 else 0
        metrics['verified_shifts'] = worker_df['is_verified'].sum()
        metrics['canceled_shifts'] = worker_df['canceled_at'].notna().sum()
        metrics['no_show_shifts'] = worker_df['is_ncns'].sum()
        
        if metrics['claimed_shifts'] > 0:
            metrics['fulfillment_rate'] = (metrics['verified_shifts'] / metrics['claimed_shifts'] * 100).round(2)
            metrics['cancellation_rate'] = (metrics['canceled_shifts'] / metrics['claimed_shifts'] * 100).round(2)
            metrics['no_show_rate'] = (metrics['no_show_shifts'] / metrics['claimed_shifts'] * 100).round(2)
        else:
            metrics['fulfillment_rate'] = 0
            metrics['cancellation_rate'] = 0
            metrics['no_show_rate'] = 0
        
        # Preferred time slots
        if len(worker_df) > 0:
            metrics['preferred_slot'] = worker_df['slot'].value_counts().index[0] if not worker_df['slot'].empty else 'Unknown'
        else:
            metrics['preferred_slot'] = 'Unknown'
        
        return metrics
    else:
        # Calculate metrics for all workers
        worker_metrics = df.groupby('worker_id').apply(lambda x: pd.Series({
            'total_views': len(x),
            'claimed_shifts': x['claimed_at'].notna().sum(),
            'verified_shifts': x['is_verified'].sum(),
            'canceled_shifts': x['canceled_at'].notna().sum(),
            'no_show_shifts': x['is_ncns'].sum()
        })).reset_index()
        
        # Calculate rates
        worker_metrics['conversion_rate'] = (worker_metrics['claimed_shifts'] / worker_metrics['total_views'] * 100).round(2)
        
        mask = worker_metrics['claimed_shifts'] > 0
        worker_metrics.loc[mask, 'fulfillment_rate'] = (worker_metrics.loc[mask, 'verified_shifts'] / 
                                                      worker_metrics.loc[mask, 'claimed_shifts'] * 100).round(2)
        
        worker_metrics.loc[mask, 'cancellation_rate'] = (worker_metrics.loc[mask, 'canceled_shifts'] / 
                                                       worker_metrics.loc[mask, 'claimed_shifts'] * 100).round(2)
        
        worker_metrics.loc[mask, 'no_show_rate'] = (worker_metrics.loc[mask, 'no_show_shifts'] / 
                                                  worker_metrics.loc[mask, 'claimed_shifts'] * 100).round(2)
        
        worker_metrics = worker_metrics.fillna(0)
        
        # Get preferred slot for each worker
        preferred_slots = df.groupby(['worker_id', 'slot']).size().reset_index(name='count')
        preferred_slots = preferred_slots.loc[preferred_slots.groupby('worker_id')['count'].idxmax()]
        preferred_slots = preferred_slots[['worker_id', 'slot']].rename(columns={'slot': 'preferred_slot'})
        
        # Merge with worker metrics
        worker_metrics = worker_metrics.merge(preferred_slots, on='worker_id', how='left')
        
        return worker_metrics

def calculate_workplace_metrics(df, workplace_id=None):
    """
    Calculate metrics for a specific workplace or all workplaces
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
    workplace_id : str, optional
        Workplace ID to calculate metrics for
        
    Returns:
    --------
    dict or pandas.DataFrame
        Dictionary with metrics for a specific workplace or DataFrame with metrics for all workplaces
    """
    if workplace_id is not None:
        # Filter by workplace
        workplace_df = df[df['workplace_id'] == workplace_id]
        
        # Unique shifts for this workplace
        unique_shifts = workplace_df[['shift_id']].drop_duplicates()
        
        # Calculate metrics
        metrics = {}
        metrics['total_shifts'] = len(unique_shifts)
        metrics['total_views'] = len(workplace_df)
        metrics['views_per_shift'] = (metrics['total_views'] / metrics['total_shifts']).round(2) if metrics['total_shifts'] > 0 else 0
        
        # Count unique shifts that were claimed
        claimed_shifts = workplace_df[workplace_df['claimed_at'].notna()][['shift_id']].drop_duplicates()
        metrics['claimed_shifts'] = len(claimed_shifts)
        
        # Count unique shifts that were verified
        verified_shifts = workplace_df[workplace_df['is_verified'] == True][['shift_id']].drop_duplicates()
        metrics['verified_shifts'] = len(verified_shifts)
        
        # Count unique shifts that were deleted
        deleted_shifts = workplace_df[workplace_df['deleted_at'].notna()][['shift_id']].drop_duplicates()
        metrics['deleted_shifts'] = len(deleted_shifts)
        
        # Calculate rates
        metrics['fill_rate'] = (metrics['claimed_shifts'] / metrics['total_shifts'] * 100).round(2) if metrics['total_shifts'] > 0 else 0
        metrics['completion_rate'] = (metrics['verified_shifts'] / metrics['claimed_shifts'] * 100).round(2) if metrics['claimed_shifts'] > 0 else 0
        
        # Average rates
        metrics['avg_pay_rate'] = workplace_df['pay_rate'].mean().round(2)
        metrics['avg_charge_rate'] = workplace_df['charge_rate'].mean().round(2)
        metrics['avg_markup'] = (workplace_df['charge_rate'] - workplace_df['pay_rate']).mean().round(2)
        
        # Lead time
        if 'lead_time_hours' not in workplace_df.columns:
            workplace_df['lead_time_hours'] = (workplace_df['shift_start_at'] - workplace_df['shift_created_at']).dt.total_seconds() / 3600
        
        metrics['avg_lead_time_hours'] = workplace_df['lead_time_hours'].mean().round(2)
        
        # Most common time slot
        if len(workplace_df) > 0:
            metrics['most_common_slot'] = workplace_df['slot'].value_counts().index[0] if not workplace_df['slot'].empty else 'Unknown'
        else:
            metrics['most_common_slot'] = 'Unknown'
        
        return metrics
    else:
        # Get unique shift-workplace combinations
        shift_workplace = df[['shift_id', 'workplace_id']].drop_duplicates()
        
        # Count shifts per workplace
        shifts_per_workplace = shift_workplace.groupby('workplace_id').size().reset_index(name='total_shifts')
        
        # Count views per workplace
        views_per_workplace = df.groupby('workplace_id').size().reset_index(name='total_views')
        
        # Count claimed shifts per workplace
        claimed_per_workplace = df[df['claimed_at'].notna()][['shift_id', 'workplace_id']].drop_duplicates().groupby('workplace_id').size().reset_index(name='claimed_shifts')
        
        # Count verified shifts per workplace
        verified_per_workplace = df[df['is_verified'] == True][['shift_id', 'workplace_id']].drop_duplicates().groupby('workplace_id').size().reset_index(name='verified_shifts')
        
        # Count deleted shifts per workplace
        deleted_per_workplace = df[df['deleted_at'].notna()][['shift_id', 'workplace_id']].drop_duplicates().groupby('workplace_id').size().reset_index(name='deleted_shifts')
        
        # Merge all metrics
        workplace_metrics = shifts_per_workplace.merge(views_per_workplace, on='workplace_id', how='left')
        workplace_metrics = workplace_metrics.merge(claimed_per_workplace, on='workplace_id', how='left')
        workplace_metrics = workplace_metrics.merge(verified_per_workplace, on='workplace_id', how='left')
        workplace_metrics = workplace_metrics.merge(deleted_per_workplace, on='workplace_id', how='left')
        
        # Fill NAs with 0
        workplace_metrics = workplace_metrics.fillna(0)
        
        # Calculate rates
        workplace_metrics['views_per_shift'] = (workplace_metrics['total_views'] / workplace_metrics['total_shifts']).round(2)
        workplace_metrics['fill_rate'] = (workplace_metrics['claimed_shifts'] / workplace_metrics['total_shifts'] * 100).round(2)
        
        mask = workplace_metrics['claimed_shifts'] > 0
        workplace_metrics.loc[mask, 'completion_rate'] = (workplace_metrics.loc[mask, 'verified_shifts'] / 
                                                        workplace_metrics.loc[mask, 'claimed_shifts'] * 100).round(2)
        
        # Calculate average rate metrics per workplace
        rate_metrics = df.groupby('workplace_id').agg({
            'pay_rate': 'mean',
            'charge_rate': 'mean'
        }).reset_index()
        
        rate_metrics['avg_markup'] = (rate_metrics['charge_rate'] - rate_metrics['pay_rate']).round(2)
        
        # Round rate columns
        for col in ['pay_rate', 'charge_rate']:
            rate_metrics[col] = rate_metrics[col].round(2)
        
        workplace_metrics = workplace_metrics.merge(rate_metrics, on='workplace_id', how='left')
        
        # Calculate lead time per workplace
        if 'lead_time_hours' not in df.columns:
            df['lead_time_hours'] = (df['shift_start_at'] - df['shift_created_at']).dt.total_seconds() / 3600
        
        lead_time = df.groupby('workplace_id')['lead_time_hours'].mean().round(2).reset_index(name='avg_lead_time_hours')
        workplace_metrics = workplace_metrics.merge(lead_time, on='workplace_id', how='left')
        
        # Get most common slot for each workplace
        slot_counts = df.groupby(['workplace_id', 'slot']).size().reset_index(name='count')
        most_common_slots = slot_counts.loc[slot_counts.groupby('workplace_id')['count'].idxmax()]
        most_common_slots = most_common_slots[['workplace_id', 'slot']].rename(columns={'slot': 'most_common_slot'})
        
        workplace_metrics = workplace_metrics.merge(most_common_slots, on='workplace_id', how='left')
        
        return workplace_metrics
