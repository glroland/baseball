import logging
from pprint import pprint
from feast import (
    FeatureStore,
)

logger = logging.getLogger(__name__)

# Setup Logging
logging.basicConfig(level=logging.DEBUG,
    handlers=[
        logging.StreamHandler()
    ])

feature_store = FeatureStore(repo_path="feature_repo")

feature_service = feature_store.get_feature_service("fs_game_play")

entity_sql = f"""
    SELECT
        game_play_id,
        event_timestamp
    FROM ({feature_store.get_data_source("source_pitch_count").get_table_query_string()}) as play
"""

df = feature_store.get_historical_features(
                        features=feature_service, 
                        entity_df=entity_sql
                ).to_df()

print(df.info())

print(df.head())

pprint(df)
