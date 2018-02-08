import argparse

from genius_crawler import scrape_song
from genius_crawler import scrape_songs
from genius_crawler import scrape_songs_of_artist


def cli():
    # Read and parse command line arguments.
    parser = argparse.ArgumentParser(description='Driver program to ' +
                                     'initiate the scraping process')
    target_choices = ['all', 'popular', 'artist', 'song']
    parser.add_argument('target', choices=target_choices,
                        help='defines wether all song, only popular ' +
                             'songs, song from a single artist, or only a ' +
                             'single song should be scraped')
    # Take letters of type `list` so that 'abc' becomes ['a', 'b', 'c'].
    parser.add_argument('-l', '--letters', type=list,
                        help='only scrape songs from artists beginning ' +
                             'with one of the specified letters')
    parser.add_argument('-apl', '--artists_per_letter', type=int,
                        help='number of artist per letter to scrape')
    parser.add_argument('-ppa', '--pages_per_artist', type=int,
                        help='number of pages per per to scrape')
    parser.add_argument('-spp', '--songs_per_page', type=int,
                        help='number of songs per page to scrape')
    parser.add_argument('-a', '--artist',
                        help='the name of the artist to scrape')
    parser.add_argument('-t', '--title',
                        help='the title of the song to scrape')
    args = parser.parse_args()

    # Call crawler based on target.
    if args.target in ['all', 'popular']:
        scrape_songs(popular_only=args.target == 'popular',
                     letters=args.letters,
                     artists_per_letter=args.artists_per_letter,
                     pages_per_artist=args.pages_per_artist,
                     songs_per_page=args.songs_per_page)
    elif args.target == 'artist':
        if args.artist:
            scrape_songs_of_artist.delay(
                artist_name=args.artist,
                pages_per_artist=args.pages_per_artist,
                songs_per_page=args.songs_per_page
            )
        else:
            raise ValueError("The --artist parameter has to be set when " +
                             "using 'artist' as target")
    elif args.target == 'song':
        if args.artist and args.title:
            scrape_song.delay(artist=args.artist, title=args.title)
        else:
            raise ValueError("Both --artist and --title parameters have to " +
                             "be set when using 'song' as target")


if __name__ == '__main__':
    cli()
