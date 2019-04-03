from datetime import datetime, timezone

import pytest

from shrike.entities.post import Post


GOOD_OID = 100
GOOD_AUTHOR_OID = 111
GOOD_CREATED_TIME = datetime(2018, 12, 31, 23, 58, tzinfo=timezone.utc)
GOOD_TITLE = 'The World is Doomed'
GOOD_BODY = 'No hot sauce was found in the house.'

class TestGeneralProperties:

    def test_minimal_init(self):
        post = Post(GOOD_TITLE, GOOD_BODY)
        assert post.oid is None
        assert post.title == GOOD_TITLE
        assert post.body == GOOD_BODY
        assert post.author_oid is None
        assert post.created_time is None

    def test_keyword_init(self):
        post = Post(
            oid=GOOD_OID,
            title=GOOD_TITLE,
            body=GOOD_BODY,
            author_oid=GOOD_AUTHOR_OID,
            created_time=GOOD_CREATED_TIME,
        )
        assert post.oid == GOOD_OID
        assert post.title == GOOD_TITLE
        assert post.body == GOOD_BODY
        assert post.author_oid == GOOD_AUTHOR_OID
        assert post.created_time == GOOD_CREATED_TIME
