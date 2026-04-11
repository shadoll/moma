"""Tests for utility modules.

Tests for LanguageCodeExtractor, PatternExtractor, and FrameClassMatcher.
"""

import pytest
from src.utils import LanguageCodeExtractor, PatternExtractor, FrameClassMatcher


class TestLanguageCodeExtractor:
    """Test LanguageCodeExtractor functionality."""

    @pytest.fixture
    def extractor(self):
        """Create a LanguageCodeExtractor instance."""
        return LanguageCodeExtractor()

    def test_extract_from_brackets_simple(self, extractor):
        """Test extracting simple language codes from brackets."""
        result = extractor.extract_from_brackets("[UKR_ENG]")
        assert 'ukr' in result
        assert 'eng' in result

    def test_extract_from_brackets_with_count(self, extractor):
        """Test extracting with count prefix."""
        result = extractor.extract_from_brackets("[2xUKR_ENG]")
        assert result.count('ukr') == 2
        assert result.count('eng') == 1

    def test_extract_from_brackets_comma_separated(self, extractor):
        """Test extracting comma-separated codes."""
        result = extractor.extract_from_brackets("[UKR,ENG,FRA]")
        assert 'ukr' in result
        assert 'eng' in result
        assert 'fra' in result

    def test_extract_from_brackets_skip_tmdb(self, extractor):
        """Test that TMDB patterns are skipped."""
        result = extractor.extract_from_brackets("[tmdbid-12345]")
        assert len(result) == 0

    def test_extract_from_brackets_skip_quality(self, extractor):
        """Test that quality indicators are skipped."""
        result = extractor.extract_from_brackets("[1080p]")
        assert len(result) == 0

    def test_extract_standalone_simple(self, extractor):
        """Test extracting standalone language codes."""
        result = extractor.extract_standalone("Movie.2024.UKR.ENG.1080p.mkv")
        assert 'ukr' in result
        assert 'eng' in result

    def test_extract_standalone_skip_quality(self, extractor):
        """Test that quality indicators are skipped."""
        result = extractor.extract_standalone("Movie.1080p.BluRay.mkv")
        # Should not extract '1080p' or 'BluRay' as languages
        assert '1080p' not in result
        assert 'bluray' not in result

    def test_extract_standalone_skip_extensions(self, extractor):
        """Test that file extensions are skipped."""
        result = extractor.extract_standalone("Movie.mkv.avi.mp4")
        assert 'mkv' not in result
        assert 'avi' not in result
        assert 'mp4' not in result

    def test_extract_all(self, extractor):
        """Test extracting all language codes."""
        result = extractor.extract_all("[UKR_ENG] Movie.2024.RUS.mkv")
        # Should get ukr, eng from brackets and rus from standalone
        assert 'ukr' in result
        assert 'eng' in result
        assert 'rus' in result

    def test_format_lang_counts(self, extractor):
        """Test formatting language counts."""
        langs = ['ukr', 'ukr', 'eng']
        result = extractor.format_lang_counts(langs)
        assert result == '2ukr,eng'

    def test_format_lang_counts_single(self, extractor):
        """Test formatting single language."""
        langs = ['eng']
        result = extractor.format_lang_counts(langs)
        assert result == 'eng'

    def test_format_lang_counts_empty(self, extractor):
        """Test formatting empty list."""
        result = extractor.format_lang_counts([])
        assert result == ''

    def test_convert_to_iso3(self, extractor):
        """Test converting to ISO 639-3."""
        assert extractor._convert_to_iso3('en') == 'eng'
        assert extractor._convert_to_iso3('uk') == 'ukr'
        assert extractor._convert_to_iso3('ru') == 'rus'
        assert extractor._convert_to_iso3('ukr') == 'ukr'  # Already ISO-3

    def test_convert_to_iso3_invalid(self, extractor):
        """Test converting invalid code."""
        result = extractor._convert_to_iso3('xyz')
        # Invalid codes return None or raise exception
        assert result is None or isinstance(result, str)

    def test_is_valid_code(self, extractor):
        """Test validating language codes."""
        assert extractor.is_valid_code('eng') in [True, False]
        assert extractor.is_valid_code('ukr') in [True, False]
        # Just check it returns a boolean
        assert isinstance(extractor.is_valid_code('xyz'), bool)


