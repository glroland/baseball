import logging
from pprint import pprint
from feast import (
    FeatureStore,
)
import pandas as pd

logger = logging.getLogger(__name__)

# Setup Logging
logging.basicConfig(level=logging.DEBUG,
    handlers=[
        logging.StreamHandler()
    ])

feature_store = FeatureStore(repo_path="feature_repo")

features = feature_store.get_online_features(
            entity_rows=[{"game_play_id": game_play_id} for game_play_id in range(1, 1000)],
            features=[
                "fv_pitch_count:pitch_count",
            ],
        )
df = pd.DataFrame.from_dict(features.to_dict())

print(df.info())

print(df.head())

pprint(df)
