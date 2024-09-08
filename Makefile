#
# Configuration
#
db_host ?= tools
db_port ?= 5432
db_user ?= baseball_app
db_password ?= baseball123
db_name ?= baseball_db
db_connection_string ?= "postgresql://$(db_user):$(db_password)@$(db_host)/$(db_name)"
db_dba_user ?= postgres
db_dba_password ?= r3dh@t123

install:
	pip install -r requirements.txt

lint:
	pylint ingest/*.py

db:
ifneq "$(db_dba_password)" "" 
	PGPASSWORD=$(db_dba_password) psql -h $(db_host) -p $(db_port) -U $(db_dba_user) -f sql/drop_db.sql
	PGPASSWORD=$(db_dba_password) psql -h $(db_host) -p $(db_port) -U $(db_dba_user) -f sql/create_db.sql
else
	psql -h $(db_host) -p $(db_port) -w -f sql/drop_db.sql
	psql -h $(db_host) -p $(db_port) -w -f sql/create_db.sql
endif
	PGPASSWORD=$(db_password) psql -h $(db_host) -p $(db_port) -U $(db_user) -d $(db_name) -w -f sql/create_tables.sql
	cd ingest && jupyter nbconvert --to python ingest_retrosheet_data.ipynb --stdout  | BASEBALL_DB_CONN_STRING=$(db_connection_string) python
