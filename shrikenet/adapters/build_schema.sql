-- create data tables
DROP TABLE IF EXISTS app_user;
CREATE TABLE app_user (
    oid INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    name TEXT,
    password_hash TEXT,
    needs_password_change TEXT ,
    is_locked TEXT,
    is_dormant TEXT,
    ongoing_password_failure_count INTEGER,
    last_password_failure_time TEXT
);

DROP TABLE IF EXISTS log_entry;
CREATE TABLE log_entry (
    oid INTEGER PRIMARY KEY,
    time TEXT,
    app_user_oid INTEGER,
    tag TEXT,
    text TEXT,
    usecase_tag TEXT
);

DROP TABLE IF EXISTS post;
CREATE TABLE post (
    oid INTEGER PRIMARY KEY,
    title TEXT,
    body TEXT,
    author_oid INTEGER,
    created_time TEXT
);

DROP TABLE IF EXISTS rule;
CREATE TABLE rule (
    tag TEXT PRIMARY KEY,
    tag_value TEXT,
    tag_type TEXT
);

-- load default data
INSERT INTO rule (tag, tag_value, tag_type)
VALUES
    ('login_fail_threshold_count', '3', 'int'),
    ('login_fail_lock_minutes', '15', 'int');
