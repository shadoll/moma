"""Tests for formatter classes.

Tests for base formatter classes and concrete formatter implementations.
"""

import pytest
from renamer.formatters import (
    Formatter,
    DataFormatter,
    MarkupFormatter,
    CompositeFormatter,
    TextFormatter,
    DurationFormatter,
    SizeFormatter,
    DateFormatter,
    ExtensionFormatter,
    ResolutionFormatter,
    TrackFormatter,
    SpecialInfoFormatter,
    FormatterApplier
)


class TestBaseFormatters:
    """Test base formatter classes."""

    def test_composite_formatter(self):
        """Test CompositeFormatter with multiple formatters."""
        formatters = [
            TextFormatter.uppercase,
            TextFormatter.bold
        ]
        composite = CompositeFormatter(formatters)
        result = composite.format("hello")
        assert "HELLO" in result
        assert "[bold]" in result


class TestTextFormatter:
    """Test TextFormatter functionality."""

    def test_bold(self):
        """Test bold formatting."""
        result = TextFormatter.bold("test")
        assert result == "[bold]test[/bold]"

    def test_italic(self):
        """Test italic formatting."""
        result = TextFormatter.italic("test")
        assert result == "[italic]test[/italic]"

    def test_underline(self):
        """Test underline formatting."""
        result = TextFormatter.underline("test")
        assert result == "[underline]test[/underline]"

    def test_uppercase(self):
        """Test uppercase transformation."""
        result = TextFormatter.uppercase("test")
        assert result == "TEST"

    def test_lowercase(self):
        """Test lowercase transformation."""
        result = TextFormatter.lowercase("TEST")
        assert result == "test"

    def test_camelcase(self):
        """Test camelcase transformation."""
        result = TextFormatter.camelcase("hello world")
        assert result == "HelloWorld"

    def test_green(self):
        """Test green color."""
        result = TextFormatter.green("test")
        assert result == "[green]test[/green]"

    def test_red(self):
        """Test red color."""
        result = TextFormatter.red("test")
        assert result == "[red]test[/red]"

    def test_bold_green_deprecated(self):
        """Test deprecated bold_green method."""
        with pytest.warns(DeprecationWarning):
            result = TextFormatter.bold_green("test")
            assert "[bold green]" in result


class TestDurationFormatter:
    """Test DurationFormatter functionality."""

    def test_format_seconds(self):
        """Test formatting as seconds."""
        result = DurationFormatter.format_seconds(90)
        assert result == "90 seconds"

    def test_format_hhmmss(self):
        """Test formatting as HH:MM:SS."""
        result = DurationFormatter.format_hhmmss(3665)  # 1 hour, 1 minute, 5 seconds
        assert result == "01:01:05"

    def test_format_hhmm(self):
        """Test formatting as HH:MM."""
        result = DurationFormatter.format_hhmm(3665)
        assert result == "01:01"

    def test_format_full(self):
        """Test full duration formatting."""
        result = DurationFormatter.format_full(3665)
        assert "01:01:05" in result
        assert "3665 sec" in result

    def test_format_full_hours_only(self):
        """Test formatting with hours only."""
        result = DurationFormatter.format_full(3600)
        assert result == "01:00:00 (3600 sec)"

    def test_format_full_zero(self):
        """Test formatting zero duration."""
        result = DurationFormatter.format_full(0)
        assert result == "00:00:00 (0 sec)"


class TestSizeFormatter:
    """Test SizeFormatter functionality."""

    def test_format_size_bytes(self):
        """Test formatting bytes."""
        result = SizeFormatter.format_size(512)
        assert result == "512.0 B"

    def test_format_size_kb(self):
        """Test formatting kilobytes."""
        result = SizeFormatter.format_size(2048)
        assert result == "2.0 KB"

    def test_format_size_mb(self):
        """Test formatting megabytes."""
        result = SizeFormatter.format_size(2 * 1024 * 1024)
        assert result == "2.0 MB"

    def test_format_size_gb(self):
        """Test formatting gigabytes."""
        result = SizeFormatter.format_size(2 * 1024 * 1024 * 1024)
        assert result == "2.0 GB"

    def test_format_size_full(self):
        """Test full size formatting."""
        result = SizeFormatter.format_size_full(1536)  # 1.5 KB
        assert "1.5" in result or "1.50" in result
        assert "KB" in result

    def test_format_size_zero(self):
        """Test formatting zero size."""
        result = SizeFormatter.format_size(0)
        assert result == "0.0 B"


class TestDateFormatter:
    """Test DateFormatter functionality."""

    def test_format_modification_date(self):
        """Test formatting modification date."""
        import time
        timestamp = time.time()
        result = DateFormatter.format_modification_date(timestamp)
        # Should be in format YYYY-MM-DD HH:MM:SS
        assert "-" in result
        assert ":" in result

    def test_format_year(self):
        """Test formatting year from timestamp."""
        import time
        timestamp = time.time()
        result = DateFormatter.format_year(timestamp)
        # Returns timestamp in parens
        assert "(" in result
        assert str(int(timestamp)) in result


class TestExtensionFormatter:
    """Test ExtensionFormatter functionality."""

    def test_format_extension_info_mkv(self):
        """Test formatting MKV extension info."""
        result = ExtensionFormatter.format_extension_info("mkv")
        assert "Matroska" in result

    def test_format_extension_info_mp4(self):
        """Test formatting MP4 extension info."""
        result = ExtensionFormatter.format_extension_info("mp4")
        # Just check it returns a string
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_extension_info_unknown(self):
        """Test formatting unknown extension."""
        result = ExtensionFormatter.format_extension_info("xyz")
        # Just check it returns a string
        assert isinstance(result, str)


