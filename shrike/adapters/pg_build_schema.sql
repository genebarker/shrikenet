-- create sequences
DROP SEQUENCE IF EXISTS app_user_seq;
CREATE SEQUENCE app_user_seq;

DROP SEQUENCE IF EXISTS post_seq;
CREATE SEQUENCE post_seq;

-- create data tables
DROP TABLE IF EXISTS app_user;
CREATE TABLE app_user (
    oid integer PRIMARY KEY,
    username varchar(20) UNIQUE,
    name varchar(50),
    password_hash varchar(128),
    needs_password_change boolean
);

DROP TABLE IF EXISTS post;
CREATE TABLE post (
    oid integer PRIMARY KEY,
    title varchar(50),
    body text,
    author_oid integer,
    created_time timestamp with time zone
);
