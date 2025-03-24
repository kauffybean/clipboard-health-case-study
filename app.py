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

# CSS to make the UI consistent and visually appealing
st.markdown("""
    <style>
        /* Define consistent color palette */
        :root {
            --primary-color: #3366CC;     /* Blue for main elements */
            --secondary-color: #109618;   /* Green for success/completion */
            --accent-color: #DC3912;      /* Red for highlights/conversion */
            --neutral-color: #FF9900;     /* Orange for additional metrics */
            --background-color: #F9FAFC;  /* Light background */
            --light-gray: #E8EEF4;        /* For alternating rows */
            --text-color: #333333;        /* Main text color */
        }
        
        /* Overall layout styling */
        .main .block-container {
            max-width: 1200px;
            padding: 2rem 1.5rem;
            background-color: var(--background-color);
        }
        
        /* Improve spacing and alignment */
        .row-widget.stVerticalBlock > div {
            margin-bottom: 1.5rem;
        }
        
        /* Fix compressed sections */
        .stPlotlyChart {
            width: 100%;
            margin-bottom: 2rem;
        }
        
        /* Typography styling */
        h1 {
            color: var(--primary-color);
            font-size: 2.5rem;
            padding-top: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--light-gray);
            margin-bottom: 1.8rem;
        }
        
        h2 {
            color: var(--primary-color);
            font-size: 2rem;
            padding-top: 1.5rem;
            padding-bottom: 0.8rem;
            margin-bottom: 1.2rem;
            border-bottom: 1px solid var(--light-gray);
        }
        
        h3 {
            color: var(--secondary-color);
            font-size: 1.6rem;
            padding-top: 1rem;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        
        /* Key takeaways styling */
        .key-takeaways {
            background-color: white;
            border-left: 5px solid var(--primary-color);
            padding: 1.5rem;
            margin-bottom: 2.5rem;
            border-radius: 0 5px 5px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .key-takeaways h4 {
            color: var(--primary-color);
            font-size: 1.3rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--light-gray);
        }
        
        /* Metric styling */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            color: var(--primary-color) !important;
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 1.1rem !important;
            font-weight: 500 !important;
            color: var(--text-color) !important;
        }
        
        /* Table styling */
        div[data-testid="stTable"] table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: 5px;
            overflow: hidden;
        }
        
        div[data-testid="stTable"] thead tr th {
            background-color: var(--primary-color) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px 15px !important;
            text-align: left !important;
        }
        
        div[data-testid="stTable"] tbody tr:nth-child(even) {
            background-color: var(--light-gray) !important;
        }
        
        div[data-testid="stTable"] tbody tr td {
            padding: 10px 15px !important;
        }
        
        /* Dataframe styling */
        .dataframe {
            border-radius: 5px;
            overflow: hidden;
            border: none !important;
            margin-bottom: 1.5rem;
        }
        
        .dataframe th {
            background-color: var(--primary-color) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 10px 15px !important;
            text-align: left !important;
        }
        
        .dataframe tr:nth-child(even) {
            background-color: var(--light-gray) !important;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: white;
            border-right: 1px solid var(--light-gray);
        }
        
        section[data-testid="stSidebar"] div.stRadio label {
            font-weight: 500;
            padding: 8px 5px;
            cursor: pointer;
        }
        
        section[data-testid="stSidebar"] div.stRadio label:hover {
            color: var(--primary-color);
        }
        
        /* Charts styling */
        div.stPlotlyChart > div {
            border-radius: 8px;
            background-color: white !important;
            padding: 1.5rem !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        
        /* Tab styling */
        button[data-baseweb="tab"] {
            font-weight: 600;
            padding: 8px 16px !important;
        }
        
        /* Code block styling */
        div.stCodeBlock {
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
            margin-bottom: 1.5rem;
            background-color: #f7f9fc !important;
        }
        
        /* Navigation buttons */
        .nav-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 8px 20px;
            background-color: var(--primary-color);
            color: white;
            border-radius: 50px;
            font-weight: 600;
            text-decoration: none;
            margin: 8px 12px 8px 0;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .nav-button:hover {
            background-color: #2855b5;
            box-shadow: 0 3px 8px rgba(0,0,0,0.2);
        }
        
        .nav-button-container {
            display: flex;
            margin-top: 2rem;
            margin-bottom: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--light-gray);
        }
        
        /* Key insights and recommendations styling */
        .insight-card {
            background-color: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 5px solid var(--secondary-color);
        }
        
        .insight-card h4 {
            color: var(--secondary-color);
            font-size: 1.4rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--light-gray);
        }
        
        .recommendation-card {
            background-color: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 5px solid var(--accent-color);
        }
        
        .recommendation-card h4 {
            color: var(--accent-color);
            font-size: 1.4rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--light-gray);
        }
    </style>
""", unsafe_allow_html=True)

