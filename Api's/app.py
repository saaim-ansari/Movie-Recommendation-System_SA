import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

st.set_page_config(layout="wide")

# Set up a session with retries
session = requests.Session()
retry = Retry(
    total=5,
    read=5,
    connect=5,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504)
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def get_poster(movie_id):
    try:
        json_file = session.get('https://api.themoviedb.org/3/movie/{}?api_key=a958ef580cc1af01ad3200dd4faf3c97&language=en-US'.format(movie_id))
        json_file.raise_for_status()
        data = json_file.json()
        return "http://image.tmdb.org/t/p/w500/" + data["poster_path"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster for movie ID {movie_id}: {e}")
        return None

def recommender(movie):
    lst = []
    movie_index = movies_tmdb[movies_tmdb['title'] == movie].index[0]
    distances_list = cosine_sim[movie_index]
    movie_list = sorted(list(enumerate(distances_list)), reverse=True, key=lambda x: x[-1])[1:11]
    movie_poster = []
    for j in movie_list:
        lst.append(movies_tmdb.iloc[j[0]].title)
        poster_url = get_poster(movies_tmdb.iloc[j[0]].movie_id)
        if poster_url:
            movie_poster.append(poster_url)
        else:
            movie_poster.append('')  # Add an empty string to maintain the list length
    return lst, movie_poster

movies_tmdb = pickle.load(open('movies_tmdb.pkl', 'rb'))
movies_tmdb = pd.DataFrame(movies_tmdb)

cosine_sim = pickle.load(open('cosine_sim.pkl', 'rb'))
cosine_sim = pd.DataFrame(cosine_sim)

st.title("Movie Recommender System")

movie_selected = st.selectbox(
    'Choose a movie you want recommendations on',
    movies_tmdb['title'].values
)

if st.button("Recommend"):
    recommendations, posters = recommender(movie_selected)

    cols = st.columns(4)
    for i in range(len(recommendations)):
        if posters[i]:  # Only display if there is a poster URL
            with cols[i % 4]:
                st.text(recommendations[i])
                st.image(posters[i], width=250)
