import cmarkgfm
from cmarkgfm.cmark import Options as cmarkgfmOptions


from shrikenet.entities.text_transformer import TextTransformer


class MarkdownAdapter(TextTransformer):

    def __init__(self):
        self.options = (
            cmarkgfmOptions.CMARK_OPT_FOOTNOTES
            | cmarkgfmOptions.CMARK_OPT_STRIKETHROUGH_DOUBLE_TILDE
        )

    def transform_to_html(self, plain_text):
        if plain_text is None:
            return ""

        return cmarkgfm.github_flavored_markdown_to_html(
            plain_text, self.options
        )
