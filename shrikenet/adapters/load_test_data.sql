-- assumes:
--   use of SwapcaseAdapter
INSERT INTO app_user (username, name, password_hash,
                      needs_password_change, is_locked, is_dormant,
                      ongoing_password_failure_count,
                      last_password_failure_time)
VALUES
    ('test', 'Mr. Test', 'TEST', 'false', 'false', 'false', 1,
     '2019-01-02 18:00:00'),
    ('other', 'Mrs. Other', 'OTHER', 'false', 'false', 'false', 0,
      NULL),
    ('mrlock', 'Mr. Lock', 'MRLOCK', 'false', 'true', 'false', 10,
     datetime()),
    ('fmulder', 'Fox Mulder', 'SCULLY', 'false', 'false', 'false', 0,
     NULL);

INSERT INTO post (title, body, author_oid, created_time)
VALUES
    ('test title', 'test body', 1, '2018-01-01 00:00:00');
