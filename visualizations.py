import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def plot_overview_metrics(df):
    """
    Plot overview metrics dashboard
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with overview metrics
    """
    # Calculate metrics
    total_views = len(df)
    unique_shifts = df['shift_id'].nunique()
    unique_workers = df['worker_id'].nunique()
    unique_workplaces = df['workplace_id'].nunique()
    claimed_shifts = df['claimed_at'].notna().sum()
    conversion_rate = (claimed_shifts / total_views * 100).round(2)
    verified_shifts = df['is_verified'].sum()
    avg_pay_rate = df['pay_rate'].mean().round(2)
    avg_charge_rate = df['charge_rate'].mean().round(2)
    
    # Create a figure with subplots
    fig = go.Figure()
    
    # Add metrics as annotations
    metrics = [
        f"Total Views: {total_views:,}",
        f"Unique Shifts: {unique_shifts:,}",
        f"Unique Workers: {unique_workers:,}",
        f"Unique Workplaces: {unique_workplaces:,}",
        f"Claimed Shifts: {claimed_shifts:,}",
        f"Conversion Rate: {conversion_rate}%",
        f"Verified Shifts: {verified_shifts:,}",
        f"Avg Pay Rate: ${avg_pay_rate}",
        f"Avg Charge Rate: ${avg_charge_rate}"
    ]
    
    # Calculate positions for a 3x3 grid
    positions = []
    for i in range(3):
        for j in range(3):
            positions.append((i*0.25 + 0.25, j*0.25 + 0.25))
    
    # Add annotations for each metric
    for i, (metric, position) in enumerate(zip(metrics, positions)):
        fig.add_annotation(
            x=position[0],
            y=position[1],
            text=metric,
            showarrow=False,
            font=dict(
                size=14,
                color="black"
            ),
            align="center",
            bordercolor="black",
            borderwidth=1,
            borderpad=4,
            bgcolor="white",
            opacity=0.8
        )
    
    # Update layout
    fig.update_layout(
        title="Marketplace Overview Metrics",
        showlegend=False,
        height=400,
        plot_bgcolor="white",
        margin=dict(t=70, b=0, l=0, r=0)
    )
    
    # Remove axes
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    
    return fig

def plot_conversion_funnel(df):
    """
    Plot conversion funnel visualization
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with conversion funnel
    """
    # Calculate funnel metrics
    total_views = len(df)
    claimed_shifts = df['claimed_at'].notna().sum()
    claimed_not_canceled = claimed_shifts - df['canceled_at'].notna().sum()
    verified_shifts = df['is_verified'].sum()
    
    # Create funnel values and labels
    values = [total_views, claimed_shifts, claimed_not_canceled, verified_shifts]
    labels = ['Viewed', 'Claimed', 'Not Canceled', 'Verified']
    
    # Calculate percentages for display
    percentages = [100]  # First stage is 100%
    for i in range(1, len(values)):
        # Calculate percentage relative to previous stage
        if values[i-1] > 0:
            pct = (values[i] / values[i-1]) * 100
        else:
            pct = 0
        percentages.append(pct)
    
    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y=labels,
        x=values,
        textinfo="value+percent previous",
        marker=dict(
            color=["#3366CC", "#DC3912", "#FF9900", "#109618"]
        ),
        connector=dict(line=dict(color="royalblue", dash="dot", width=3))
    ))
    
    # Update layout
    fig.update_layout(
        title="Conversion Funnel",
        margin=dict(l=100, r=10),
        height=500
    )
    
    return fig

def plot_timeslot_distribution(df):
    """
    Plot distribution of shifts by time slot
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with time slot distribution
    """
    # Calculate time slot distribution
    slot_dist = df['slot'].value_counts().reset_index()
    slot_dist.columns = ['Time Slot', 'Count']
    
    # Create pie chart
    fig = px.pie(slot_dist, names='Time Slot', values='Count',
                title='Distribution of Shifts by Time Slot',
                color_discrete_sequence=px.colors.qualitative.Set3)
    
    # Update layout
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def plot_rate_distribution(df):
    """
    Plot distribution of pay rates
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with pay rate distribution
    """
    # Create histogram
    fig = px.histogram(df, x='pay_rate', nbins=30,
                     title='Distribution of Pay Rates',
                     labels={'pay_rate': 'Pay Rate ($)'},
                     color_discrete_sequence=['#3366CC'])
    
    # Update layout
    fig.update_layout(
        xaxis_title="Pay Rate ($)",
        yaxis_title="Count",
        height=400,
        bargap=0.1
    )
    
    # Add mean line
    mean_pay = df['pay_rate'].mean()
    fig.add_vline(x=mean_pay, line_dash="dash", line_color="red",
                annotation_text=f"Mean: ${mean_pay:.2f}",
                annotation_position="top right")
    
    return fig

