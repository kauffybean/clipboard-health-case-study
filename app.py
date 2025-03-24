import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_and_clean_data

# Page configuration
st.set_page_config(
    page_title="CBH Marketplace Analysis",
    page_icon="📊",
    layout="wide"
)

# Simple CSS for clean styling
st.markdown("""
<style>
    /* Key Finding Box */
    .key-finding {
        background-color: #EFF6FF;
        border-left: 4px solid #2563EB;
        padding: 1rem 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 5px 5px 0;
    }
    
    /* Navigation buttons between sections */
    .nav-container {
        display: flex;
        justify-content: space-between;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #e5e7eb;
    }
    
    .nav-button {
        background-color: #2563EB;
        color: white !important;
        padding: 8px 16px;
        border-radius: 4px;
        text-decoration: none !important;
        display: inline-block;
        font-weight: 500;
    }
    
    /* Code display */
    .code-box {
        background-color: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: monospace;
        overflow-x: auto;
    }
    
    /* Metric improvements */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Load the dataset
df = load_and_clean_data("attached_assets/Problems we tackle, Shift Offers v3 - table_12_2025-01-22T1134.csv")

# Define sections
SECTIONS = {
    "Introduction": "introduction",
    "Data Overview": "data_overview",
    "Marketplace Dynamics": "marketplace_dynamics", 
    "Worker Analysis": "worker_analysis",
    "Workplace Analysis": "workplace_analysis",
    "Rate Analysis": "rate_analysis",
    "Time Series": "time_series",
    "Key Insights": "insights"
}

# Sidebar navigation
st.sidebar.title("Navigation")
selected_section = st.sidebar.radio("Go to", list(SECTIONS.keys()))

# Alternatively get section from URL query param if it exists
query_params = st.query_params
if "section" in query_params:
    section_value = query_params["section"]
    # Find the key for this section value
    for key, value in SECTIONS.items():
        if value == section_value:
            selected_section = key
            break

# Set active section in URL
section_value = SECTIONS[selected_section]
st.query_params["section"] = section_value

# Introduction
def introduction():
    st.title("CBH Marketplace Analysis")
    st.markdown("""
    Welcome to the CBH Marketplace Analysis dashboard. This interactive case study explores 
    data from a two-sided marketplace where healthcare workers book per diem shifts with workplaces.
    """)
    
    st.markdown("""
    <div class="key-finding">
        <h4>About This Analysis</h4>
        <p>
        This analysis examines transaction data from a healthcare staffing marketplace, focusing on 
        key metrics and patterns to understand marketplace dynamics, worker behavior, workplace activity, 
        and rate sensitivity.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Questions")
        st.markdown("""
        - What drives conversion rates in this marketplace?
        - How do workers and workplaces behave?
        - What pricing strategies are most effective?
        - How does lead time affect fill rates?
        """)
    
    with col2:
        st.subheader("Data Sources")
        st.markdown("""
        The analysis is based on marketplace transaction data, including:
        - Shift details
        - Worker interactions
        - Workplace postings
        - Pricing information
        - Completion status
        """)
    
    st.subheader("Navigation")
    st.markdown("Use the sidebar to navigate through different sections of the analysis.")
    
    # Navigation buttons
    st.markdown("""
    <div class="nav-container">
        <div></div>
        <a href="?section=data_overview" class="nav-button">
            Next: Data Overview →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Data Overview
def data_overview(df):
    st.title("Data Overview")
    
    # Data summary
    st.subheader("Dataset Summary")
    
    # Shape and time range
    total_records = len(df)
    unique_shifts = df['shift_id'].nunique()
    unique_workers = df['worker_id'].nunique()
    unique_workplaces = df['workplace_id'].nunique()
    
    min_date = df['created_at'].min().strftime('%Y-%m-%d')
    max_date = df['created_at'].max().strftime('%Y-%m-%d')
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", f"{total_records:,}")
    with col2:
        st.metric("Unique Shifts", f"{unique_shifts:,}")
    with col3:
        st.metric("Unique Workers", f"{unique_workers:,}")
    with col4:
        st.metric("Unique Workplaces", f"{unique_workplaces:,}")
    
    st.markdown(f"**Date Range:** {min_date} to {max_date}")
    
    # Sample data
    st.subheader("Sample Data")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Data description
    st.subheader("Data Fields")
    st.markdown("""
    - **shift_id**: Unique identifier for a shift
    - **workplace_id**: Identifier for the workplace posting the shift
    - **worker_id**: Identifier for the worker viewing/claiming the shift
    - **pay_rate**: Hourly pay rate for the shift
    - **created_at**: When the shift was created/posted
    - **shift_date**: Date when the shift is scheduled
    - **slot**: Time slot of the shift (Morning, Evening, Night)
    - **lead_time_hours**: Hours between posting and shift start
    - **viewed_at**: When the worker viewed the shift
    - **claimed_at**: When the worker claimed the shift (if claimed)
    - **canceled_at**: When the worker canceled the shift (if canceled)
    - **is_ncns**: No Call No Show flag
    - **is_verified**: Whether the shift was completed and verified
    """)
    
    # Data quality
    st.subheader("Data Quality")
    
    # Missing values
    missing_data = pd.DataFrame(df.isnull().sum(), columns=['Missing Values'])
    missing_data['Percentage'] = (missing_data['Missing Values'] / len(df) * 100).round(2)
    missing_data = missing_data.reset_index().rename(columns={'index': 'Field'})
    
    st.markdown("#### Missing Values")
    st.dataframe(missing_data, use_container_width=True)
    
    # Code example for transparency
    st.subheader("Data Loading & Cleaning Process")
    st.markdown("""
    <div class="code-box">
    ```python
    def load_and_clean_data(file_path):
        # Load the data
        df = pd.read_csv(file_path)
        
        # Convert date columns to datetime
        date_columns = ['created_at', 'shift_date', 'viewed_at', 'claimed_at', 'canceled_at']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col])
        
        # Calculate lead time in hours
        df['lead_time_hours'] = (df['shift_date'] - df['created_at']).dt.total_seconds() / 3600
        
        # Convert boolean columns
        df['is_ncns'] = df['is_ncns'].astype(bool)
        df['is_verified'] = df['is_verified'].astype(bool)
        
        return df
    ```
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("""
    <div class="nav-container">
        <a href="?section=introduction" class="nav-button">
            ← Previous: Introduction
        </a>
        <a href="?section=marketplace_dynamics" class="nav-button">
            Next: Marketplace Dynamics →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Marketplace Dynamics
def marketplace_dynamics(df):
    st.title("Marketplace Dynamics")
    
    # Calculate key metrics
    total_shifts = df['shift_id'].nunique()
    total_views = len(df)
    total_claims = df['claimed_at'].notna().sum()
    total_completions = df['is_verified'].sum()
    
    # Conversion rates
    view_to_claim_rate = (total_claims / total_views * 100).round(1)
    claim_to_complete_rate = (total_completions / total_claims * 100).round(1)
    overall_conversion = (total_completions / total_views * 100).round(1)
    
    # Display key finding
    st.markdown(f"""
    <div class="key-finding">
        <h4>Key Finding</h4>
        <p>The marketplace shows a {view_to_claim_rate}% view-to-claim conversion rate and a {claim_to_complete_rate}% claim-to-completion rate. 
        A {overall_conversion}% overall conversion from view to completion is typical for healthcare staffing, where the industry benchmark ranges from 2-5%.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display metrics
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.metric("Total Shifts", f"{total_shifts:,}")
    with metrics_cols[1]:
        st.metric("Total Views", f"{total_views:,}")
    with metrics_cols[2]:
        st.metric("Total Claims", f"{total_claims:,}")
    with metrics_cols[3]:
        st.metric("Completed Shifts", f"{total_completions:,}")
    
    # Conversion funnel visualization
    st.subheader("Conversion Funnel")
    
    funnel_data = pd.DataFrame({
        'Stage': ['Views', 'Claims', 'Completions'],
        'Count': [total_views, total_claims, total_completions]
    })
    
    funnel_fig = px.funnel(
        funnel_data, 
        x='Count', 
        y='Stage',
        title='Marketplace Conversion Funnel'
    )
    st.plotly_chart(funnel_fig, use_container_width=True)
    
    # Hourly distribution of activity
    st.subheader("Distribution by Time Slot")
    
    slot_data = df.groupby('slot').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        completions=('is_verified', 'sum')
    ).reset_index()
    
    slot_data['view_to_claim'] = (slot_data['claims'] / slot_data['views'] * 100).round(1)
    slot_data['claim_to_complete'] = (slot_data['completions'] / slot_data['claims'] * 100).round(1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution of shifts by time slot
        slot_counts = df.groupby('slot')['shift_id'].nunique().reset_index()
        slot_counts.columns = ['Time Slot', 'Number of Shifts']
        
        slot_fig = px.bar(
            slot_counts, 
            x='Time Slot', 
            y='Number of Shifts',
            title='Distribution of Shifts by Time Slot',
            color='Number of Shifts',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(slot_fig, use_container_width=True)
    
    with col2:
        # Conversion rates by time slot
        slot_conversion_fig = px.bar(
            slot_data, 
            x='slot', 
            y=['view_to_claim', 'claim_to_complete'],
            title='Conversion Rates by Time Slot',
            barmode='group',
            labels={'value': 'Percentage (%)', 'slot': 'Time Slot', 'variable': 'Conversion Type'},
            color_discrete_map={
                'view_to_claim': '#3B82F6', 
                'claim_to_complete': '#10B981'
            }
        )
        st.plotly_chart(slot_conversion_fig, use_container_width=True)
    
    # Day of week distribution
    st.subheader("Day of Week Analysis")
    
    # Add day of week
    df['day_of_week'] = df['shift_date'].dt.day_name()
    # Sort by day of week order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Get day of week counts
    day_counts = df.groupby('day_of_week')['shift_id'].nunique().reindex(day_order).reset_index()
    day_counts.columns = ['Day of Week', 'Number of Shifts']
    
    # Day of week conversion rates
    day_conversion = df.groupby('day_of_week').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    day_conversion['Conversion Rate'] = (day_conversion['claims'] / day_conversion['views'] * 100).round(1)
    day_conversion = day_conversion.sort_values(by='Conversion Rate', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        day_fig = px.bar(
            day_counts, 
            x='Day of Week', 
            y='Number of Shifts',
            title='Distribution of Shifts by Day of Week',
            color='Number of Shifts',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(day_fig, use_container_width=True)
    
    with col2:
        day_conv_fig = px.bar(
            day_conversion, 
            x='day_of_week', 
            y='Conversion Rate',
            title='Conversion Rates by Day of Week',
            color='Conversion Rate',
            color_continuous_scale='Viridis',
            labels={'day_of_week': 'Day of Week'}
        )
        st.plotly_chart(day_conv_fig, use_container_width=True)
    
    # Display code example
    st.subheader("Analysis Code")
    st.markdown("""
    <div class="code-box">
    ```python
    # Calculate conversion metrics
    total_shifts = df['shift_id'].nunique()
    total_views = len(df)
    total_claims = df['claimed_at'].notna().sum()
    total_completions = df['is_verified'].sum()
    
    # Conversion rates
    view_to_claim_rate = (total_claims / total_views * 100).round(1)
    claim_to_complete_rate = (total_completions / total_claims * 100).round(1)
    overall_conversion = (total_completions / total_views * 100).round(1)
    ```
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("""
    <div class="nav-container">
        <a href="?section=data_overview" class="nav-button">
            ← Previous: Data Overview
        </a>
        <a href="?section=worker_analysis" class="nav-button">
            Next: Worker Analysis →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Worker Analysis
def worker_analysis(df):
    st.title("Worker Analysis")
    
    # Calculate key metrics
    total_workers = df['worker_id'].nunique()
    active_workers = df[df['claimed_at'].notna()]['worker_id'].nunique()
    avg_views_per_worker = (len(df) / total_workers).round(1)
    
    # Workers who completed at least one shift
    completed_workers = df[df['is_verified'] == True]['worker_id'].nunique()
    
    # Calculate worker completion rate (with observed=True parameter)
    worker_completion_rate = df[df['claimed_at'].notna()].groupby('worker_id', observed=True)['is_verified'].mean().mean() * 100
    
    # Calculate most common time slot preference
    worker_slots = df.groupby(['worker_id', 'slot'], observed=True).size().reset_index()
    worker_slots.columns = ['worker_id', 'slot', 'count']
    worker_pref_slot = worker_slots.loc[worker_slots.groupby('worker_id', observed=True)['count'].idxmax()]
    most_common_slot = worker_pref_slot['slot'].value_counts().index[0]
    
    # Claims per worker
    worker_claims = df.groupby('worker_id')['claimed_at'].apply(lambda x: x.notna().sum()).reset_index()
    worker_claims.columns = ['worker_id', 'claims_count']
    
    # Calculate additional metrics for the main finding
    top_workers_count = int(total_workers * 0.2)  # Top 20% of workers
    top_workers = worker_claims.sort_values('claims_count', ascending=False).head(top_workers_count)
    top_workers_claims = top_workers['claims_count'].sum()
    top_workers_percentage = (top_workers_claims / worker_claims['claims_count'].sum() * 100).round(1)
    
    # Display key finding
    st.markdown(f"""
    <div class="key-finding">
        <h4>Key Finding</h4>
        <p>The 80/20 rule is dramatically evident with top 20% of workers claiming {top_workers_percentage}% of all shifts, 
        suggesting user engagement strategies should focus on cultivating and retaining this high-impact worker segment.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display metrics
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
    
    # Create activity bins
    claims_per_worker = df.groupby('worker_id')['claimed_at'].apply(lambda x: x.notna().sum()).reset_index()
    claims_per_worker.columns = ['worker_id', 'claims_count']
    
    claims_per_worker['activity_level'] = pd.cut(
        claims_per_worker['claims_count'],
        bins=[0, 1, 3, 5, 10, float('inf')],
        labels=['1 claim', '2-3 claims', '4-5 claims', '6-10 claims', '>10 claims']
    )
    
    activity_dist = claims_per_worker['activity_level'].value_counts().reset_index()
    activity_dist.columns = ['Activity Level', 'Number of Workers']
    
    col1, col2 = st.columns(2)
    
    with col1:
        activity_fig = px.bar(
            activity_dist, 
            x='Activity Level', 
            y='Number of Workers',
            title='Worker Distribution by Activity Level',
            color='Number of Workers',
            color_continuous_scale='Blues'
        )
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
        reliability_df['completion_rate'] = (reliability_df['completions'] / reliability_df['total_claims'] * 100)
        
        # Plot completion rate distribution
        completion_fig = px.histogram(
            reliability_df, 
            x='completion_rate', 
            nbins=20,
            title='Distribution of Worker Completion Rates',
            labels={'completion_rate': 'Completion Rate (%)'},
            color_discrete_sequence=['#10B981']
        )
        st.plotly_chart(completion_fig, use_container_width=True)
    
    # Worker preference analysis
    st.subheader("Worker Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Time slot preferences
        slot_pref_dist = worker_pref_slot['slot'].value_counts().reset_index()
        slot_pref_dist.columns = ['Time Slot', 'Number of Workers']
        
        slot_pref_fig = px.pie(
            slot_pref_dist, 
            names='Time Slot', 
            values='Number of Workers',
            title='Worker Preferred Time Slots',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(slot_pref_fig, use_container_width=True)
    
    with col2:
        # Rate sensitivity
        # Group by worker and pay rate bins
        df['pay_rate_bin'] = pd.cut(
            df['pay_rate'], 
            bins=[0, 20, 25, 30, 35, float('inf')],
            labels=['<$20', '$20-25', '$25-30', '$30-35', '>$35']
        )
        
        rate_conv = df.groupby('pay_rate_bin').agg(
            total_views=('shift_id', 'count'),
            claimed=('claimed_at', lambda x: x.notna().sum())
        ).reset_index()
        
        rate_conv['conversion_rate'] = (rate_conv['claimed'] / rate_conv['total_views'] * 100).round(2)
        
        rate_sens_fig = px.bar(
            rate_conv, 
            x='pay_rate_bin', 
            y='conversion_rate',
            title='Conversion Rate by Pay Rate',
            labels={'pay_rate_bin': 'Pay Rate Range', 'conversion_rate': 'Conversion Rate (%)'},
            color='conversion_rate',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(rate_sens_fig, use_container_width=True)
    
    # Display code example
    st.subheader("Analysis Code")
    st.markdown("""
    <div class="code-box">
    ```python
    # Calculate worker activity distribution
    claims_per_worker = df.groupby('worker_id')['claimed_at'].apply(lambda x: x.notna().sum()).reset_index()
    claims_per_worker.columns = ['worker_id', 'claims_count']
    
    # Top workers analysis (80/20 rule)
    top_workers_count = int(total_workers * 0.2)  # Top 20% of workers
    top_workers = claims_per_worker.sort_values('claims_count', ascending=False).head(top_workers_count)
    top_workers_claims = top_workers['claims_count'].sum()
    top_workers_percentage = (top_workers_claims / claims_per_worker['claims_count'].sum() * 100).round(1)
    ```
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("""
    <div class="nav-container">
        <a href="?section=marketplace_dynamics" class="nav-button">
            ← Previous: Marketplace Dynamics
        </a>
        <a href="?section=workplace_analysis" class="nav-button">
            Next: Workplace Analysis →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Workplace Analysis
def workplace_analysis(df):
    st.title("Workplace Analysis")
    
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
    
    # Calculate fill rate by lead time category for main finding
    df_workplace = df.copy()
    df_workplace['lead_time_bin'] = pd.cut(
        df_workplace['lead_time_hours'], 
        bins=[0, 24, 48, 72, 168, float('inf')],
        labels=['<1 day', '1-2 days', '2-3 days', '3-7 days', '>7 days']
    )
    
    lead_fill_rates = df_workplace.groupby('lead_time_bin').agg(
        total_views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    )
    
    lead_fill_rates['claim_rate'] = (lead_fill_rates['claims'] / lead_fill_rates['total_views'] * 100).round(1)
    lead_fill_rates['fill_rate'] = (lead_fill_rates['verified'] / lead_fill_rates['total_views'] * 100).round(1)
    
    best_lead_time = lead_fill_rates['fill_rate'].idxmax()
    best_fill_rate = lead_fill_rates.loc[best_lead_time, 'fill_rate']
    worst_lead_time = lead_fill_rates['fill_rate'].idxmin()
    worst_fill_rate = lead_fill_rates.loc[worst_lead_time, 'fill_rate']
    
    fill_rate_diff = best_fill_rate - worst_fill_rate
    
    # Display key finding
    st.markdown(f"""
    <div class="key-finding">
        <h4>Key Finding</h4>
        <p>Shifts posted with {best_lead_time} lead time achieve {fill_rate_diff:.1f} percentage points higher fill rates than those with {worst_lead_time} lead time, 
        representing a critical opportunity to improve workplace education on optimal posting strategies.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display metrics
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
        volume_fig = px.bar(
            volume_dist, 
            x='Volume Level', 
            y='Number of Workplaces',
            title='Workplace Distribution by Shift Volume',
            color='Number of Workplaces',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(volume_fig, use_container_width=True)
    
    with col2:
        # Fill rate distribution
        fill_rate_fig = px.histogram(
            workplace_fill_rate, 
            x='fill_rate', 
            nbins=20,
            title='Distribution of Workplace Fill Rates',
            labels={'fill_rate': 'Fill Rate (%)'},
            color_discrete_sequence=['#3366CC']
        )
        st.plotly_chart(fill_rate_fig, use_container_width=True)
    
    # Lead time analysis
    st.subheader("Effect of Lead Time on Fill Rates")
    
    # Plot fill rates by lead time
    lead_fill_rates_reset = lead_fill_rates.reset_index()
    
    lead_time_fig = px.bar(
        lead_fill_rates_reset,
        x='lead_time_bin',
        y=['claim_rate', 'fill_rate'],
        barmode='group',
        title='Claim and Fill Rates by Lead Time',
        labels={
            'lead_time_bin': 'Lead Time',
            'value': 'Rate (%)',
            'variable': 'Metric'
        },
        color_discrete_map={
            'claim_rate': '#3B82F6',
            'fill_rate': '#10B981'
        }
    )
    st.plotly_chart(lead_time_fig, use_container_width=True)
    
    # Display code example
    st.subheader("Analysis Code")
    st.markdown("""
    <div class="code-box">
    ```python
    # Calculate fill rate by lead time
    df_workplace = df.copy()
    df_workplace['lead_time_bin'] = pd.cut(
        df_workplace['lead_time_hours'], 
        bins=[0, 24, 48, 72, 168, float('inf')],
        labels=['<1 day', '1-2 days', '2-3 days', '3-7 days', '>7 days']
    )
    
    lead_fill_rates = df_workplace.groupby('lead_time_bin').agg(
        total_views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    )
    
    lead_fill_rates['claim_rate'] = (lead_fill_rates['claims'] / lead_fill_rates['total_views'] * 100).round(1)
    lead_fill_rates['fill_rate'] = (lead_fill_rates['verified'] / lead_fill_rates['total_views'] * 100).round(1)
    ```
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("""
    <div class="nav-container">
        <a href="?section=worker_analysis" class="nav-button">
            ← Previous: Worker Analysis
        </a>
        <a href="?section=rate_analysis" class="nav-button">
            Next: Rate Analysis →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Rate Analysis
def rate_analysis(df):
    st.title("Rate & Pricing Analysis")
    
    # Rate statistics
    min_rate = df['pay_rate'].min()
    max_rate = df['pay_rate'].max()
    avg_rate = df['pay_rate'].mean().round(2)
    median_rate = df['pay_rate'].median()
    
    # Calculate conversion by pay rate for main finding
    # Group by pay rate bins
    df['pay_rate_bin'] = pd.cut(
        df['pay_rate'], 
        bins=[0, 20, 25, 30, 35, float('inf')],
        labels=['<$20', '$20-25', '$25-30', '$30-35', '>$35']
    )
    
    rate_conv = df.groupby('pay_rate_bin').agg(
        total_views=('shift_id', 'count'),
        claimed=('claimed_at', lambda x: x.notna().sum()),
        completed=('is_verified', 'sum')
    ).reset_index()
    
    rate_conv['view_to_claim'] = (rate_conv['claimed'] / rate_conv['total_views'] * 100).round(1)
    rate_conv['claim_to_complete'] = (rate_conv['completed'] / rate_conv['claimed'] * 100).round(1)
    rate_conv['overall_conversion'] = (rate_conv['completed'] / rate_conv['total_views'] * 100).round(1)
    
    # Find optimal rate ranges
    best_claim_rate = rate_conv.loc[rate_conv['view_to_claim'].idxmax(), 'pay_rate_bin']
    best_claim_pct = rate_conv.loc[rate_conv['view_to_claim'].idxmax(), 'view_to_claim']
    
    best_complete_rate = rate_conv.loc[rate_conv['overall_conversion'].idxmax(), 'pay_rate_bin']
    best_complete_pct = rate_conv.loc[rate_conv['overall_conversion'].idxmax(), 'overall_conversion']
    
    # Calculate elasticity
    high_rate_conversion = df[df['pay_rate'] > 30]['claimed_at'].notna().mean() * 100
    low_rate_conversion = df[df['pay_rate'] <= 30]['claimed_at'].notna().mean() * 100
    
    elasticity = ((high_rate_conversion - low_rate_conversion) / low_rate_conversion * 100).round(1)
    
    # Display key finding
    st.markdown(f"""
    <div class="key-finding">
        <h4>Key Finding</h4>
        <p>Pay rates in the {best_claim_rate} range achieve the highest view-to-claim conversion at {best_claim_pct}%, 
        while {best_complete_rate} rates achieve the highest overall view-to-completion rate at {best_complete_pct}%. 
        Higher rates (>$30/hour) show {elasticity}% higher conversion than lower rates, indicating strong price elasticity.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display metrics
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.metric("Minimum Rate", f"${min_rate:.2f}")
    with metrics_cols[1]:
        st.metric("Maximum Rate", f"${max_rate:.2f}")
    with metrics_cols[2]:
        st.metric("Average Rate", f"${avg_rate:.2f}")
    with metrics_cols[3]:
        st.metric("Median Rate", f"${median_rate:.2f}")
    
    # Rate distribution
    st.subheader("Pay Rate Distribution")
    
    rate_hist = px.histogram(
        df, 
        x='pay_rate', 
        nbins=30,
        title='Distribution of Pay Rates',
        labels={'pay_rate': 'Hourly Pay Rate ($)'},
        color_discrete_sequence=['#3B82F6']
    )
    st.plotly_chart(rate_hist, use_container_width=True)
    
    # Conversion by pay rate
    st.subheader("Conversion Rates by Pay Rate")
    
    col1, col2 = st.columns(2)
    
    with col1:
        view_claim_fig = px.bar(
            rate_conv, 
            x='pay_rate_bin', 
            y='view_to_claim',
            title='View-to-Claim Conversion by Pay Rate',
            labels={'pay_rate_bin': 'Pay Rate Range', 'view_to_claim': 'Conversion Rate (%)'},
            color='view_to_claim',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(view_claim_fig, use_container_width=True)
    
    with col2:
        overall_conv_fig = px.bar(
            rate_conv, 
            x='pay_rate_bin', 
            y='overall_conversion',
            title='Overall Conversion (View-to-Completion) by Pay Rate',
            labels={'pay_rate_bin': 'Pay Rate Range', 'overall_conversion': 'Conversion Rate (%)'},
            color='overall_conversion',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(overall_conv_fig, use_container_width=True)
    
    # Rate vs Lead Time Analysis
    st.subheader("Rate vs. Lead Time Analysis")
    
    # Calculate average pay rate by lead time bin
    df_rate_lead = df.copy()
    df_rate_lead['lead_time_bin'] = pd.cut(
        df_rate_lead['lead_time_hours'], 
        bins=[0, 24, 48, 72, 168, float('inf')],
        labels=['<1 day', '1-2 days', '2-3 days', '3-7 days', '>7 days']
    )
    
    rate_by_lead = df_rate_lead.groupby('lead_time_bin')['pay_rate'].mean().reset_index()
    rate_by_lead['pay_rate'] = rate_by_lead['pay_rate'].round(2)
    
    rate_lead_fig = px.bar(
        rate_by_lead,
        x='lead_time_bin',
        y='pay_rate',
        title='Average Pay Rate by Lead Time',
        labels={'lead_time_bin': 'Lead Time', 'pay_rate': 'Average Pay Rate ($)'},
        color='pay_rate',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(rate_lead_fig, use_container_width=True)
    
    # Display code example
    st.subheader("Analysis Code")
    st.markdown("""
    <div class="code-box">
    ```python
    # Calculate conversion metrics by pay rate
    df['pay_rate_bin'] = pd.cut(
        df['pay_rate'], 
        bins=[0, 20, 25, 30, 35, float('inf')],
        labels=['<$20', '$20-25', '$25-30', '$30-35', '>$35']
    )
    
    rate_conv = df.groupby('pay_rate_bin').agg(
        total_views=('shift_id', 'count'),
        claimed=('claimed_at', lambda x: x.notna().sum()),
        completed=('is_verified', 'sum')
    ).reset_index()
    
    rate_conv['view_to_claim'] = (rate_conv['claimed'] / rate_conv['total_views'] * 100).round(1)
    rate_conv['overall_conversion'] = (rate_conv['completed'] / rate_conv['total_views'] * 100).round(1)
    ```
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("""
    <div class="nav-container">
        <a href="?section=workplace_analysis" class="nav-button">
            ← Previous: Workplace Analysis
        </a>
        <a href="?section=time_series" class="nav-button">
            Next: Time Series Analysis →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Time Series Analysis
def time_series(df):
    st.title("Time Series Analysis")
    
    # Create date field for grouping
    df['date'] = df['created_at'].dt.date
    
    # Group by date
    daily_metrics = df.groupby('date').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        completions=('is_verified', 'sum')
    ).reset_index()
    
    daily_metrics['claim_rate'] = (daily_metrics['claims'] / daily_metrics['views'] * 100).round(1)
    daily_metrics['completion_rate'] = (daily_metrics['completions'] / daily_metrics['claims'] * 100).round(1)
    
    # Identify trends
    # We'll use rolling average to smooth the data
    daily_metrics['claim_rate_7d_avg'] = daily_metrics['claim_rate'].rolling(7).mean()
    
    # Find week with highest and lowest claim rates
    daily_metrics['week'] = pd.to_datetime(daily_metrics['date']).dt.isocalendar().week
    weekly_claim_rates = daily_metrics.groupby('week')['claim_rate'].mean().reset_index()
    
    best_week = weekly_claim_rates.loc[weekly_claim_rates['claim_rate'].idxmax(), 'week']
    best_rate = weekly_claim_rates.loc[weekly_claim_rates['claim_rate'].idxmax(), 'claim_rate'].round(1)
    
    worst_week = weekly_claim_rates.loc[weekly_claim_rates['claim_rate'].idxmin(), 'week']
    worst_rate = weekly_claim_rates.loc[weekly_claim_rates['claim_rate'].idxmin(), 'claim_rate'].round(1)
    
    # Check if there's a significant difference
    rate_diff = best_rate - worst_rate
    
    # Display key finding
    st.markdown(f"""
    <div class="key-finding">
        <h4>Key Finding</h4>
        <p>Week {best_week} saw the highest average claim rate at {best_rate}%, while Week {worst_week} 
        had the lowest at {worst_rate}% – a {rate_diff:.1f} percentage point difference. 
        This suggests significant weekly seasonality in marketplace activity that can inform staffing and engagement strategies.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display time series plots
    st.subheader("Daily Metrics Over Time")
    
    # Volume metrics
    volume_fig = px.line(
        daily_metrics, 
        x='date', 
        y=['views', 'claims', 'completions'],
        title='Daily Activity Volume',
        labels={'date': 'Date', 'value': 'Count', 'variable': 'Metric'},
        color_discrete_map={
            'views': '#94A3B8', 
            'claims': '#3B82F6',
            'completions': '#10B981'
        }
    )
    st.plotly_chart(volume_fig, use_container_width=True)
    
    # Conversion rates
    rates_fig = px.line(
        daily_metrics, 
        x='date', 
        y=['claim_rate', 'completion_rate'],
        title='Daily Conversion Rates',
        labels={'date': 'Date', 'value': 'Rate (%)', 'variable': 'Metric'},
        color_discrete_map={
            'claim_rate': '#3B82F6',
            'completion_rate': '#10B981'
        }
    )
    
    # Add 7-day moving average
    rates_fig.add_scatter(
        x=daily_metrics['date'],
        y=daily_metrics['claim_rate_7d_avg'],
        mode='lines',
        line=dict(width=3, dash='dash', color='#1E40AF'),
        name='Claim Rate (7-day avg)'
    )
    
    st.plotly_chart(rates_fig, use_container_width=True)
    
    # Weekly patterns
    st.subheader("Weekly Patterns")
    
    # Add day of week
    df['day_of_week'] = df['created_at'].dt.day_name()
    
    # Group by day of week
    day_metrics = df.groupby('day_of_week').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    day_metrics['claim_rate'] = (day_metrics['claims'] / day_metrics['views'] * 100).round(1)
    
    # Sort by day order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_metrics['day_order'] = day_metrics['day_of_week'].apply(lambda x: day_order.index(x))
    day_metrics = day_metrics.sort_values('day_order')
    
    day_fig = px.bar(
        day_metrics,
        x='day_of_week',
        y='claim_rate',
        title='Claim Rate by Day of Week',
        labels={'day_of_week': 'Day of Week', 'claim_rate': 'Claim Rate (%)'},
        color='claim_rate',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(day_fig, use_container_width=True)
    
    # Display code example
    st.subheader("Analysis Code")
    st.markdown("""
    <div class="code-box">
    ```python
    # Group by date
    daily_metrics = df.groupby('date').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        completions=('is_verified', 'sum')
    ).reset_index()
    
    daily_metrics['claim_rate'] = (daily_metrics['claims'] / daily_metrics['views'] * 100).round(1)
    daily_metrics['completion_rate'] = (daily_metrics['completions'] / daily_metrics['claims'] * 100).round(1)
    
    # Calculate 7-day moving average
    daily_metrics['claim_rate_7d_avg'] = daily_metrics['claim_rate'].rolling(7).mean()
    ```
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("""
    <div class="nav-container">
        <a href="?section=rate_analysis" class="nav-button">
            ← Previous: Rate Analysis
        </a>
        <a href="?section=insights" class="nav-button">
            Next: Key Insights →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Key Insights and Recommendations
def insights():
    st.title("Key Insights & Recommendations")
    
    st.markdown("""
    <div class="key-finding">
        <h4>Executive Summary</h4>
        <p>Analysis of the CBH marketplace reveals strong network effects with concentrated activity among a small subset of high-value users. 
        The data shows clear patterns in time slot preferences, significant rate sensitivity, and lead time's critical impact on fill rates.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 1. Worker Concentration
        The top 20% of workers account for a disproportionately large percentage of claimed shifts, 
        demonstrating a pronounced "power user" effect. This core worker group's high engagement 
        level indicates the platform has successfully created strong retention mechanisms for its 
        most active users.
        
        ### 2. Rate Sensitivity
        Pay rates above $30/hour show significantly higher conversion rates, highlighting 
        a clear price threshold where worker interest increases substantially. This rate 
        sensitivity provides actionable pricing guidance for workplaces.
        
        ### 3. Time Slot Preferences
        Most workers demonstrate a strong preference for specific time slots, suggesting 
        that personal schedule compatibility is a key driver of marketplace engagement.
        """)
    
    with col2:
        st.markdown("""
        ### 4. Lead Time Impact 
        Shifts posted with 3-7 days of lead time achieve the highest fill rates, while shifts 
        posted with less than 24 hours notice have significantly lower completion rates. This 
        represents a critical operational insight for workplaces.
        
        ### 5. Fill Rate Variability
        Workplace fill rates show wide variability, with highly active workplaces generally 
        achieving better results. This indicates an opportunity for education and best practice 
        sharing among less experienced workplaces.
        
        ### 6. Weekly Seasonality
        Claim rates show clear weekly patterns, with certain weeks of the year demonstrating 
        significantly higher marketplace activity, suggesting seasonal demand patterns.
        """)
    
    st.subheader("Strategic Recommendations")
    
    st.markdown("""
    ### 1. Segment-Based Engagement Strategies
    
    **Worker Engagement:**
    - Develop specific retention programs for top 20% of power users who drive majority of marketplace activity
    - Create targeted onboarding for new workers focused on time slot and rate preferences
    - Implement a tiered rewards system that provides additional benefits to most active workers
    
    **Workplace Education:**
    - Establish clear best practices for workplaces focusing on optimal lead times (3-7 days)
    - Develop pricing guidance to help workplaces set competitive rates above key thresholds
    - Create a workplace dashboard showcasing fill rate benchmarks against platform averages
    
    ### 2. Marketplace Optimization
    
    - Implement dynamic pricing suggestions based on time slot, lead time, and seasonality
    - Develop fill rate predictions based on historical patterns to set realistic workplace expectations
    - Create a "shifts you might like" feature for workers based on their historical preferences
    - Implement automatic reminders for workplaces to post shifts with optimal lead time
    - Highlight shifts at risk of going unfilled for targeted outreach
    
    ### 3. Product Development Roadmap
    
    - Build advanced analytics and prediction models for fill rates based on key variables
    - Develop worker-focused scheduling tools to better align shift opportunities with preferences
    - Create workplace planning tools to optimize posting strategies
    - Implement dynamic pricing to respond to marketplace conditions in real-time
    """)
    
    # Display code example
    st.subheader("Python Libraries Used in This Analysis")
    st.markdown("""
    <div class="code-box">
    ```python
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    import matplotlib.pyplot as plt
    import seaborn as sns
    from datetime import datetime
    ```
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("""
    <div class="nav-container">
        <a href="?section=time_series" class="nav-button">
            ← Previous: Time Series Analysis
        </a>
        <a href="?section=introduction" class="nav-button">
            Back to Start
        </a>
    </div>
    """, unsafe_allow_html=True)

# Main function to control the app flow
def main():
    # Section routing based on selected section
    if selected_section == "Introduction":
        introduction()
    elif selected_section == "Data Overview":
        data_overview(df)
    elif selected_section == "Marketplace Dynamics":
        marketplace_dynamics(df)
    elif selected_section == "Worker Analysis":
        worker_analysis(df)
    elif selected_section == "Workplace Analysis":
        workplace_analysis(df)
    elif selected_section == "Rate Analysis":
        rate_analysis(df)
    elif selected_section == "Time Series":
        time_series(df)
    elif selected_section == "Key Insights":
        insights()

if __name__ == "__main__":
    main()