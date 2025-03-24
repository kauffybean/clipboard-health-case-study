import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def compute_summary_stats(df):
    """
    Compute summary statistics for the marketplace data
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    dict
        Dictionary with summary statistics
    """
    summary = {}
    
    # Basic counts
    summary['total_records'] = len(df)
    summary['unique_shifts'] = df['shift_id'].nunique()
    summary['unique_workers'] = df['worker_id'].nunique()
    summary['unique_workplaces'] = df['workplace_id'].nunique()
    
    # Date range
    summary['date_min'] = df['shift_start_at'].min()
    summary['date_max'] = df['shift_start_at'].max()
    summary['date_range_days'] = (summary['date_max'] - summary['date_min']).days
    
    # Conversion metrics
    summary['viewed_shifts'] = summary['total_records']
    summary['claimed_shifts'] = df['claimed_at'].notna().sum()
    summary['conversion_rate'] = round(summary['claimed_shifts'] / summary['viewed_shifts'] * 100, 2)
    
    # Fulfillment metrics
    summary['verified_shifts'] = df['is_verified'].sum()
    summary['canceled_shifts'] = df['canceled_at'].notna().sum()
    summary['deleted_shifts'] = df['deleted_at'].notna().sum()
    summary['ncns_shifts'] = df['is_ncns'].sum()
    
    if summary['claimed_shifts'] > 0:
        summary['fulfillment_rate'] = round(summary['verified_shifts'] / summary['claimed_shifts'] * 100, 2)
        summary['cancellation_rate'] = round(summary['canceled_shifts'] / summary['claimed_shifts'] * 100, 2)
        summary['ncns_rate'] = round(summary['ncns_shifts'] / summary['claimed_shifts'] * 100, 2)
    else:
        summary['fulfillment_rate'] = 0
        summary['cancellation_rate'] = 0
        summary['ncns_rate'] = 0
    
    # Payment metrics
    summary['avg_pay_rate'] = round(df['pay_rate'].mean(), 2)
    summary['min_pay_rate'] = round(df['pay_rate'].min(), 2)
    summary['max_pay_rate'] = round(df['pay_rate'].max(), 2)
    
    summary['avg_charge_rate'] = round(df['charge_rate'].mean(), 2)
    summary['min_charge_rate'] = round(df['charge_rate'].min(), 2)
    summary['max_charge_rate'] = round(df['charge_rate'].max(), 2)
    
    # Calculate markup
    df['markup'] = df['charge_rate'] - df['pay_rate']
    df['markup_pct'] = (df['markup'] / df['pay_rate']) * 100
    
    summary['avg_markup'] = round(df['markup'].mean(), 2)
    summary['avg_markup_pct'] = round(df['markup_pct'].mean(), 2)
    
    # Time slot distribution
    slot_dist = df['slot'].value_counts(normalize=True) * 100
    summary['slot_distribution'] = {slot: round(pct, 2) for slot, pct in slot_dist.items()}
    
    # Duration metrics
    summary['avg_duration'] = round(df['duration'].mean(), 2)
    summary['min_duration'] = round(df['duration'].min(), 2)
    summary['max_duration'] = round(df['duration'].max(), 2)
    
    return summary

