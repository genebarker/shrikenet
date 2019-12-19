-- assumes:
--   use of SwapcaseAdapter
--   passwords are the same as the usernames
INSERT INTO app_user (oid, username, name, password_hash,
                      needs_password_change)
VALUES
    (nextval('app_user_seq'), 'test', 'Mr. Test', 'TEST', false),
    (nextval('app_user_seq'), 'other', 'Mrs. Other', 'OTHER', false);

INSERT INTO post (oid, title, body, author_oid, created_time)
VALUES
    (nextval('post_seq'), 'test title', 'test' || E'\n' || 'body', 1,
     '2018-01-01 00:00:00+0');
