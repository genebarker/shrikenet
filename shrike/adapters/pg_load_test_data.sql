INSERT INTO app_user (oid, username, name, password_hash)
VALUES
    (nextval('app_user_seq'), 'test', 'Mr. Test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
    (nextval('app_user_seq'), 'other', 'Mrs. Other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO post (oid, title, body, author_oid, created_time)
VALUES
    (nextval('post_seq'), 'test title', 'test' || E'\n' || 'body', 1, '2018-01-01 00:00:00+0');