def analyze_marketplace_dynamics(df):
    """
    Analyze marketplace dynamics, including conversions and activity patterns
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    dict
        Dictionary with marketplace dynamics analysis
    """
    dynamics = {}
    
    # Calculate lead time (hours between shift creation and start)
    df['lead_time_hours'] = (df['shift_start_at'] - df['shift_created_at']).dt.total_seconds() / 3600
    
    # Calculate view time (hours between shift creation and viewing)
    df['view_time_hours'] = (df['offer_viewed_at'] - df['shift_created_at']).dt.total_seconds() / 3600
    
    # Calculate decision time (minutes between viewing and claiming, for claimed shifts)
    claimed_df = df[df['claimed_at'].notna()].copy()
    claimed_df['decision_time_minutes'] = (claimed_df['claimed_at'] - claimed_df['offer_viewed_at']).dt.total_seconds() / 60
    
    # Lead time metrics
    dynamics['avg_lead_time_hours'] = round(df['lead_time_hours'].mean(), 2)
    dynamics['median_lead_time_hours'] = round(df['lead_time_hours'].median(), 2)
    
    # View time metrics
    dynamics['avg_view_time_hours'] = round(df['view_time_hours'].mean(), 2)
    dynamics['median_view_time_hours'] = round(df['view_time_hours'].median(), 2)
    
    # Decision time metrics
    dynamics['avg_decision_time_minutes'] = round(claimed_df['decision_time_minutes'].mean(), 2)
    dynamics['median_decision_time_minutes'] = round(claimed_df['decision_time_minutes'].median(), 2)
    
    # Analyze lead time vs. conversion
    # Create lead time bins
    df['lead_time_bin'] = pd.cut(df['lead_time_hours'], 
                                bins=[0, 24, 48, 72, 168, float('inf')],
                                labels=['<1 day', '1-2 days', '2-3 days', '3-7 days', '>7 days'])
    
    lead_time_conv = df.groupby('lead_time_bin').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    lead_time_conv['conversion_rate'] = round(lead_time_conv['claims'] / lead_time_conv['views'] * 100, 2)
    
    dynamics['lead_time_conversion'] = lead_time_conv.to_dict('records')
    
    # Analyze time slot vs. conversion
    slot_conv = df.groupby('slot').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    slot_conv['conversion_rate'] = round(slot_conv['claims'] / slot_conv['views'] * 100, 2)
    
    dynamics['slot_conversion'] = slot_conv.to_dict('records')
    
    # Analyze day of week patterns
    df['day_of_week'] = df['shift_start_at'].dt.day_name()
    
    # Order days correctly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)
    
    dow_conv = df.groupby('day_of_week').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    dow_conv['conversion_rate'] = round(dow_conv['claims'] / dow_conv['views'] * 100, 2)
    dow_conv = dow_conv.sort_values('day_of_week')
    
    dynamics['day_of_week_conversion'] = dow_conv.to_dict('records')
    
    # Analyze hour of day patterns
    df['hour_of_day'] = df['shift_start_at'].dt.hour
    
    hour_conv = df.groupby('hour_of_day').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    hour_conv['conversion_rate'] = round(hour_conv['claims'] / hour_conv['views'] * 100, 2)
    hour_conv = hour_conv.sort_values('hour_of_day')
    
    dynamics['hour_of_day_conversion'] = hour_conv.to_dict('records')
    
    return dynamics

