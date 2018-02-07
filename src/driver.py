import argparse

from genius_crawler import scrape_songs


def cli():
    # Read and parse command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('target', choices=['all', 'popular'],
                        help='defines wether all song or only popular ' +
                        'songs should be scraped')
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
    args = parser.parse_args()

    # Call crawler based on target.
    if args.target in ['all', 'popular']:
        scrape_songs(popular_only=args.target == 'popular',
                     letters=args.letters,
                     artists_per_letter=args.artists_per_letter,
                     pages_per_artist=args.pages_per_artist,
                     songs_per_page=args.songs_per_page)


if __name__ == '__main__':
    cli()
