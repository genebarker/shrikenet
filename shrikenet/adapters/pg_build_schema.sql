-- create sequences
DROP SEQUENCE IF EXISTS app_user_seq;
CREATE SEQUENCE app_user_seq;

DROP SEQUENCE IF EXISTS event_seq;
CREATE SEQUENCE event_seq;

DROP SEQUENCE IF EXISTS post_seq;
CREATE SEQUENCE post_seq;

-- create data tables
DROP TABLE IF EXISTS app_user;
CREATE TABLE app_user (
    oid integer PRIMARY KEY,
    username varchar(20) UNIQUE,
    name varchar(50),
    password_hash varchar(128),
    needs_password_change boolean,
    is_locked boolean,
    is_dormant boolean,
    ongoing_password_failure_count integer,
    last_password_failure_time timestamp with time zone
);

DROP TABLE IF EXISTS event;
CREATE TABLE event (
    oid integer PRIMARY KEY,
    time timestamp with time zone,
    app_user_oid integer,
    tag varchar(50),
    text text,
    usecase_tag varchar(50)
);

DROP TABLE IF EXISTS post;
CREATE TABLE post (
    oid integer PRIMARY KEY,
    title varchar(50),
    body text,
    author_oid integer,
    created_time timestamp with time zone
);

DROP TABLE IF EXISTS rule;
CREATE TABLE rule (
    tag varchar(50) PRIMARY KEY,
    tag_value text,
    tag_type varchar(20)
);

-- load default data
INSERT INTO rule (tag, tag_value, tag_type)
VALUES
    ('login_fail_threshold_count', '3', 'int'),
    ('login_fail_lock_minutes', '15', 'int');
