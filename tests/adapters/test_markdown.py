import pytest

from shrikenet.adapters.markdown import Markdown
from shrikenet.entities.text_transformer import TextTransformer


class TestMarkdown:

    @pytest.fixture
    def text_transformer(self):
        return Markdown()

    def test_is_a_text_transformer(self, text_transformer):
        assert isinstance(text_transformer, TextTransformer)

    def test_empty_string_when_none(self, text_transformer):
        assert text_transformer.transform_to_html(None) == ''

    def test_performs_a_markdown_transform(self, text_transformer):
        assert (
            text_transformer.transform_to_html('*foo bar*')
            == '<p><em>foo bar</em></p>\n'
        )

    def test_raw_html_escaped(self, text_transformer):
        assert (
            text_transformer.transform_to_html('<b>foo bar</b>')
            == '<p>&lt;b&gt;foo bar&lt;/b&gt;</p>\n'
        )