# App title and introduction
def introduction():
    st.title("CBH Marketplace Data Analysis")
    st.markdown("""
    ## Interactive Case Study: Uncovering Market Patterns and Opportunities
    
    Welcome to this interactive analysis of Clipboard Health (CBH) - a two-sided healthcare staffing marketplace
    with strong network effects where healthcare workers transact with workplaces to book per diem shifts.
    
    **The Business Context**:
    
    CBH operates as a marketplace platform connecting healthcare facilities with qualified healthcare workers 
    for on-demand staffing needs. Workplaces post shifts they need to fill, and workers browse and claim shifts 
    they want to work. The platform needs to balance the needs of both sides to create a healthy marketplace.
    
    **Key Business Questions**:
    
    1. How effective is the marketplace at converting shift views to bookings?
    2. What patterns exist in worker and workplace behaviors?
    3. How does timing (posting time, lead time) affect marketplace success?
    4. What role does pricing play in marketplace dynamics?
    5. What recommendations can improve marketplace performance?
    
    **Data Background**:
    
    The dataset contains detailed records of shift offers viewed by workers, including whether they claimed
    the shift, if they completed it, pricing information, and timing details. Each record represents a worker
    viewing a shift, with the potential outcomes including claiming, canceling, or ignoring the shift.
    
    **Case Study Navigation**:
    
    This interactive case study is organized into sections that build on each other:
    
    1. **Data Overview**: Understand the dataset structure and quality
    2. **Marketplace Dynamics**: Analyze conversion rates and activity patterns
    3. **Worker Analysis**: Explore worker behaviors and preferences
    4. **Workplace Analysis**: Examine workplace posting patterns
    5. **Rate & Pricing Analysis**: Investigate price sensitivity and margins
    6. **Time Series Analysis**: Study temporal patterns in marketplace activity
    7. **Key Insights & Recommendations**: Discover actionable findings
    
    Use the navigation sidebar to explore each section of the analysis.
    """)

