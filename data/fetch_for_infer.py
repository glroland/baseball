import logging
from pprint import pprint
from feast import FeatureStore

logger = logging.getLogger(__name__)

# Setup Logging
logging.basicConfig(level=logging.DEBUG,
    handlers=[
        logging.StreamHandler()
    ])

feature_store = FeatureStore(repo_path="feature_repo")

feature_service = feature_store.get_feature_service("baseball_plays_v1")

entity_sql = f"""
    SELECT
        game_play_id,
        event_timestamp
    FROM ({feature_store.get_data_source("baseball_plays").get_table_query_string()}) as tmp
--    WHERE event_timestamp BETWEEN '2021-01-01' and '2025-12-31'
"""

training_df = feature_store.get_historical_features(
                        features=feature_service, 
                        entity_df=entity_sql
                ).to_df()

print(training_df.info())

print(training_df.head())

pprint(training_df)