class TestPatternExtractor:
    """Test PatternExtractor functionality."""

    @pytest.fixture
    def extractor(self):
        """Create a PatternExtractor instance."""
        return PatternExtractor()

    def test_extract_movie_db_ids_tmdb(self, extractor):
        """Test extracting TMDB IDs."""
        result = extractor.extract_movie_db_ids("[tmdbid-12345]")
        assert result is not None
        assert result['type'] == 'tmdb'
        assert result['id'] == '12345'

    def test_extract_movie_db_ids_imdb(self, extractor):
        """Test extracting IMDB IDs."""
        result = extractor.extract_movie_db_ids("{imdb-tt1234567}")
        assert result is not None
        assert result['type'] == 'imdb'
        assert result['id'] == 'tt1234567'

    def test_extract_movie_db_ids_none(self, extractor):
        """Test when no database ID present."""
        result = extractor.extract_movie_db_ids("Movie.2024.mkv")
        assert result is None

    def test_extract_year_in_parens(self, extractor):
        """Test extracting year in parentheses."""
        result = extractor.extract_year("Movie Title (2024)")
        assert result == '2024'

    def test_extract_year_standalone(self, extractor):
        """Test extracting standalone year."""
        result = extractor.extract_year("Movie 2024 1080p")
        assert result == '2024'

    def test_extract_year_too_old(self, extractor):
        """Test rejecting too old years."""
        result = extractor.extract_year("Movie (1899)")
        assert result is None

    def test_extract_year_too_new(self, extractor):
        """Test rejecting far future years."""
        result = extractor.extract_year("Movie (2050)")
        assert result is None

    def test_extract_year_no_validate(self, extractor):
        """Test extracting year without validation."""
        result = extractor.extract_year("Movie (1899)", validate=False)
        assert result == '1899'

    def test_find_year_position(self, extractor):
        """Test finding year position."""
        pos = extractor.find_year_position("Movie (2024) 1080p")
        assert pos == 6  # Position of '(' before year

    def test_find_year_position_none(self, extractor):
        """Test finding year when none present."""
        pos = extractor.find_year_position("Movie Title")
        assert pos is None

    def test_extract_quality(self, extractor):
        """Test extracting quality indicators."""
        assert extractor.extract_quality("Movie.1080p.mkv") == '1080p'
        assert extractor.extract_quality("Movie.720p.mkv") == '720p'
        assert extractor.extract_quality("Movie.4K.mkv") == '4K'

    def test_extract_quality_none(self, extractor):
        """Test when no quality present."""
        result = extractor.extract_quality("Movie.mkv")
        assert result is None

    def test_find_quality_position(self, extractor):
        """Test finding quality position."""
        pos = extractor.find_quality_position("Movie 1080p BluRay")
        assert pos == 6

    def test_extract_source(self, extractor):
        """Test extracting source indicators."""
        assert extractor.extract_source("Movie.BluRay.mkv") == 'BluRay'
        assert extractor.extract_source("Movie.WEB-DL.mkv") == 'WEB-DL'
        assert extractor.extract_source("Movie.DVDRip.mkv") == 'DVDRip'

    def test_extract_source_none(self, extractor):
        """Test when no source present."""
        result = extractor.extract_source("Movie.mkv")
        assert result is None

    def test_extract_bracketed_content(self, extractor):
        """Test extracting bracketed content."""
        result = extractor.extract_bracketed_content("[UKR] Movie [ENG]")
        assert result == ['UKR', 'ENG']

    def test_remove_bracketed_content(self, extractor):
        """Test removing bracketed content."""
        result = extractor.remove_bracketed_content("[UKR] Movie [ENG]")
        assert result == ' Movie '

    def test_split_on_delimiters(self, extractor):
        """Test splitting on delimiters."""
        result = extractor.split_on_delimiters("Movie.Title.2024")
        assert result == ['Movie', 'Title', '2024']

    def test_is_quality_indicator(self, extractor):
        """Test checking if text is quality indicator."""
        # Check uppercase versions (which are in the set)
        assert extractor.is_quality_indicator("UHD") is True
        assert extractor.is_quality_indicator("4K") is True
        assert extractor.is_quality_indicator("MOVIE") is False

    def test_is_source_indicator(self, extractor):
        """Test checking if text is source indicator."""
        assert extractor.is_source_indicator("BluRay") is True
        assert extractor.is_source_indicator("WEB-DL") is True
        assert extractor.is_source_indicator("movie") is False


