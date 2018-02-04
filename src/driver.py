import sys

from genius_crawler import scrape_songs


def print_usage():
    print("Usage: python driver.py [all | popular | validate]")


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print_usage()
        sys.exit(1)

    popular_only_flag = args[0]
    if popular_only_flag == 'validate':
        scrape_songs(popular_only=True,
                     letters=list('abc'),
                     artists_per_letter=3,
                     pages_per_artist=1,
                     songs_per_page=3)
        sys.exit(0)
    elif popular_only_flag == 'popular':
        popular_only = True
    elif popular_only_flag == 'all':
        popular_only = False
    else:
        print_usage()
        sys.exit(1)

    scrape_songs(popular_only=popular_only)
