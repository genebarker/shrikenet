import pytest

from shrike.adapters.markdown_adapter import MarkdownAdapter
from shrike.entities.text_transformer import TextTransformer

class TestInterfaceIsAbstract:

    @pytest.fixture
    def text_transformer(self):
        class FakeTransformer(TextTransformer):
            def __init__(self):
                pass
        
        return FakeTransformer()

    def test_interface_cant_be_instantiated(self):
        with pytest.raises(NotImplementedError):
            TextTransformer()

    def test_transform_method_cant_be_called(self, text_transformer):
        with pytest.raises(NotImplementedError):
            text_transformer.transform_to_html(None)


class TestMarkdownAdapterUsed:

    @pytest.fixture
    def text_transformer(self):
        return MarkdownAdapter()

    def test_is_a_text_transformer(self, text_transformer):
        assert isinstance(text_transformer, TextTransformer)

    def test_empty_string_when_none(self, text_transformer):
        assert text_transformer.transform_to_html(None) == ''

    # def test_empty_when_just_whitespace(self, text_transformer):
    #     assert text_transformer.transform_to_html('   ') == ''

    # def test_performs_a_markdown_transform(self, text_transformer):
    #     assert text_transformer.transform_to_html('*foo bar*') == '<p><em>foo bar</em></p>'
