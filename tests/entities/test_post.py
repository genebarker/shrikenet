from datetime import datetime, timedelta, timezone

import pytest

from shrike.entities.post import Post


GOOD_OID = 100
GOOD_AUTHOR_OID = 111
GOOD_CREATED_TIME = datetime(2018, 12, 31, 23, 58, tzinfo=timezone.utc)
GOOD_TITLE = 'The World is Doomed'
GOOD_BODY = 'No hot sauce was found in the house.'

def create_good_post():
    return Post(
            oid=GOOD_OID,
            title=GOOD_TITLE,
            body=GOOD_BODY,
            author_oid=GOOD_AUTHOR_OID,
            created_time=GOOD_CREATED_TIME,
        )
    
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

class TestEquals:

    def test_equals(self):
        post_one = create_good_post()
        post_two = create_good_post()
        assert post_one == post_two

    def test_unequal_when_class_different(self):
        class FakePost:
            def __init__(self, title, body):
                self.title = title
                self.body = body
        
        post_one = Post(GOOD_TITLE, GOOD_BODY)
        post_two = FakePost(GOOD_TITLE, GOOD_BODY)
        assert post_one != post_two

    @pytest.mark.parametrize(('oid', 'title', 'body', 'author_oid', 'created_time'), (
        (999, GOOD_TITLE, GOOD_BODY, GOOD_AUTHOR_OID, GOOD_CREATED_TIME),
        (GOOD_OID, 'Different', GOOD_BODY, GOOD_AUTHOR_OID, GOOD_CREATED_TIME),
        (GOOD_OID, GOOD_TITLE, 'Different', GOOD_AUTHOR_OID, GOOD_CREATED_TIME),
        (GOOD_OID, GOOD_TITLE, GOOD_BODY, 999, GOOD_CREATED_TIME),
        (GOOD_OID, GOOD_TITLE, GOOD_BODY, GOOD_AUTHOR_OID, GOOD_CREATED_TIME + timedelta(seconds=1)),
    ))
    def test_unequal_when_attribute_different(
            self, oid, title, body, author_oid, created_time):
        post_one = create_good_post()
        post_two = Post(
            oid=oid,
            title=title,
            body=body,
            author_oid=author_oid,
            created_time=created_time,
        )
        assert post_one != post_two
