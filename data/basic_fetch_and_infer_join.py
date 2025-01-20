import logging
from pprint import pprint
from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
)
from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination

logger = logging.getLogger(__name__)

# Setup Logging
logging.basicConfig(level=logging.DEBUG,
    handlers=[
        logging.StreamHandler()
    ])

feature_store = FeatureStore(repo_path="feature_repo")


# This groups features into a model version
feature_service = FeatureService(
    name="play",
    features=[pitch_count_fv, runners_fv]
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)

entity_sql = f"""
    SELECT
        runner_1b,
        pitch_count,
        event_timestamp
    FROM ({feature_store.get_data_source("pitch_count").get_table_query_string()}) as tmp
    WHERE event_timestamp BETWEEN '2024-09-01' and '2025-12-31'
"""

training_df = feature_store.get_historical_features(features=feature_service, 
                                                    entity_df=entity_sql
                ).to_df()

print(training_df.info())

print(training_df.head())

pprint(training_df)
