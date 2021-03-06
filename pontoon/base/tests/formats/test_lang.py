import os.path
from textwrap import dedent

from django_nose.tools import assert_equal

from pontoon.base.formats import lang
from pontoon.base.tests import assert_attributes_equal, TestCase
from pontoon.base.tests.formats import FormatTestsMixin


class LangTests(FormatTestsMixin, TestCase):
    parse = staticmethod(lang.parse)

    def test_load_utf8_bom(self):
        """
        Ensure that the langfile parser can load UTF-8 files with an encoded
        BOM at the beginning of the file.

        See https://docs.python.org/2/library/codecs.html for details (search
        for the string "utf-8-sig").
        """
        current_dir = os.path.dirname(__file__)
        resource = lang.parse(os.path.join(current_dir, 'bom.lang'))
        assert_equal(len(resource.translations), 1)
        assert_attributes_equal(
            resource.translations[0],
            source_string='Source String',
            strings={None: 'Translated String'}
        )

    def test_parse_comments_arbitrary_hash(self):
        """Comments can have an arbitrary amount of #s at the start."""
        path, resource = self.parse_string(dedent("""
            # 1 hash
            ## 2 hash
            ### 3 hash

            # 1 hash
            ## 2 hash
            ### 3 hash
            ; Source
            Translated
        """))

        assert_equal(resource.children[1].content, '1 hash')
        assert_equal(resource.children[2].content, '2 hash')
        assert_equal(resource.children[3].content, '3 hash')
        assert_equal(resource.translations[0].comments, ['1 hash', '2 hash', '3 hash'])

    def test_parse_eof(self):
        """Langfiles do not need to end in a newline."""
        path, resource = self.parse_string(';Source\nTranslation')
        assert_equal(resource.translations[0].source_string, 'Source')
        assert_equal(resource.translations[0].strings, {None: 'Translation'})

    def test_preserve_comment_hashes(self):
        """
        If a langfile is parsed and then saved without being modified,
        it should not modify the contents of the file.
        """
        expected = dedent("""
            ## Example langfile with a few constructs that might break

            # Entity comment
            ;Source
            Translated

            # Single hash standalone comment

            ### Entity comment with multiple hashes
            ;Identical
            Identical {ok}

            ###Free standing comment at the end. WOW
        """)
        path, resource = self.parse_string(expected)
        resource.save(self.locale)
        self.assert_file_content(path, expected)
