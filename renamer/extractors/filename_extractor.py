import re
from pathlib import Path
from collections import Counter
from ..constants import SOURCE_DICT, FRAME_CLASSES, MOVIE_DB_DICT
import langcodes


class FilenameExtractor:
    """Class to extract information from filename"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_name = file_path.name

    def _get_frame_class_from_height(self, height: int) -> str | None:
        """Get frame class from video height using FRAME_CLASSES constant"""
        for frame_class, info in FRAME_CLASSES.items():
            if height == info['nominal_height']:
                return frame_class
        return None

    def extract_title(self) -> str | None:
        """Extract movie title from filename"""
        # Find positions of year, source, and quality brackets
        year_pos = -1
        source_pos = -1
        quality_pos = -1
        paren_match = None
        dot_match = None
        
        # Find year position (either (YYYY) or .YYYY.)
        paren_match = re.search(r'\((\d{4})\)', self.file_name)
        if paren_match:
            year_pos = paren_match.start()
        else:
            dot_match = re.search(r'\.(\d{4})\.', self.file_name)
            if dot_match:
                year_pos = dot_match.start()
        
        # Find source position
        source = self.extract_source()
        if source:
            for alias in SOURCE_DICT[source]:
                match = re.search(r'\b' + re.escape(alias) + r'\b', self.file_name, re.IGNORECASE)
                if match:
                    source_pos = match.start()
                    break
        
        # Find quality bracket position (like [720p,ukr,eng])
        quality_match = re.search(r'\[[^\]]*(?:720p|1080p|2160p|480p|SD|HD|HDR)[^\]]*\]', self.file_name)
        if quality_match:
            quality_pos = quality_match.start()
        
        # Find the earliest position that's not at the beginning
        positions = [pos for pos in [year_pos, source_pos, quality_pos] if pos > 0]
        cut_pos = min(positions) if positions else -1
        
        # Extract title (everything before the cut position)
        if cut_pos > 0:
            title = self.file_name[:cut_pos].strip()
        else:
            # No delimiters found after position 0, take everything before the last dot
            title = self.file_name.rsplit('.', 1)[0].strip()
        
        # If year is at the beginning, remove it
        if year_pos == 0:
            if paren_match and paren_match.start() == 0:
                title = re.sub(r'^\(\d{4}\)\s*', '', title)
            elif dot_match and dot_match.start() == 0:
                title = re.sub(r'^\.\d{4}\.\s*', '', title)
        
        # Remove common prefixes that are not part of the title
        # Remove bracketed prefixes like [01.1], [1], etc.
        title = re.sub(r'^\s*\[[^\]]+\]\s*', '', title)
        
        # Clean up title: remove leading/trailing brackets and dots
        title = title.strip('[](). ')
        
        # Replace colons with periods in the title
        title = title.replace(':', '.')
        
        return title if title else None

    def extract_year(self) -> str | None:
        """Extract year from filename"""
        # First try to find year in parentheses (most common and reliable)
        paren_match = re.search(r'\((\d{4})\)', self.file_name)
        if paren_match:
            return paren_match.group(1)
        
        # Fallback: look for year in dots (like .1971.)
        dot_match = re.search(r'\.(\d{4})\.', self.file_name)
        if dot_match:
            return dot_match.group(1)
        
        # Last resort: any 4-digit number (but this is less reliable)
        any_match = re.search(r'\b(\d{4})\b', self.file_name)
        if any_match:
            year = any_match.group(1)
            # Basic sanity check: years should be between 1900 and current year + a few years
            current_year = 2025  # Update this as needed
            if 1900 <= int(year) <= current_year + 10:
                return year
        
        return None

    def extract_source(self) -> str | None:
        """Extract video source from filename"""
        temp_name = re.sub(r'\s*\(\d{4}\)\s*|\s*\d{4}\s*|\.\d{4}\.', ' ', self.file_name)

        for src, aliases in SOURCE_DICT.items():
            for alias in aliases:
                if alias.upper() in temp_name.upper():
                    return src
        return None

    def extract_frame_class(self) -> str | None:
        """Extract frame class from filename (480p, 720p, 1080p, 2160p, etc.)"""
        # First check for specific numeric resolutions
        match = re.search(r'(\d{3,4})[pi]', self.file_name, re.IGNORECASE)
        if match:
            height = int(match.group(1))
            return self._get_frame_class_from_height(height)
        
        # If no specific resolution found, check for quality indicators
        unclassified_indicators = ['SD', 'LQ', 'HD', 'QHD']
        for indicator in unclassified_indicators:
            if re.search(r'\b' + re.escape(indicator) + r'\b', self.file_name, re.IGNORECASE):
                return None
        
        return None

    def extract_hdr(self) -> str | None:
        """Extract HDR information from filename"""
        # Check for SDR first - indicates no HDR
        if re.search(r'\bSDR\b', self.file_name, re.IGNORECASE):
            return None
        
        # Check for HDR, but not NoHDR
        if re.search(r'\bHDR\b', self.file_name, re.IGNORECASE) and not re.search(r'\bNoHDR\b', self.file_name, re.IGNORECASE):
            return 'HDR'
        
        return None

    def extract_movie_db(self) -> tuple[str, str] | None:
        """Extract movie database identifier from filename"""
        # Look for patterns at the end of filename in brackets or braces
        # Patterns: [tmdbid-123] {imdb-tt123} [imdbid-tt123] etc.
        
        # Match patterns like [tmdbid-123456] or {imdb-tt1234567}
        pattern = r'[\[\{]([a-zA-Z]+(?:id)?)[-\s]*([a-zA-Z0-9]+)[\]\}]'
        matches = re.findall(pattern, self.file_name)
        
        if matches:
            # Take the last match (closest to end of filename)
            db_type, db_id = matches[-1]
            
            # Normalize database type
            db_type_lower = db_type.lower()
            for db_key, db_info in MOVIE_DB_DICT.items():
                if any(db_type_lower.startswith(pattern.rstrip('-')) for pattern in db_info['patterns']):
                    return (db_key, db_id)
        
        return None

    def extract_audio_langs(self) -> str:
        """Extract audio languages from filename"""
        # Look for language patterns in brackets and outside brackets
        # Skip subtitle indicators and focus on audio languages
        
        langs = []
        
        # First, look for languages inside brackets
        bracket_pattern = r'\[([^\]]+)\]'
        brackets = re.findall(bracket_pattern, self.file_name)
        
        for bracket in brackets:
            bracket_lower = bracket.lower()
            
            # Skip brackets that contain movie database patterns
            if any(db in bracket_lower for db in ['imdb', 'tmdb', 'tvdb']):
                continue
            
            # Parse items separated by commas or underscores
            items = re.split(r'[,_]', bracket)
            items = [item.strip() for item in items]
            
            for item in items:
                # Skip empty items or items that are clearly not languages
                if not item or len(item) < 2:
                    continue
                
                item_lower = item.lower()
                
                # Skip subtitle indicators
                if item_lower in ['sub', 'subs', 'subtitle']:
                    continue
                
                # Check if item contains language codes (2-3 letter codes)
                # Pattern: optional number + optional 'x' + language code
                # Allow the language code to be at the end of the item
                lang_match = re.search(r'(?:(\d+)x?)?([a-z]{2,3})$', item_lower)
                if lang_match:
                    count = int(lang_match.group(1)) if lang_match.group(1) else 1
                    lang_code = lang_match.group(2)
                    
                    # Skip if it's a quality/resolution indicator
                    if lang_code in ['sd', 'hd', 'lq', 'qhd', 'uhd', 'p', 'i', 'hdr', 'sdr']:
                        continue
                    
                    # Skip if the language code is not at the end or if there are extra letters after
                    # But allow prefixes like numbers and 'x'
                    prefix = item_lower[:-len(lang_code)]
                    if not re.match(r'^(?:\d+x?)?$', prefix):
                        continue
                    
                    # Convert to 3-letter ISO code
                    try:
                        lang_obj = langcodes.Language.get(lang_code)
                        iso3_code = lang_obj.to_alpha3()
                        langs.extend([iso3_code] * count)
                    except:
                        # Skip invalid language codes
                        pass
        
        # Second, look for standalone language codes outside brackets
        # Remove bracketed content first
        text_without_brackets = re.sub(r'\[([^\]]+)\]', '', self.file_name)
        
        # Known language codes (2-3 letter ISO 639-1 or 639-3)
        known_language_codes = {
            'eng', 'ukr', 'rus', 'fra', 'deu', 'spa', 'ita', 'por', 'nor', 'swe', 'dan', 'fin', 'pol', 'cze', 'hun', 'tur', 'ara', 'heb', 'hin', 'jpn', 'kor', 'chi', 'tha', 'vie', 'und',
            'dut', 'nld', 'bel', 'bul', 'hrv', 'ces', 'dan', 'nld', 'est', 'fin', 'fra', 'deu', 'ell', 'heb', 'hin', 'hrv', 'hun', 'ind', 'ita', 'jpn', 'kor', 'lav', 'lit', 'mkd', 'nor', 'pol', 'por', 'ron', 'rus', 'slk', 'slv', 'spa', 'srp', 'swe', 'tha', 'tur', 'ukr', 'vie', 'und', 'zho',
            'arb', 'ben', 'hin', 'mar', 'tam', 'tel', 'urd', 'guj', 'kan', 'mal', 'ori', 'pan', 'asm', 'mai', 'bho', 'nep', 'sin', 'san', 'tib', 'mon', 'kaz', 'uzb', 'kir', 'tuk', 'aze', 'kat', 'hye', 'geo', 'ell', 'sqi', 'bos', 'hrv', 'srp', 'slv', 'mkd', 'bul', 'alb', 'ron', 'mol', 'hun',
            'fin', 'swe', 'nor', 'dan', 'isl', 'fao', 'est', 'lav', 'lit', 'bel', 'ukr', 'rus', 'pol', 'cze', 'slk', 'slv', 'hrv', 'bos', 'srp', 'mkd', 'bul', 'ell', 'alb', 'ron', 'hun', 'tur', 'aze', 'geo', 'arm', 'kat', 'hye', 'per', 'kur', 'pus', 'urd', 'ara', 'heb', 'san', 'hin', 'ben', 'tam', 'tel', 'mar', 'guj', 'kan', 'mal', 'ori', 'pan', 'asm', 'mai', 'bho', 'awa', 'mag', 'nep', 'sin', 'div', 'tib', 'mon', 'kaz', 'kir', 'tuk', 'uzb', 'jpn', 'kor', 'chi', 'tha', 'vie', 'und', 'lao', 'khm', 'mya', 'vie', 'und', 'ind', 'msa', 'zho', 'yue', 'wuu', 'nan', 'hak', 'gan', 'hsn',
            'spa', 'por', 'fra', 'ita', 'deu', 'nld', 'dut', 'swe', 'nor', 'dan', 'fin', 'est', 'lav', 'lit', 'pol', 'cze', 'slk', 'slv', 'hrv', 'bos', 'srp', 'mkd', 'bul', 'ell', 'alb', 'ron', 'hun', 'tur', 'aze', 'geo', 'arm', 'kat', 'hye', 'per', 'kur', 'pus', 'urd', 'ara', 'heb', 'san', 'hin', 'ben', 'tam', 'tel', 'mar', 'guj', 'kan', 'mal', 'ori', 'pan', 'asm', 'mai', 'bho', 'awa', 'mag', 'nep', 'sin', 'div', 'tib', 'mon', 'kaz', 'kir', 'tuk', 'uzb', 'jpn', 'kor', 'chi', 'tha', 'vie', 'und', 'lao', 'khm', 'mya', 'vie', 'und', 'ind', 'msa', 'zho', 'yue', 'wuu', 'nan', 'hak', 'gan', 'hsn'
        }
        
        allowed_title_case = {'ukr', 'nor', 'eng', 'rus', 'fra', 'deu', 'spa', 'ita', 'por', 'swe', 'dan', 'fin', 'pol', 'cze', 'hun', 'tur', 'ara', 'heb', 'hin', 'jpn', 'kor', 'chi', 'tha', 'vie', 'und'}
        # Look for language codes in various formats:
        # - Uppercase: ENG, UKR, NOR
        # - Title case: Ukr, Nor, Eng  
        # - Lowercase: ukr, nor, eng
        # - In dot-separated parts: .ukr. .eng.
        
        # Split on dots, spaces, and underscores
        parts = re.split(r'[.\s_]+', text_without_brackets)
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue
            
            part_lower = part.lower()
            
            # Check if this part is a 2-3 letter language code
            if re.match(r'^[a-zA-Z]{2,3}$', part):
                # Skip title case 2-letter words to avoid false positives like "In" -> "ind"
                if part.istitle() and len(part) == 2:
                    continue
                if part.istitle() and part_lower not in allowed_title_case:
                    continue
                skip_words = [
                    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'has', 'let', 'put', 'say', 'she', 'too', 'use',
                    'avi', 'mkv', 'mp4', 'mpg', 'mov', 'wmv', 'flv', 'webm', 'm4v', 'm2ts', 'ts', 'vob', 'iso', 'img',
                    'sd', 'hd', 'lq', 'qhd', 'uhd', 'p', 'i', 'hdr', 'sdr', '4k', '8k', '2160p', '1080p', '720p', '480p', '360p', '240p', '144p',
                    'web', 'dl', 'rip', 'bluray', 'dvd', 'hdtv', 'bdrip', 'dvdrip', 'xvid', 'divx', 'h264', 'h265', 'x264', 'x265', 'hevc', 'avc',
                    'ma', 'atmos', 'dts', 'aac', 'ac3', 'mp3', 'flac', 'wav', 'wma', 'ogg', 'opus'
                ]
                
                if part_lower not in skip_words and part_lower in known_language_codes:
                    lang_code = part_lower
                    
                    # Convert to 3-letter ISO code
                    try:
                        lang_obj = langcodes.Language.get(lang_code)
                        iso3_code = lang_obj.to_alpha3()
                        langs.append(iso3_code)
                    except:
                        # Skip invalid language codes
                        pass
        
        if not langs:
            return ''
            
        # Count occurrences and format like mediainfo: "2ukr,eng"
        lang_counts = Counter(langs)
        audio_langs = [f"{count}{lang}" if count > 1 else lang for lang, count in lang_counts.items()]
        return ','.join(sorted(audio_langs))

    def extract_audio_tracks(self) -> list[dict]:
        """Extract audio track data from filename (simplified version with only language)"""
        # Similar to extract_audio_langs but returns list of dicts
        
        tracks = []
        
        # First, look for languages inside brackets
        bracket_pattern = r'\[([^\]]+)\]'
        brackets = re.findall(bracket_pattern, self.file_name)
        
        for bracket in brackets:
            bracket_lower = bracket.lower()
            
            # Skip brackets that contain movie database patterns
            if any(db in bracket_lower for db in ['imdb', 'tmdb', 'tvdb']):
                continue
            
            # Parse items separated by commas or underscores
            items = re.split(r'[,_]', bracket)
            items = [item.strip() for item in items]
            
            for item in items:
                # Skip empty items or items that are clearly not languages
                if not item or len(item) < 2:
                    continue
                
                item_lower = item.lower()
                
                # Skip subtitle indicators
                if item_lower in ['sub', 'subs', 'subtitle']:
                    continue
                
                # Check if item contains language codes (2-3 letter codes)
                # Pattern: optional number + optional 'x' + language code
                # Allow the language code to be at the end of the item
                lang_match = re.search(r'(?:(\d+)x?)?([a-z]{2,3})$', item_lower)
                if lang_match:
                    count = int(lang_match.group(1)) if lang_match.group(1) else 1
                    lang_code = lang_match.group(2)
                    
                    # Skip if it's a quality/resolution indicator
                    if lang_code in ['sd', 'hd', 'lq', 'qhd', 'uhd', 'p', 'i', 'hdr', 'sdr']:
                        continue
                    
                    # Skip if the language code is not at the end or if there are extra letters after
                    # But allow prefixes like numbers and 'x'
                    prefix = item_lower[:-len(lang_code)]
                    if not re.match(r'^(?:\d+x?)?$', prefix):
                        continue
                    
                    # Convert to 3-letter ISO code
                    try:
                        lang_obj = langcodes.Language.get(lang_code)
                        iso3_code = lang_obj.to_alpha3()
                        tracks.append({'language': iso3_code})
                    except:
                        # Skip invalid language codes
                        pass
        
        # Second, look for standalone language codes outside brackets
        # Remove bracketed content first
        text_without_brackets = re.sub(r'\[([^\]]+)\]', '', self.file_name)
        
        # Known language codes (2-3 letter ISO 639-1 or 639-3)
        known_language_codes = {
            'eng', 'ukr', 'rus', 'fra', 'deu', 'spa', 'ita', 'por', 'nor', 'swe', 'dan', 'fin', 'pol', 'cze', 'hun', 'tur', 'ara', 'heb', 'hin', 'jpn', 'kor', 'chi', 'tha', 'vie', 'und',
            'dut', 'nld', 'bel', 'bul', 'hrv', 'ces', 'dan', 'nld', 'est', 'fin', 'fra', 'deu', 'ell', 'heb', 'hin', 'hrv', 'hun', 'ind', 'ita', 'jpn', 'kor', 'lav', 'lit', 'mkd', 'nor', 'pol', 'por', 'ron', 'rus', 'slk', 'slv', 'spa', 'srp', 'swe', 'tha', 'tur', 'ukr', 'vie', 'und', 'zho',
            'arb', 'ben', 'hin', 'mar', 'tam', 'tel', 'urd', 'guj', 'kan', 'mal', 'ori', 'pan', 'asm', 'mai', 'bho', 'nep', 'sin', 'san', 'tib', 'mon', 'kaz', 'uzb', 'kir', 'tuk', 'aze', 'kat', 'hye', 'geo', 'ell', 'sqi', 'bos', 'hrv', 'srp', 'slv', 'mkd', 'bul', 'alb', 'ron', 'mol', 'hun',
            'fin', 'swe', 'nor', 'dan', 'isl', 'fao', 'est', 'lav', 'lit', 'bel', 'ukr', 'rus', 'pol', 'cze', 'slk', 'slv', 'hrv', 'bos', 'srp', 'mkd', 'bul', 'ell', 'alb', 'ron', 'hun', 'tur', 'aze', 'geo', 'arm', 'kat', 'hye', 'per', 'kur', 'pus', 'urd', 'ara', 'heb', 'san', 'hin', 'ben', 'tam', 'tel', 'mar', 'guj', 'kan', 'mal', 'ori', 'pan', 'asm', 'mai', 'bho', 'awa', 'mag', 'nep', 'sin', 'div', 'tib', 'mon', 'kaz', 'kir', 'tuk', 'uzb', 'jpn', 'kor', 'chi', 'tha', 'vie', 'und', 'lao', 'khm', 'mya', 'vie', 'und', 'ind', 'msa', 'zho', 'yue', 'wuu', 'nan', 'hak', 'gan', 'hsn',
            'spa', 'por', 'fra', 'ita', 'deu', 'nld', 'dut', 'swe', 'nor', 'dan', 'fin', 'est', 'lav', 'lit', 'pol', 'cze', 'slk', 'slv', 'hrv', 'bos', 'srp', 'mkd', 'bul', 'ell', 'alb', 'ron', 'hun', 'tur', 'aze', 'geo', 'arm', 'kat', 'hye', 'per', 'kur', 'pus', 'urd', 'ara', 'heb', 'san', 'hin', 'ben', 'tam', 'tel', 'mar', 'guj', 'kan', 'mal', 'ori', 'pan', 'asm', 'mai', 'bho', 'awa', 'mag', 'nep', 'sin', 'div', 'tib', 'mon', 'kaz', 'kir', 'tuk', 'uzb', 'jpn', 'kor', 'chi', 'tha', 'vie', 'und', 'lao', 'khm', 'mya', 'vie', 'und', 'ind', 'msa', 'zho', 'yue', 'wuu', 'nan', 'hak', 'gan', 'hsn'
        }
        allowed_title_case = {'ukr', 'nor', 'eng', 'rus', 'fra', 'deu', 'spa', 'ita', 'por', 'swe', 'dan', 'fin', 'pol', 'cze', 'hun', 'tur', 'ara', 'heb', 'hin', 'jpn', 'kor', 'chi', 'tha', 'vie', 'und'}
        
        # Look for language codes in various formats:
        # - Uppercase: ENG, UKR, NOR
        # - Title case: Ukr, Nor, Eng  
        # - Lowercase: ukr, nor, eng
        # - In dot-separated parts: .ukr. .eng.
        
        # Split on dots, spaces, and underscores
        parts = re.split(r'[.\s_]+', text_without_brackets)
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue
            
            part_lower = part.lower()
            
            # Check if this part is a 2-3 letter language code
            if re.match(r'^[a-zA-Z]{2,3}$', part):
                # Skip title case 2-letter words to avoid false positives like "In" -> "ind"
                if part.istitle() and len(part) == 2:
                    continue
                if part.istitle() and part_lower not in allowed_title_case:
                    continue
                skip_words = [
                    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'has', 'let', 'put', 'say', 'she', 'too', 'use',
                    'avi', 'mkv', 'mp4', 'mpg', 'mov', 'wmv', 'flv', 'webm', 'm4v', 'm2ts', 'ts', 'vob', 'iso', 'img',
                    'sd', 'hd', 'lq', 'qhd', 'uhd', 'p', 'i', 'hdr', 'sdr', '4k', '8k', '2160p', '1080p', '720p', '480p', '360p', '240p', '144p',
                    'web', 'dl', 'rip', 'bluray', 'dvd', 'hdtv', 'bdrip', 'dvdrip', 'xvid', 'divx', 'h264', 'h265', 'x264', 'x265', 'hevc', 'avc',
                    'ma', 'atmos', 'dts', 'aac', 'ac3', 'mp3', 'flac', 'wav', 'wma', 'ogg', 'opus'
                ]
                
                if part_lower not in skip_words and part_lower in known_language_codes:
                    lang_code = part_lower
                    
                    # Convert to 3-letter ISO code
                    try:
                        lang_obj = langcodes.Language.get(lang_code)
                        iso3_code = lang_obj.to_alpha3()
                        tracks.append({'language': iso3_code})
                    except:
                        # Skip invalid language codes
                        pass
        
        return tracks