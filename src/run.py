from collections import namedtuple
from string import ascii_lowercase
import sys

from bs4 import BeautifulSoup
from celery import Celery
import langdetect
from langdetect.lang_detect_exception import LangDetectException
from pymongo import MongoClient
import requests

from url_builder import build_genius_url
from url_builder import parse_raw_string


# Define Song data type.
Song = namedtuple('Song', ['artist', 'title', 'text', 'language'])

# Setup Celery with RabbitMQ as the broker.
app = Celery('genius_lyrics_crawler', broker='amqp://user:pass@rabbitmq:5672')

# Setup MongoDB connection.
client = MongoClient('mongodb', 27017)
db = client.mole
repo = db.lyrics


def scrape_songs(popular_only=False):
    """Scrape songs from Genius for all letters."""
    for current_letter in ascii_lowercase:
        if popular_only:
            artists = get_popular_artists_for_letter(current_letter)
        else:
            artists = get_all_artists_for_letter(current_letter)

        for current_artist in artists:
            song_generator = get_all_songs_for_artist(current_artist)

            for current_song in song_generator:
                yield current_song


def get_popular_artists_for_letter(letter):
    """Get all artist from Genius' popular page for the given letter."""
    url_template = 'https://genius.com/artists-index/%s'

    url = url_template % letter

    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html5lib')

    lists = soup.find_all('ul', class_='artists_index_list')
    list_ = lists[1]
    list_items = list_.find_all('li')
    artists = [li.a.text for li in list_items]

    return artists


def get_all_artists_for_letter(letter):
    """Get all artist from Genius for the given letter."""
    url_template = 'https://genius.com/artists-index/%s/all?page=%d'
    # This header is necessary to not load the whole HTML page but only
    # the additional artists for page n.
    headers = {'x-requested-with': 'XMLHttpRequest'}

    current_page = 1
    while current_page:
        url = url_template % (letter, current_page)

        content = requests.get(url, headers=headers).text
        soup = BeautifulSoup(content, 'html5lib')

        list_items = soup.find_all('li')
        artists = [li.a.text for li in list_items]

        yield artists

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


def get_all_songs_for_artist(artist_name, max_page=None):
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

        for song in songs:
            artist = song['primary_artist']['name']
            title = song['title']
            text = scrape_lyrics(artist, title)
            if not text:
                continue

            # Remove structural info like [Chorus].
            text = '\n'.join([line for line in text.split('\n')
                              if not line.startswith('[')])
            # Skip instrumentals that only contain [Instrumental].
            if not text:
                continue

            try:
                language = langdetect.detect(text)
            except LangDetectException as lde:
                print("Language could not be detected for '%s - %s':\n%s"
                      % (artist, title, lde))
                continue

            song_obj = Song(artist, title, text, language)

            yield song_obj

        if max_page and current_page > max_page:
            current_page = None
        else:
            current_page = next_page


def scrape_lyrics(artist, title):
    """Scrape the lyrice for a given artist/song name."""
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


def print_usage():
    print("Usage: python run.py [all | popular]")


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print_usage()
        sys.exit(1)

    popular_only_flag = args[0]
    if popular_only_flag == 'popular':
        popular_only = True
    elif popular_only_flag == 'all':
        popular_only = False
    else:
        print_usage()
        sys.exit(1)

    songs = scrape_songs(popular_only=popular_only)

    for song in songs:
        repo.insert_one(song._asdict())
