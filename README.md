# Genius Lyrics Crawler

![alt text](./temporary_logo.png)

A simple crawler to store lyrics from [Genius](http://genius.com) in MongoDB.

## Features
- [x] Scrape all songs
- [x] Scrape popular songs
- [x] Simple CLI
- [x] Concurrent crawling
- [x] Use multiple crawler instances

## Usage
Using the provided [Docker Compose configuration](docker-compose.yml), the crawler can be run by using only two simple steps.

1. The infrastructure for the crawler (including Celery worker(s), MongoDB, and Fluentd) can be started using:
```
$ docker-compose up
```
By appending an additional `--scale worker=n` argument, _n_ instances of the Celery worker will be started, whereby the number of workers should depend on the computational power of your machine.

2. To start the scraping process, the driver program needs to be started like so:
```
$ docker-compose run driver
```
The driver program can thereby be used as follows:
```
usage: driver [-h] [-l LETTERS] [-apl ARTISTS_PER_LETTER]
              [-ppa PAGES_PER_ARTIST] [-spp SONGS_PER_PAGE] [-a ARTIST]
              [-t TITLE]
              {all,popular,artist,song}

Driver program to initiate the scraping process

positional arguments:
  {all,popular,artist,song}
                        defines wether all song, only popular songs, song from
                        a single artist, or only a single song should be
                        scraped

optional arguments:
  -h, --help            show this help message and exit
  -l LETTERS, --letters LETTERS
                        only scrape songs from artists beginning with one of
                        the specified letters
  -apl ARTISTS_PER_LETTER, --artists_per_letter ARTISTS_PER_LETTER
                        number of artist per letter to scrape
  -ppa PAGES_PER_ARTIST, --pages_per_artist PAGES_PER_ARTIST
                        number of pages per per to scrape
  -spp SONGS_PER_PAGE, --songs_per_page SONGS_PER_PAGE
                        number of songs per page to scrape
  -a ARTIST, --artist ARTIST
                        the name of the artist to scrape
  -t TITLE, --title TITLE
                        the title of the song to scrape
```
