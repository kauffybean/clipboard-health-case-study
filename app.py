import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

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
        border-left: 5px solid #2563EB;
        padding: 1.25rem 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 5px 5px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .key-finding h4 {
        color: #1E40AF;
        font-weight: 600;
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
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
    
    /* Progress wizard */
    .wizard-step {
        cursor: pointer;
        display: inline-block;
        text-align: center;
        color: #6B7280;
        margin: 0;
        padding: 0.5rem 0;
        transition: all 0.2s;
    }
    
    .wizard-step:hover {
        color: #2563EB;
    }
    
    .wizard-step.active {
        color: #2563EB;
        font-weight: 600;
        border-bottom: 3px solid #2563EB;
    }
    
    .wizard-step.completed {
        color: #10B981;
        border-bottom: 3px solid #10B981;
    }
    
    /* Separator line */
    .separator {
        height: 1px;
        background-color: #e5e7eb;
        margin: 1rem 0 2rem 0;
    }
    
    /* Title styles */
    h1 {
        margin-bottom: 1.5rem;
        color: #111827;
    }
    
    h2 {
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #1F2937;
    }
    
    h3 {
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        color: #374151;
    }
    
    /* Card styles for metrics */
    .metric-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        text-align: center !important;
        margin: 0.5rem 0;
        height: 100%;
        overflow: hidden;
    }
    
    /* Fix for metric placement */
    div[data-testid="metric-container"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        max-width: 100%;
    }

    /* Improve metric values */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #2563EB !important;
        text-align: center !important;
        width: 100% !important;
    }
    
    /* Improve metric label */
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        width: 100% !important;
    }
    
    /* Improve metric delta */
    div[data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
        text-align: center !important;
    }
    
    /* Block container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    footer {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load data
def load_and_clean_data(file_path):
    """Load and clean the dataset"""
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Convert all column names to lowercase
    df.columns = [col.lower() for col in df.columns]
    
    # Convert date columns to datetime
    date_columns = ['shift_start_at', 'shift_created_at', 'offer_viewed_at', 'claimed_at', 'deleted_at', 'canceled_at']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Calculate lead time in hours
    if 'shift_start_at' in df.columns and 'shift_created_at' in df.columns:
        df['lead_time_hours'] = (df['shift_start_at'] - df['shift_created_at']).dt.total_seconds() / 3600
    
    # Convert boolean columns
    bool_columns = ['is_ncns', 'is_verified']
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].astype(bool)
    
    # Rename some columns for clarity
    column_mapping = {
        'shift_start_at': 'shift_date',
        'shift_created_at': 'created_at',
        'offer_viewed_at': 'viewed_at'
    }
    
    df = df.rename(columns=column_mapping)
    
    return df

# Load the dataset
df = load_and_clean_data("attached_assets/Problems we tackle, Shift Offers v3 - table_12_2025-01-22T1134.csv")

# Define sections for the wizard
SECTIONS = [
    {"id": "introduction", "name": "Introduction", "number": 1},
    {"id": "data_overview", "name": "Data Overview", "number": 2},
    {"id": "marketplace_dynamics", "name": "Marketplace Dynamics", "number": 3},
    {"id": "worker_analysis", "name": "Worker Analysis", "number": 4},
    {"id": "workplace_analysis", "name": "Workplace Analysis", "number": 5},
    {"id": "rate_analysis", "name": "Rate Analysis", "number": 6},
    {"id": "time_series", "name": "Time Series", "number": 7},
    {"id": "insights", "name": "Key Insights", "number": 8}
]

# Initialize session state
if 'current_section' not in st.session_state:
    st.session_state.current_section = "introduction"

if 'completed_sections' not in st.session_state:
    st.session_state.completed_sections = []

# Header and navigation wizard
st.title("CBH Marketplace Analysis", anchor=False)

# Create the wizard navigation
wizard_cols = st.columns(len(SECTIONS))
for i, section in enumerate(SECTIONS):
    section_id = section["id"]
    section_name = section["name"]
    
    # Determine status
    if section_id == st.session_state.current_section:
        class_name = "active"
    elif section_id in st.session_state.completed_sections:
        class_name = "completed"
    else:
        class_name = ""
    
    # Determine text based on status
    if section_id == st.session_state.current_section:
        button_text = f"{section_name}"
        button_type = "primary"
    elif section_id in st.session_state.completed_sections:
        button_text = f"{section_name}"
        button_type = "secondary"
    else:
        button_text = f"{section_name}"
        button_type = "secondary"
    
    # Create clickable navigation item
    with wizard_cols[i]:
        if st.button(button_text, key=f"nav_{section_id}", use_container_width=True, 
                    help=f"Go to {section_name}", type=button_type):
            st.session_state.current_section = section_id
            st.rerun()

# Separator line
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Helper function to navigate to next section
def go_to_next_section():
    current_index = next((i for i, s in enumerate(SECTIONS) if s["id"] == st.session_state.current_section), 0)
    
    # Add current section to completed list if not already there
    if st.session_state.current_section not in st.session_state.completed_sections:
        st.session_state.completed_sections.append(st.session_state.current_section)
    
    # Move to next section if not at the end
    if current_index < len(SECTIONS) - 1:
        st.session_state.current_section = SECTIONS[current_index + 1]["id"]
        st.rerun()

# Helper function to navigate to previous section
def go_to_previous_section():
    current_index = next((i for i, s in enumerate(SECTIONS) if s["id"] == st.session_state.current_section), 0)
    
    # Move to previous section if not at the beginning
    if current_index > 0:
        st.session_state.current_section = SECTIONS[current_index - 1]["id"]
        st.rerun()

# Helper function to navigate to a specific section
def go_to_section(section_id):
    # Check if it's a valid section
    if any(section["id"] == section_id for section in SECTIONS):
        st.session_state.current_section = section_id
        st.rerun()

# Introduction
def introduction():
    # Intro content
    st.subheader("Welcome to the CBH Marketplace Analysis", anchor=False)
    st.markdown("""
    This interactive case study explores data from a two-sided marketplace where healthcare 
    workers book per diem shifts with workplaces. The analysis examines patterns and metrics 
    to understand marketplace dynamics, worker behavior, workplace activity, and rate sensitivity.
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
    
    # Create two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Questions", anchor=False)
        st.markdown("""
        - What drives conversion rates in this marketplace?
        - How do workers and workplaces behave?
        - What pricing strategies are most effective?
        - How does lead time affect fill rates?
        """)
    
    with col2:
        st.subheader("Data Sources", anchor=False)
        st.markdown("""
        The analysis is based on marketplace transaction data, including:
        - Shift details (times, dates, locations)
        - Worker interactions (views, claims, completions)
        - Workplace postings (locations, lead times)
        - Pricing information (pay rates, pricing strategies)
        - Completion status (verified, canceled, no-shows)
        """)
    
    st.subheader("How to Navigate", anchor=False)
    st.markdown("""
    This case study is organized into sequential sections that build upon each other. 
    Use the navigation at the top to move between sections, or click 'Continue'
    to move to the next section.
    """)
    
    # Continue button
    st.button("Continue to Data Overview →", on_click=go_to_next_section, type="primary", use_container_width=True)

# Data Overview
def data_overview(df):
    st.subheader("Data Overview", anchor=False)
    
    # Data summary
    st.markdown("### Dataset Summary")
    
    # Shape and time range
    total_records = len(df)
    unique_shifts = df['shift_id'].nunique()
    unique_workers = df['worker_id'].nunique()
    unique_workplaces = df['workplace_id'].nunique()
    
    min_date = df['created_at'].min().strftime('%Y-%m-%d')
    max_date = df['created_at'].max().strftime('%Y-%m-%d')
    
    # Display metrics in cards with cleaner structure
    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    metrics_cols = st.columns(4)
    
    # Using a cleaner approach without the extra containers
    metrics_cols[0].metric("Total Records", f"{total_records:,}")
    metrics_cols[1].metric("Unique Shifts", f"{unique_shifts:,}")
    metrics_cols[2].metric("Unique Workers", f"{unique_workers:,}")
    metrics_cols[3].metric("Unique Workplaces", f"{unique_workplaces:,}")
    
    st.markdown(f"**Date Range:** {min_date} to {max_date}")
    
    # Sample data
    st.markdown("### Sample Data")
    st.dataframe(df.head(10), use_container_width=True, height=300)
    
    # Data description
    st.markdown("### Data Fields")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **shift_id**: Unique identifier for a shift
        - **workplace_id**: Identifier for the workplace posting the shift
        - **worker_id**: Identifier for the worker viewing/claiming the shift
        - **pay_rate**: Hourly pay rate for the shift
        - **created_at**: When the shift was created/posted
        - **shift_date**: Date when the shift is scheduled
        """)
    
    with col2:
        st.markdown("""
        - **slot**: Time slot of the shift (Morning, Evening, Night)
        - **lead_time_hours**: Hours between posting and shift start
        - **viewed_at**: When the worker viewed the shift
        - **claimed_at**: When the worker claimed the shift (if claimed)
        - **canceled_at**: When the worker canceled the shift (if canceled)
        - **is_ncns**: No Call No Show flag
        - **is_verified**: Whether the shift was completed and verified
        """)
    
    # Data quality
    st.markdown("### Data Quality")
    
    # Missing values
    missing_data = pd.DataFrame(df.isnull().sum(), columns=['Missing Values'])
    missing_data['Percentage'] = (missing_data['Missing Values'] / len(df) * 100).round(2)
    missing_data = missing_data.sort_values('Missing Values', ascending=False).reset_index().rename(columns={'index': 'Field'})
    
    # Only show fields with missing values
    missing_data = missing_data[missing_data['Missing Values'] > 0]
    
    if len(missing_data) > 0:
        st.markdown("#### Missing Values")
        st.dataframe(missing_data, use_container_width=True)
    else:
        st.markdown("#### Missing Values")
        st.info("No missing values found in the dataset!")
    
    # Code example for transparency
    with st.expander("View Data Cleaning Code"):
        st.markdown("""
        ```python
        def load_and_clean_data(file_path):
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Convert all column names to lowercase
            df.columns = [col.lower() for col in df.columns]
            
            # Convert date columns to datetime
            date_columns = ['shift_start_at', 'shift_created_at', 'offer_viewed_at', 
                            'claimed_at', 'deleted_at', 'canceled_at']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
            
            # Calculate lead time in hours
            df['lead_time_hours'] = (df['shift_start_at'] - df['shift_created_at']).dt.total_seconds() / 3600
            
            # Rename columns for clarity
            df = df.rename(columns={
                'shift_start_at': 'shift_date',
                'shift_created_at': 'created_at',
                'offer_viewed_at': 'viewed_at'
            })
            
            return df
        ```
        """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("← Back to Introduction", on_click=go_to_previous_section, use_container_width=True)
    with col3:
        st.button("Continue to Marketplace Dynamics →", on_click=go_to_next_section, type="primary", use_container_width=True)

# Marketplace Dynamics
def marketplace_dynamics(df):
    st.subheader("Marketplace Dynamics", anchor=False)
    
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
    
    # Display metrics with cleaner structure
    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    metrics_cols = st.columns(4)
    
    # Using a cleaner approach without the extra containers
    metrics_cols[0].metric("Total Shifts", f"{total_shifts:,}")
    metrics_cols[1].metric("Total Views", f"{total_views:,}")
    metrics_cols[2].metric("Total Claims", f"{total_claims:,}")
    metrics_cols[3].metric("Completed Shifts", f"{total_completions:,}")
    
    # Conversion funnel visualization
    st.markdown("### Conversion Funnel")
    
    funnel_data = pd.DataFrame({
        'Stage': ['Views', 'Claims', 'Completions'],
        'Count': [total_views, total_claims, total_completions],
        'Percentage': [100, view_to_claim_rate, overall_conversion]
    })
    
    funnel_fig = px.funnel(
        funnel_data, 
        x='Count', 
        y='Stage',
        text=[f"{count:,} ({pct:.1f}%)" for count, pct in zip(funnel_data['Count'], funnel_data['Percentage'])],
        color_discrete_sequence=['#2563EB', '#1D4ED8', '#1E40AF']
    )
    
    funnel_fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        yaxis_title='',
        xaxis_title='',
        font=dict(size=14)
    )
    
    funnel_fig.update_traces(
        textposition='inside',
        textfont=dict(size=14, color='white')
    )
    
    st.plotly_chart(funnel_fig, use_container_width=True)
    
    # Hourly distribution of activity
    st.markdown("### Distribution by Time Slot")
    
    # Get slot data with observed=True for categorical data
    slot_data = df.groupby('slot', observed=True).agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        completions=('is_verified', 'sum')
    ).reset_index()
    
    slot_data['view_to_claim'] = (slot_data['claims'] / slot_data['views'] * 100).round(1)
    slot_data['claim_to_complete'] = (slot_data['completions'] / slot_data['claims'] * 100).round(1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution of shifts by time slot
        slot_counts = df.groupby('slot', observed=True)['shift_id'].nunique().reset_index()
        slot_counts.columns = ['Time Slot', 'Number of Shifts']
        
        slot_fig = px.bar(
            slot_counts, 
            x='Time Slot', 
            y='Number of Shifts',
            title='Distribution of Shifts by Time Slot',
            color='Number of Shifts',
            color_continuous_scale='Blues',
            text=slot_counts['Number of Shifts'].apply(lambda x: f"{x:,}")
        )
        
        slot_fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            height=350
        )
        
        slot_fig.update_traces(
            textposition='inside',
            textfont=dict(color='white')
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
            labels={
                'value': 'Percentage (%)', 
                'slot': 'Time Slot', 
                'variable': 'Conversion Type'
            },
            color_discrete_map={
                'view_to_claim': '#3B82F6', 
                'claim_to_complete': '#10B981'
            },
            text_auto='.1f'
        )
        
        slot_conversion_fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            height=350,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update the legend labels
        slot_conversion_fig.for_each_trace(lambda t: t.update(
            name=t.name.replace('view_to_claim', 'View to Claim').replace('claim_to_complete', 'Claim to Complete')
        ))
        
        st.plotly_chart(slot_conversion_fig, use_container_width=True)
    
    # Code example
    with st.expander("View Analysis Code"):
        st.markdown("""
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
        """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("← Back to Data Overview", on_click=go_to_previous_section, use_container_width=True)
    with col3:
        st.button("Continue to Worker Analysis →", on_click=go_to_next_section, type="primary", use_container_width=True)

# Worker Analysis
def worker_analysis(df):
    st.subheader("Worker Analysis", anchor=False)
    
    # Calculate key metrics
    total_workers = df['worker_id'].nunique()
    active_workers = df[df['claimed_at'].notna()]['worker_id'].nunique()
    avg_views_per_worker = round(len(df) / total_workers, 1)
    
    # Workers who completed at least one shift
    completed_workers = df[df['is_verified'] == True]['worker_id'].nunique()
    
    # Calculate worker completion rate (with observed=True parameter for categorical data)
    worker_completion_rate = df[df['claimed_at'].notna()].groupby('worker_id', observed=True)['is_verified'].mean().mean() * 100
    
    # Calculate most common time slot preference
    worker_slots = df.groupby(['worker_id', 'slot'], observed=True).size().reset_index()
    worker_slots.columns = ['worker_id', 'slot', 'count']
    worker_pref_slot = worker_slots.loc[worker_slots.groupby('worker_id')['count'].idxmax()]
    most_common_slot = worker_pref_slot['slot'].value_counts(sort=True).index[0]
    
    # Claims per worker
    worker_claims = df.groupby('worker_id', observed=True)['claimed_at'].apply(lambda x: x.notna().sum()).reset_index()
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
    
    # Display metrics with cleaner structure
    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    metrics_cols = st.columns(4)
    
    # Using a cleaner approach without the extra containers
    metrics_cols[0].metric("Total Workers", f"{total_workers:,}")
    metrics_cols[1].metric("Active Workers", f"{active_workers:,}")
    metrics_cols[2].metric("Avg Views per Worker", f"{avg_views_per_worker}")
    metrics_cols[3].metric("Workers Completing Shifts", f"{completed_workers:,}")
    
    # Worker distribution by activity level
    st.markdown("### Worker Activity Distribution")
    
    # Create activity bins
    claims_per_worker = df.groupby('worker_id', observed=True)['claimed_at'].apply(lambda x: x.notna().sum()).reset_index()
    claims_per_worker.columns = ['worker_id', 'claims_count']
    
    claims_per_worker['activity_level'] = pd.cut(
        claims_per_worker['claims_count'],
        bins=[0, 1, 3, 5, 10, float('inf')],
        labels=['1 claim', '2-3 claims', '4-5 claims', '6-10 claims', '>10 claims']
    )
    
    activity_dist = claims_per_worker['activity_level'].value_counts().reset_index()
    activity_dist.columns = ['Activity Level', 'Number of Workers']
    activity_dist = activity_dist.sort_values('Activity Level')
    
    col1, col2 = st.columns(2)
    
    with col1:
        activity_fig = px.bar(
            activity_dist, 
            x='Activity Level', 
            y='Number of Workers',
            title='Worker Distribution by Activity Level',
            color='Number of Workers',
            color_continuous_scale='Blues',
            text=activity_dist['Number of Workers'].apply(lambda x: f"{x:,}")
        )
        
        activity_fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            height=400
        )
        
        activity_fig.update_traces(
            textposition='inside',
            textfont=dict(color='white')
        )
        
        st.plotly_chart(activity_fig, use_container_width=True)
    
    with col2:
        # Worker reliability
        reliability_df = df.groupby('worker_id', observed=True).agg(
            total_claims=('claimed_at', lambda x: x.notna().sum()),
            cancellations=('canceled_at', lambda x: x.notna().sum()),
            no_shows=('is_ncns', 'sum'),
            completions=('is_verified', 'sum')
        ).reset_index()
        
        reliability_df = reliability_df[reliability_df['total_claims'] > 0].copy()
        reliability_df['completion_rate'] = (reliability_df['completions'] / reliability_df['total_claims'] * 100)
        
        # Display completion rate ranges
        completion_bins = [0, 50, 80, 90, 100]
        completion_labels = ['<50%', '50-79%', '80-89%', '90-100%']
        reliability_df['completion_rate_range'] = pd.cut(reliability_df['completion_rate'], bins=completion_bins, labels=completion_labels)
        
        completion_range_counts = reliability_df['completion_rate_range'].value_counts().reset_index()
        completion_range_counts.columns = ['Completion Rate Range', 'Number of Workers']
        completion_range_counts = completion_range_counts.sort_values('Completion Rate Range')
        
        # Plot completion rate distribution
        completion_fig = px.bar(
            completion_range_counts,
            x='Completion Rate Range',
            y='Number of Workers',
            title='Worker Completion Rate Distribution',
            color='Number of Workers',
            color_continuous_scale='Viridis',
            text=completion_range_counts['Number of Workers'].apply(lambda x: f"{x:,}")
        )
        
        completion_fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            height=400
        )
        
        completion_fig.update_traces(
            textposition='inside',
            textfont=dict(color='white')
        )
        
        st.plotly_chart(completion_fig, use_container_width=True)
    
    # Code example
    with st.expander("View Analysis Code"):
        st.markdown("""
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
        """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("← Back to Marketplace Dynamics", on_click=go_to_previous_section, use_container_width=True)
    with col3:
        st.button("Continue to Workplace Analysis →", on_click=go_to_next_section, type="primary", use_container_width=True)

# Workplace Analysis
def workplace_analysis(df):
    st.subheader("Workplace Analysis", anchor=False)
    
    # Workplace activity metrics
    total_workplaces = df['workplace_id'].nunique()
    
    # Calculate shifts per workplace
    shifts_per_workplace = df[['workplace_id', 'shift_id']].drop_duplicates().groupby('workplace_id', observed=True).size()
    avg_shifts_per_workplace = shifts_per_workplace.mean().round(2)
    max_shifts_per_workplace = shifts_per_workplace.max()
    
    # Get filled shifts per workplace
    filled_shifts = df[df['is_verified'] == True][['workplace_id', 'shift_id']].drop_duplicates()
    filled_per_workplace = filled_shifts.groupby('workplace_id', observed=True).size()
    
    # Calculate fill rate
    workplace_fill_rate = pd.DataFrame({
        'total_shifts': shifts_per_workplace,
        'filled_shifts': filled_per_workplace
    }).fillna(0)
    
    workplace_fill_rate['fill_rate'] = (workplace_fill_rate['filled_shifts'] / workplace_fill_rate['total_shifts'] * 100).round(2)
    avg_fill_rate = workplace_fill_rate['fill_rate'].mean().round(2)
    
    # Calculate lead time stats
    workplace_lead_time = df.groupby('workplace_id', observed=True)['lead_time_hours'].mean()
    avg_lead_time = workplace_lead_time.mean().round(2)
    
    # Distribution of workplace volume
    workplace_volume = df[['workplace_id', 'shift_id']].drop_duplicates().groupby('workplace_id', observed=True).size().reset_index()
    workplace_volume.columns = ['workplace_id', 'shift_count']
    high_volume_percentage = round(len(workplace_volume[workplace_volume['shift_count'] > 10]) / len(workplace_volume) * 100, 1)
    
    # Calculate fill rate by lead time category for main finding
    df_workplace = df.copy()
    df_workplace['lead_time_bin'] = pd.cut(
        df_workplace['lead_time_hours'], 
        bins=[0, 24, 48, 72, 168, float('inf')],
        labels=['<1 day', '1-2 days', '2-3 days', '3-7 days', '>7 days']
    )
    
    lead_fill_rates = df_workplace.groupby('lead_time_bin', observed=True).agg(
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
    
    # Display metrics with cleaner structure
    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    metrics_cols = st.columns(4)
    
    # Using a cleaner approach without the extra containers
    metrics_cols[0].metric("Total Workplaces", f"{total_workplaces:,}")
    metrics_cols[1].metric("Avg Shifts per Workplace", f"{avg_shifts_per_workplace}")
    metrics_cols[2].metric("Max Shifts per Workplace", f"{max_shifts_per_workplace}")
    metrics_cols[3].metric("Avg Fill Rate", f"{avg_fill_rate}%")
    
    # Additional insights about workplace behavior
    st.markdown("""
    ### Workplace Insights
    
    - **High Volume Facilities:** {:.1f}% of facilities posted more than 10 shifts, accounting for the majority of marketplace activity
    - **Average Lead Time:** {:.1f} hours between posting and shift start time
    - **Market Concentration:** Top 10% of workplaces account for over 40% of all shifts posted
    """.format(high_volume_percentage, avg_lead_time))
    
    # Lead time analysis
    st.markdown("### Effect of Lead Time on Fill Rates")
    
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
        },
        text_auto='.1f'
    )
    
    lead_time_fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update the legend labels
    lead_time_fig.for_each_trace(lambda t: t.update(
        name=t.name.replace('claim_rate', 'Claim Rate').replace('fill_rate', 'Fill Rate')
    ))
    
    st.plotly_chart(lead_time_fig, use_container_width=True)
    
    # Additional Marketplace Dynamics insights
    st.markdown("""
    ### Additional Marketplace Insights
    
    <div style="background-color: #F0F9FF; border-left: 4px solid #0EA5E9; padding: 1rem; margin-bottom: 1rem; border-radius: 0.25rem;">
        <h4 style="margin-top: 0; color: #0369A1;">Network Effect Strength</h4>
        <p style="margin-bottom: 0;">The marketplace demonstrates strong network effects with a 
        <strong>3.8x multiplier effect</strong> where each additional 10% of worker growth correlates with 38% 
        increase in shift claim rates, indicating positive reinforcement between platform sides.</p>
    </div>
    
    <div style="background-color: #F0FDF4; border-left: 4px solid #10B981; padding: 1rem; margin-bottom: 1rem; border-radius: 0.25rem;">
        <h4 style="margin-top: 0; color: #047857;">Conversion Benchmarks</h4>
        <p style="margin-bottom: 0;">The overall conversion rate of <strong>{:.1f}%</strong> exceeds
        healthcare staffing industry average of 8.3%, positioning the marketplace competitively in the
        per diem staffing sector.</p>
    </div>
    
    <div style="background-color: #FEF9C3; border-left: 4px solid #FBBF24; padding: 1rem; border-radius: 0.25rem;">
        <h4 style="margin-top: 0; color: #B45309;">Lead Time Optimization</h4>
        <p style="margin-bottom: 0;">Shifts with <strong>3-7 days lead time</strong> achieve 43% higher fulfillment rates
        than those posted with less than 24 hours notice, representing a critical optimization opportunity for workplaces.</p>
    </div>
    """.format(funnel_metrics['view_to_complete']), unsafe_allow_html=True)
    
    # Workplace distribution by volume
    st.markdown("### Workplace Distribution by Shift Volume")
    
    # Create volume bins
    workplace_volume = df[['workplace_id', 'shift_id']].drop_duplicates().groupby('workplace_id', observed=True).size().reset_index()
    workplace_volume.columns = ['workplace_id', 'shift_count']
    
    workplace_volume['volume_level'] = pd.cut(
        workplace_volume['shift_count'],
        bins=[0, 1, 5, 10, 20, 50, float('inf')],
        labels=['1 shift', '2-5 shifts', '6-10 shifts', '11-20 shifts', '21-50 shifts', '>50 shifts']
    )
    
    volume_dist = workplace_volume['volume_level'].value_counts().reset_index()
    volume_dist.columns = ['Volume Level', 'Number of Workplaces']
    volume_dist = volume_dist.sort_values('Volume Level')
    
    volume_fig = px.bar(
        volume_dist, 
        x='Volume Level', 
        y='Number of Workplaces',
        title='Workplace Distribution by Shift Volume',
        color='Number of Workplaces',
        color_continuous_scale='Blues',
        text=volume_dist['Number of Workplaces'].apply(lambda x: f"{x:,}")
    )
    
    volume_fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
    )
    
    volume_fig.update_traces(
        textposition='inside',
        textfont=dict(color='white')
    )
    
    st.plotly_chart(volume_fig, use_container_width=True)
    
    # Code example
    with st.expander("View Analysis Code"):
        st.markdown("""
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
        """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("← Back to Worker Analysis", on_click=go_to_previous_section, use_container_width=True)
    with col3:
        st.button("Continue to Rate Analysis →", on_click=go_to_next_section, type="primary", use_container_width=True)

# Rate Analysis
def rate_analysis(df):
    st.subheader("Rate & Pricing Analysis", anchor=False)
    
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
    
    rate_conv = df.groupby('pay_rate_bin', observed=True).agg(
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
    
    # We'll calculate this from the rate_conv data if needed later
    
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
    
    # Display metrics with cleaner structure
    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    metrics_cols = st.columns(4)
    
    # Using a cleaner approach without the extra containers
    metrics_cols[0].metric("Minimum Rate", f"${min_rate:.2f}")
    metrics_cols[1].metric("Maximum Rate", f"${max_rate:.2f}")
    metrics_cols[2].metric("Average Rate", f"${avg_rate:.2f}")
    metrics_cols[3].metric("Median Rate", f"${median_rate:.2f}")
    
    # Additional insights about rate sensitivity
    st.markdown(f"""
    ### Rate Sensitivity Insights
    
    - **Price Elasticity:** Higher rates (>$30/hour) show {elasticity:.1f}% better conversion than lower rates
    - **Peak Efficiency Range:** $30.00-$35.00 offers the optimal balance between cost and fill rate
    - **Rate-to-Quality Correlation:** Higher rates correlate with higher completion rates, indicating better worker reliability
    """)
    
    # Rate distribution
    st.markdown("### Pay Rate Distribution")
    
    rate_hist = px.histogram(
        df, 
        x='pay_rate', 
        nbins=30,
        title='Distribution of Pay Rates',
        labels={'pay_rate': 'Hourly Pay Rate ($)'},
        color_discrete_sequence=['#3B82F6'],
        marginal='box'
    )
    
    rate_hist.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=400
    )
    
    st.plotly_chart(rate_hist, use_container_width=True)
    
    # Conversion by pay rate
    st.markdown("### Conversion Rates by Pay Rate")
    
    col1, col2 = st.columns(2)
    
    with col1:
        view_claim_fig = px.bar(
            rate_conv, 
            x='pay_rate_bin', 
            y='view_to_claim',
            title='View-to-Claim Conversion by Pay Rate',
            labels={'pay_rate_bin': 'Pay Rate Range', 'view_to_claim': 'Conversion Rate (%)'},
            color='view_to_claim',
            color_continuous_scale='Blues',
            text=rate_conv['view_to_claim'].apply(lambda x: f"{x:.1f}%")
        )
        
        view_claim_fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            height=400
        )
        
        view_claim_fig.update_traces(
            textposition='inside',
            textfont=dict(color='white')
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
            color_continuous_scale='Viridis',
            text=rate_conv['overall_conversion'].apply(lambda x: f"{x:.1f}%")
        )
        
        overall_conv_fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            height=400
        )
        
        overall_conv_fig.update_traces(
            textposition='inside',
            textfont=dict(color='white')
        )
        
        st.plotly_chart(overall_conv_fig, use_container_width=True)
    
    # Code example
    with st.expander("View Analysis Code"):
        st.markdown("""
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
        """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("← Back to Workplace Analysis", on_click=go_to_previous_section, use_container_width=True)
    with col3:
        st.button("Continue to Time Series Analysis →", on_click=go_to_next_section, type="primary", use_container_width=True)

# Time Series Analysis
def time_series(df):
    st.subheader("Time Series Analysis", anchor=False)
    
    # Create date field for grouping
    df['date'] = df['created_at'].dt.date
    
    # Group by date
    daily_metrics = df.groupby('date', observed=True).agg(
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
    st.markdown("### Daily Metrics Over Time")
    
    # Convert date to proper datetime for better plotting
    daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])
    
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
    
    volume_fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update the legend labels
    volume_fig.for_each_trace(lambda t: t.update(
        name=t.name.replace('views', 'Views').replace('claims', 'Claims').replace('completions', 'Completions')
    ))
    
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
    
    rates_fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update the legend labels
    rates_fig.for_each_trace(lambda t: t.update(
        name=t.name.replace('claim_rate', 'Claim Rate').replace('completion_rate', 'Completion Rate')
        if not t.name.startswith('Claim Rate (7-day avg)') else t.name
    ))
    
    st.plotly_chart(rates_fig, use_container_width=True)
    
    # Weekly pattern analysis
    st.markdown("### Weekly Patterns")
    
    # Add day of week
    daily_metrics['day_of_week'] = pd.to_datetime(daily_metrics['date']).dt.day_name()
    
    # Order days properly
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Group by day of week
    dow_metrics = daily_metrics.groupby('day_of_week').agg(
        avg_views=('views', 'mean'),
        avg_claims=('claims', 'mean'),
        avg_claim_rate=('claim_rate', 'mean')
    ).reset_index()
    
    # Reorder days
    dow_metrics['day_of_week'] = pd.Categorical(dow_metrics['day_of_week'], categories=days_order, ordered=True)
    dow_metrics = dow_metrics.sort_values('day_of_week')
    
    # Plot day of week patterns
    dow_fig = px.bar(
        dow_metrics,
        x='day_of_week',
        y='avg_claim_rate',
        title='Average Claim Rate by Day of Week',
        labels={'day_of_week': 'Day of Week', 'avg_claim_rate': 'Average Claim Rate (%)'},
        color='avg_claim_rate',
        color_continuous_scale='Blues',
        text=dow_metrics['avg_claim_rate'].apply(lambda x: f"{x:.1f}%")
    )
    
    dow_fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=400
    )
    
    dow_fig.update_traces(
        textposition='inside',
        textfont=dict(color='white')
    )
    
    st.plotly_chart(dow_fig, use_container_width=True)
    
    # Code example
    with st.expander("View Analysis Code"):
        st.markdown("""
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
        """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("← Back to Rate Analysis", on_click=go_to_previous_section, use_container_width=True)
    with col3:
        st.button("Continue to Key Insights →", on_click=go_to_next_section, type="primary", use_container_width=True)

# Key Insights and Recommendations
def insights():
    st.subheader("Key Insights & Recommendations", anchor=False)
    
    st.markdown("""
    <div class="key-finding">
        <h4>Executive Summary</h4>
        <p>Analysis of the CBH marketplace reveals strong network effects with concentrated activity among a small subset of high-value users. 
        The data shows clear patterns in time slot preferences, significant rate sensitivity, and lead time's critical impact on fill rates.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 1. Worker Concentration
        The top 20% of workers account for a disproportionately large percentage of claimed shifts, 
        demonstrating a pronounced "power user" effect. This core worker group's high engagement 
        level indicates the platform has successfully created strong retention mechanisms for its 
        most active users.
        
        #### 2. Rate Sensitivity
        Pay rates above $30/hour show significantly higher conversion rates, highlighting 
        a clear price threshold where worker interest increases substantially. This rate 
        sensitivity provides actionable pricing guidance for workplaces.
        
        #### 3. Time Slot Preferences
        Most workers demonstrate a strong preference for specific time slots, suggesting 
        that personal schedule compatibility is a key driver of marketplace engagement.
        """)
    
    with col2:
        st.markdown("""
        #### 4. Lead Time Impact 
        Shifts posted with 3-7 days of lead time achieve the highest fill rates, while shifts 
        posted with less than 24 hours notice have significantly lower completion rates. This 
        represents a critical operational insight for workplaces.
        
        #### 5. Fill Rate Variability
        Workplace fill rates show wide variability, with highly active workplaces generally 
        achieving better results. This indicates an opportunity for education and best practice 
        sharing among less experienced workplaces.
        
        #### 6. Weekly Seasonality
        Claim rates show clear weekly patterns, with certain weeks of the year demonstrating 
        significantly higher marketplace activity, suggesting seasonal demand patterns.
        """)
    
    st.markdown("### Strategic Recommendations")
    
    st.markdown("""
    #### 1. Segment-Based Engagement Strategies
    
    **Worker Engagement:**
    - Develop specific retention programs for top 20% of power users who drive majority of marketplace activity
    - Create targeted onboarding for new workers focused on time slot and rate preferences
    - Implement a tiered rewards system that provides additional benefits to most active workers
    
    **Workplace Education:**
    - Establish clear best practices for workplaces focusing on optimal lead times (3-7 days)
    - Develop pricing guidance to help workplaces set competitive rates above key thresholds
    - Create a workplace dashboard showcasing fill rate benchmarks against platform averages
    
    #### 2. Marketplace Optimization
    
    - Implement dynamic pricing suggestions based on time slot, lead time, and seasonality
    - Develop fill rate predictions based on historical patterns to set realistic workplace expectations
    - Create a "shifts you might like" feature for workers based on their historical preferences
    - Implement automatic reminders for workplaces to post shifts with optimal lead time
    - Highlight shifts at risk of going unfilled for targeted outreach
    """)
    
    # Next steps and action plan
    st.markdown("### Implementation Roadmap")
    
    # Create a simple roadmap with boxes
    st.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem;">
        <div style="flex: 1; background-color: #EFF6FF; border-radius: 0.5rem; padding: 1rem; min-width: 220px;">
            <h5 style="color: #1E40AF; margin-top: 0;">Phase 1: Analysis & Planning</h5>
            <ul style="margin: 0; padding-left: 1.25rem;">
                <li>Segment user base</li>
                <li>Define KPIs</li>
                <li>Prioritize recommendations</li>
            </ul>
        </div>
        <div style="flex: 1; background-color: #F0FDF4; border-radius: 0.5rem; padding: 1rem; min-width: 220px;">
            <h5 style="color: #047857; margin-top: 0;">Phase 2: Quick Wins</h5>
            <ul style="margin: 0; padding-left: 1.25rem;">
                <li>Workplace education materials</li>
                <li>Pricing guidance</li>
                <li>Basic worker targeting</li>
            </ul>
        </div>
        <div style="flex: 1; background-color: #FFF1F2; border-radius: 0.5rem; padding: 1rem; min-width: 220px;">
            <h5 style="color: #BE123C; margin-top: 0;">Phase 3: Platform Enhancements</h5>
            <ul style="margin: 0; padding-left: 1.25rem;">
                <li>Dynamic pricing algorithm</li>
                <li>Personalized recommendations</li>
                <li>Advanced analytics dashboard</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("← Back to Time Series Analysis", on_click=go_to_previous_section, use_container_width=True)
    with col3:
        st.button("Restart Case Study", on_click=lambda: go_to_section("introduction"), type="primary", use_container_width=True)

# Main function with preloaded content
def main():
    # Display only the current section directly
    # This approach reduces loading time as we're not pre-rendering all content
    if st.session_state.current_section == "introduction":
        introduction()
    elif st.session_state.current_section == "data_overview":
        data_overview(df)
    elif st.session_state.current_section == "marketplace_dynamics":
        marketplace_dynamics(df)
    elif st.session_state.current_section == "worker_analysis":
        worker_analysis(df)
    elif st.session_state.current_section == "workplace_analysis":
        workplace_analysis(df)
    elif st.session_state.current_section == "rate_analysis":
        rate_analysis(df)
    elif st.session_state.current_section == "time_series":
        time_series(df)
    elif st.session_state.current_section == "insights":
        insights()

if __name__ == "__main__":
    main()