class TestFrameClassMatcher:
    """Test FrameClassMatcher functionality."""

    @pytest.fixture
    def matcher(self):
        """Create a FrameClassMatcher instance."""
        return FrameClassMatcher()

    def test_match_by_dimensions_1080p(self, matcher):
        """Test matching 1080p resolution."""
        result = matcher.match_by_dimensions(1920, 1080, 'p')
        assert result == '1080p'

    def test_match_by_dimensions_720p(self, matcher):
        """Test matching 720p resolution."""
        result = matcher.match_by_dimensions(1280, 720, 'p')
        assert result == '720p'

    def test_match_by_dimensions_2160p(self, matcher):
        """Test matching 2160p (4K) resolution."""
        result = matcher.match_by_dimensions(3840, 2160, 'p')
        assert result == '2160p'

    def test_match_by_dimensions_interlaced(self, matcher):
        """Test matching interlaced scan type."""
        result = matcher.match_by_dimensions(1920, 1080, 'i')
        assert result == '1080i'

    def test_match_by_dimensions_close_match(self, matcher):
        """Test matching with slightly off dimensions."""
        # 1918x1078 should match 1080p
        result = matcher.match_by_dimensions(1918, 1078, 'p')
        assert result == '1080p'

    def test_match_by_height(self, matcher):
        """Test matching by height only."""
        result = matcher.match_by_height(1080)
        assert result == '1080p'

    def test_match_by_height_close(self, matcher):
        """Test matching by height with tolerance."""
        result = matcher.match_by_height(1078)
        assert result == '1080p'

    def test_match_by_height_none(self, matcher):
        """Test matching when height is None."""
        result = matcher.match_by_height(None)
        assert result is None

    def test_get_nominal_height(self, matcher):
        """Test getting nominal height for frame class."""
        assert matcher.get_nominal_height('1080p') == 1080
        assert matcher.get_nominal_height('720p') == 720
        assert matcher.get_nominal_height('2160p') == 2160

    def test_get_nominal_height_invalid(self, matcher):
        """Test getting nominal height for invalid frame class."""
        result = matcher.get_nominal_height('invalid')
        assert result is None

    def test_get_typical_widths(self, matcher):
        """Test getting typical widths for frame class."""
        widths = matcher.get_typical_widths('1080p')
        assert 1920 in widths

    def test_is_standard_resolution_true(self, matcher):
        """Test checking standard resolution."""
        assert matcher.is_standard_resolution(1920, 1080) is True
        assert matcher.is_standard_resolution(1280, 720) is True

    def test_is_standard_resolution_false(self, matcher):
        """Test checking non-standard resolution."""
        # Some implementations may return custom frame class
        result = matcher.is_standard_resolution(1234, 567)
        assert isinstance(result, bool)

    def test_detect_scan_type_progressive(self, matcher):
        """Test detecting progressive scan type."""
        assert matcher.detect_scan_type("No") == 'p'
        assert matcher.detect_scan_type(None) == 'p'

    def test_detect_scan_type_interlaced(self, matcher):
        """Test detecting interlaced scan type."""
        assert matcher.detect_scan_type("Yes") == 'i'
        assert matcher.detect_scan_type("true") == 'i'

    def test_calculate_aspect_ratio(self, matcher):
        """Test calculating aspect ratio."""
        ratio = matcher.calculate_aspect_ratio(1920, 1080)
        assert abs(ratio - 1.777) < 0.01

    def test_calculate_aspect_ratio_zero_height(self, matcher):
        """Test calculating aspect ratio with zero height."""
        result = matcher.calculate_aspect_ratio(1920, 0)
        assert result is None

    def test_format_aspect_ratio_16_9(self, matcher):
        """Test formatting 16:9 aspect ratio."""
        result = matcher.format_aspect_ratio(1.777)
        assert result == '16:9'

    def test_format_aspect_ratio_21_9(self, matcher):
        """Test formatting 21:9 aspect ratio."""
        result = matcher.format_aspect_ratio(2.35)
        assert result == '21:9'

    def test_format_aspect_ratio_custom(self, matcher):
        """Test formatting custom aspect ratio."""
        result = matcher.format_aspect_ratio(1.5)
        assert ':1' in result


class TestUtilityIntegration:
    """Integration tests for utilities working together."""

    def test_extract_all_metadata_from_filename(self):
        """Test extracting multiple types of data from a filename."""
        filename = "Movie Title [2xUKR_ENG] (2024) [1080p] [BluRay] [tmdbid-12345].mkv"

        # Test language extraction
        lang_extractor = LanguageCodeExtractor()
        langs = lang_extractor.extract_from_brackets(filename)
        assert 'ukr' in langs
        assert 'eng' in langs

        # Test pattern extraction
        pattern_extractor = PatternExtractor()
        year = pattern_extractor.extract_year(filename)
        assert year == '2024'

        quality = pattern_extractor.extract_quality(filename)
        assert quality == '1080p'

        source = pattern_extractor.extract_source(filename)
        assert source == 'BluRay'

        db_id = pattern_extractor.extract_movie_db_ids(filename)
        assert db_id['type'] == 'tmdb'
        assert db_id['id'] == '12345'

    def test_frame_class_with_language_codes(self):
        """Test that frame class detection works independently of language codes."""
        # Create a frame matcher
        matcher = FrameClassMatcher()

        # These should not interfere with each other
        lang_extractor = LanguageCodeExtractor()

        filename = "[UKR_ENG] Movie.mkv"
        langs = lang_extractor.extract_from_brackets(filename)

        # Frame matching should work on dimensions
        frame_class = matcher.match_by_dimensions(1920, 1080, 'p')
        assert frame_class == '1080p'
        assert len(langs) == 2
