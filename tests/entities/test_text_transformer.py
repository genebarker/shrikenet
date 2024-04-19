import pytest

from shrikenet.entities.text_transformer import TextTransformer


def test_interface_cant_be_instantiated():
    with pytest.raises(NotImplementedError):
        TextTransformer()


@pytest.fixture
def text_transformer():
    class FakeTransformer(TextTransformer):
        def __init__(self):
            pass

    return FakeTransformer()


def test_transform_method_cant_be_called(text_transformer):
    with pytest.raises(NotImplementedError):
        text_transformer.transform_to_html(None)
