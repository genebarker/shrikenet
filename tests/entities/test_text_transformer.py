import pytest

from shrike.entities.text_transformer import TextTransformer

class TestTextTransformer:

    def test_cant_be_instantiated(self):
        with pytest.raises(NotImplementedError):
            TextTransformer()

    @pytest.fixture
    def text_transformer(self):
        class FakeTransformer(TextTransformer):
            def __init__(self):
                pass
        return FakeTransformer()

    def test_transform_method_abstract(self, text_transformer):
        with pytest.raises(NotImplementedError):
            text_transformer.transform(None)
