"""Tests for ProposedNameFormatter with decorator pattern."""

import pytest
from pathlib import Path
from renamer.formatters.proposed_name_formatter import ProposedNameFormatter


class TestProposedNameFormatter:
    """Test ProposedNameFormatter with decorator pattern."""

    def test_basic_formatting(self):
        """Test basic filename formatting with all fields."""
        extractor = {
            'order': '01',
            'title': 'Movie Title',
            'year': 2020,
            'source': 'BDRip',
            'frame_class': '1080p',
            'hdr': 'HDR',
            'audio_langs': 'ukr,eng',
            'special_info': ["Director's Cut"],
            'movie_db': ['tmdb', '12345'],
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        result = formatter.rename_line

        assert '[01]' in result
        assert 'Movie Title' in result
        assert '(2020)' in result
        assert 'BDRip' in result
        assert '1080p' in result
        assert 'HDR' in result
        assert 'ukr,eng' in result
        assert "Director's Cut" in result
        assert 'tmdbid-12345' in result
        assert '.mkv' in result

    def test_minimal_formatting(self):
        """Test formatting with minimal fields."""
        extractor = {
            'title': 'Simple Movie',
            'year': 2020,
            'extension': 'mp4'
        }

        formatter = ProposedNameFormatter(extractor)
        result = formatter.rename_line

        assert 'Simple Movie' in result
        assert '(2020)' in result
        assert '.mp4' in result
        assert '[01]' not in result  # No order

    def test_title_slash_replacement(self):
        """Test that slashes in title are replaced with dashes."""
        extractor = {
            'title': 'Movie/Title\\Test',
            'year': 2020,
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        result = formatter.rename_line

        assert 'Movie-Title-Test' in result
        assert '/' not in result
        assert '\\' not in result

    def test_none_title(self):
        """Test formatting when title is None (extractor should provide default)."""
        extractor = {
            'title': None,
            'year': 2020,
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        result = formatter.rename_line

        # Since title is None, it won't appear (unless extractor provides default)
        assert result is not None

    def test_none_extension(self):
        """Test formatting when extension is None (extractor should provide default)."""
        extractor = {
            'title': 'Movie',
            'year': 2020,
            'extension': None
        }

        formatter = ProposedNameFormatter(extractor)
        result = formatter.rename_line

        # Extension handling depends on extractor default
        assert result is not None

    def test_special_info_list_formatting(self):
        """Test special info list is formatted correctly."""
        extractor = {
            'title': 'Movie',
            'year': 2020,
            'special_info': ['Extended Edition', 'Remastered'],
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        result = formatter.rename_line

        assert 'Extended Edition, Remastered' in result

    def test_database_info_formatting(self):
        """Test database info is formatted correctly."""
        extractor = {
            'title': 'Movie',
            'year': 2020,
            'movie_db': {'name': 'imdb', 'id': 'tt1234567'},
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        result = formatter.rename_line

        assert 'imdbid-tt1234567' in result

    def test_str_method(self):
        """Test __str__ method returns same as rename_line()."""
        extractor = {
            'title': 'Movie',
            'year': 2020,
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        assert str(formatter) == formatter.rename_line

    def test_formatted_display_matching_name(self):
        """Test rename_line_formatted when filename matches proposed name."""
        extractor = {
            'title': 'Movie',
            'year': 2020,
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        proposed = str(formatter)
        file_path = Path(proposed)

        result = formatter.rename_line_formatted(file_path)
        assert '>>' in result
        assert '<<' in result
        assert '[green]' in result

    def test_formatted_display_different_name(self):
        """Test rename_line_formatted when filename differs from proposed name."""
        extractor = {
            'title': 'Movie',
            'year': 2020,
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        file_path = Path('different_name.mkv')

        result = formatter.rename_line_formatted(file_path)
        assert '>>' in result
        assert '<<' in result

    def test_year_formatting(self):
        """Test year is wrapped in parentheses."""
        extractor = {
            'title': 'Movie',
            'year': 2020,
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        result = formatter.rename_line

        assert '(2020)' in result

    def test_no_year(self):
        """Test formatting when no year provided."""
        extractor = {
            'title': 'Movie',
            'year': None,
            'extension': 'mkv'
        }

        formatter = ProposedNameFormatter(extractor)
        result = formatter.rename_line

        # Should not have empty parentheses
        assert '()' not in result
