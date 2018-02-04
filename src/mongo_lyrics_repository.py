import hashlib

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class MongoLyricsRepository(object):
    """A MongoDB-based repository to store song lyrics."""

    def __init__(self, host, port):
        """Initialize a new MongoLyricsRepository object."""
        client = MongoClient(host, port)

        db = client.mole
        self._lyrics = db.lyrics

    @staticmethod
    def _generate_song_id(song):
        string = '{}{}'.format(song.artist, song.title)
        bytes_ = string.encode('utf-8')
        generated_id = hashlib.sha256(bytes_).hexdigest()
        return generated_id

    def store_raw_lyrics(self, song):
        """Store a RawLyrics object to DB."""
        song_dict = song._asdict()
        song_id = MongoLyricsRepository._generate_song_id(song)

        mongo_document = dict({'_id': song_id}, **song_dict)

        try:
            inserted_id = self._lyrics.insert_one(mongo_document).inserted_id
            if inserted_id != song_id:
                raise Exception("Error while storing raw lyrics: " +
                                "Wrong inserted ID")
        except DuplicateKeyError:
            print("A song with the given key already exist. Update...")
            self._lyrics.replace_one({'_id': song_id}, mongo_document)

        return mongo_document
