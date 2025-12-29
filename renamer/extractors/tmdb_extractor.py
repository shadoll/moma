import json
import os
import time
import hashlib
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from ..secrets import TMDB_API_KEY, TMDB_ACCESS_TOKEN


class TMDBExtractor:
    """Class to extract TMDB movie information"""

    def __init__(self, file_path: Path, cache=None, ttl_seconds: int = 21600):
        self.file_path = file_path
        self.cache = cache
        self.ttl_seconds = ttl_seconds
        self._movie_db_info = None

    def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if valid"""
        if self.cache:
            return self.cache.get(f"tmdb_{cache_key}")
        return None

    def _set_cached_data(self, cache_key: str, data: Dict[str, Any]):
        """Store data in cache"""
        if self.cache:
            self.cache.set(f"tmdb_{cache_key}", data, self.ttl_seconds)

    def _make_tmdb_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make a request to TMDB API"""
        base_url = "https://api.themoviedb.org/3"
        url = f"{base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
            "accept": "application/json"
        }
        
        if params is None:
            params = {}
        params['api_key'] = TMDB_API_KEY

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            return None

    def _search_movie_by_title_year(self, title: str, year: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search for movie by title and optionally year"""
        cache_key = f"search_{title}_{year or 'no_year'}"
        
        # Check cache first
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached

        params = {'query': title}
        if year:
            params['year'] = year

        result = self._make_tmdb_request('/search/movie', params)
        if result and result.get('results'):
            movies = result['results']
            
            # If year provided, try exact match first
            if year:
                exact_matches = [m for m in movies if str(m.get('release_date', ''))[:4] == year]
                if exact_matches:
                    movie = exact_matches[0]
                else:
                    # Try ±1 year
                    year_int = int(year)
                    close_matches = [m for m in movies if abs(int(str(m.get('release_date', ''))[:4]) - year_int) <= 1]
                    if close_matches:
                        movie = close_matches[0]
                    else:
                        movie = movies[0]  # Fallback to first result
            else:
                movie = movies[0]  # No year filter, take first result
            
            # Cache the result
            self._set_cached_data(cache_key, movie)
            return movie
        
        return None

    def _get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed movie information by ID"""
        cache_key = f"movie_{movie_id}"
        
        # Check cache first
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached

        result = self._make_tmdb_request(f'/movie/{movie_id}')
        if result:
            # Cache the result
            self._set_cached_data(cache_key, result)
            return result
        
        return None

    def _extract_movie_db_from_filename(self) -> Optional[Tuple[str, str]]:
        """Extract movie database ID from filename (similar to FilenameExtractor.extract_movie_db)"""
        import re
        from ..constants import MOVIE_DB_DICT
        
        file_name = self.file_path.name
        
        # Look for patterns at the end of filename in brackets or braces
        # Patterns: [tmdbid-123] {imdb-tt123} [imdbid-tt123] etc.
        
        # Match patterns like [tmdbid-123456] or {imdb-tt1234567}
        pattern = r'[\[\{]([a-zA-Z]+(?:id)?)[-\s]*([a-zA-Z0-9]+)[\]\}]'
        matches = re.findall(pattern, file_name)
        
        if matches:
            # Take the last match (closest to end of filename)
            db_type, db_id = matches[-1]
            
            # Normalize database type
            db_type_lower = db_type.lower()
            for db_key, db_info in MOVIE_DB_DICT.items():
                if any(db_type_lower.startswith(pattern.rstrip('-')) for pattern in db_info['patterns']):
                    return (db_key, db_id)
        
        return None

    def _get_movie_info(self) -> Optional[Dict[str, Any]]:
        """Get movie information from TMDB"""
        if self._movie_db_info is not None:
            return self._movie_db_info

        # First, check if we have a TMDB ID in the filename
        movie_db = self._extract_movie_db_from_filename()
        if movie_db and movie_db[0] == 'tmdb':
            try:
                movie_id = int(movie_db[1])
                movie_data = self._get_movie_details(movie_id)
                if movie_data:
                    self._movie_db_info = movie_data
                    return movie_data
            except ValueError:
                pass  # Invalid ID format

        # If no TMDB ID or failed to get details, try searching by title/year
        # We need title and year from filename extraction
        from .filename_extractor import FilenameExtractor
        filename_extractor = FilenameExtractor(self.file_path)
        title = filename_extractor.extract_title()
        year = filename_extractor.extract_year()
        
        if title:
            movie_data = self._search_movie_by_title_year(title, year)
            if movie_data:
                self._movie_db_info = movie_data
                return movie_data

        self._movie_db_info = None
        return None

    def extract_tmdb_id(self) -> Optional[str]:
        """Extract TMDB ID"""
        movie_info = self._get_movie_info()
        if movie_info:
            return str(movie_info.get('id'))
        return None

    def extract_title(self) -> Optional[str]:
        """Extract TMDB title"""
        movie_info = self._get_movie_info()
        if movie_info:
            return movie_info.get('title')
        return None

    def extract_original_title(self) -> Optional[str]:
        """Extract TMDB original title"""
        movie_info = self._get_movie_info()
        if movie_info:
            return f"({movie_info.get('original_language')}) {movie_info.get('original_title')}"
        return None

    def extract_year(self) -> Optional[str]:
        """Extract TMDB release year"""
        movie_info = self._get_movie_info()
        if movie_info and movie_info.get('release_date'):
            return movie_info['release_date'][:4]
        return None

    def extract_tmdb_url(self) -> Optional[str]:
        """Extract TMDB movie URL"""
        movie_id = self.extract_tmdb_id()
        if movie_id:
            return f"https://www.themoviedb.org/movie/{movie_id}"
        return None

    def extract_duration(self) -> Optional[str]:
        """Extract TMDB runtime in minutes"""
        movie_info = self._get_movie_info()
        if movie_info and movie_info.get('runtime'):
            return str(movie_info['runtime'])
        return None

    def extract_popularity(self) -> Optional[str]:
        """Extract TMDB popularity"""
        movie_info = self._get_movie_info()
        if movie_info:
            return str(movie_info.get('popularity', ''))
        return None

    def extract_vote_average(self) -> Optional[str]:
        """Extract TMDB vote average"""
        movie_info = self._get_movie_info()
        if movie_info:
            return str(movie_info.get('vote_average', ''))
        return None

    def extract_overview(self) -> Optional[str]:
        """Extract TMDB overview"""
        movie_info = self._get_movie_info()
        if movie_info:
            return movie_info.get('overview')
        return None

    def extract_genres(self) -> Optional[str]:
        """Extract TMDB genres as codes"""
        movie_info = self._get_movie_info()
        if movie_info and movie_info.get('genres'):
            return ', '.join(genre['name'] for genre in movie_info['genres'])
        return None

    def extract_poster_path(self) -> Optional[str]:
        """Extract TMDB poster path"""
        movie_info = self._get_movie_info()
        if movie_info:
            return movie_info.get('poster_path')
        return None

    def extract_poster_image_path(self) -> Optional[str]:
        """Download and cache poster image, return local path"""
        poster_path = self.extract_poster_path()
        if not poster_path or not self.cache:
            return None
        
        cache_key = f"poster_{poster_path}"
        cached_path = self.cache.get_image(cache_key)
        if cached_path:
            return str(cached_path)
        
        # Download poster
        base_url = "https://image.tmdb.org/t/p/w500"  # Medium size
        url = f"{base_url}{poster_path}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image_data = response.content
            
            # Cache image
            local_path = self.cache.set_image(cache_key, image_data, self.ttl_seconds)
            return str(local_path) if local_path else None
        except requests.RequestException:
            return None
