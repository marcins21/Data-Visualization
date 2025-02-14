import streamlit as st
import pandas as pd
import charts
from spotifySt import *
import spotipy

st.set_page_config(layout='wide')

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        print(f"\n[FAILED] path '{path}' doesn't exist!")

options_for_sidebar = st.sidebar.selectbox("Wybierz dane do wyświetlenia", ["Albums", "Artists"])

class Album:
    def __init__(self, ars_name, rel_date, gens, descs, avg_rat, duration_ms, album):
        self.ars_name = ars_name
        self.rel_date = rel_date
        self.gens = gens
        self.descs = descs
        self.avg_rat = avg_rat
        self.duration_ms = duration_ms
        self.album = album
        self.albums = []

    def add_album(self, album):
        self.albums.append(album)


class AlbumCollector:
    def __init__(self):
        self.albums = []

    def add_album(self, album):
        self.albums.append(album)

    def get_albums(self, reverse_input=False, number_of_albums_to_show=1):
        if len(self.albums) > 0:
            # sortowanie po avr_rat
            self.albums.sort(key=lambda x: x.avg_rat, reverse=reverse_input)
            return self.albums[:number_of_albums_to_show]
        else:
            st.write(f"There is no albums")


def display_album(album, idx, total_albums):
    with st.expander(label=f"Top {idx + 1}:", expanded=True):

        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            charts.spotifyProfilePicture(album.ars_name)

        with col2:
            st.subheader(f"Album: {album.album}")
            st.write(f"Artist: {album.ars_name}")
            st.write(f"Release Date: {album.rel_date}")
            st.write(f"Genres: {album.gens}")
            st.write(f"Description: {album.descs}")
            st.write(f"Average Rating: {album.avg_rat}")
            st.write(f"Duration : {album.duration_ms / 100}")
        with col3:
            charts.spotifyAlbumPicture(album.ars_name)
            
            
# def get_available_genres():
#     genres = sp.recommendation_genre_seeds()['genres']
#     return genres

# def get_top_artists(limit=None, genre=None):
#     if genre:
#         query = f"year:2022 genre:{genre}"
#     else:
#         query = "year:2022"

#     results = sp.search(q=query, type='artist', limit=limit)
#     artists = results['artists']['items']
#     top_artists = []
#     for artist in artists:
#         ars_name = artist['name']
#         genres = artist['genres']
#         popularity = artist['popularity']
#         image_url = artist['images'][0]['url'] if artist['images'] else None

#         top_artists.append({
#             'ars_name': ars_name,
#             'genres': genres,
#             'popularity': popularity,
#             'image_url': image_url
#         })
#     top_artists = sorted(top_artists, key=lambda x: x['popularity'], reverse=True)
#     return top_artists

def run():
    data = load_data("csvs/Top5000_album_rating.csv")
    if options_for_sidebar == "Albums":
        st.title("Top Albums")
        num_albums = st.number_input("Enter the number of albums to display:", min_value=1, max_value=len(data),
                                     value=5,
                                     step=1)

        album_collector = AlbumCollector()
        for index, row in data.iterrows():
            album = Album(row['ars_name'], row['rel_date'], row['gens'], row['descs'], row['avg_rat'],
                          row['duration_ms'],
                          row['album'])
            album_collector.add_album(album)

        # reverse_input -  True od najwiekszych ocen False - od najmniejszych ocen, number_of_albums_to_show - ile albumów wyswietlac
        sorted_albums_by_avr = album_collector.get_albums(reverse_input=True, number_of_albums_to_show=num_albums)

        #wyswietlanie rekordów
        for idx, album in enumerate(sorted_albums_by_avr):
            display_album(album, idx, num_albums)

    elif options_for_sidebar == "Artists":
        st.title("Top Artists")
        num_artists = st.number_input("Enter the number of artists to display:", min_value=1, max_value=50, value=10,
                                      step=1)

        available_genres = get_available_genres()

        genre_input = st.selectbox("Select a genre:", available_genres)

        top_artists = get_top_artists(limit=num_artists, genre=genre_input)

        if top_artists == None:
            return st.header("There is no such an artist ")
        # Liczba kolumn expanderów w każdym wierszu
        num_cols = 2
        # Obliczenie liczby wierszy
        num_rows = (len(top_artists) + num_cols - 1) // num_cols

        for row in range(num_rows):
            expander_row = st.columns(num_cols, gap="medium")

            for col in range(num_cols):
                idx = row * num_cols + col
                if idx < len(top_artists):
                    artist = top_artists[idx]
                    with expander_row[col]:
                        with st.expander(label=f"Top: {idx + 1}", expanded=True):
                            col1, col2 = st.columns([2, 7])

                            with col1:
                                if artist['image_url']:
                                    st.image(artist['image_url'])

                            with col2:
                                artist_genres = artist['genres']
                                genres_string = ", ".join(artist_genres)
                                st.header(f"Artist: {artist['ars_name']}")
                                st.write(f"Genres: {genres_string}")
                                st.write(f"Popularity: {artist['popularity']}")

run()
