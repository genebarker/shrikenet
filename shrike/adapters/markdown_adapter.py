import io 

import mistletoe

from shrike.entities.text_transformer import TextTransformer

class MarkdownAdapter(TextTransformer):

    def __init__(self):
        pass

    def transform_to_html(self, plain_text):
        text_stream = io.StringIO(plain_text)
        with text_stream as stream:
            return mistletoe.markdown(stream)
