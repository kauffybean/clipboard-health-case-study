import streamlit as st
import pandas as pd
import numpy as np
import time
import io
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_and_clean_data, create_download_link
from analysis import (compute_summary_stats, analyze_marketplace_dynamics, 
                     analyze_worker_behavior, analyze_workplace_patterns,
                     analyze_rate_pricing, analyze_time_series)
from visualizations import (plot_overview_metrics, plot_conversion_funnel, 
                           plot_timeslot_distribution, plot_rate_distribution,
                           plot_time_series, plot_geographical_distribution,
                           plot_worker_retention, plot_marketplace_balance,
                           plot_workplace_activity, plot_pricing_strategy)

# Page configuration
st.set_page_config(
    page_title="CBH Marketplace Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define app sections
SECTIONS = {
    "Introduction": "introduction",
    "Data Overview": "data_overview",
    "Marketplace Dynamics": "marketplace_dynamics",
    "Worker Analysis": "worker_analysis",
    "Workplace Analysis": "workplace_analysis",
    "Rate & Pricing Analysis": "rate_analysis",
    "Time Series Analysis": "time_series",
    "Key Insights & Recommendations": "insights"
}

# CSS hack to make plots more appealing
st.markdown("""
    <style>
        .stPlotlyChart {
            width: 100%;
        }
        .main .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# App title and introduction
def introduction():
    st.title("CBH Marketplace Data Analysis")
    st.markdown("""
    ## Welcome to the CBH Marketplace Analyzer
    
    This application will guide you through a comprehensive analysis of the CBH marketplace data, 
    exploring the dynamics between workers and workplaces.
    
    **About CBH Marketplace**:
    CBH is a two-sided marketplace with strong network effects where workers transact with workplaces to book per diem shifts.
    
    **Analysis Flow**:
    1. Upload your marketplace data
    2. Explore summary statistics
    3. Analyze marketplace dynamics
    4. Investigate worker behaviors
    5. Understand workplace patterns
    6. Examine rate and pricing strategies
    7. Review time-series trends
    8. Generate insights and recommendations
    
    Let's get started by uploading your data!
    """)

# Data overview section
def data_overview(df):
    st.header("Data Overview")
    
    # Data summary
    st.subheader("Dataset Summary")
    st.write(f"📊 Total Records: {len(df):,}")
    st.write(f"🕒 Date Range: {df['shift_start_at'].min().date()} to {df['shift_start_at'].max().date()}")
    st.write(f"👤 Unique Workers: {df['worker_id'].nunique():,}")
    st.write(f"🏢 Unique Workplaces: {df['workplace_id'].nunique():,}")
    st.write(f"💼 Unique Shifts: {df['shift_id'].nunique():,}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Sample")
        st.dataframe(df.head(10), height=300)
    
    with col2:
        st.subheader("Data Glossary")
        glossary_data = {
            'Column': [
                'shift_id', 'worker_id', 'workplace_id', 'shift_start_at', 
                'shift_created_at', 'offer_viewed_at', 'duration', 'slot',
                'claimed_at', 'deleted_at', 'is_verified', 'canceled_at', 
                'is_ncns', 'pay_rate', 'charge_rate'
            ],
            'Description': [
                'Unique identifier for a shift',
                'Unique identifier for a worker',
                'Unique identifier for a workplace',
                'Time shift starts (UTC)',
                'Time shift was posted to the marketplace (UTC)',
                'Time worker viewed the shift offer (UTC)',
                'Duration of shift in hours',
                'Timeslot of shift (NOC = overnight)',
                'Time shift was booked by worker (UTC)',
                'Time shift was deleted by workplace (UTC)',
                'Worker worked shift',
                'Time shift was canceled by worker (UTC)',
                'Worker was a no call no show',
                'Hourly rate offered to worker for the shift',
                'Hourly charge per labor hour at a facility'
            ]
        }
        glossary_df = pd.DataFrame(glossary_data)
        st.dataframe(glossary_df, height=300)
    
    # Data quality summary
    st.subheader("Data Quality Summary")
    
    # Missing values
    missing_data = df.isnull().sum().to_frame().reset_index()
    missing_data.columns = ['Column', 'Missing Values']
    missing_data['Missing Percentage'] = (missing_data['Missing Values'] / len(df) * 100).round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Missing Values")
        st.dataframe(missing_data, height=300)
    
    with col2:
        # Data types
        st.write("Data Types")
        dtypes_df = pd.DataFrame({
            'Column': df.dtypes.index,
            'Type': df.dtypes.values
        })
        st.dataframe(dtypes_df, height=300)
    
    # Summary statistics
    st.subheader("Summary Statistics for Numerical Columns")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    stats_df = df[numeric_cols].describe().round(2)
    st.dataframe(stats_df, height=400)

# Marketplace dynamics analysis
def marketplace_dynamics(df):
    st.header("Marketplace Dynamics")
    
    # Calculate conversion metrics
    total_views = len(df)
    claimed_shifts = df['claimed_at'].notna().sum()
    conversion_rate = (claimed_shifts / total_views * 100).round(2)
    canceled_shifts = df['canceled_at'].notna().sum()
    deleted_shifts = df['deleted_at'].notna().sum()
    completed_shifts = df['is_verified'].sum()
    
    st.subheader("Conversion Funnel")
    
    # Display metrics
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.metric("Total Views", f"{total_views:,}")
    with metrics_cols[1]:
        st.metric("Claimed Shifts", f"{claimed_shifts:,}")
    with metrics_cols[2]:
        st.metric("Conversion Rate", f"{conversion_rate}%")
    with metrics_cols[3]:
        st.metric("Completed Shifts", f"{completed_shifts:,}")
    
    # Plot conversion funnel
    funnel_fig = plot_conversion_funnel(df)
    st.plotly_chart(funnel_fig, use_container_width=True)
    
    # Time slot analysis
    st.subheader("Shift Distribution by Time Slot")
    
    slot_dist = df['slot'].value_counts().reset_index()
    slot_dist.columns = ['Time Slot', 'Count']
    
    col1, col2 = st.columns(2)
    
    with col1:
        slot_fig = px.pie(slot_dist, names='Time Slot', values='Count', 
                         title='Distribution of Shifts by Time Slot',
                         color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(slot_fig, use_container_width=True)
    
    with col2:
        # Conversion rate by time slot
        slot_conversion = df.groupby('slot').agg(
            total_views=('shift_id', 'count'),
            claimed=('claimed_at', lambda x: x.notna().sum())
        ).reset_index()
        slot_conversion['conversion_rate'] = (slot_conversion['claimed'] / slot_conversion['total_views'] * 100).round(2)
        
        conv_fig = px.bar(slot_conversion, x='slot', y='conversion_rate',
                         title='Conversion Rate by Time Slot (%)',
                         labels={'slot': 'Time Slot', 'conversion_rate': 'Conversion Rate (%)'},
                         color='conversion_rate',
                         color_continuous_scale='Viridis')
        st.plotly_chart(conv_fig, use_container_width=True)
    
    # Lead time analysis
    st.subheader("Lead Time Analysis")
    
    # Calculate lead time (time between shift creation and start)
    df['lead_time_hours'] = (df['shift_start_at'] - df['shift_created_at']).dt.total_seconds() / 3600
    
    # Calculate view time (time between creation and viewing)
    df['view_time_hours'] = (df['offer_viewed_at'] - df['shift_created_at']).dt.total_seconds() / 3600
    
    # Calculate decision time (time between viewing and claiming, for claimed shifts)
    claimed_df = df[df['claimed_at'].notna()].copy()
    claimed_df['decision_time_minutes'] = (claimed_df['claimed_at'] - claimed_df['offer_viewed_at']).dt.total_seconds() / 60
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution of lead times
        lead_fig = px.histogram(df, x='lead_time_hours', nbins=50,
                               title='Distribution of Lead Times (Hours)',
                               labels={'lead_time_hours': 'Lead Time (hours)'},
                               color_discrete_sequence=['#3366CC'])
        st.plotly_chart(lead_fig, use_container_width=True)
    
    with col2:
        # Distribution of decision times
        decision_fig = px.histogram(claimed_df, x='decision_time_minutes', nbins=50,
                                   title='Distribution of Decision Times (Minutes)',
                                   labels={'decision_time_minutes': 'Decision Time (minutes)'},
                                   color_discrete_sequence=['#109618'])
        decision_fig.update_layout(xaxis_range=[0, 60])  # Focus on first hour
        st.plotly_chart(decision_fig, use_container_width=True)
    
    # Lead time vs conversion rate
    st.subheader("Lead Time vs. Conversion Rate")
    
    # Create lead time bins
    df['lead_time_bin'] = pd.cut(df['lead_time_hours'], 
                                 bins=[0, 24, 48, 72, 168, float('inf')],
                                 labels=['<1 day', '1-2 days', '2-3 days', '3-7 days', '>7 days'])
    
    lead_conv = df.groupby('lead_time_bin').agg(
        total_views=('shift_id', 'count'),
        claimed=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    lead_conv['conversion_rate'] = (lead_conv['claimed'] / lead_conv['total_views'] * 100).round(2)
    
    lead_conv_fig = px.bar(lead_conv, x='lead_time_bin', y='conversion_rate',
                         title='Conversion Rate by Lead Time',
                         labels={'lead_time_bin': 'Lead Time', 'conversion_rate': 'Conversion Rate (%)'},
                         color='conversion_rate',
                         color_continuous_scale='Viridis')
    st.plotly_chart(lead_conv_fig, use_container_width=True)

# Worker analysis
def worker_analysis(df):
    st.header("Worker Analysis")
    
    # Worker activity metrics
    total_workers = df['worker_id'].nunique()
    avg_views_per_worker = df.groupby('worker_id').size().mean().round(2)
    
    worker_claims = df[df['claimed_at'].notna()].groupby('worker_id').size().reset_index()
    worker_claims.columns = ['worker_id', 'claims_count']
    active_workers = len(worker_claims)
    
    # Workers who completed at least one shift
    completed_workers = df[df['is_verified'] == True]['worker_id'].nunique()
    
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.metric("Total Workers", f"{total_workers:,}")
    with metrics_cols[1]:
        st.metric("Active Workers", f"{active_workers:,}")
    with metrics_cols[2]:
        st.metric("Avg Views per Worker", f"{avg_views_per_worker}")
    with metrics_cols[3]:
        st.metric("Workers Completing Shifts", f"{completed_workers:,}")
    
    # Worker distribution by activity level
    st.subheader("Worker Activity Distribution")
    
    # Calculate claims per worker
    claims_per_worker = df.groupby('worker_id')['claimed_at'].apply(lambda x: x.notna().sum()).reset_index()
    claims_per_worker.columns = ['worker_id', 'claims_count']
    
    # Create activity bins
    claims_per_worker['activity_level'] = pd.cut(
        claims_per_worker['claims_count'],
        bins=[0, 1, 3, 5, 10, float('inf')],
        labels=['1 claim', '2-3 claims', '4-5 claims', '6-10 claims', '>10 claims']
    )
    
    activity_dist = claims_per_worker['activity_level'].value_counts().reset_index()
    activity_dist.columns = ['Activity Level', 'Number of Workers']
    
    col1, col2 = st.columns(2)
    
    with col1:
        activity_fig = px.bar(activity_dist, x='Activity Level', y='Number of Workers',
                             title='Worker Distribution by Activity Level',
                             color='Number of Workers',
                             color_continuous_scale='Viridis')
        st.plotly_chart(activity_fig, use_container_width=True)
    
    with col2:
        # Worker reliability
        reliability_df = df.groupby('worker_id').agg(
            total_claims=('claimed_at', lambda x: x.notna().sum()),
            cancellations=('canceled_at', lambda x: x.notna().sum()),
            no_shows=('is_ncns', 'sum'),
            completions=('is_verified', 'sum')
        ).reset_index()
        
        reliability_df = reliability_df[reliability_df['total_claims'] > 0].copy()
        reliability_df['cancellation_rate'] = (reliability_df['cancellations'] / reliability_df['total_claims'] * 100)
        reliability_df['no_show_rate'] = (reliability_df['no_shows'] / reliability_df['total_claims'] * 100)
        reliability_df['completion_rate'] = (reliability_df['completions'] / reliability_df['total_claims'] * 100)
        
        # Plot completion rate distribution
        completion_fig = px.histogram(reliability_df, x='completion_rate', nbins=20,
                                    title='Distribution of Worker Completion Rates',
                                    labels={'completion_rate': 'Completion Rate (%)'},
                                    color_discrete_sequence=['#109618'])
        st.plotly_chart(completion_fig, use_container_width=True)
    
    # Worker preference analysis
    st.subheader("Worker Preferences")
    
    # Time slot preferences
    worker_slots = df.groupby(['worker_id', 'slot']).size().reset_index()
    worker_slots.columns = ['worker_id', 'slot', 'count']
    
    # For each worker, find their preferred slot
    worker_pref_slot = worker_slots.loc[worker_slots.groupby('worker_id')['count'].idxmax()]
    slot_pref_dist = worker_pref_slot['slot'].value_counts().reset_index()
    slot_pref_dist.columns = ['Time Slot', 'Number of Workers']
    
    col1, col2 = st.columns(2)
    
    with col1:
        slot_pref_fig = px.pie(slot_pref_dist, names='Time Slot', values='Number of Workers',
                              title='Worker Preferred Time Slots',
                              color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(slot_pref_fig, use_container_width=True)
    
    with col2:
        # Rate sensitivity
        # Group by worker and pay rate bins
        df['pay_rate_bin'] = pd.cut(df['pay_rate'], 
                                   bins=[0, 20, 25, 30, 35, float('inf')],
                                   labels=['<$20', '$20-25', '$25-30', '$30-35', '>$35'])
        
        rate_conv = df.groupby('pay_rate_bin').agg(
            total_views=('shift_id', 'count'),
            claimed=('claimed_at', lambda x: x.notna().sum())
        ).reset_index()
        
        rate_conv['conversion_rate'] = (rate_conv['claimed'] / rate_conv['total_views'] * 100).round(2)
        
        rate_sens_fig = px.bar(rate_conv, x='pay_rate_bin', y='conversion_rate',
                             title='Conversion Rate by Pay Rate',
                             labels={'pay_rate_bin': 'Pay Rate Range', 'conversion_rate': 'Conversion Rate (%)'},
                             color='conversion_rate',
                             color_continuous_scale='Viridis')
        st.plotly_chart(rate_sens_fig, use_container_width=True)

# Workplace analysis
def workplace_analysis(df):
    st.header("Workplace Analysis")
    
    # Workplace activity metrics
    total_workplaces = df['workplace_id'].nunique()
    
    # Calculate shifts per workplace
    shifts_per_workplace = df[['workplace_id', 'shift_id']].drop_duplicates().groupby('workplace_id').size()
    avg_shifts_per_workplace = shifts_per_workplace.mean().round(2)
    max_shifts_per_workplace = shifts_per_workplace.max()
    
    # Get filled shifts per workplace
    filled_shifts = df[df['is_verified'] == True][['workplace_id', 'shift_id']].drop_duplicates()
    filled_per_workplace = filled_shifts.groupby('workplace_id').size()
    
    # Calculate fill rate
    workplace_fill_rate = pd.DataFrame({
        'total_shifts': shifts_per_workplace,
        'filled_shifts': filled_per_workplace
    }).fillna(0)
    
    workplace_fill_rate['fill_rate'] = (workplace_fill_rate['filled_shifts'] / workplace_fill_rate['total_shifts'] * 100).round(2)
    avg_fill_rate = workplace_fill_rate['fill_rate'].mean().round(2)
    
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.metric("Total Workplaces", f"{total_workplaces:,}")
    with metrics_cols[1]:
        st.metric("Avg Shifts per Workplace", f"{avg_shifts_per_workplace}")
    with metrics_cols[2]:
        st.metric("Max Shifts per Workplace", f"{max_shifts_per_workplace}")
    with metrics_cols[3]:
        st.metric("Avg Fill Rate", f"{avg_fill_rate}%")
    
    # Workplace distribution by volume
    st.subheader("Workplace Distribution by Shift Volume")
    
    # Create volume bins
    workplace_volume = df[['workplace_id', 'shift_id']].drop_duplicates().groupby('workplace_id').size().reset_index()
    workplace_volume.columns = ['workplace_id', 'shift_count']
    
    workplace_volume['volume_level'] = pd.cut(
        workplace_volume['shift_count'],
        bins=[0, 1, 5, 10, 20, 50, float('inf')],
        labels=['1 shift', '2-5 shifts', '6-10 shifts', '11-20 shifts', '21-50 shifts', '>50 shifts']
    )
    
    volume_dist = workplace_volume['volume_level'].value_counts().reset_index()
    volume_dist.columns = ['Volume Level', 'Number of Workplaces']
    
    col1, col2 = st.columns(2)
    
    with col1:
        volume_fig = px.bar(volume_dist, x='Volume Level', y='Number of Workplaces',
                          title='Workplace Distribution by Shift Volume',
                          color='Number of Workplaces',
                          color_continuous_scale='Viridis')
        st.plotly_chart(volume_fig, use_container_width=True)
    
    with col2:
        # Fill rate distribution
        fill_rate_fig = px.histogram(workplace_fill_rate, x='fill_rate', nbins=20,
                                   title='Distribution of Workplace Fill Rates',
                                   labels={'fill_rate': 'Fill Rate (%)'},
                                   color_discrete_sequence=['#3366CC'])
        st.plotly_chart(fill_rate_fig, use_container_width=True)
    
    # Lead time analysis for workplaces
    st.subheader("Workplace Posting Behavior")
    
    # Calculate average lead time for each workplace
    workplace_lead_time = df.groupby('workplace_id')['lead_time_hours'].mean().reset_index()
    workplace_lead_time.columns = ['workplace_id', 'avg_lead_time']
    
    # Create lead time bins
    workplace_lead_time['lead_time_category'] = pd.cut(
        workplace_lead_time['avg_lead_time'],
        bins=[0, 24, 48, 72, 168, float('inf')],
        labels=['<1 day', '1-2 days', '2-3 days', '3-7 days', '>7 days']
    )
    
    lead_time_dist = workplace_lead_time['lead_time_category'].value_counts().reset_index()
    lead_time_dist.columns = ['Lead Time', 'Number of Workplaces']
    
    # Plot lead time distribution
    lead_time_fig = px.bar(lead_time_dist, x='Lead Time', y='Number of Workplaces',
                         title='Workplace Distribution by Average Lead Time',
                         color='Number of Workplaces',
                         color_continuous_scale='Viridis')
    st.plotly_chart(lead_time_fig, use_container_width=True)
    
    # Top workplaces by volume
    st.subheader("Top Workplaces by Volume")
    
    top_workplaces = workplace_volume.sort_values('shift_count', ascending=False).head(10)
    
    top_wp_fig = px.bar(top_workplaces, x='workplace_id', y='shift_count',
                       title='Top 10 Workplaces by Shift Volume',
                       labels={'workplace_id': 'Workplace ID', 'shift_count': 'Number of Shifts'},
                       color='shift_count',
                       color_continuous_scale='Viridis')
    
    # Update to show cleaner workplace IDs
    top_wp_fig.update_layout(xaxis_tickformat='.5s')
    
    st.plotly_chart(top_wp_fig, use_container_width=True)

# Rate and pricing analysis
def rate_analysis(df):
    st.header("Rate & Pricing Analysis")
    
    # Rate summary statistics
    pay_rate_avg = df['pay_rate'].mean().round(2)
    charge_rate_avg = df['charge_rate'].mean().round(2)
    
    # Calculate markup
    df['markup'] = df['charge_rate'] - df['pay_rate']
    df['markup_percentage'] = (df['markup'] / df['pay_rate'] * 100).round(2)
    
    markup_avg = df['markup'].mean().round(2)
    markup_pct_avg = df['markup_percentage'].mean().round(2)
    
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.metric("Avg Pay Rate", f"${pay_rate_avg}")
    with metrics_cols[1]:
        st.metric("Avg Charge Rate", f"${charge_rate_avg}")
    with metrics_cols[2]:
        st.metric("Avg Markup", f"${markup_avg}")
    with metrics_cols[3]:
        st.metric("Avg Markup %", f"{markup_pct_avg}%")
    
    # Rate distributions
    st.subheader("Rate Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pay rate distribution
        pay_fig = px.histogram(df, x='pay_rate', nbins=30,
                             title='Distribution of Pay Rates',
                             labels={'pay_rate': 'Pay Rate ($)'},
                             color_discrete_sequence=['#3366CC'])
        st.plotly_chart(pay_fig, use_container_width=True)
    
    with col2:
        # Charge rate distribution
        charge_fig = px.histogram(df, x='charge_rate', nbins=30,
                               title='Distribution of Charge Rates',
                               labels={'charge_rate': 'Charge Rate ($)'},
                               color_discrete_sequence=['#DC3912'])
        st.plotly_chart(charge_fig, use_container_width=True)
    
    # Rate analysis by time slot
    st.subheader("Rate Analysis by Time Slot")
    
    slot_rates = df.groupby('slot').agg(
        avg_pay_rate=('pay_rate', 'mean'),
        avg_charge_rate=('charge_rate', 'mean'),
        avg_markup=('markup', 'mean'),
        avg_markup_pct=('markup_percentage', 'mean')
    ).reset_index()
    
    # Round numeric columns
    for col in slot_rates.columns:
        if col != 'slot':
            slot_rates[col] = slot_rates[col].round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pay and charge rates by slot
        slot_rate_fig = go.Figure()
        
        slot_rate_fig.add_trace(go.Bar(
            x=slot_rates['slot'],
            y=slot_rates['avg_pay_rate'],
            name='Pay Rate',
            marker_color='#3366CC'
        ))
        
        slot_rate_fig.add_trace(go.Bar(
            x=slot_rates['slot'],
            y=slot_rates['avg_charge_rate'],
            name='Charge Rate',
            marker_color='#DC3912'
        ))
        
        slot_rate_fig.update_layout(
            title='Average Pay and Charge Rates by Time Slot',
            xaxis_title='Time Slot',
            yaxis_title='Rate ($)',
            barmode='group'
        )
        
        st.plotly_chart(slot_rate_fig, use_container_width=True)
    
    with col2:
        # Markup by slot
        markup_slot_fig = px.bar(slot_rates, x='slot', y='avg_markup',
                               title='Average Markup by Time Slot',
                               labels={'slot': 'Time Slot', 'avg_markup': 'Average Markup ($)'},
                               color='avg_markup',
                               color_continuous_scale='Viridis')
        st.plotly_chart(markup_slot_fig, use_container_width=True)
    
    # Rate effectiveness analysis
    st.subheader("Rate Effectiveness Analysis")
    
    # Create pay rate bins
    df['pay_rate_bin'] = pd.cut(df['pay_rate'],
                              bins=[0, 20, 25, 30, 35, float('inf')],
                              labels=['<$20', '$20-25', '$25-30', '$30-35', '>$35'])
    
    # Calculate conversion rate by pay rate bin
    pay_rate_conv = df.groupby('pay_rate_bin').agg(
        total_views=('shift_id', 'count'),
        claimed=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    pay_rate_conv['conversion_rate'] = (pay_rate_conv['claimed'] / pay_rate_conv['total_views'] * 100).round(2)
    pay_rate_conv['completion_rate'] = (pay_rate_conv['verified'] / pay_rate_conv['claimed'] * 100).round(2)
    
    # Replace NaN with 0
    pay_rate_conv = pay_rate_conv.fillna(0)
    
    rate_eff_fig = go.Figure()
    
    rate_eff_fig.add_trace(go.Bar(
        x=pay_rate_conv['pay_rate_bin'],
        y=pay_rate_conv['conversion_rate'],
        name='Conversion Rate',
        marker_color='#3366CC'
    ))
    
    rate_eff_fig.add_trace(go.Bar(
        x=pay_rate_conv['pay_rate_bin'],
        y=pay_rate_conv['completion_rate'],
        name='Completion Rate',
        marker_color='#109618'
    ))
    
    rate_eff_fig.update_layout(
        title='Conversion and Completion Rates by Pay Rate',
        xaxis_title='Pay Rate Range',
        yaxis_title='Rate (%)',
        barmode='group'
    )
    
    st.plotly_chart(rate_eff_fig, use_container_width=True)

# Time series analysis
def time_series(df):
    st.header("Time Series Analysis")
    
    # Create daily and weekly aggregations
    df['date'] = df['shift_start_at'].dt.date
    df['week'] = df['shift_start_at'].dt.isocalendar().week
    df['month'] = df['shift_start_at'].dt.month
    
    # Daily metrics
    daily_metrics = df.groupby('date').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    daily_metrics['conversion_rate'] = (daily_metrics['claims'] / daily_metrics['views'] * 100).round(2)
    daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])
    
    # Weekly metrics
    weekly_metrics = df.groupby(['week']).agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    weekly_metrics['conversion_rate'] = (weekly_metrics['claims'] / weekly_metrics['views'] * 100).round(2)
    
    # Time series plots
    st.subheader("Marketplace Activity Over Time")
    
    activity_ts_fig = go.Figure()
    
    activity_ts_fig.add_trace(go.Scatter(
        x=daily_metrics['date'],
        y=daily_metrics['views'],
        name='Views',
        marker_color='#3366CC',
        mode='lines'
    ))
    
    activity_ts_fig.add_trace(go.Scatter(
        x=daily_metrics['date'],
        y=daily_metrics['claims'],
        name='Claims',
        marker_color='#DC3912',
        mode='lines'
    ))
    
    activity_ts_fig.add_trace(go.Scatter(
        x=daily_metrics['date'],
        y=daily_metrics['verified'],
        name='Verified Shifts',
        marker_color='#109618',
        mode='lines'
    ))
    
    activity_ts_fig.update_layout(
        title='Daily Marketplace Activity',
        xaxis_title='Date',
        yaxis_title='Count',
        hovermode='x unified'
    )
    
    st.plotly_chart(activity_ts_fig, use_container_width=True)
    
    # Conversion rate over time
    st.subheader("Conversion Rate Over Time")
    
    conv_ts_fig = px.line(daily_metrics, x='date', y='conversion_rate',
                         title='Daily Conversion Rate',
                         labels={'date': 'Date', 'conversion_rate': 'Conversion Rate (%)'},
                         color_discrete_sequence=['#109618'])
    
    st.plotly_chart(conv_ts_fig, use_container_width=True)
    
    # Day of week analysis
    st.subheader("Day of Week Analysis")
    
    df['day_of_week'] = df['shift_start_at'].dt.day_name()
    
    # Order days correctly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    dow_metrics = df.groupby('day_of_week').agg(
        total_views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    dow_metrics['conversion_rate'] = (dow_metrics['claims'] / dow_metrics['total_views'] * 100).round(2)
    
    # Reorder days
    dow_metrics['day_of_week'] = pd.Categorical(dow_metrics['day_of_week'], categories=day_order, ordered=True)
    dow_metrics = dow_metrics.sort_values('day_of_week')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Volume by day of week
        dow_vol_fig = px.bar(dow_metrics, x='day_of_week', y='total_views',
                           title='Shift Volume by Day of Week',
                           labels={'day_of_week': 'Day of Week', 'total_views': 'Number of Views'},
                           color='total_views',
                           color_continuous_scale='Viridis')
        st.plotly_chart(dow_vol_fig, use_container_width=True)
    
    with col2:
        # Conversion by day of week
        dow_conv_fig = px.bar(dow_metrics, x='day_of_week', y='conversion_rate',
                            title='Conversion Rate by Day of Week',
                            labels={'day_of_week': 'Day of Week', 'conversion_rate': 'Conversion Rate (%)'},
                            color='conversion_rate',
                            color_continuous_scale='Viridis')
        st.plotly_chart(dow_conv_fig, use_container_width=True)

# Key insights and recommendations
def insights():
    st.header("Key Insights & Recommendations")
    
    if 'data' not in st.session_state:
        st.warning("Please upload data in the Introduction section first to generate insights.")
        return
    
    df = st.session_state['data']
    
    # Calculate key metrics for the insights
    total_views = len(df)
    unique_shifts = df['shift_id'].nunique()
    unique_workers = df['worker_id'].nunique()
    unique_workplaces = df['workplace_id'].nunique()
    claimed_shifts = df['claimed_at'].notna().sum()
    conversion_rate = (claimed_shifts / total_views * 100).round(2)
    verified_shifts = df['is_verified'].sum()
    fulfillment_rate = (verified_shifts / claimed_shifts * 100).round(2) if claimed_shifts > 0 else 0
    
    # Calculate worker activity distribution
    worker_claims = df.groupby('worker_id')['claimed_at'].apply(lambda x: x.notna().sum()).reset_index()
    worker_claims.columns = ['worker_id', 'claims_count']
    active_workers = len(worker_claims[worker_claims['claims_count'] > 0])
    top_20_pct_claims = worker_claims.sort_values('claims_count', ascending=False)
    top_workers_threshold = int(unique_workers * 0.2)
    top_workers_claim_share = (top_20_pct_claims.head(top_workers_threshold)['claims_count'].sum() / claimed_shifts * 100).round(2)
    
    # Calculate time slot conversion rates
    slot_conv = df.groupby('slot').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    slot_conv['conversion_rate'] = (slot_conv['claims'] / slot_conv['views'] * 100).round(2)
    best_slot = slot_conv.loc[slot_conv['conversion_rate'].idxmax()]
    worst_slot = slot_conv.loc[slot_conv['conversion_rate'].idxmin()]
    
    # Calculate lead time impact
    df['lead_time_hours'] = (df['shift_start_at'] - df['shift_created_at']).dt.total_seconds() / 3600
    lead_time_bins = [0, 24, 48, 72, 168, float('inf')]
    lead_time_labels = ['<1 day', '1-2 days', '2-3 days', '3-7 days', '>7 days']
    df['lead_time_bin'] = pd.cut(df['lead_time_hours'], bins=lead_time_bins, labels=lead_time_labels)
    lead_conv = df.groupby('lead_time_bin').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    lead_conv['conversion_rate'] = (lead_conv['claims'] / lead_conv['views'] * 100).round(2)
    best_lead_time = lead_conv.loc[lead_conv['conversion_rate'].idxmax()]
    
    # Calculate rate sensitivity
    df['pay_rate_bin'] = pd.cut(df['pay_rate'], 
                              bins=[0, 20, 25, 30, 35, float('inf')],
                              labels=['<$20', '$20-25', '$25-30', '$30-35', '>$35'])
    rate_conv = df.groupby('pay_rate_bin').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    rate_conv['conversion_rate'] = (rate_conv['claims'] / rate_conv['views'] * 100).round(2)
    best_rate = rate_conv.loc[rate_conv['conversion_rate'].idxmax()]
    
    # Generate the insights markdown
    st.markdown(f"""
    ## Summary of Findings
    
    Based on the analysis of the CBH marketplace data, here are the key insights:
    
    ### Market Overview
    - **Market Size**: The dataset contains {total_views:,} shift views across {unique_shifts:,} unique shifts, with {unique_workers:,} workers and {unique_workplaces:,} workplaces.
    - **Conversion Performance**: Overall marketplace conversion rate is {conversion_rate}%, with {claimed_shifts:,} claimed shifts out of {total_views:,} views.
    - **Fulfillment Rate**: {fulfillment_rate}% of claimed shifts were successfully completed (verified).
    
    ### Marketplace Dynamics
    - **Conversion Rate**: The overall marketplace conversion rate is {conversion_rate}%, which represents the percentage of views that lead to claims.
    - **Time Slot Preferences**: The {best_slot['slot']} time slot has the highest conversion rate at {best_slot['conversion_rate']}%, while the {worst_slot['slot']} time slot has the lowest at {worst_slot['conversion_rate']}%.
    - **Lead Time Impact**: Shifts posted {best_lead_time['lead_time_bin']} before the start date show the best conversion rate at {best_lead_time['conversion_rate']}%, suggesting an optimal posting window.
    
    ### Worker Behavior
    - **Activity Distribution**: Top 20% of workers account for {top_workers_claim_share}% of all claimed shifts, showing a concentration of activity among power users.
    - **Active Worker Base**: Out of {unique_workers:,} workers who viewed shifts, {active_workers:,} ({(active_workers/unique_workers*100).round(2)}%) claimed at least one shift.
    - **Rate Sensitivity**: The highest conversion rate of {best_rate['conversion_rate']}% occurs in the {best_rate['pay_rate_bin']} pay rate range, indicating a sweet spot for worker engagement.
    
    ### Workplace Patterns
    - **Volume Distribution**: Workplaces vary widely in the number of shifts they post, with some being significantly more active than others.
    - **Fill Rates**: There are notable differences in fill rates across workplaces, suggesting varying levels of attractiveness to workers.
    - **Posting Strategy**: Workplace posting timing and lead time have significant impacts on fill success, with optimal lead times showing better performance.
    
    ### Rate & Pricing
    - **Pricing Effectiveness**: Pay rates in the {best_rate['pay_rate_bin']} range show the highest conversion at {best_rate['conversion_rate']}%, but with diminishing returns at higher rates.
    - **Markup Optimization**: Different time slots and shift types support different markup percentages, allowing for optimization.
    - **Competitive Positioning**: Market rates show clear patterns that can inform dynamic pricing strategies to maximize both conversion and margin.
    
    ## Recommendations
    
    1. **Optimized Lead Times**: Encourage workplaces to post shifts further in advance, as data shows higher conversion rates for shifts with longer lead times.
    
    2. **Dynamic Pricing Strategy**: Implement time slot-specific pricing that accounts for worker preferences and marketplace demand patterns.
    
    3. **Worker Engagement Focus**: Target retention efforts on the most active and reliable workers, while designing specific programs to increase activity among occasional workers.
    
    4. **Workplace Onboarding Improvements**: Provide data-driven guidance to workplaces on optimal posting strategies based on marketplace patterns.
    
    5. **Personalized Recommendations**: Leverage worker preference data to match workers with shifts they're most likely to claim.
    
    6. **Supply-Demand Balancing**: Identify time slots and geographic areas with supply-demand imbalances and implement targeted incentives.
    
    7. **Reliability Incentives**: Develop incentive programs that reward workers for maintaining high completion rates and low cancellation rates.
    
    8. **Pricing Tiers**: Test tiered pricing structures that optimize both conversion rates and marketplace revenue.
    """)
    
    # Create exportable report
    report_data = io.StringIO()
    
    report_content = """
    # CBH Marketplace Analysis Report
    
    ## Executive Summary
    
    The CBH marketplace demonstrates strong network effects as workers and workplaces interact to fulfill per diem shift needs. This analysis explores key dynamics, behaviors, and opportunities within the marketplace.
    
    ## Key Findings
    
    ### Marketplace Dynamics
    - Conversion rates vary significantly by time slot, day of week, and lead time
    - Lead time has a substantial impact on shift fill rates
    - Time slot preferences show clear patterns that can inform scheduling
    
    ### Worker Behavior
    - A small percentage of workers claim most shifts
    - Worker reliability metrics provide insights for targeted retention
    - Pay rate sensitivity shows patterns that can optimize pricing
    
    ### Workplace Patterns
    - Workplace posting behavior varies widely
    - Fill rates correlate with specific workplace behaviors
    - Timing of shift posting impacts success rates
    
    ### Rate & Pricing
    - Price elasticity varies by time slot and shift type
    - Optimal markup percentages differ across market segments
    - Pricing effectiveness can be improved through dynamic strategies
    
    ## Recommendations
    
    1. Optimize lead times for shift posting
    2. Implement dynamic pricing by time slot
    3. Focus on retention of most active workers
    4. Improve workplace onboarding with data-driven guidance
    5. Develop personalized shift recommendations
    6. Balance supply-demand in underserved areas
    7. Create reliability incentive programs
    8. Test tiered pricing structures
    
    ## Next Steps
    
    1. A/B test pricing recommendations
    2. Develop predictive models for conversion likelihood
    3. Create worker and workplace dashboards for performance metrics
    4. Implement automated recommendations in the marketplace
    """
    
    report_data.write(report_content)
    
    st.download_button(
        label="Download Analysis Report",
        data=report_data.getvalue(),
        file_name="cbh_marketplace_analysis.md",
        mime="text/markdown"
    )

# Main app logic
def main():
    # Create sidebar for navigation
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio("Go to", list(SECTIONS.keys()))
    
    # Introduction section does not require data
    if page == "Introduction":
        introduction()
        
        # Data upload
        uploaded_file = st.file_uploader("Upload your marketplace data (CSV format)", type="csv")
        
        if uploaded_file is not None:
            with st.spinner("Loading and processing data..."):
                try:
                    df = load_and_clean_data(uploaded_file)
                    st.session_state['data'] = df
                    st.success("Data loaded successfully!")
                    
                    # Show preview
                    st.subheader("Data Preview")
                    st.dataframe(df.head(5))
                    
                    st.markdown("**Now you can navigate to other sections using the sidebar.**")
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")
        
        # Option to use the attached demo dataset
        st.markdown("---")
        st.markdown("### Use Demo Dataset")
        if st.button("Load Demo Dataset"):
            with st.spinner("Loading demo dataset..."):
                try:
                    demo_file = "attached_assets/Problems we tackle, Shift Offers v3 - table_12_2025-01-22T1134.csv"
                    df = pd.read_csv(demo_file)
                    df = load_and_clean_data(io.StringIO(df.to_csv(index=False)))
                    st.session_state['data'] = df
                    st.success("Demo data loaded successfully!")
                    
                    # Show preview
                    st.subheader("Data Preview")
                    st.dataframe(df.head(5))
                    
                    st.markdown("**Now you can navigate to other sections using the sidebar.**")
                except Exception as e:
                    st.error(f"Error loading demo data: {str(e)}")
        
        # If data exists in session and user wants to clear it
        elif 'data' in st.session_state:
            if st.button("Clear loaded data"):
                del st.session_state['data']
                st.rerun()
    
    # All other sections require data
    elif 'data' in st.session_state:
        df = st.session_state['data']
        
        if page == "Data Overview":
            data_overview(df)
        elif page == "Marketplace Dynamics":
            marketplace_dynamics(df)
        elif page == "Worker Analysis":
            worker_analysis(df)
        elif page == "Workplace Analysis":
            workplace_analysis(df)
        elif page == "Rate & Pricing Analysis":
            rate_analysis(df)
        elif page == "Time Series Analysis":
            time_series(df)
        elif page == "Key Insights & Recommendations":
            insights()
    
    else:
        st.warning("Please upload data in the Introduction section first.")
        
        # Quick jump to introduction
        if st.button("Go to Introduction"):
            introduction_index = list(SECTIONS.keys()).index("Introduction")
            st.session_state['current_page'] = introduction_index
            st.rerun()

if __name__ == "__main__":
    main()