def plot_time_series(df, metric='conversion_rate'):
    """
    Plot time series of specified metric
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
    metric : str
        Metric to plot (default: 'conversion_rate')
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with time series plot
    """
    # Ensure date column exists
    if 'date' not in df.columns:
        df['date'] = df['shift_start_at'].dt.date
    
    # Group by date and calculate metrics
    daily_metrics = df.groupby('date').agg(
        views=('shift_id', 'count'),
        claims=('claimed_at', lambda x: x.notna().sum()),
        verified=('is_verified', 'sum')
    ).reset_index()
    
    daily_metrics['conversion_rate'] = (daily_metrics['claims'] / daily_metrics['views'] * 100).round(2)
    daily_metrics['fulfillment_rate'] = (daily_metrics['verified'] / daily_metrics['claims'] * 100).fillna(0).round(2)
    
    # Convert date to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(daily_metrics['date']):
        daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])
    
    # Create line chart
    if metric == 'conversion_rate':
        title = 'Daily Conversion Rate'
        y_title = 'Conversion Rate (%)'
        color = '#3366CC'
    elif metric == 'fulfillment_rate':
        title = 'Daily Fulfillment Rate'
        y_title = 'Fulfillment Rate (%)'
        color = '#109618'
    elif metric == 'views':
        title = 'Daily Views'
        y_title = 'Number of Views'
        color = '#FF9900'
    elif metric == 'claims':
        title = 'Daily Claims'
        y_title = 'Number of Claims'
        color = '#DC3912'
    else:
        title = f'Daily {metric.capitalize()}'
        y_title = metric.capitalize()
        color = '#3366CC'
    
    fig = px.line(daily_metrics, x='date', y=metric,
                 title=title,
                 labels={'date': 'Date', metric: y_title},
                 color_discrete_sequence=[color])
    
    # Add 7-day moving average
    daily_metrics[f'{metric}_ma7'] = daily_metrics[metric].rolling(window=7, min_periods=1).mean()
    
    fig.add_trace(go.Scatter(
        x=daily_metrics['date'],
        y=daily_metrics[f'{metric}_ma7'],
        mode='lines',
        name='7-day MA',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=y_title,
        height=400,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def plot_geographical_distribution(df):
    """
    Plot geographical distribution of marketplace activity
    Note: This is a placeholder function as we don't have geographical data
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with geographical distribution
    """
    # Since we don't have geographical data, create a placeholder
    fig = go.Figure()
    
    fig.add_annotation(
        x=0.5,
        y=0.5,
        text="Geographical data not available",
        showarrow=False,
        font=dict(
            size=20,
            color="gray"
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Geographical Distribution (Not Available)",
        height=400,
        plot_bgcolor="white"
    )
    
    # Remove axes
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    
    return fig

def plot_worker_retention(df):
    """
    Plot worker retention analysis
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with worker retention analysis
    """
    # Group by worker_id and count claims
    worker_claims = df.groupby('worker_id')['claimed_at'].apply(lambda x: x.notna().sum()).reset_index()
    worker_claims.columns = ['worker_id', 'claims_count']
    
    # Create histogram of claims per worker
    fig = px.histogram(worker_claims, x='claims_count', nbins=50,
                      title='Distribution of Claims per Worker',
                      labels={'claims_count': 'Number of Claims'},
                      color_discrete_sequence=['#3366CC'])
    
    # Add a vertical line at the mean
    mean_claims = worker_claims['claims_count'].mean()
    fig.add_vline(x=mean_claims, line_dash="dash", line_color="red",
                annotation_text=f"Mean: {mean_claims:.2f}",
                annotation_position="top right")
    
    # Update layout
    fig.update_layout(
        xaxis_title="Number of Claims per Worker",
        yaxis_title="Count of Workers",
        height=400
    )
    
    # Limit x-axis to focus on meaningful range (e.g., up to 20 claims)
    fig.update_xaxes(range=[0, 20])
    
    return fig

def plot_marketplace_balance(df):
    """
    Plot marketplace balance (supply vs. demand) by time slot
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with marketplace balance analysis
    """
    # Group by slot and calculate metrics
    slot_metrics = df.groupby('slot').agg(
        total_shifts=('shift_id', 'nunique'),
        total_views=('shift_id', 'count'),
        claimed_shifts=('claimed_at', lambda x: x.notna().sum())
    ).reset_index()
    
    # Calculate views per shift (demand indicator)
    slot_metrics['views_per_shift'] = (slot_metrics['total_views'] / slot_metrics['total_shifts']).round(2)
    
    # Calculate conversion rate (supply indicator)
    slot_metrics['conversion_rate'] = (slot_metrics['claimed_shifts'] / slot_metrics['total_views'] * 100).round(2)
    
    # Create a figure
    fig = go.Figure()
    
    # Add views per shift bar
    fig.add_trace(go.Bar(
        x=slot_metrics['slot'],
        y=slot_metrics['views_per_shift'],
        name='Views per Shift',
        marker_color='#3366CC',
        yaxis='y'
    ))
    
    # Add conversion rate line
    fig.add_trace(go.Scatter(
        x=slot_metrics['slot'],
        y=slot_metrics['conversion_rate'],
        name='Conversion Rate (%)',
        marker_color='#DC3912',
        mode='lines+markers',
        yaxis='y2'
    ))
    
    # Update layout with dual y-axes
    fig.update_layout(
        title='Marketplace Balance by Time Slot',
        xaxis=dict(
            title='Time Slot',
            titlefont=dict(
                color='black'
            )
        ),
        yaxis=dict(
            title='Views per Shift',
            titlefont=dict(
                color='#3366CC'
            ),
            side='left'
        ),
        yaxis2=dict(
            title='Conversion Rate (%)',
            titlefont=dict(
                color='#DC3912'
            ),
            side='right',
            overlaying='y',
            range=[0, 100]
        ),
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def plot_workplace_activity(df):
    """
    Plot workplace activity patterns
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with workplace activity analysis
    """
    # Get unique shift-workplace combinations
    shift_workplace = df[['shift_id', 'workplace_id']].drop_duplicates()
    
    # Count shifts per workplace
    shifts_per_workplace = shift_workplace.groupby('workplace_id').size().reset_index(name='shift_count')
    
    # Create histogram of shifts per workplace
    fig = px.histogram(shifts_per_workplace, x='shift_count', nbins=50,
                      title='Distribution of Shifts per Workplace',
                      labels={'shift_count': 'Number of Shifts'},
                      color_discrete_sequence=['#3366CC'])
    
    # Add a vertical line at the mean
    mean_shifts = shifts_per_workplace['shift_count'].mean()
    fig.add_vline(x=mean_shifts, line_dash="dash", line_color="red",
                annotation_text=f"Mean: {mean_shifts:.2f}",
                annotation_position="top right")
    
    # Update layout
    fig.update_layout(
        xaxis_title="Number of Shifts per Workplace",
        yaxis_title="Count of Workplaces",
        height=400
    )
    
    # Limit x-axis to focus on meaningful range (e.g., up to 50 shifts)
    fig.update_xaxes(range=[0, 50])
    
    return fig

def plot_pricing_strategy(df):
    """
    Plot pricing strategy effectiveness
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with marketplace data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        A figure with pricing strategy analysis
    """
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
    
    # Create figure
    fig = go.Figure()
    
    # Add bars for conversion rate
    fig.add_trace(go.Bar(
        x=pay_rate_conv['pay_rate_bin'],
        y=pay_rate_conv['conversion_rate'],
        name='Conversion Rate (%)',
        marker_color='#3366CC',
        text=pay_rate_conv['conversion_rate'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))
    
    # Add bars for completion rate
    fig.add_trace(go.Bar(
        x=pay_rate_conv['pay_rate_bin'],
        y=pay_rate_conv['completion_rate'],
        name='Completion Rate (%)',
        marker_color='#109618',
        text=pay_rate_conv['completion_rate'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))
    
    # Add count of views as line
    fig.add_trace(go.Scatter(
        x=pay_rate_conv['pay_rate_bin'],
        y=pay_rate_conv['total_views'],
        name='Number of Views',
        marker_color='#FF9900',
        mode='lines+markers',
        yaxis='y2'
    ))
    
    # Update layout with dual y-axes
    fig.update_layout(
        title='Pricing Strategy Effectiveness',
        xaxis=dict(
            title='Pay Rate Range',
            titlefont=dict(
                color='black'
            )
        ),
        yaxis=dict(
            title='Rate (%)',
            titlefont=dict(
                color='black'
            ),
            side='left',
            range=[0, 100]
        ),
        yaxis2=dict(
            title='Number of Views',
            titlefont=dict(
                color='#FF9900'
            ),
            side='right',
            overlaying='y'
        ),
        barmode='group',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
