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
model_dir ?= ../output/predict_play/
model_name ?= Baseball Predict Play - 20241204-1 - 2024-12-05T03:12:36.754Z metrics
endpoint_url ?= https://baseball-predict-play-20241204-1-2024-12-05t031236754z-baseball.apps.ocpprod.home.glroland.com/v2/models/baseball-predict-play-20241204-1-2024-12-05t031236754z/infer

install:
	pip install -r data/requirements.txt
	pip install -r import-app/requirements.txt
	pip install -r predict-svc/requirements.txt

lint:
	pylint --recursive y --exit-zero data/src
	pylint --recursive y --exit-zero import-app/src
	pylint --recursive y --exit-zero predict-svc/src

init:
ifeq "$(OS)" "Windows_NT"
	if not exist target md target
	if not exist target\zips md target\zips
	if not exist target\raw md target\raw
	if not exist target\done md target\done
else
	mkdir -p target/zips
	mkdir -p target/raw
	mkdir -p target/done
endif

db: init
ifneq "$(db_dba_password)" "" 
	psql "$(db_dba_connection_string)" -f data/sql/drop_db.sql
	psql "$(db_dba_connection_string)" -f data/sql/create_db.sql
else
	psql -v ON_ERROR_STOP=1 -h $(db_host) -p $(db_port) -w -f data/sql/drop_db.sql
	psql -v ON_ERROR_STOP=1 -h $(db_host) -p $(db_port) -w -f data/sql/create_db.sql
endif
	psql -v ON_ERROR_STOP=1 "$(db_connection_string)" -w -f data/sql/create_tables.sql
ifeq "$(OS)" "Windows_NT"
	cd data/src/ingest && set "BASEBALL_DB_CONN_STRING=$(db_connection_string)" && jupyter nbconvert --to python ingest_retrosheet_data.ipynb --stdout  | python
else
	mkdir -p target/zips
	mkdir -p target/raw
	mkdir -p target/done
	mkdir -p target/output
	cd data/src/ingest && jupyter nbconvert --to python ingest_retrosheet_data.ipynb --stdout  | BASEBALL_DB_CONN_STRING="$(db_connection_string)" python
endif

train:
	cd data/src/train && jupyter nbconvert --to python train_predict_pitch_model.ipynb --stdout  | DB_CONNECTION_STRING="$(db_connection_string)" OUTPUT_DIR="../../../target/models/predict_pitch/" python
	cd data/src/train && jupyter nbconvert --to python train_predict_play_model.ipynb --stdout  | DB_CONNECTION_STRING="$(db_connection_string)" OUTPUT_DIR="../../../target/models/predict_play/" python

run:
	cd import-app/src && python import_events_app.py

help:
	cd import-app/src && python import_events_app.py --help

etest: init
	cd import-app/src && python import_events_app.py ../../target/raw/2000ANA.EVA  --save "$(db_connection_string)" --truncate --debug ../../target/import_events_apps.log

edev: init
	cd import-app/src && python import_events_app.py ../../target/raw/ --debug ../../target/import_events_apps.log --move ../../target/done

erestore: init
ifeq "$(OS)" "Windows_NT"
	move target/done/* target/raw/
else
	mv target/done/* target/raw/
endif

events: init
#	cd src && python import_events_app.py ../data/raw/  --save "$(db_connection_string)" --truncate --debug ../import_events_apps.log --skip-errors --move ../data/done
	cd import-app/src && python import_events_app.py ../../target/raw/  --save "$(db_connection_string)" --debug ../../target/import_events_apps.log --skip-errors --move ../../target/done

model_server.test:
	cd predict-svc/src && MODEL_REGISTRY_URL="$(model_registry_url)" MODEL_REGISTRY_AUTHOR="$(model_registry_author)" MODEL_REGISTRY_TOKEN="$(model_registry_token)" python model_server_client.py

api.build:
	podman build -f predict-svc/Dockerfile --tag=predict-svc:latest .

api.dev:
	cd predict-svc/src && MODEL_REGISTRY_URL="$(model_registry_url)" MODEL_REGISTRY_AUTHOR="$(model_registry_author)" MODEL_REGISTRY_TOKEN="$(model_registry_token)" MODEL_DIR="$(model_dir)" ENDPOINT_URL="$(endpoint_url)" MODEL_NAME="$(model_name)" CONFIG_FILE="../config.ini" fastapi dev app.py

api.run:
	cd predict-svc/src && MODEL_REGISTRY_URL="$(model_registry_url)" MODEL_REGISTRY_AUTHOR="$(model_registry_author)" MODEL_REGISTRY_TOKEN="$(model_registry_token)" MODEL_DIR="$(model_dir)" ENDPOINT_URL="$(endpoint_url)" MODEL_NAME="$(model_name)" CONFIG_FILE="../config.ini" fastapi run app.py

api.test.pitch:
	curl -X 'GET' 'http://localhost:8000/predict_pitch' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{ "pitch_index": 2, "pitch_count": 43, "runner_1b": "John", "runner_2b": "",  "runner_3b": "Jane", "is_home": true, "is_night": true, "score_deficit": -4}'

api.test.play:
	curl -X 'GET' 'http://localhost:8000/predict_play' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{ "pitch_index": 3, "pitch_count": 45, "score_deficit": 4, "runner_1b": "", "runner_2b": "John", "runner_3b": "Jane", "batting_hand": "L", "pitching_hand": "R", "outs": 2 }'

test:
	cd import-app && pytest
