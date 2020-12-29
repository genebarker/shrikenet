import mistune

from shrikenet.entities.text_transformer import TextTransformer


class Markdown(TextTransformer):

    def __init__(self):
        self.markdown = mistune.create_markdown(
            plugins=['strikethrough', 'table', 'footnotes']
        )

    def transform_to_html(self, plain_text):
        if plain_text is None:
            return ''

        return self.markdown(plain_text)
