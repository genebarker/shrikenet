-- create sequences
DROP SEQUENCE IF EXISTS app_user_seq;
CREATE SEQUENCE app_user_seq;

DROP SEQUENCE IF EXISTS post_seq;
CREATE SEQUENCE post_seq;

-- create data tables
DROP TABLE IF EXISTS app_user;
CREATE TABLE app_user (
    oid INTEGER,
    username VARCHAR(20),
    name VARCHAR(50),
    password_hash VARCHAR(64),
    CONSTRAINT app_user_pkey PRIMARY KEY(oid)
);

DROP TABLE IF EXISTS post;
CREATE TABLE post (
    oid INTEGER,
    title VARCHAR(50),
    body TEXT,
    author_oid INTEGER,
    created_time TIMESTAMP WITH TIME ZONE,
    CONSTRAINT post_pkey PRIMARY KEY(oid)
);
