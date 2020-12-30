import markdown

from shrikenet.entities.text_transformer import TextTransformer


class Markdown(TextTransformer):

    def __init__(self):
        self.markdown = markdown.Markdown(
            extensions=[
                'abbr',
                'fenced_code',
                'footnotes',
                'sane_lists',
                'smarty',
                'tables',
                'pymdownx.tilde',
                'pymdownx.caret',
            ],
            extension_configs={
                'smarty': {
                    'smart_quotes': False,
                    'smart_angled_quotes': False,
                }
            },
            output_format='html5',
        )

    def transform_to_html(self, plain_text):
        if plain_text is None:
            return ''

        return self.markdown.convert(plain_text)
