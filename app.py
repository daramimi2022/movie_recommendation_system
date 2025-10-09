import pickle
import streamlit as st
import requests
import gdown
import os
import base64

# ================================
# 🖼️ BACKGROUND IMAGE FUNCTION
# ================================
def add_bg_from_local(image_file):
    """Set background image from a local file using base64 encoding."""
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        /* Optional styling to make text readable on backgrounds */
        .stHeader, .stMarkdown, .stText, .stSelectbox label {{
            color: white;
            text-shadow: 1px 1px 3px black;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ Add your background image file here (place it in the same folder as this script)
add_bg_from_local("10179962.jpg")  # change to your file name

# ================================
# 📂 CONFIGURATION
# ================================
MOVIE_LIST_ID = "1sK8ev58VOHHeNuiyvAIlxIpH6j8-jUln"
SIMILARITY_ID = "1uWEmk1IuWDhLQdlA0AXWHe-9QylpPA3t"

MOVIE_FILE = "movie_list.pkl"
SIMILARITY_FILE = "similarity.pkl"

MOVIE_URL = f"https://drive.google.com/uc?id={MOVIE_LIST_ID}"
SIMILARITY_URL = f"https://drive.google.com/uc?id={SIMILARITY_ID}"

TMDB_API_KEY = "217ac9198152df3a566eb6c1ab840091"

# ================================
# 📥 HELPER FUNCTIONS
# ================================
def download_file_if_not_exists(url, filename):
    """Download file from Google Drive if it does not exist locally."""
    if not os.path.exists(filename):
        st.info(f"📥 Downloading {filename} ...")
        gdown.download(url, filename, quiet=False)
        st.success(f"✅ {filename} downloaded successfully!")

@st.cache_resource
def load_artifacts():
    """Load the movie and similarity pickle files."""
    download_file_if_not_exists(MOVIE_URL, MOVIE_FILE)
    download_file_if_not_exists(SIMILARITY_URL, SIMILARITY_FILE)
    movies = pickle.load(open(MOVIE_FILE, "rb"))
    similarity = pickle.load(open(SIMILARITY_FILE, "rb"))
    return movies, similarity

def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', None)
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return "https://via.placeholder.com/500x750?text=No+Image"

def recommend(movie, movies, similarity):
    """Get top 5 recommended movies and their posters."""
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_names = []
    recommended_posters = []
    for i in distances[1:6]:  # Skip the first because it's the same movie
        movie_id = movies.iloc[i[0]].movie_id
        recommended_names.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_names, recommended_posters

# ================================
# 🖼️ STREAMLIT UI
# ================================
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.header('🎬 Movies Recommendation System Using Machine Learning')

# Load movies and similarity
movies, similarity = load_artifacts()

# UI: Select movie
movie_list = movies['title'].values
selected_movie = st.selectbox('🎥 Type or select a movie to get recommendations', movie_list)

# Button: Show recommendation
if st.button('Show recommendation'):
    names, posters = recommend(selected_movie, movies, similarity)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.text(names[i])
            st.image(posters[i])

