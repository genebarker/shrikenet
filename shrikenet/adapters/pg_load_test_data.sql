-- assumes:
--   use of SwapcaseAdapter
--   passwords are the same as the usernames
INSERT INTO app_user (oid, username, name, password_hash,
                      needs_password_change, is_locked, is_dormant,
                      ongoing_password_failure_count,
                      last_password_failure_time)
VALUES
    (nextval('app_user_seq'), 'test', 'Mr. Test', 'TEST', false, false,
     false, 1, '2019-01-02 18:00:00+0'),
    (nextval('app_user_seq'), 'other', 'Mrs. Other', 'OTHER', false, false,
     false, 0, NULL),
    (nextval('app_user_seq'), 'mrlock', 'Mr. Lock', 'MRLOCK', false, true,
     false, 10, now());

INSERT INTO post (oid, title, body, author_oid, created_time)
VALUES
    (nextval('post_seq'), 'test title', 'test body', 1,
     '2018-01-01 00:00:00+0');
