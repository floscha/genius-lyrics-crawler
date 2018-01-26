"""Contains helper methods for building urls based on an artist/song name."""
import re
import unicodedata


def normalize_unicode(unicode_string):
    """Normalize unicode characters to their base form."""
    normalized_string = (unicodedata
                         .normalize('NFD', unicode_string)
                         .encode('ascii', 'ignore'))
    normalized_string = normalized_string.decode()
    return normalized_string


def parse_raw_string(raw_string):
    """Parse the raw string so that it can be used in an URL."""
    s = raw_string
    s = s.strip()
    s = s.lower()

    # Genius-specific modifications.
    s = s.replace('&', '-and-')
    s = s.replace('$', 's')

    # Normalize letters like e.g. french accents.
    s = normalize_unicode(s)
    # Replace spaces by dashes.
    s = s.replace(' ', '-')
    # Remove stuff in brackets (e.g. features).
    s = re.sub(r'\([\w\d-]+\)', '', s)
    # Remove remaining illegal chars.
    s = re.sub(r'[^\w\d-]+', '', s)
    # Replace multiple dashes by a single one.
    s = re.sub(r'-+', '-', s)
    # Remove leading and closing dashes.
    s = s.strip('-')

    return s


def build_genius_url(raw_artist_name, raw_song_name):
    """Build the link to the lyrics of a given song on genius.com."""
    base_url = 'https://genius.com/'
    suffix = 'lyrics'

    parsed_artist_name = parse_raw_string(raw_artist_name)
    parsed_song_name = parse_raw_string(raw_song_name)

    generated_link = (base_url
                      + parsed_artist_name
                      + '-'
                      + parsed_song_name
                      + '-'
                      + suffix)
    return generated_link
