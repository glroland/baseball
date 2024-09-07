create user baseball_app with password 'baseball123';
ALTER USER baseball_app WITH SUPERUSER;

create database baseball_db with owner baseball_app;
