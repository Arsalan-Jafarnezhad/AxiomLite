"""Tests for accounts utility functions."""

import pytest
from django.core.exceptions import ValidationError

from accounts.utils.ids import (
    generate_public_id,
    generate_slug,
)
from accounts.utils.upload_paths import safe_extension


class TestIDUtilities:
    """Test identifier utilities."""

    def test_generate_public_id(self):
        public_id = generate_public_id()

        assert isinstance(public_id, str)
        assert len(public_id) == 16

    def test_generate_public_ids_are_different(self):
        first = generate_public_id()
        second = generate_public_id()

        assert first != second

    def test_generate_slug(self):
        assert generate_slug("Hello World!") == "hello-world"


class TestUploadUtilities:
    """Test upload-related utilities."""

    @pytest.mark.parametrize(
        "filename, extension",
        [
            ("image.jpg", ".jpg"),
            ("image.JPEG", ".jpeg"),
            ("image.png", ".png"),
            ("image.webp", ".webp"),
        ],
    )
    def test_safe_extension(self, filename, extension):
        assert safe_extension(filename) == extension

    def test_safe_extension_rejects_unknown_extension(self):
        with pytest.raises(ValidationError):
            safe_extension("malware.exe")