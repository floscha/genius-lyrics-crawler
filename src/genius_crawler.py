from collections import namedtuple
import os
from string import ascii_lowercase

from bs4 import BeautifulSoup
from celery import Celery
import langdetect
from langdetect.lang_detect_exception import LangDetectException
from pymongo import MongoClient
import requests

from mongo_lyrics_repository import MongoLyricsRepository
from url_builder import build_genius_url
from url_builder import parse_raw_string


# Define Song data type.
Song = namedtuple('Song', ['artist', 'title', 'text', 'language'])

# Setup Celery with RabbitMQ as the broker.
broker_user = os.getenv('RABBITMQ_USER')
broker_pass = os.getenv('RABBITMQ_PASS')
assert broker_pass and broker_pass, "Both 'RABBITMQ_USER' and " + \
                                    "'RABBITMQ_PASS' have to be set in ENV"
app = Celery('genius_lyrics_crawler',
             broker='amqp://gavin:hooli@rabbitmq:5672')

# Setup repository to store lyrics in MongoDB.
repo = MongoLyricsRepository('mongodb', 27017)


def scrape_songs(popular_only=False,
                 letters=None,
                 artists_per_letter=None,
                 pages_per_artist=None,
                 songs_per_page=None):
    """Scrape songs from Genius for all letters."""
    print("Start scraping process...")

    letters = letters or ascii_lowercase
    for current_letter in letters:
        if popular_only:
            scrape_popular_artists_for_letter.delay(
                current_letter,
                artists_per_letter,
                pages_per_artist,
                songs_per_page
            )
        else:
            scrape_all_artists_for_letter(
                current_letter,
                artists_per_letter,
                pages_per_artist,
                songs_per_page
            )


@app.task
def scrape_popular_artists_for_letter(letter,
                                      artists_per_letter=None,
                                      pages_per_artist=None,
                                      songs_per_page=None):
    """Get all artist from Genius' popular page for the given letter."""
    url_template = 'https://genius.com/artists-index/%s'

    url = url_template % letter

    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html5lib')

    lists = soup.find_all('ul', class_='artists_index_list')
    list_ = lists[1]
    list_items = list_.find_all('li')
    artists = [li.a.text for li in list_items]

    for i, artist in enumerate(artists):
        if artists_per_letter and i >= artists_per_letter:
            break

        scrape_songs_of_artist.delay(artist,
                                     pages_per_artist,
                                     songs_per_page)


@app.task
def scrape_all_artists_for_letter(letter,
                                  artists_per_letter=None,
                                  pages_per_artist=None,
                                  songs_per_page=None):
    """Get all artist from Genius for the given letter."""
    url_template = 'https://genius.com/artists-index/%s/all?page=%d'
    # This header is necessary to not load the whole HTML page but only
    # the additional artists for page n.
    headers = {'x-requested-with': 'XMLHttpRequest'}

    i = 0
    current_page = 1
    while current_page:
        url = url_template % (letter, current_page)

        content = requests.get(url, headers=headers).text
        soup = BeautifulSoup(content, 'html5lib')

        list_items = soup.find_all('li')
        artists = [li.a.text for li in list_items]

        for artist in artists:
            if artists_per_letter and i >= artists_per_letter:
                break

            scrape_songs_of_artist.delay(artist,
                                         pages_per_artist,
                                         songs_per_page)
            i += 1

        next_page = int(soup.div.find('a', {'rel': 'next'}).text)
        current_page = next_page


def _get_artist_id_from_name(artist_name):
    """Get the Genius artist ID for the artist's name."""
    parsed_artist_name = parse_raw_string(artist_name)
    content = requests.get('https://genius.com/artists/%s'
                           % parsed_artist_name).text
    soup = BeautifulSoup(content, 'html5lib')

    meta_element = soup.find('meta', {'name': 'newrelic-resource-path'})
    artist_id = int(meta_element['content'].split('/')[-1])

    return artist_id


@app.task
def scrape_songs_of_artist(artist_name,
                           pages_per_artist,
                           songs_per_page):
    """Get all songs from the given artist."""
    artist_id = _get_artist_id_from_name(artist_name)

    url_template = 'https://genius.com/api/artists/%d/songs?page=%d'

    current_page = 1
    while current_page:
        print("Scraping page %d for artist '%s'..."
              % (current_page, artist_name))
        url = url_template % (artist_id, current_page)

        r = requests.get(url)
        json_response = r.json()['response']
        songs = json_response['songs']
        next_page = json_response['next_page']

        for i, song in enumerate(songs):
            if songs_per_page and i >= songs_per_page:
                break

            scrape_song.delay(song)

        if pages_per_artist and current_page > pages_per_artist:
            break

        current_page = next_page


@app.task
def scrape_song(song):
    """Scrape a single song."""
    artist = song['primary_artist']['name']
    title = song['title']
    text = scrape_lyrics(artist, title)
    if not text:
        return

    # Remove structural info like [Chorus].
    text = '\n'.join([line for line in text.split('\n')
                      if not line.startswith('[')])
    # Skip instrumentals that only contain [Instrumental].
    if not text:
        return

    try:
        language = langdetect.detect(text)
    except LangDetectException as lde:
        print("Language could not be detected for '%s - %s':\n%s"
              % (artist, title, lde))
        return

    song_obj = Song(artist, title, text, language)

    repo.insert_one(song_obj._asdict())


def scrape_lyrics(artist, title):
    """Scrape the lyrics for a given artist/song name."""
    url = build_genius_url(artist, title)
    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html5lib')

    if soup.find('div', class_='render_404'):
        print("No lyrics found for '%s - %s' on Genius (%s)"
              % (artist, title, url))
        return

    try:
        lyrics = soup.find('div', class_='lyrics').get_text().strip()
    except Exception as e:
        print("Error while scraping '%s - %s':\n%s"
              % (artist, title, e))
        return

    return lyrics