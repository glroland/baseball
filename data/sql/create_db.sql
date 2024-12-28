create user baseball_app with password 'baseball123';
ALTER USER baseball_app WITH SUPERUSER;
create database baseball_db with owner baseball_app;

create user baseball_ml with password 'baseball123';
ALTER USER baseball_ml WITH SUPERUSER;
create database baseball_features_db with owner baseball_ml;
