# Sports Analytics Dashboard

## Introduction
The Sports Analytics Dashboard is designed to provide insights and visualizations related to sports data, leveraging the power of data analytics and visualization. Built using Python and a range of powerful libraries, this dashboard allows users to interact with data in real-time, gaining insights into player performance, match statistics, team comparisons, and other analytics relevant to sports enthusiasts, analysts, and professionals.

## Objective
The primary objective of this project is to create a dynamic, user-friendly sports analytics platform that:
- Enables real-time data visualization and analysis.
- Provides meaningful insights into various aspects of sports performance.
- Supports informed decision-making for sports analysts, coaches, and fans.

## Scope of the Project
- **Data Import and Preprocessing**: Loading and cleaning data from various sources to prepare it for analysis.
- **Statistical Analysis and Visualization**: Using statistical methods and visualizations to highlight key trends and insights.
- **Real-time Interactivity**: Allowing users to explore data through interactive plots and filters.

## Requirements

### Software Requirements
- **Python**: Version 3.8 or higher
- **IDE/Editor**: Visual Studio Code, PyCharm, or Jupyter Notebook (for development and testing)

### Python Libraries
- `Streamlit` (v0.8): Used for building interactive dashboards and web applications.
- `pandas` (v1.3.3): Essential for data manipulation and analysis.
- `numpy` (v1.21.2): Provides support for large, multi-dimensional arrays and matrices.
- `json5` (v0.9.5): Useful for parsing JSON data in a flexible manner.
- `matplotlib` (v3.4.3): Base library for static data visualizations.
- `plotly` (v5.3.1): For interactive graphing and visualization.
- `beautifulsoup4` (v4.10.0): Helps in web scraping and extracting data from websites if needed.

### Data Requirements
The dashboard requires data on sports events, team statistics, player performance, etc., typically gathered from open APIs or web-scraped sources.

## Project Structure
- **HomePage.py**: Contains the main interface for the dashboard, including navigation and an overview of key metrics.
- **NHL.py**: Houses the specific functionalities and visualizations for hockey analytics, such as player statistics, match insights, and league comparisons.
- **3_🏒_NHL.py**: Implements additional hockey-specific data processing and visualization, focusing on team and player metrics.

## Functionalities and Features

### Data Processing and Analysis
- **Data Cleaning**: Removing or handling missing values, outliers, and ensuring data consistency.
- **Data Transformation**: Normalizing or scaling data for accurate analysis.

### Visualization and Interaction
- **Static Visualizations (Matplotlib)**: Bar charts, line plots, and heatmaps to show trends and distributions.
- **Interactive Visualizations (Plotly)**: Dynamic charts allowing users to zoom in, filter data, and explore insights in real-time.
- **Filtering and Sorting**: Options to filter by team, player, season, and more.

### User Interface
- **Streamlit-based Layout**: A clean, organized layout enabling easy navigation between different sections of the dashboard.
- **Navigation Panel**: Allows users to switch between different sports, teams, and analysis types.

## Implementation

### Data Collection
Data was collected through APIs and/or web scraping using BeautifulSoup.

### Data Preprocessing
Data pre-processing steps included removing inconsistencies, normalizing values, and creating derived metrics for in-depth analysis.

## Getting Started
To get started with the Sports Analytics Dashboard, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/narthparang/sports-statistic-dashboard.git
   cd sports-statistic-dashboard
