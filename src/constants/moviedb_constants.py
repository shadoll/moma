"""Movie database identifier constants.

This module defines movie and TV database services (TMDB, IMDB, Trakt, TVDB)
and their identifier patterns.
"""

MOVIE_DB_DICT = {
    "tmdb": {
        "name": "The Movie Database (TMDb)",
        "description": "Community built movie and TV database",
        "url": "https://www.themoviedb.org/",
        "patterns": ["tmdbid", "tmdb", "tmdbid-", "tmdb-"],
    },
    "imdb": {
        "name": "Internet Movie Database (IMDb)",
        "description": "Comprehensive movie, TV, and celebrity database",
        "url": "https://www.imdb.com/",
        "patterns": ["imdbid", "imdb", "imdbid-", "imdb-"],
    },
    "trakt": {
        "name": "Trakt.tv",
        "description": "Service that integrates with media centers for scrobbling",
        "url": "https://trakt.tv/",
        "patterns": ["traktid", "trakt", "traktid-", "trakt-"],
    },
    "tvdb": {
        "name": "The TV Database (TVDB)",
        "description": "Community driven TV database",
        "url": "https://thetvdb.com/",
        "patterns": ["tvdbid", "tvdb", "tvdbid-", "tvdb-"],
    },
}
