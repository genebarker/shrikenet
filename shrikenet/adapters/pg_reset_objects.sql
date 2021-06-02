-- reset sequences
SELECT SETVAL('app_user_seq', 1, FALSE);
SELECT SETVAL('log_entry_seq', 1, FALSE);
SELECT SETVAL('post_seq', 1, FALSE);

-- reset data tables
DELETE FROM app_user;
DELETE FROM log_entry;
DELETE FROM post;

DELETE FROM rule;
INSERT INTO rule (tag, tag_value, tag_type)
VALUES
    ('login_fail_threshold_count', '3', 'int'),
    ('login_fail_lock_minutes', '15', 'int');
