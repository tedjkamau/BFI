# BFI Data Engineer Task: Enhanced Box Office Data Visualization

## Overview

This project is a small-scale demo designed to enhance the BFI weekly box office release data. The goal is to make the data more engaging, accessible, and informative by integrating additional data from external sources and presenting it through an interactive dashboard.

## Features

- **Data Integration with TMDB API:**
  - Retrieves movie posters, descriptions, genres, trailers, runtimes, ratings, and release dates.
- **Interactive Dashboard with Streamlit:**
  - Allows users to explore the box office data for the top 15 UK films, filter by title, and view detailed information about each film.
- **Data Visualization:**
  - Visualizes box office trends, including week-over-week gross changes and total gross.

## Prerequisites

- Python 3.8+
- An API key from [TMDB](https://www.themoviedb.org/) (The Movie Database)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
2. **Install dependencies**: Install all required Python linraries using the provided `requirements.txt` file:
   ```bash
   pip install -r requirements.txt

# Running the Scripts

1. Running `BFI Data.ipynb` to Fetch and Process Data
   The `BFI Data.ipynb` script fetches adn processes box office data from Box Office Mojoand enriches it with additional details from the TMDB API.
   
   The script will:
   
     - Read and clean the BFI box office data.
   
     - Fetch movie details from the TMDB API.
   
     - Save the gross data to `gross.csv` from Box Office Mojo after being scrapped.
   
     - Save enriched data to `movie_data.csv` from TMDB

2. Running `main.py` to Launch the Interacitve Dashboard

   The `main.py` script uses Streamlit to create an interactive dashbpard that visualises the box office data.

   **Step by step instructions:**

     1. Ensure `gross.csv` and `movie_data.csv` has been generated by running `BFI Data.ipynb`.
  
     2. Run the Streamlit app:
        ```bash
        streamlit run main.py
  
      3. Open the URL provided by Streamlit in your browser if automatically opened.
  
   **Features of the Dashboard:**
     1. Select a movie to view its details, including the poster, description, genres trailer and box office perfromance.
  
     2. Visualise box office trends using line and bar charts.

**File Structure**
1. `BFI Data.ipynb` - Contains the script for data scraping, API intergration and data processing.
2. `main.py` - Hosts the Streamlit app for data visualisation and user interaction.
3. `requirements.txt` - Lists all the Python dependencies required to run the scripts.

**Further Development**
1. Integrate addional data sources(i.e. Rotten Tomatoes, IMDB).
2. Implement dynamic data fetching based on user-selected dates.
3. Add more visualisations for deeper trend analysis. 
