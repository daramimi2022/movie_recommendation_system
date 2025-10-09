import pickle
import streamlit as st
import requests
import gdown
import os

# ✅ Correct Google Drive file IDs
MOVIE_LIST_ID = "1sK8ev58VOHHeNuiyvAIlxIpH6j8-jUln"
SIMILARITY_ID = "1uWEmk1IuWDhLQdlA0AXWHe-9QylpPA3t"

# 📥 Download artifacts from Google Drive if not already present
if not os.path.exists("movie_list.pkl"):
    gdown.download(f"https://drive.google.com/uc?id={MOVIE_LIST_ID}", "movie_list.pkl", quiet=False)

if not os.path.exists("similarity.pkl"):
    gdown.download(f"https://drive.google.com/uc?id={SIMILARITY_ID}", "similarity.pkl", quiet=False)

# 📂 Load artifacts
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=217ac9198152df3a566eb6c1ab840091"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    return f"https://image.tmdb.org/t/p/w500/{poster_path}"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movies_name = []
    recommended_movies_poster = []
    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies_poster.append(fetch_poster(movie_id))
        recommended_movies_name.append(movies.iloc[i[0]].title)

    return recommended_movies_name, recommended_movies_poster

# 🖼️ Streamlit UI
st.header('🎬 Movies Recommendation System Using Machine Learning')
movie_list = movies['title'].values
selected_movie = st.selectbox('Type or select a movie to get recommendation', movie_list)

if st.button('Show recommendation'):
    recommended_movies_name, recommended_movies_poster = recommend(selected_movie)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.text(recommended_movies_name[i])
            st.image(recommended_movies_poster[i])
