#
# Configuration
#
db_host ?= localhost
db_port ?= 5432
db_user ?= baseball_app
db_password ?= baseball123
db_name ?= baseball_db
db_connection_string ?= "postgresql://$(db_user):$(db_password)@$(db_host):$(db_port)/$(db_name)"
db_dba_user ?= postgres
db_dba_password ?= d8nnyr0cks
db_dba_connection_string ?= "postgresql://$(db_dba_user):$(db_dba_password)@$(db_host):$(db_port)"

install:
	pip install -r requirements.txt

lint:
	pylint --recursive y src

db:
ifneq "$(db_dba_password)" "" 
	psql $(db_dba_connection_string) -f sql/drop_db.sql
	psql $(db_dba_connection_string) -f sql/create_db.sql
else
	psql -v ON_ERROR_STOP=1 -h $(db_host) -p $(db_port) -w -f sql/drop_db.sql
	psql -v ON_ERROR_STOP=1 -h $(db_host) -p $(db_port) -w -f sql/create_db.sql
endif
	psql -v ON_ERROR_STOP=1 $(db_connection_string) -w -f sql/create_tables.sql
	cd src && jupyter nbconvert --to python ingest/ingest_retrosheet_data.ipynb --stdout  | BASEBALL_DB_CONN_STRING=$(db_connection_string) python

run:
	cd src && python import_events_app.py

help:
	cd src && python import_events_app.py --help

etest:
	cd src && python import_events_app.py ../data/raw/2000ANA.EVA  --save $(db_connection_string) --truncate --debug ../import_events_apps.log

edev:
	mkdir -p data/done
	cd src && python import_events_app.py ../data/raw/ --debug ../import_events_apps.log --move ../data/done

erestore:
	mkdir -p data/done
	mv data/done/* data/raw/

events:
	mkdir -p data/done
	cd src && python import_events_app.py ../data/raw/  --save $(db_connection_string) --truncate --debug ../import_events_apps.log --skip-errors --move ../data/done

test:
	pytest
