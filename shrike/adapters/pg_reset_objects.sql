-- reset sequences
SELECT SETVAL('app_user_seq', 1, FALSE);
SELECT SETVAL('post_seq', 1, FALSE);

-- reset data tables
DELETE FROM app_user;
DELETE FROM post;
DELETE FROM parameter;