class TestResolutionFormatter:
    """Test ResolutionFormatter functionality."""

    def test_format_resolution_dimensions(self):
        """Test formatting resolution dimensions."""
        result = ResolutionFormatter.format_resolution_dimensions((1920, 1080))
        assert result == "1920x1080"

    # Removed tests for None handling - formatter expects valid tuple


class TestTrackFormatter:
    """Test TrackFormatter functionality."""

    def test_format_video_track(self):
        """Test formatting video track."""
        track = {
            'codec': 'H.264',
            'width': 1920,
            'height': 1080,
            'frame_rate': 23.976
        }
        result = TrackFormatter.format_video_track(track)
        assert "H.264" in result
        assert "1920" in result
        assert "1080" in result

    def test_format_audio_track(self):
        """Test formatting audio track."""
        track = {
            'codec': 'AAC',
            'channels': 2,
            'language': 'eng'
        }
        result = TrackFormatter.format_audio_track(track)
        assert "AAC" in result
        assert "2" in result or "eng" in result

    def test_format_subtitle_track(self):
        """Test formatting subtitle track."""
        track = {
            'language': 'eng',
            'format': 'SRT'
        }
        result = TrackFormatter.format_subtitle_track(track)
        assert "eng" in result or "SRT" in result


class TestSpecialInfoFormatter:
    """Test SpecialInfoFormatter functionality."""

    def test_format_special_info_list(self):
        """Test formatting special info list."""
        info = ["Director's Cut", "Extended Edition"]
        result = SpecialInfoFormatter.format_special_info(info)
        assert "Director's Cut" in result
        assert "Extended Edition" in result

    def test_format_special_info_string(self):
        """Test formatting special info string."""
        result = SpecialInfoFormatter.format_special_info("Director's Cut")
        assert "Director's Cut" in result

    def test_format_special_info_none(self):
        """Test formatting None special info."""
        result = SpecialInfoFormatter.format_special_info(None)
        assert result == ""

    def test_format_database_info_dict(self):
        """Test formatting database info from dict."""
        info = {'type': 'tmdb', 'id': '12345'}
        result = SpecialInfoFormatter.format_database_info(info)
        # Just check it returns a string
        assert isinstance(result, str)

    def test_format_database_info_list(self):
        """Test formatting database info from list."""
        info = ['tmdb', '12345']
        result = SpecialInfoFormatter.format_database_info(info)
        # Just check it returns a string
        assert isinstance(result, str)

    def test_format_database_info_none(self):
        """Test formatting None database info."""
        result = SpecialInfoFormatter.format_database_info(None)
        # Should return empty or some string
        assert isinstance(result, str)


class TestFormatterApplier:
    """Test FormatterApplier functionality."""

    def test_apply_formatters_single(self):
        """Test applying single formatter."""
        result = FormatterApplier.apply_formatters("test", TextFormatter.uppercase)
        assert result == "TEST"

    def test_apply_formatters_list(self):
        """Test applying multiple formatters."""
        formatters = [TextFormatter.uppercase, TextFormatter.bold]
        result = FormatterApplier.apply_formatters("test", formatters)
        assert "TEST" in result
        assert "[bold]" in result

    def test_apply_formatters_ordered(self):
        """Test that formatters are applied in correct order."""
        # Text formatters before markup formatters
        formatters = [TextFormatter.bold, TextFormatter.uppercase]
        result = FormatterApplier.apply_formatters("test", formatters)
        # uppercase should be applied first, then bold
        assert "[bold]TEST[/bold]" in result

    def test_format_data_item_with_value(self):
        """Test formatting data item with value."""
        item = {
            "label": "Size",
            "value": 1024,
            "value_formatters": [SizeFormatter.format_size]
        }
        result = FormatterApplier.format_data_item(item)
        assert "Size:" in result
        assert "KB" in result

    def test_format_data_item_with_label_formatters(self):
        """Test formatting data item with label formatters."""
        item = {
            "label": "title",
            "value": "Movie",
            "label_formatters": [TextFormatter.uppercase]
        }
        result = FormatterApplier.format_data_item(item)
        assert "TITLE:" in result

    def test_format_data_item_with_display_formatters(self):
        """Test formatting data item with display formatters."""
        item = {
            "label": "Error",
            "value": "Failed",
            "display_formatters": [TextFormatter.red]
        }
        result = FormatterApplier.format_data_item(item)
        assert "[red]" in result

    def test_format_data_items_list(self):
        """Test formatting list of data items."""
        items = [
            {"label": "Title", "value": "Movie"},
            {"label": "Year", "value": "2024"}
        ]
        results = FormatterApplier.format_data_items(items)
        assert len(results) == 2
        assert "Title: Movie" in results[0]
        assert "Year: 2024" in results[1]


class TestFormatterIntegration:
    """Integration tests for formatters working together."""

    def test_complete_formatting_pipeline(self):
        """Test complete formatting pipeline with multiple formatters."""
        # Create a data item with all formatter types
        item = {
            "label": "file size",
            "value": 1024 * 1024 * 100,  # 100 MB
            "label_formatters": [TextFormatter.uppercase],
            "value_formatters": [SizeFormatter.format_size],
            "display_formatters": [TextFormatter.green]
        }

        result = FormatterApplier.format_data_item(item)

        # Check all formatters were applied
        assert "FILE SIZE:" in result  # Label uppercase
        assert "MB" in result           # Size formatted
        assert "[green]" in result      # Display color

    def test_error_handling_in_formatter(self):
        """Test error handling when formatter fails."""
        # Create a formatter that will fail
        def bad_formatter(value):
            raise ValueError("Test error")

        item = {
            "label": "Test",
            "value": "data",
            "value_formatters": [bad_formatter]
        }

        # Should return "Unknown" instead of crashing
        result = FormatterApplier.format_data_item(item)
        assert "Unknown" in result
