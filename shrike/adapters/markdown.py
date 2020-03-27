import pypandoc

from shrike.entities.text_transformer import TextTransformer


class Markdown(TextTransformer):

    def __init__(self):
        pass

    def transform_to_html(self, plain_text):
        if plain_text is None:
            return ''

        input_format = 'markdown-raw_html'
        output_format = 'html5'
        output = pypandoc.convert_text(plain_text, output_format, input_format)
        return output