def analyze_worker_behavior(df):
    """
    Analyze worker behavior, including preferences and reliability
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    dict
        Dictionary with worker behavior analysis
    """
    worker_behavior = {}
    
    # Calculate views per worker
    views_per_worker = df.groupby('worker_id').size().reset_index(name='view_count')
    
    worker_behavior['avg_views_per_worker'] = round(views_per_worker['view_count'].mean(), 2)
    worker_behavior['median_views_per_worker'] = round(views_per_worker['view_count'].median(), 2)
    worker_behavior['max_views_per_worker'] = views_per_worker['view_count'].max()
    
    # Calculate claims per worker
    claims_per_worker = df.groupby('worker_id')['claimed_at'].apply(lambda x: x.notna().sum()).reset_index(name='claim_count')
    claims_per_worker = claims_per_worker[claims_per_worker['claim_count'] > 0]
    
    worker_behavior['avg_claims_per_worker'] = round(claims_per_worker['claim_count'].mean(), 2)
    worker_behavior['median_claims_per_worker'] = round(claims_per_worker['claim_count'].median(), 2)
    worker_behavior['max_claims_per_worker'] = claims_per_worker['claim_count'].max()
    
    # Calculate worker reliability metrics
    reliability_metrics = df.groupby('worker_id').agg(
        total_claims=('claimed_at', lambda x: x.notna().sum()),
        cancellations=('canceled_at', lambda x: x.notna().sum()),
        no_shows=('is_ncns', 'sum'),
        completions=('is_verified', 'sum')
    ).reset_index()
    
    # Filter workers with at least one claim
    reliability_metrics = reliability_metrics[reliability_metrics['total_claims'] > 0].copy()
    
    reliability_metrics['cancellation_rate'] = (reliability_metrics['cancellations'] / reliability_metrics['total_claims'] * 100).round(2)
    reliability_metrics['no_show_rate'] = (reliability_metrics['no_shows'] / reliability_metrics['total_claims'] * 100).round(2)
    reliability_metrics['completion_rate'] = (reliability_metrics['completions'] / reliability_metrics['total_claims'] * 100).round(2)
    
    worker_behavior['avg_completion_rate'] = round(reliability_metrics['completion_rate'].mean(), 2)
    worker_behavior['avg_cancellation_rate'] = round(reliability_metrics['cancellation_rate'].mean(), 2)
    worker_behavior['avg_no_show_rate'] = round(reliability_metrics['no_show_rate'].mean(), 2)
    
    # Analyze worker preferences by time slot
    worker_slot_pref = df.groupby(['worker_id', 'slot']).size().reset_index(name='count')
    worker_slot_pref = worker_slot_pref.loc[worker_slot_pref.groupby('worker_id')['count'].idxmax()]
    
    slot_pref_dist = worker_slot_pref['slot'].value_counts(normalize=True) * 100
    worker_behavior['slot_preferences'] = {slot: round(pct, 2) for slot, pct in slot_pref_dist.items()}
    
    # Worker activity level distribution
    # Create activity bins for claims
    claims_per_worker['activity_level'] = pd.cut(
        claims_per_worker['claim_count'],
        bins=[0, 1, 3, 5, 10, float('inf')],
        labels=['1 claim', '2-3 claims', '4-5 claims', '6-10 claims', '>10 claims']
    )
    
    activity_dist = claims_per_worker['activity_level'].value_counts(normalize=True) * 100
    worker_behavior['activity_distribution'] = {level: round(pct, 2) for level, pct in activity_dist.items()}
    
    # Analyze rate sensitivity
    # Group by pay rate bins
    df['pay_rate_bin'] = pd.cut(df['pay_rate'],
                              bins=[0, 20, 25, 30, 35, float('inf')],
                              labels=['<$20', '$20-25', '$25-30', '$30-35', '>$35'])
    
    rate_conv = df.groupby('pay_rate_bin').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    rate_conv['conversion_rate'] = round(rate_conv['claims'] / rate_conv['views'] * 100, 2)
    
    worker_behavior['rate_sensitivity'] = rate_conv.to_dict('records')
    
    return worker_behavior

