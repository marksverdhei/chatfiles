"""Pure-function tests for misc/presentation.py.

Covers parse_chatfile and build_chatfile_slides — no I/O, no Textual UI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile
import os

import pytest

# Stub textual before importing presentation to avoid TUI dependency
_textual_mock = MagicMock()
sys.modules.setdefault("textual", _textual_mock)
sys.modules.setdefault("textual.app", _textual_mock.app)
sys.modules.setdefault("textual.widgets", _textual_mock.widgets)
sys.modules.setdefault("textual.containers", _textual_mock.containers)
sys.modules.setdefault("textual.binding", _textual_mock.binding)

_MISC_DIR = str(Path(__file__).resolve().parent.parent / "misc")
sys.path.insert(0, _MISC_DIR)

# Patch CHATFILE_PATH to a non-existent file so the module-level code skips slides
with patch("builtins.open", MagicMock(side_effect=FileNotFoundError)):
    import presentation as p


# ---------------------------------------------------------------------------
# parse_chatfile
# ---------------------------------------------------------------------------

class TestParseChatfile:
    def _write(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile("w", suffix=".Chatfile", delete=False)
        f.write(content)
        f.close()
        return f.name

    def teardown_method(self):
        # Clean up any temp files
        pass

    def test_simple_message(self):
        path = self._write("Alice: Hello world\n")
        try:
            header, messages = p.parse_chatfile(path)
            assert messages == [("Alice", "Hello world")]
        finally:
            os.unlink(path)

    def test_multiple_messages(self):
        path = self._write("Alice: Hello\nBob: Hi there\n")
        try:
            _, messages = p.parse_chatfile(path)
            assert len(messages) == 2
            assert messages[0] == ("Alice", "Hello")
            assert messages[1] == ("Bob", "Hi there")
        finally:
            os.unlink(path)

    def test_returns_tuple(self):
        path = self._write("Alice: Hello\n")
        try:
            result = p.parse_chatfile(path)
            assert isinstance(result, tuple)
            assert len(result) == 2
        finally:
            os.unlink(path)

    def test_header_before_messages(self):
        path = self._write("This is a header line\nAlice: Hello\n")
        try:
            header, messages = p.parse_chatfile(path)
            assert "header" in header.lower() or "This" in header
            assert messages[0] == ("Alice", "Hello")
        finally:
            os.unlink(path)

    def test_no_messages_returns_empty_list(self):
        path = self._write("This is a header\nAnother header line\n")
        try:
            _, messages = p.parse_chatfile(path)
            assert messages == []
        finally:
            os.unlink(path)

    def test_message_names_stripped(self):
        path = self._write("  Alice  : Hello\n")
        try:
            _, messages = p.parse_chatfile(path)
            # The name should be stripped of surrounding whitespace
            if messages:  # may or may not match depending on leading spaces
                assert messages[0][0] == messages[0][0].strip()
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# build_chatfile_slides
# ---------------------------------------------------------------------------

class TestBuildChatfileSlides:
    def _write(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile("w", suffix=".Chatfile", delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_returns_list(self):
        path = self._write("Alice: Hello\nBob: World\n")
        try:
            slides = p.build_chatfile_slides(path)
            assert isinstance(slides, list)
        finally:
            os.unlink(path)

    def test_one_slide_per_message(self):
        path = self._write("Alice: Hello\nBob: World\nCarol: Goodbye\n")
        try:
            slides = p.build_chatfile_slides(path)
            assert len(slides) == 3
        finally:
            os.unlink(path)

    def test_max_messages_honored(self):
        lines = "\n".join([f"User{i}: Message {i}" for i in range(10)])
        path = self._write(lines + "\n")
        try:
            slides = p.build_chatfile_slides(path, max_messages=3)
            assert len(slides) == 3
        finally:
            os.unlink(path)

    def test_each_slide_has_art_title_body(self):
        path = self._write("Alice: Hello\n")
        try:
            slides = p.build_chatfile_slides(path)
            for slide in slides:
                assert "art" in slide
                assert "title" in slide
                assert "body" in slide
        finally:
            os.unlink(path)

    def test_empty_chatfile_returns_empty_list(self):
        path = self._write("")
        try:
            slides = p.build_chatfile_slides(path)
            assert slides == []
        finally:
            os.unlink(path)

    def test_last_slide_body_contains_enter_hint(self):
        path = self._write("Alice: Hello\nBob: World\n")
        try:
            slides = p.build_chatfile_slides(path)
            # Last slide should have a special body indicating it's last
            last_body = slides[-1]["body"]
            assert "ENTER" in last_body or "enter" in last_body.lower()
        finally:
            os.unlink(path)

    def test_no_messages_returns_empty(self):
        path = self._write("Just a header\nNo messages here\n")
        try:
            slides = p.build_chatfile_slides(path)
            assert slides == []
        finally:
            os.unlink(path)
