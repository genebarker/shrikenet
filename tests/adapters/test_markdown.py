import pytest

from shrikenet.adapters.markdown import MarkdownAdapter
from shrikenet.entities.text_transformer import TextTransformer


@pytest.fixture
def text_transformer():
    return MarkdownAdapter()


def test_is_a_text_transformer(text_transformer):
    assert isinstance(text_transformer, TextTransformer)


def test_empty_string_when_none(text_transformer):
    assert text_transformer.transform_to_html(None) == ""


def test_performs_a_markdown_transform(text_transformer):
    assert (
        text_transformer.transform_to_html("*foo bar*")
        == "<p><em>foo bar</em></p>\n"
    )


def test_transforms_strikeout(text_transformer):
    assert (
        text_transformer.transform_to_html("~~Strike this out.~~")
        == "<p><del>Strike this out.</del></p>\n"
    )
