import streamlit as st
import pandas as pd
import seaborn as sns
from datetime import datetime, timedelta
import requests
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

#Future modification for dates to be dynamic based on the users entry date 
# Currently will show the previous weekend dates only

# figures_string = f"{(datetime.today() - timedelta(days=(datetime.today().weekday() - 4) % 7 + 7)).strftime('%d/%m/%Y')} - {(datetime.today() - timedelta(days=(datetime.today().weekday() - 4) % 7 + 5)).strftime('%d/%m/%Y')}"

#Modification where a date can be selected by user and a function will scrape the data from Box Office Mojo and T


#BFI link 
bfi = "https://www.bfi.org.uk/"

st.markdown(
    f"""
    <a href="{bfi}">
        <img src="https://imgs.search.brave.com/JIBPuINvze6trCmeJscd36Jt49Z8Ms7WN_UmqLJUHUE/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly91cGxv/YWQud2lraW1lZGlh/Lm9yZy93aWtpcGVk/aWEvZW4vdGh1bWIv/NS81YS9Ccml0aXNo/X0ZpbG1fSW5zdGl0/dXRlX2xvZ28uc3Zn/LzUxMnB4LUJyaXRp/c2hfRmlsbV9JbnN0/aXR1dGVfbG9nby5z/dmcucG5n" style="width:100px;height:100px;">
    </a>
    """,
    unsafe_allow_html=True,
)


#Streamlit title
st.title(f'Weekend box office figures for 09/08/2024 - 11/08/2024')

#Streamlit header
st.header('Each week the BFI publishes box office figures for the top 15 films released in the UK, all other British releases and newly-released films.')

#Streamlit subheader
st.subheader('The figures cover box offices grosses in pounds sterling, Friday to Sunday, and show the performance of each film compared to the previous week and its total UK box office gross since release.')

#import data 
movies = pd.read_csv('movie_data.csv')

# Movie selection dropdown
selected_movie = st.selectbox(
    'Select a movie title:',
    options=movies['Title'].unique()
)

# Filter the DataFrame to get the selected movie's details
movie_details = movies[movies['Title'] == selected_movie].iloc[0]

# Base URL for TMDb images
base_url = "https://image.tmdb.org/t/p/w185"


# Create two columns: One for the poster and one for the movie information
col1, col2 = st.columns([1, 2])

with col1:
    # Display the poster image from TMDb
    st.image(f"{base_url}{movie_details['Poster']}", caption=selected_movie, width=200)

with col2:
    #Display movie 
    st.write(movie_details['Overview'])
    st.write("### Movie Details")
    col2_1, col2_2 = st.columns(2)

    with col2_1:
        st.write(f'Release Date: {movie_details["Release Year"]}')

        weeks_since_release = (datetime.today() - datetime.strptime(movie_details['Release Year'], '%Y-%m-%d')).days // 7
        st.write(f'Weeks since release: {weeks_since_release}')
    
    with col2_2:
        st.write(f'Genres: {movie_details["Genres"]}')
        st.write(f'Rating: {movie_details["Rating"]} ⭐')
# Display the trailer
st.video(movie_details['Trailer'],autoplay=False)



# Plot the box office figures
st.write("### Box Office Figures")

gross = pd.read_csv('gross.csv')
gross = gross[gross['Film'] == selected_movie]

st.subheader(f'Box office figures for {selected_movie}')



# Loop through each unique film
for film in gross['Film'].unique():
    # Filter data for the specific film and sort by date
    film_data = gross[gross['Film'] == film].sort_values(by='Weekend Since Release',ascending=True)

    # Calculate the week-over-week gross change
    film_data['Gross Change'] = film_data['Weekend Gross'].diff().fillna(0)
        # Display the total gross for each film
    total_gross = film_data['Weekend Gross'].sum()
    st.markdown(
        f"""
        <div style="
            display: inline-block;
            padding: 10px 20px;
            border-radius: 30px;
            background-color: #00cc99;
            color: white;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        ">
            Total Gross for {film}: £{total_gross:,.2f}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Line chart for Weekend Gross
    fig1,ax1 = plt.subplots(figsize = (10,5))
    sns.lineplot(data=film_data, x='Date', y='Weekend Gross', ax=ax1, marker='o', color='b')
    ax1.set_title(f'Box Office Figures for {film}')
    ax1.set_ylabel('Gross (£)')
    ax1.set_xlabel('Week')

    # Bar chart for Week-over-Week Gross Change
    fig2,ax2 = plt.subplots(figsize = (10,5))
    sns.barplot(data=film_data, x='Date', y='Gross Change', ax=ax2, palette='RdYlGn', dodge=False)
    ax2.set_title(f'Week-over-Week Gross Change for {film}')
    ax2.set_ylabel('Gross Change (£)')
    ax2.set_xlabel('Week')

    # Adjust plot layout
    plt.tight_layout()

    cont1, cont2 = st.columns(2)

    with cont1:
        st.pyplot(fig1)

    with cont2:
        st.pyplot(fig2)
    
    # Add a dataframe for the box office figures
    st.write(film_data)
    


