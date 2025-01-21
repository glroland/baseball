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
            entity_rows=[{"team_code": "ATL"}],
            features=[
                "fv_team:team_name",
            ],
        )
df = pd.DataFrame.from_dict(features.to_dict())

print(df.info())

print(df.head())

pprint(df)
