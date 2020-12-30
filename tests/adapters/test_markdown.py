import pytest

from shrikenet.adapters.markdown import Markdown
from shrikenet.entities.text_transformer import TextTransformer


@pytest.fixture
def text_transformer():
    return Markdown()


def test_is_a_text_transformer(text_transformer):
    assert isinstance(text_transformer, TextTransformer)


def test_empty_string_when_none(text_transformer):
    assert text_transformer.transform_to_html(None) == ''


def test_performs_a_markdown_transform(text_transformer):
    assert (
        text_transformer.transform_to_html('*foo bar*')
        == '<p><em>foo bar</em></p>'
    )


def test_transforms_strikeout(text_transformer):
    assert (
        text_transformer.transform_to_html('~~Strike this out.~~')
        == '<p><del>Strike this out.</del></p>'
    )


def test_transforms_subscript(text_transformer):
    assert (
        text_transformer.transform_to_html('H~2~O')
        == '<p>H<sub>2</sub>O</p>'
    )


def test_transforms_superscript(text_transformer):
    assert (
        text_transformer.transform_to_html('10^2^ = 100')
        == '<p>10<sup>2</sup> = 100</p>'
    )