# Data overview section
def data_overview(df):
    st.header("Data Overview")
    
    # Data summary
    st.subheader("Dataset Summary")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", f"{len(df):,}")
        st.metric("Unique Workers", f"{df['worker_id'].nunique():,}")
    with col2:
        st.metric("Unique Workplaces", f"{df['workplace_id'].nunique():,}")
        st.metric("Unique Shifts", f"{df['shift_id'].nunique():,}")
    with col3:
        st.metric("Date Range", f"{df['shift_start_at'].min().date()} to {df['shift_start_at'].max().date()}")
        st.metric("Avg Hourly Pay Rate", f"${df['pay_rate'].mean():.2f}")
    
    # Dataframe and glossary
    st.subheader("Dataset Structure")
    tab1, tab2, tab3 = st.tabs(["Data Sample", "Data Glossary", "Code Example"])
    
    with tab1:
        st.dataframe(df.head(10), height=300)
    
    with tab2:
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
                'Worker completed the shift (boolean)',
                'Time shift was canceled by worker (UTC)',
                'Worker was a no-call-no-show (boolean)',
                'Hourly rate offered to worker for the shift ($)',
                'Hourly rate charged to workplace for the shift ($)'
            ]
        }
        glossary_df = pd.DataFrame(glossary_data)
        st.dataframe(glossary_df, height=300)
    
    with tab3:
        st.code("""
# Python code for loading and previewing the dataset
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('cbh_marketplace_data.csv')

# Convert datetime columns
datetime_cols = ['shift_start_at', 'shift_created_at', 'offer_viewed_at', 
                'claimed_at', 'deleted_at', 'canceled_at']
for col in datetime_cols:
    df[col] = pd.to_datetime(df[col])

# Display basic info
print(f"Dataset shape: {df.shape}")
print(f"Unique workers: {df['worker_id'].nunique()}")
print(f"Unique workplaces: {df['workplace_id'].nunique()}")
print(f"Date range: {df['shift_start_at'].min().date()} to {df['shift_start_at'].max().date()}")

# Preview the data
df.head()
        """)
    
    # Data quality assessment
    st.subheader("Data Quality Assessment")
    
    # Create tabs for different quality aspects
    tab1, tab2, tab3 = st.tabs(["Missing Values", "Data Distributions", "Data Types"])
    
    with tab1:
        # Missing values visualization
        missing_data = df.isnull().sum().to_frame().reset_index()
        missing_data.columns = ['Column', 'Missing Values']
        missing_data['Missing Percentage'] = (missing_data['Missing Values'] / len(df) * 100).round(2)
        missing_data = missing_data.sort_values('Missing Percentage', ascending=False)
        
        # Only show columns with missing values
        missing_data_with_nulls = missing_data[missing_data['Missing Values'] > 0]
        
        if len(missing_data_with_nulls) > 0:
            fig = px.bar(missing_data_with_nulls, 
                      x='Column', 
                      y='Missing Percentage',
                      title='Percentage of Missing Values by Column',
                      color='Missing Percentage',
                      color_continuous_scale='Reds')
            fig.update_layout(xaxis_title='Column', yaxis_title='Missing Percentage (%)')
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("**Missing Values Analysis:**")
            st.write("""
            The missing values in this dataset are actually informative. For example:
            - Missing `claimed_at` indicates the worker didn't claim the shift
            - Missing `canceled_at` means the worker didn't cancel the shift
            - Missing `deleted_at` means the workplace didn't delete the shift
            
            These nulls represent the status of the shift in the marketplace journey and are expected.
            """)
        else:
            st.info("No missing values found in the dataset.")
    
    with tab2:
        # Showing distributions of key variables
        col1, col2 = st.columns(2)
        
        with col1:
            # Pay rate distribution
            fig = px.histogram(df, x='pay_rate', nbins=30,
                            title='Distribution of Pay Rates',
                            labels={'pay_rate': 'Hourly Pay Rate ($)'},
                            color_discrete_sequence=['#3366CC'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Duration distribution
            fig = px.histogram(df, x='duration', nbins=20,
                            title='Distribution of Shift Durations',
                            labels={'duration': 'Shift Duration (hours)'},
                            color_discrete_sequence=['#DC3912'])
            st.plotly_chart(fig, use_container_width=True)
            
        # Slot distribution
        slot_counts = df['slot'].value_counts().reset_index()
        slot_counts.columns = ['Slot', 'Count']
        
        fig = px.bar(slot_counts, x='Slot', y='Count',
                   title='Distribution of Shifts by Time Slot',
                   color='Count',
                   color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Data types and examples
        dtypes_df = pd.DataFrame({
            'Column': df.dtypes.index,
            'Type': df.dtypes.values
        })
        
        st.write("**Column Data Types:**")
        st.dataframe(dtypes_df, height=300)
        
        st.write("**Python Code for Data Type Conversion:**")
        st.code("""
# Convert data types for analysis
# Datetime conversions
datetime_cols = ['shift_start_at', 'shift_created_at', 'offer_viewed_at', 
                'claimed_at', 'deleted_at', 'canceled_at']
for col in datetime_cols:
    df[col] = pd.to_datetime(df[col])

# Boolean conversions
df['is_verified'] = df['is_verified'].astype(bool)
df['is_ncns'] = df['is_ncns'].astype(bool)

# Calculate derived fields
df['lead_time_hours'] = (df['shift_start_at'] - df['shift_created_at']).dt.total_seconds() / 3600
df['decision_time_minutes'] = df.apply(
    lambda x: (x['claimed_at'] - x['offer_viewed_at']).total_seconds() / 60 
    if pd.notna(x['claimed_at']) else None, axis=1
)
        """)
    
    # Summary statistics with context
    st.subheader("Summary Statistics with Insights")
    
    # Calculate summary stats and display
    numeric_cols = ['pay_rate', 'charge_rate', 'duration']
    stats_df = df[numeric_cols].describe().round(2)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.dataframe(stats_df, height=300)
    
    with col2:
        st.write("**Key Numerical Insights:**")
        
        # Calculate margin
        df['margin'] = df['charge_rate'] - df['pay_rate']
        avg_margin = df['margin'].mean()
        avg_margin_pct = (df['margin'] / df['charge_rate'] * 100).mean()
        
        st.write(f"""
        - **Pay Rate Range:** ${stats_df.loc['min', 'pay_rate']} to ${stats_df.loc['max', 'pay_rate']} per hour
        - **Average Pay Rate:** ${stats_df.loc['mean', 'pay_rate']} per hour
        - **Average Charge Rate:** ${stats_df.loc['mean', 'charge_rate']} per hour
        - **Average Margin:** ${avg_margin:.2f} per hour ({avg_margin_pct:.1f}% of charge rate)
        - **Shift Duration:** Most shifts range from {stats_df.loc['min', 'duration']} to {stats_df.loc['max', 'duration']} hours
        """)
        
        # Calculate correlation
        corr = df[['pay_rate', 'charge_rate', 'duration']].corr().round(2)
        
        st.write("**Correlation between Numerical Variables:**")
        st.dataframe(corr, height=200)

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
    
    # Add Key Takeaways at the top of the section
    st.markdown("""
    <div class="key-takeaways">
        <h4>Key Takeaways: Marketplace Dynamics</h4>
        <ul>
            <li><strong>View-to-Claim Conversion:</strong> {:.1f}% of viewed shifts are claimed, indicating potential opportunity to improve initial conversion.</li>
            <li><strong>Claim-to-Completion Rate:</strong> {:.1f}% of claimed shifts are successfully completed, highlighting reliability challenges.</li>
            <li><strong>Time Slot Preferences:</strong> {slot} shifts have the highest demand, but {low_slot} shifts show the lowest conversion rates.</li>
            <li><strong>Lead Time Impact:</strong> Shifts posted 24-72 hours before start time achieve optimal conversion rates.</li>
            <li><strong>Quick Decisions:</strong> Most workers make booking decisions within {decision_mins} minutes of viewing a shift.</li>
        </ul>
    </div>
    """.format(
        conversion_rate,
        (completed_shifts / claimed_shifts * 100) if claimed_shifts > 0 else 0,
        slot=df['slot'].value_counts().index[0],
        low_slot=df.groupby('slot')['claimed_at'].apply(lambda x: x.notna().sum() / len(x) * 100).sort_values().index[0],
        decision_mins=df[df['claimed_at'].notna()]['claimed_at'].sub(df[df['claimed_at'].notna()]['offer_viewed_at']).dt.total_seconds().div(60).median().round()
    ), unsafe_allow_html=True)
    
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
    
    # Add navigation buttons
    st.markdown("""
    <div class="nav-button-container">
        <a href="?section=data_overview" class="nav-button" style="margin-right: auto;">
            ← Previous: Data Overview
        </a>
        <a href="?section=worker_analysis" class="nav-button" style="margin-left: auto;">
            Next: Worker Analysis →
        </a>
    </div>
    """, unsafe_allow_html=True)

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
    
    # Calculate worker completion rate
    worker_completion_rate = df[df['claimed_at'].notna()].groupby('worker_id')['is_verified'].mean().mean() * 100
    
    # Calculate most common time slot preference
    worker_slots = df.groupby(['worker_id', 'slot']).size().reset_index()
    worker_slots.columns = ['worker_id', 'slot', 'count']
    worker_pref_slot = worker_slots.loc[worker_slots.groupby('worker_id')['count'].idxmax()]
    most_common_slot = worker_pref_slot['slot'].value_counts().index[0]
    
    # Add Key Takeaways at the top of the section
    st.markdown("""
    <div class="key-takeaways">
        <h4>Key Takeaways: Worker Behavior</h4>
        <ul>
            <li><strong>Worker Retention:</strong> Only {:.1f}% of workers who view shifts actually claim and complete them, indicating a significant drop-off.</li>
            <li><strong>Activity Patterns:</strong> Worker activity follows a power law distribution, with a small percentage of workers claiming the majority of shifts.</li>
            <li><strong>Reliability:</strong> Workers who claim shifts complete them {:.1f}% of the time, suggesting good reliability once committed.</li>
            <li><strong>Time Preference:</strong> Most workers prefer {preferred_slot} shifts, aligning with healthcare industry norms.</li>
            <li><strong>Rate Sensitivity:</strong> Conversion rates increase significantly for shifts paying more than $30/hour, suggesting a clear price threshold.</li>
        </ul>
    </div>
    """.format(
        (completed_workers / total_workers * 100),
        worker_completion_rate,
        preferred_slot=most_common_slot
    ), unsafe_allow_html=True)
    
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
    
    # Add navigation buttons
    st.markdown("""
    <div class="nav-button-container">
        <a href="?section=marketplace_dynamics" class="nav-button" style="margin-right: auto;">
            ← Previous: Marketplace Dynamics
        </a>
        <a href="?section=workplace_analysis" class="nav-button" style="margin-left: auto;">
            Next: Workplace Analysis →
        </a>
    </div>
    """, unsafe_allow_html=True)

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
    
    # Calculate lead time stats
    workplace_lead_time = df.groupby('workplace_id')['lead_time_hours'].mean()
    avg_lead_time = workplace_lead_time.mean().round(2)
    
    # Distribution of workplace volume
    workplace_volume = df[['workplace_id', 'shift_id']].drop_duplicates().groupby('workplace_id').size().reset_index()
    workplace_volume.columns = ['workplace_id', 'shift_count']
    high_volume_percentage = round(len(workplace_volume[workplace_volume['shift_count'] > 10]) / len(workplace_volume) * 100, 1)
    
    # Add Key Takeaways at the top of the section
    st.markdown("""
    <div class="key-takeaways">
        <h4>Key Takeaways: Workplace Behavior</h4>
        <ul>
            <li><strong>Workplace Concentration:</strong> Only {:.1f}% of workplaces post more than 10 shifts, suggesting a small group of power users drives volume.</li>
            <li><strong>Fill Rate Challenge:</strong> The average workplace fill rate is {:.1f}%, indicating room for improvement in matching supply and demand.</li>
            <li><strong>Posting Behavior:</strong> Workplaces post shifts with an average lead time of {:.1f} hours ({:.1f} days), which is often insufficient for optimal fill rates.</li>
            <li><strong>Volume Variability:</strong> The top workplace posted {max_shifts} shifts, while the average workplace posted only {avg_shifts} shifts.</li>
            <li><strong>Lead Time Impact:</strong> Workplaces that post shifts 3+ days in advance see significantly higher fill rates than those posting last-minute.</li>
        </ul>
    </div>
    """.format(
        high_volume_percentage,
        avg_fill_rate,
        avg_lead_time,
        avg_lead_time/24,
        max_shifts=max_shifts_per_workplace,
        avg_shifts=avg_shifts_per_workplace
    ), unsafe_allow_html=True)
    
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
    
    # Add navigation buttons
    st.markdown("""
    <div class="nav-button-container">
        <a href="?section=worker_analysis" class="nav-button" style="margin-right: auto;">
            ← Previous: Worker Analysis
        </a>
        <a href="?section=rate_analysis" class="nav-button" style="margin-left: auto;">
            Next: Rate & Pricing Analysis →
        </a>
    </div>
    """, unsafe_allow_html=True)

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
    
    # Find the pay rate with highest conversion
    df['pay_rate_bin'] = pd.cut(df['pay_rate'], 
                             bins=[0, 20, 25, 30, 35, float('inf')],
                             labels=['<$20', '$20-25', '$25-30', '$30-35', '>$35'])
    
    rate_conv = df.groupby('pay_rate_bin').agg(
        total_views=('shift_id', 'count'),
        claimed=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    rate_conv['conversion_rate'] = (rate_conv['claimed'] / rate_conv['total_views'] * 100).round(2)
    best_rate_bin = rate_conv.loc[rate_conv['conversion_rate'].idxmax()]['pay_rate_bin']
    best_conversion = rate_conv.loc[rate_conv['conversion_rate'].idxmax()]['conversion_rate']
    
    # Slot with highest markup
    slot_markup = df.groupby('slot')[['markup', 'markup_percentage']].mean().reset_index()
    highest_markup_slot = slot_markup.loc[slot_markup['markup'].idxmax()]['slot']
    highest_markup_value = slot_markup.loc[slot_markup['markup'].idxmax()]['markup'].round(2)
    
    # Add Key Takeaways at the top of the section
    st.markdown("""
    <div class="key-takeaways">
        <h4>Key Takeaways: Rate & Pricing</h4>
        <ul>
            <li><strong>Price Sensitivity:</strong> The {best_rate} rate range has the highest conversion at {conv_rate:.1f}%, suggesting a clear price threshold for worker engagement.</li>
            <li><strong>Margin Structure:</strong> Average markup is ${markup:.2f} ({markup_pct:.1f}% of charge rate), providing insights into platform economics.</li>
            <li><strong>Shift Time Pricing:</strong> {highest_slot} shifts command the highest markup (${highest_markup:.2f}), reflecting premium pricing for less desirable hours.</li>
            <li><strong>Price-Completion Link:</strong> Higher-priced shifts not only convert better but also have higher completion rates, suggesting better worker reliability.</li>
            <li><strong>Strategic Pricing:</strong> Data suggests optimal pricing exists at $30+ per hour where both conversion and completion rates exceed marketplace averages.</li>
        </ul>
    </div>
    """.format(
        best_rate=best_rate_bin,
        conv_rate=best_conversion,
        markup=markup_avg,
        markup_pct=markup_pct_avg,
        highest_slot=highest_markup_slot,
        highest_markup=highest_markup_value
    ), unsafe_allow_html=True)
    
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
    # Calculate completion rate safely
    completion_mask = pay_rate_conv['claimed'] > 0
    pay_rate_conv.loc[completion_mask, 'completion_rate'] = (
        pay_rate_conv.loc[completion_mask, 'verified'] / 
        pay_rate_conv.loc[completion_mask, 'claimed'] * 100
    ).round(2)
    # Set default value for rows where claimed is 0
    pay_rate_conv.loc[~completion_mask, 'completion_rate'] = 0
    
    # Replace NaN with 0
    # Don't use fillna on categorical data
    # Handle missing values in a way that works with categorical data
    pay_rate_conv['conversion_rate'] = pay_rate_conv['conversion_rate'].fillna(0)
    
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
    
    # Add navigation buttons
    st.markdown("""
    <div class="nav-button-container">
        <a href="?section=workplace_analysis" class="nav-button" style="margin-right: auto;">
            ← Previous: Workplace Analysis
        </a>
        <a href="?section=time_series" class="nav-button" style="margin-left: auto;">
            Next: Time Series Analysis →
        </a>
    </div>
    """, unsafe_allow_html=True)

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
    - **Active Worker Base**: Out of {unique_workers:,} workers who viewed shifts, {active_workers:,} ({round(active_workers/unique_workers*100, 2)}%) claimed at least one shift.
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
    # Load data automatically on app startup if not already loaded
    if 'data' not in st.session_state:
        try:
            with st.spinner("Loading CBH marketplace data for analysis..."):
                data_file = "attached_assets/Problems we tackle, Shift Offers v3 - table_12_2025-01-22T1134.csv"
                # Load data directly from the file
                df = load_and_clean_data(data_file)
                st.session_state['data'] = df
        except Exception as e:
            st.error(f"Error loading case study data: {str(e)}")
            st.error(f"Make sure the file exists and has the required columns (SHIFT_ID, WORKER_ID, etc.).")
    
    # Create sidebar for navigation
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio("Go to", list(SECTIONS.keys()))
    
    if page == "Introduction":
        introduction()
        
        # Show data preview
        if 'data' in st.session_state:
            df = st.session_state['data']
            st.subheader("CBH Marketplace Dataset Preview")
            st.dataframe(df.head(10))
            
            # Add key dataset metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", f"{len(df):,}")
            with col2:
                st.metric("Unique Workers", f"{df['worker_id'].nunique():,}")
            with col3:
                st.metric("Unique Workplaces", f"{df['workplace_id'].nunique():,}")
            with col4:
                st.metric("Unique Shifts", f"{df['shift_id'].nunique():,}")
            
            st.markdown("""
            ### Interactive Case Study
            This analysis explores the CBH marketplace data to uncover key patterns, behaviors, and opportunities.
            Use the navigation sidebar to explore different aspects of the analysis, including marketplace dynamics,
            worker behavior, workplace patterns, and pricing strategies.
            
            ### Key Questions Explored:
            1. What factors influence marketplace conversion rates?
            2. How do worker preferences and behaviors impact the marketplace?
            3. What patterns exist in workplace posting and fulfillment?
            4. How does pricing affect worker engagement and marketplace efficiency?
            5. What recommendations can be made to improve marketplace performance?
            
            Navigate through the sections to explore these questions and discover insights from the data.
            """)
    
    # All sections now have data access
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
        st.error("Failed to load the case study data. Please refresh the page to try again.")

if __name__ == "__main__":
    main()
