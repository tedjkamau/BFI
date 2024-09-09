import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

def get_top_films(date):
    """
    Get the top 15 films from the Box Office Mojo weekend page for the given date.

    Args:
    date (str or datetime): The date to fetch the top films for.

    Returns:
    dict: A dictionary with film names as keys and their URLs as values.
    """
    # Convert the date to a datetime object and extract year and week
    date = pd.to_datetime(date)
    year = date.year
    week = date.isocalendar().week
    #When  a week is less than 10 the website will not be able to find the data hence we need to add a 0 in front of the week number
    if week < 10:
        week = '0' + str(week)

    # Construct the Box Office Mojo URL, data will be from the UK area 
    '''
    Args:
    Date has to be in the format of 'YYYY-MM-DD'
    
    Date year has to be greater than 2001-01-01
    '''
    url = f'https://www.boxofficemojo.com/weekend/{year}W{week}/?area=GB&ref_=bo_wey_table_3'

    # Get the response from the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table containing film data
    film_links = {}
    films_table = soup.find('table')

    # Extract film names and links
    if films_table:
        rows = films_table.find_all('tr')[1:16]  # Process the first 15 rows, skipping the header
        for row in rows:
            film_cell = row.find('a')
            if film_cell and 'href' in film_cell.attrs:
                film_name = film_cell.text.strip()
                film_link = 'https://www.boxofficemojo.com' + film_cell['href']
                film_links[film_name] = film_link

    return film_links

def get_film_data(film_link):
    """
    Fetch detailed data for a specific film from its Box Office Mojo page, including distributor.

    Args:
    film_link (str): The URL of the film's page.

    Returns:
    DataFrame: A DataFrame containing the film's weekend grossing data and distributor.

    Improvements:
    Recalculate the Gross Change/Week and Change in Theatres column since we have some missing values
    
    """
    # Request the film page
    film_response = requests.get(film_link)
    film_soup = BeautifulSoup(film_response.content, 'html.parser')

    # Find the table containing weekend grossing data
    table = film_soup.find('table')

    # Initialize an empty DataFrame for film data
    film_data = pd.DataFrame()

    # Extract the distributor information
    distributor = ''
    distributor_element = film_soup.find(text='Distributor')
    if distributor_element:
        distributor = distributor_element.find_next('span').text.strip()

    if table:
        # Extract data from the table
        data = [
            [col.text.strip() for col in row.find_all('td')]
            for row in table.find_all('tr')[1:]  # Skip the header row
        ]

        # Create a DataFrame from the extracted data
        film_data = pd.DataFrame(data, columns=['Date', 'Rank', 'Weekend Gross', 'Gross Change/Week', 'Theater', 'Change', 'Average', 'To Date', 'Weekend Since Release', 'Been Preprocessed'])

        # Drop the unnecessary 'Been Preprocessed' column
        film_data.drop(columns=['Been Preprocessed'], inplace=True)

        # Add distributor information to the DataFrame
        film_data['Distributor'] = distributor
        
        # In the distributor column, remove the .See full company information from the string
        film_data['Distributor'] = film_data['Distributor'].str.replace('.See full company information', '')


        # Convert numeric columns and handle non-numeric characters
        for col in ['Weekend Gross', 'To Date', 'Average']:
            film_data[col] = pd.to_numeric(film_data[col].str.replace(r'[^\d.]', '', regex=True), errors='coerce')

        # Convert to GBP using the exchange rate
        exchange_rate = 0.78
        for col in ['Weekend Gross', 'To Date', 'Average']:
            film_data[col] *= exchange_rate

    return film_data

# # Example usage:
# Get the top films for a given date
top_films = get_top_films('2024-01-01')

# Select a specific film to fetch its data
if top_films:
    selected_film_name = list(top_films.keys())[0]  # Example: select the first film
    selected_film_link = top_films[selected_film_name]
    film_data = get_film_data(selected_film_link)
    film_data['Film'] = selected_film_name
    print(film_data)



'''
The backend for Box Mojo works sucessfully and the data is being fetched from the website.
The data is then cleaned and converted to GBP using the exchange rate
'''