def analyze_workplace_patterns(df):
    """
    Analyze workplace posting and fulfillment patterns
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    dict
        Dictionary with workplace pattern analysis
    """
    workplace_patterns = {}
    
    # Get unique shift-workplace combinations
    shift_workplace = df[['shift_id', 'workplace_id']].drop_duplicates()
    
    # Calculate shifts per workplace
    shifts_per_workplace = shift_workplace.groupby('workplace_id').size().reset_index(name='shift_count')
    
    workplace_patterns['avg_shifts_per_workplace'] = round(shifts_per_workplace['shift_count'].mean(), 2)
    workplace_patterns['median_shifts_per_workplace'] = round(shifts_per_workplace['shift_count'].median(), 2)
    workplace_patterns['max_shifts_per_workplace'] = shifts_per_workplace['shift_count'].max()
    
    # Create volume bins
    shifts_per_workplace['volume_level'] = pd.cut(
        shifts_per_workplace['shift_count'],
        bins=[0, 1, 5, 10, 20, 50, float('inf')],
        labels=['1 shift', '2-5 shifts', '6-10 shifts', '11-20 shifts', '21-50 shifts', '>50 shifts']
    )
    
    volume_dist = shifts_per_workplace['volume_level'].value_counts(normalize=True) * 100
    workplace_patterns['volume_distribution'] = {level: round(pct, 2) for level, pct in volume_dist.items()}
    
    # Analyze workplace fill rates
    # Count claimed shifts per workplace
    claimed_shifts = df[df['claimed_at'].notna()][['shift_id', 'workplace_id']].drop_duplicates()
    claimed_per_workplace = claimed_shifts.groupby('workplace_id').size().reset_index(name='claimed_count')
    
    # Merge with total shifts
    workplace_fill = shifts_per_workplace.merge(claimed_per_workplace, on='workplace_id', how='left')
    workplace_fill['claimed_count'] = workplace_fill['claimed_count'].fillna(0)
    
    # Calculate fill rate
    workplace_fill['fill_rate'] = (workplace_fill['claimed_count'] / workplace_fill['shift_count'] * 100).round(2)
    
    workplace_patterns['avg_fill_rate'] = round(workplace_fill['fill_rate'].mean(), 2)
    workplace_patterns['median_fill_rate'] = round(workplace_fill['fill_rate'].median(), 2)
    
    # Distribution of fill rates
    workplace_fill['fill_rate_bin'] = pd.cut(
        workplace_fill['fill_rate'],
        bins=[0, 20, 40, 60, 80, 100],
        labels=['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
    )
    
    fill_rate_dist = workplace_fill['fill_rate_bin'].value_counts(normalize=True) * 100
    workplace_patterns['fill_rate_distribution'] = {bin_name: round(pct, 2) for bin_name, pct in fill_rate_dist.items()}
    
    # Analyze workplace lead time patterns
    workplace_lead_times = df.groupby('workplace_id')['lead_time_hours'].mean().reset_index(name='avg_lead_time')
    
    workplace_patterns['avg_workplace_lead_time'] = round(workplace_lead_times['avg_lead_time'].mean(), 2)
    workplace_patterns['median_workplace_lead_time'] = round(workplace_lead_times['avg_lead_time'].median(), 2)
    
    # Create lead time bins
    workplace_lead_times['lead_time_bin'] = pd.cut(
        workplace_lead_times['avg_lead_time'],
        bins=[0, 24, 48, 72, 168, float('inf')],
        labels=['<1 day', '1-2 days', '2-3 days', '3-7 days', '>7 days']
    )
    
    lead_time_dist = workplace_lead_times['lead_time_bin'].value_counts(normalize=True) * 100
    workplace_patterns['lead_time_distribution'] = {bin_name: round(pct, 2) for bin_name, pct in lead_time_dist.items()}
    
    # Analyze workplace time slot patterns
    workplace_slots = df.groupby(['workplace_id', 'slot']).size().reset_index(name='count')
    workplace_pref_slot = workplace_slots.loc[workplace_slots.groupby('workplace_id')['count'].idxmax()]
    
    slot_dist = workplace_pref_slot['slot'].value_counts(normalize=True) * 100
    workplace_patterns['slot_distribution'] = {slot: round(pct, 2) for slot, pct in slot_dist.items()}
    
    # Analyze lead time vs. fill rate
    lead_fill = workplace_lead_times.merge(workplace_fill[['workplace_id', 'fill_rate']], on='workplace_id', how='inner')
    
    lead_fill_agg = lead_fill.groupby('lead_time_bin')['fill_rate'].mean().reset_index()
    lead_fill_agg['fill_rate'] = lead_fill_agg['fill_rate'].round(2)
    
    workplace_patterns['lead_time_vs_fill_rate'] = lead_fill_agg.to_dict('records')
    
    return workplace_patterns

def analyze_rate_pricing(df):
    """
    Analyze rate and pricing patterns in the marketplace
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    dict
        Dictionary with rate and pricing analysis
    """
    rate_pricing = {}
    
    # Calculate markup
    df['markup'] = df['charge_rate'] - df['pay_rate']
    df['markup_percentage'] = (df['markup'] / df['pay_rate'] * 100).round(2)
    
    # Overall rate metrics
    rate_pricing['avg_pay_rate'] = round(df['pay_rate'].mean(), 2)
    rate_pricing['avg_charge_rate'] = round(df['charge_rate'].mean(), 2)
    rate_pricing['avg_markup'] = round(df['markup'].mean(), 2)
    rate_pricing['avg_markup_percentage'] = round(df['markup_percentage'].mean(), 2)
    
    # Rate distribution
    pay_bins = [0, 20, 25, 30, 35, float('inf')]
    pay_labels = ['<$20', '$20-25', '$25-30', '$30-35', '>$35']
    
    df['pay_rate_bin'] = pd.cut(df['pay_rate'], bins=pay_bins, labels=pay_labels)
    
    pay_dist = df['pay_rate_bin'].value_counts(normalize=True) * 100
    rate_pricing['pay_rate_distribution'] = {bin_name: round(pct, 2) for bin_name, pct in pay_dist.items()}
    
    # Analyze rates by time slot
    slot_rates = df.groupby('slot').agg(
        avg_pay_rate=('pay_rate', 'mean'),
        avg_charge_rate=('charge_rate', 'mean'),
        avg_markup=('markup', 'mean'),
        avg_markup_percentage=('markup_percentage', 'mean')
    ).reset_index()
    
    # Round values
    for col in slot_rates.columns:
        if col != 'slot':
            slot_rates[col] = slot_rates[col].round(2)
    
    rate_pricing['slot_rates'] = slot_rates.to_dict('records')
    
    # Analyze rate effectiveness (conversion by rate)
    rate_conv = df.groupby('pay_rate_bin').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    rate_conv['conversion_rate'] = (rate_conv['claims'] / rate_conv['views'] * 100).round(2)
    rate_conv['completion_rate'] = (rate_conv['verified'] / rate_conv['claims'] * 100).fillna(0).round(2)
    
    rate_pricing['rate_effectiveness'] = rate_conv.to_dict('records')
    
    # Analyze markup vs. conversion
    df['markup_bin'] = pd.cut(
        df['markup'],
        bins=[0, 5, 10, 15, 20, float('inf')],
        labels=['$0-5', '$5-10', '$10-15', '$15-20', '>$20']
    )
    
    markup_conv = df.groupby('markup_bin').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    markup_conv['conversion_rate'] = (markup_conv['claims'] / markup_conv['views'] * 100).round(2)
    
    rate_pricing['markup_effectiveness'] = markup_conv.to_dict('records')
    
    # Analyze markup percentage vs. conversion
    df['markup_pct_bin'] = pd.cut(
        df['markup_percentage'],
        bins=[0, 25, 50, 75, 100, float('inf')],
        labels=['0-25%', '25-50%', '50-75%', '75-100%', '>100%']
    )
    
    markup_pct_conv = df.groupby('markup_pct_bin').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    markup_pct_conv['conversion_rate'] = (markup_pct_conv['claims'] / markup_pct_conv['views'] * 100).round(2)
    
    rate_pricing['markup_pct_effectiveness'] = markup_pct_conv.to_dict('records')
    
    # Analyze duration vs. rates
    duration_rates = df.groupby('duration').agg(
        avg_pay_rate=('pay_rate', 'mean'),
        avg_charge_rate=('charge_rate', 'mean'),
        avg_markup=('markup', 'mean'),
        conversion_rate=('claimed_at', lambda x: x.notna().sum() / len(x) * 100)
    ).reset_index()
    
    # Round values
    for col in duration_rates.columns:
        if col != 'duration':
            duration_rates[col] = duration_rates[col].round(2)
    
    rate_pricing['duration_rates'] = duration_rates.to_dict('records')
    
    return rate_pricing

def analyze_time_series(df):
    """
    Analyze time series patterns in the marketplace data
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    dict
        Dictionary with time series analysis
    """
    time_series = {}
    
    # Create date and time fields
    df['date'] = df['shift_start_at'].dt.date
    df['week'] = df['shift_start_at'].dt.isocalendar().week
    df['month'] = df['shift_start_at'].dt.month
    df['day_of_week'] = df['shift_start_at'].dt.day_name()
    df['hour'] = df['shift_start_at'].dt.hour
    
    # Daily metrics
    daily_metrics = df.groupby('date').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    daily_metrics['conversion_rate'] = (daily_metrics['claims'] / daily_metrics['views'] * 100).round(2)
    daily_metrics['fulfillment_rate'] = (daily_metrics['verified'] / daily_metrics['claims'] * 100).fillna(0).round(2)
    
    # Convert date to string for JSON serialization
    daily_metrics['date'] = daily_metrics['date'].astype(str)
    
    time_series['daily_metrics'] = daily_metrics.to_dict('records')
    
    # Weekly metrics
    weekly_metrics = df.groupby(['week']).agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    weekly_metrics['conversion_rate'] = (weekly_metrics['claims'] / weekly_metrics['views'] * 100).round(2)
    weekly_metrics['fulfillment_rate'] = (weekly_metrics['verified'] / weekly_metrics['claims'] * 100).fillna(0).round(2)
    
    time_series['weekly_metrics'] = weekly_metrics.to_dict('records')
    
    # Monthly metrics
    monthly_metrics = df.groupby(['month']).agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    monthly_metrics['conversion_rate'] = (monthly_metrics['claims'] / monthly_metrics['views'] * 100).round(2)
    monthly_metrics['fulfillment_rate'] = (monthly_metrics['verified'] / monthly_metrics['claims'] * 100).fillna(0).round(2)
    
    time_series['monthly_metrics'] = monthly_metrics.to_dict('records')
    
    # Day of week metrics
    # Order days correctly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)
    
    dow_metrics = df.groupby('day_of_week').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    dow_metrics['conversion_rate'] = (dow_metrics['claims'] / dow_metrics['views'] * 100).round(2)
    dow_metrics['fulfillment_rate'] = (dow_metrics['verified'] / dow_metrics['claims'] * 100).fillna(0).round(2)
    
    dow_metrics = dow_metrics.sort_values('day_of_week')
    
    time_series['day_of_week_metrics'] = dow_metrics.to_dict('records')
    
    # Hourly metrics
    hour_metrics = df.groupby('hour').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    hour_metrics['conversion_rate'] = (hour_metrics['claims'] / hour_metrics['views'] * 100).round(2)
    hour_metrics['fulfillment_rate'] = (hour_metrics['verified'] / hour_metrics['claims'] * 100).fillna(0).round(2)
    
    hour_metrics = hour_metrics.sort_values('hour')
    
    time_series['hourly_metrics'] = hour_metrics.to_dict('records')
    
    # Time slot metrics over time
    slot_time_metrics = df.groupby(['date', 'slot']).agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    slot_time_metrics['conversion_rate'] = (slot_time_metrics['claims'] / slot_time_metrics['views'] * 100).round(2)
    
    # Convert date to string for JSON serialization
    slot_time_metrics['date'] = slot_time_metrics['date'].astype(str)
    
    time_series['slot_time_metrics'] = slot_time_metrics.to_dict('records')
    
    # Rate metrics over time
    df['pay_rate_bin'] = pd.cut(df['pay_rate'],
                             bins=[0, 20, 25, 30, 35, float('inf')],
                             labels=['<$20', '$20-25', '$25-30', '$30-35', '>$35'])
    
    rate_time_metrics = df.groupby(['date', 'pay_rate_bin']).agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    rate_time_metrics['conversion_rate'] = (rate_time_metrics['claims'] / rate_time_metrics['views'] * 100).round(2)
    
    # Convert date to string for JSON serialization
    rate_time_metrics['date'] = rate_time_metrics['date'].astype(str)
    
    time_series['rate_time_metrics'] = rate_time_metrics.to_dict('records')
    
    return time_series
