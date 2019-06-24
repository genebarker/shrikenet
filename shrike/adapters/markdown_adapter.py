import html

import pypandoc

from shrike.entities.text_transformer import TextTransformer

class MarkdownAdapter(TextTransformer):

    def __init__(self):
        pass

    def transform_to_html(self, plain_text):
        if plain_text is None: return ''
        escaped_text = html.escape(plain_text)
        input_format = 'md'
        output_format = 'html5'
        output = pypandoc.convert_text(escaped_text, output_format, input_format)
        return output
