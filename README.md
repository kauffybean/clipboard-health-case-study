# CBH Marketplace Analysis – Replit Vibe Coding Goes Analyst Mode

**A data analysis engine disguised as a case study.**

🔗 [Live Demo](https://anna-case-study-cbh.replit.app/)

---

## Why I Built This

Clipboard Health’s first interview screen is a case study — basically, solve this data analysis prompt and *maybe* we’ll talk to you. I saw some horror stories about this process on Reddit and TikTok and thought: why not just build something fun and see what happens?

So instead of answering in a doc or Jupyter notebook, I built a full exploratory analysis platform in Replit using Streamlit. It was kind of a flex, kind of a test of how good Replit is for analysis work. TL;DR: it worked. 

---
## Project Overview

A comprehensive data analysis platform built with Streamlit that provides interactive exploration of CBH (Clipboard Health) marketplace data. This application serves as a case study demonstrating how to analyze a two-sided healthcare marketplace where workers book per diem shifts with workplaces.

The platform offers advanced analytics and visualizations to understand marketplace dynamics, worker behavior, workplace activity, and pricing strategies.

## Features

### Interactive Dashboard Sections

1. **Introduction**: Overview of the project, key questions, and data sources
2. **Data Overview**: Summary statistics, data sample, and quality assessment
3. **Marketplace Dynamics**: Conversion rates, activity patterns, and funnel analysis
4. **Worker Analysis**: Worker behavior, preferences, and reliability metrics
5. **Workplace Analysis**: Posting patterns, fulfillment rates, and workplace activity
6. **Rate Analysis**: Price sensitivity, rate distribution, and pricing strategy evaluation
7. **Time Series Analysis**: Temporal patterns, seasonality, and trend analysis
8. **Key Insights & Recommendations**: Executive summary and strategic recommendations

### Technical Features

- **Wizard Navigation**: Intuitive step-by-step interface for guided analysis
- **Interactive Visualizations**: Dynamic charts and graphs with Plotly and Matplotlib
- **Data Transparency**: Python code samples for educational purposes
- **Optimized Performance**: Data caching and efficient processing for better user experience
- **Professional UI**: Clean, modern interface with consistent styling

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/cbh-marketplace-analysis.git
   cd cbh-marketplace-analysis
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

## Project Structure

```
.
├── app.py                  # Main application with all analysis sections
├── deploy.py               # Simplified version for deployment
├── utils.py                # Data loading and utility functions
├── analysis.py             # Core analytical functions
├── visualizations.py       # Data visualization components
├── attached_assets/        # Data files and resources
│   ├── deployment_dataset.csv           # Smaller dataset for deployment
│   └── Problems we tackle, Shift Offers v3 - table_12_2025-01-22T1134.csv  # Full dataset
├── .streamlit/             # Streamlit configuration
│   └── config.toml         # Configuration settings
└── README.md               # Project documentation
```

## Data Description

The analysis uses marketplace transaction data including:

- **Shifts**: Unique identifiers, date/time, and slot information
- **Workers**: Worker IDs, view timestamps, claim timestamps
- **Workplaces**: Workplace IDs, creation timestamps, lead times
- **Rates**: Pay rates, pricing strategies
- **Status**: Verification status, cancellations, no-shows

## Key Insights

The application highlights several key insights from the marketplace data:

1. **Conversion Factors**: Analysis of what drives worker engagement and shift fulfillment
2. **Supply-Demand Balance**: Assessment of marketplace equilibrium across time slots
3. **Price Sensitivity**: Evaluation of how rates affect worker behavior
4. **Lead Time Impact**: Analysis of how posting timing affects fill rates
5. **Worker Retention**: Patterns in worker engagement over time

## Usage Guide

1. **Navigation**: Use the wizard at the top to navigate between sections or click the "Continue" button at the bottom of each page
2. **Interactive Elements**: Hover over charts for detailed information, use dropdowns to filter data
3. **Code Transparency**: Expand code sections to view the underlying Python implementation
4. **Key Findings**: Look for highlighted boxes that emphasize important insights

## Deployment

For deployment, a simplified version (`deploy.py`) has been created that loads faster and requires fewer resources. Use this version when deploying to production environments:

```
streamlit run deploy.py --server.port 5000 --server.address 0.0.0.0
```

## Dependencies

- Python 3.8+
- Streamlit
- Pandas
- NumPy
- Matplotlib
- Plotly
- Seaborn

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data provided by Clipboard Health
- Built with Streamlit and Python data science libraries
- Deployed on Replit

---

*This project was created as a demonstration of data analysis capabilities and marketplace dynamics understanding.*
