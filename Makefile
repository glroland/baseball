#
# Configuration
#
db_host ?= db
db_port ?= 5432
db_user ?= baseball_app
db_password ?= baseball123
db_name ?= baseball_db
db_connection_string ?= postgresql://$(db_user):$(db_password)@$(db_host):$(db_port)/$(db_name)
db_dba_user ?= postgres
db_dba_password ?= d8nnyr0cks
db_dba_connection_string ?= postgresql://$(db_dba_user):$(db_dba_password)@$(db_host):$(db_port)
model_registry_url ?= https://my-model-registry-rest.apps.ocpprod.home.glroland.com
model_registry_token ?= $(shell oc whoami -t)
model_registry_author ?= Baseball Author
model_dir ?= ../output/predict_pitch/
model_name ?= model.onnx
endpoint_url ?= http://localhost:8080

install:
	pip install -r requirements.txt

lint:
	pylint --recursive y src

db:
ifneq "$(db_dba_password)" "" 
	psql "$(db_dba_connection_string)" -f sql/drop_db.sql
	psql "$(db_dba_connection_string)" -f sql/create_db.sql
else
	psql -v ON_ERROR_STOP=1 -h $(db_host) -p $(db_port) -w -f sql/drop_db.sql
	psql -v ON_ERROR_STOP=1 -h $(db_host) -p $(db_port) -w -f sql/create_db.sql
endif
	psql -v ON_ERROR_STOP=1 "$(db_connection_string)" -w -f sql/create_tables.sql
ifeq "$(OS)" "Windows_NT"
	if not exist data\zips md data\zips
	if not exist output md output
	cd src && set "BASEBALL_DB_CONN_STRING=$(db_connection_string)" && jupyter nbconvert --to python ingest/ingest_retrosheet_data.ipynb --stdout  | python
else
	mkdir -p data/zips
	mkdir -p output
	cd src && jupyter nbconvert --to python ingest/ingest_retrosheet_data.ipynb --stdout  | BASEBALL_DB_CONN_STRING="$(db_connection_string)" python
endif

run:
	cd src && python import_events_app.py

help:
	cd src && python import_events_app.py --help

etest:
	cd src && python import_events_app.py ../data/raw/2000ANA.EVA  --save "$(db_connection_string)" --truncate --debug ../import_events_apps.log

edev:
ifeq "$(OS)" "Windows_NT"
	if not exist data\done md data\done
else
	mkdir -p data/done
endif
	cd src && python import_events_app.py ../data/raw/ --debug ../import_events_apps.log --move ../data/done

erestore:
ifeq "$(OS)" "Windows_NT"
	if not exist data\done md data\done
else
	mkdir -p data/done
endif
	mv data/done/* data/raw/

events:
ifeq "$(OS)" "Windows_NT"
	if not exist data\done md data\done
else
	mkdir -p data/done
endif
#	cd src && python import_events_app.py ../data/raw/  --save "$(db_connection_string)" --truncate --debug ../import_events_apps.log --skip-errors --move ../data/done
	cd src && python import_events_app.py ../data/raw/  --save "$(db_connection_string)" --debug ../import_events_apps.log --skip-errors --move ../data/done

model_server.test:
	cd src && MODEL_REGISTRY_URL="$(model_registry_url)" MODEL_REGISTRY_AUTHOR="$(model_registry_author)" MODEL_REGISTRY_TOKEN="$(model_registry_token)" python utils/model_server_client.py

api.dev:
	cd src && MODEL_REGISTRY_URL="$(model_registry_url)" MODEL_REGISTRY_AUTHOR="$(model_registry_author)" MODEL_REGISTRY_TOKEN="$(model_registry_token)" MODEL_DIR="$(model_dir)" ENDPOINT_URL="$(endpoint_url)" MODEL_NAME="$(model_name)" fastapi dev prediction_api.py

api.test:
	curl -X 'GET' 'http://localhost:8000/predict_pitch' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{ "pitch_index": 2, "pitch_count": 43, "runner_1b": "John", "runner_2b": "",  "runner_3b": "Jane", "is_home": true, "is_night": true, "score_deficit": -4}'

test:
	pytest