def get_movie_details(film, api_key=None):
    """
    Fetch detailed movie information from the TMDB API.
    
    Args:
    film (str): The name of the film to search for.
    api_key (str): The API key for TMDB API. If not provided, will look for an environment variable.

    Returns:
    dict: A dictionary containing detailed information about the movie.
    """
    # Check API key
    api_key = "9121de210a58fbaa7cd5f0654a7ec8d9" or os.getenv('TMDB_API_KEY')
    if not api_key:
        raise ValueError("API key is required. Set it as an argument or an environment variable 'TMDB_API_KEY'.")

    # Base URL for the API
    base_url = "https://api.themoviedb.org/3"

    try:
        # Fetch genre details for movies
        movies_genre_url = f"{base_url}/genre/movie/list?api_key={api_key}"
        movies_genre_response = requests.get(movies_genre_url)
        movies_genre_response.raise_for_status()
        movies_genre_data = movies_genre_response.json()
        movie_genres = {genre['id']: genre['name'] for genre in movies_genre_data.get('genres', [])}

        # Fetch movie details
        movies_url = f"{base_url}/search/movie?api_key={api_key}&query={film}"
        search_response = requests.get(movies_url)
        search_response.raise_for_status()
        search_data = search_response.json()

        # Check if the search results are not empty
        if not search_data['results']:
            return {'Error': 'No movie found with the provided title.'}
        
        # Get the most relevant result
        first_result = search_data['results'][0]
        content_id = first_result.get('id')
        content_genres = [movie_genres.get(genre_id, 'Unknown') for genre_id in first_result.get('genre_ids', [])]
        
        # Fetch additional details, trailer, reviews, and recommendations
        details_url = f"{base_url}/movie/{content_id}?api_key={api_key}"
        trailer_url = f"{base_url}/movie/{content_id}/videos?api_key={api_key}"
        reviews_url = f"{base_url}/movie/{content_id}/reviews?api_key={api_key}"
        recommendations_url = f"{base_url}/movie/{content_id}/recommendations?api_key={api_key}"

        details_response = requests.get(details_url)
        trailer_response = requests.get(trailer_url)
        reviews_response = requests.get(reviews_url)
        recommendations_response = requests.get(recommendations_url)

        details_response.raise_for_status()
        trailer_response.raise_for_status()
        reviews_response.raise_for_status()
        recommendations_response.raise_for_status()

        # Process additional data
        content_infos = details_response.json()
        trailer_data = trailer_response.json()
        reviews_data = reviews_response.json()
        recommendations_data = recommendations_response.json()

        # Find the most relevant trailer
        trailer_key = next((trailer.get('key') for trailer in trailer_data.get('results', []) if trailer.get('type') == 'Trailer' and 'official' in trailer.get('name', '').lower()), 'N/A')
        trailer_link = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key != 'N/A' else 'N/A'

        # Extract reviews
        top_reviews = [review.get('content', 'No content') for review in reviews_data.get('results', [])[:10]]

        # Extract recommendations
        recommendations_info = [{
            'Title': rec.get('title'),
            'Poster': rec.get('poster_path'),
            'Content ID': rec.get('id')
        } for rec in recommendations_data.get('results', [])]

        # Construct the final movie details
        content_info = {
            'Title': first_result.get('title'),
            'Content ID': content_id,
            'Poster': first_result.get('poster_path'),
            'Backdrop': first_result.get('backdrop_path'),
            'Overview': first_result.get('overview'),
            'Trailer': trailer_link,
            'Genres': ', '.join(content_genres),
            'Runtime (minutes)': content_infos.get('runtime', 'N/A'),
            'Rating': round(first_result.get('vote_average', 0), 2),
            'Release Year': first_result.get('release_date', 'N/A'),
            'Origin Country': next((company.get('origin_country') for company in content_infos.get('production_companies', [])), 'N/A'),
            'Reviews': top_reviews,
            'Recommendations': recommendations_info
        }

        return content_info

    except requests.exceptions.RequestException as e:
        return {'Error': f"Failed to fetch movie details: {e}"}


import pandas as pd
from datetime import datetime

# Set a specific date for the weekend you want to analyze
date_to_analyze = '2024-01-01'  # Example: Use any date in 'YYYY-MM-DD' format

# Step 1: Scrape Box Office Mojo for the top 15 films of the specified weekend
print(f"Fetching top films for the weekend of {date_to_analyze}...")

# Get the top films for the specified date
top_films = get_top_films(date_to_analyze)

# Display the list of top films
if top_films:
    print("Top 15 films for the weekend:")
    for index, (film_name, film_link) in enumerate(top_films.items(), start=1):
        print(f"{index}. {film_name}")

    # Ask the user to select a film by entering a number
    selected_index = int(input(f"Enter the number of the film you want to analyze (1-{len(top_films)}): "))

    # Validate the selected index
    if 1 <= selected_index <= len(top_films):
        selected_film_name = list(top_films.keys())[selected_index - 1]
        selected_film_link = top_films[selected_film_name]

        # Step 2: Fetch grossing data for the selected film
        print(f"Fetching Box Office data for {selected_film_name}...")

        film_data = get_film_data(selected_film_link)
        film_data['Film'] = selected_film_name  # Add film name to the DataFrame

        print(f"Grossing data for {selected_film_name}:")
        print(film_data)

        # Step 3: Fetch additional details from TMDB for the selected film
        print(f"Fetching additional details from TMDB for {selected_film_name}...")

        tmdb_data = get_movie_details(selected_film_name)

        # Combine Box Office Mojo data with TMDB data
        combined_data = film_data.assign(**tmdb_data)

        # Display the final combined data
        print(f"Combined data for {selected_film_name}:")
        print(combined_data)
    else:
        print("Invalid selection. Please choose a number from the list.")
else:
    print("No top films found for the specified weekend.")
