# Genius Lyrics Crawler

A simple crawler to store lyrics from [Genius](http://genius.com) in MongoDB.

## Features
- [x] Scrape all songs
- [x] Scrape popular songs
- [ ] Simple CLI
- [ ] Concurrent crawling
- [ ] Use multiple crawler instances

## Usage
The easiest way to run the crawler by using the provided Docker image.

1. Build the image:
```
$ docker build . -t genius-lyrics-crawler
```

2. Run the image:
```
$ docker run genius-lyrics-crawler
```
