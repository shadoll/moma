"""Tests for formatter decorators."""

import pytest
from renamer.formatters import (
    date_decorators,
    special_info_decorators,
    text_decorators,
    conditional_decorators
)


class TestDateDecorators:
    """Test date formatting decorators."""

    def test_modification_date_decorator(self):
        """Test @date_decorators.modification_date() decorator."""
        class TestClass:
            def __init__(self, mtime):
                self.mtime = mtime

            @date_decorators.modification_date()
            def get_mtime(self):
                return self.mtime

        # Test with a known timestamp (2020-01-01 00:00:00 UTC)
        obj = TestClass(1577836800.0)
        result = obj.get_mtime()
        assert "2020-01-01" in result  # Date part should be present


class TestSpecialInfoDecorators:
    """Test special info formatting decorators."""

    def test_special_info_decorator(self):
        """Test @special_info_decorators.special_info() decorator."""
        class TestClass:
            def __init__(self, special_info):
                self.special_info = special_info

            @special_info_decorators.special_info()
            def get_special_info(self):
                return self.special_info

        obj = TestClass(["Director's Cut", "Extended Edition"])
        assert obj.get_special_info() == "Director's Cut, Extended Edition"

        obj_none = TestClass(None)
        assert obj_none.get_special_info() == ""

    def test_database_info_decorator(self):
        """Test @special_info_decorators.database_info() decorator."""
        class TestClass:
            def __init__(self, db_info):
                self.db_info = db_info

            @special_info_decorators.database_info()
            def get_db_info(self):
                return self.db_info

        obj = TestClass(["tmdb", "12345"])
        assert obj.get_db_info() == "tmdbid-12345"

        obj_dict = TestClass({"name": "imdb", "id": "tt1234567"})
        assert obj_dict.get_db_info() == "imdbid-tt1234567"


class TestTextDecorators:
    """Test text formatting decorators."""

    def test_bold_decorator(self):
        """Test @text_decorators.bold() decorator."""
        class TestClass:
            @text_decorators.bold()
            def get_text(self):
                return "Hello"

        obj = TestClass()
        assert obj.get_text() == "[bold]Hello[/bold]"

    def test_green_decorator(self):
        """Test @text_decorators.green() decorator."""
        class TestClass:
            @text_decorators.green()
            def get_text(self):
                return "Success"

        obj = TestClass()
        assert obj.get_text() == "[green]Success[/green]"


class TestConditionalDecorators:
    """Test conditional formatting decorators."""

    def test_wrap_decorator_both_sides(self):
        """Test @conditional_decorators.wrap() with both left and right."""
        class TestClass:
            def __init__(self, order):
                self.order = order

            @conditional_decorators.wrap("[", "] ")
            def get_order(self):
                return self.order

        obj = TestClass("01")
        assert obj.get_order() == "[01] "

        obj_none = TestClass(None)
        assert obj_none.get_order() == ""

    def test_wrap_decorator_prefix_only(self):
        """Test @conditional_decorators.wrap() as prefix (right="")."""
        class TestClass:
            def __init__(self, source):
                self.source = source

            @conditional_decorators.wrap(" ")
            def get_source(self):
                return self.source

        obj = TestClass("BDRip")
        assert obj.get_source() == " BDRip"

        obj_none = TestClass(None)
        assert obj_none.get_source() == ""

    def test_wrap_decorator_suffix_only(self):
        """Test @conditional_decorators.wrap() as suffix (left="")."""
        class TestClass:
            def __init__(self, hdr):
                self.hdr = hdr

            @conditional_decorators.wrap("", ",")
            def get_hdr(self):
                return self.hdr

        obj = TestClass("HDR")
        assert obj.get_hdr() == "HDR,"

        obj_none = TestClass(None)
        assert obj_none.get_hdr() == ""

    def test_replace_slashes_decorator(self):
        """Test @conditional_decorators.replace_slashes() decorator."""
        class TestClass:
            def __init__(self, title):
                self.title = title

            @conditional_decorators.replace_slashes()
            def get_title(self):
                return self.title

        obj = TestClass("Movie/Title\\Test")
        assert obj.get_title() == "Movie-Title-Test"

    def test_default_decorator(self):
        """Test @conditional_decorators.default() decorator."""
        class TestClass:
            def __init__(self, title):
                self.title = title

            @conditional_decorators.default("Unknown Title")
            def get_title(self):
                return self.title

        obj = TestClass(None)
        assert obj.get_title() == "Unknown Title"

        obj_with_title = TestClass("Movie Title")
        assert obj_with_title.get_title() == "Movie Title"

    def test_chained_decorators(self):
        """Test chaining multiple decorators."""
        class TestClass:
            def __init__(self, title):
                self.title = title

            @conditional_decorators.replace_slashes()
            @conditional_decorators.default("Unknown Title")
            def get_title(self):
                return self.title

        obj = TestClass("Movie/Title")
        assert obj.get_title() == "Movie-Title"

        obj_none = TestClass(None)
        assert obj_none.get_title() == "Unknown Title"
