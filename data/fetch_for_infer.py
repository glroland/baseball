from pprint import pprint
from feast import FeatureStore

feature_store = FeatureStore(repo_path="feature_repo")

feature_service = feature_store.get_feature_service("baseball_plays_v1")

entity_sql = f"""
    SELECT
        driver_id,
        event_timestamp
    FROM {feature_store.get_data_source("baseball_plays").get_table_query_string()}
    WHERE event_timestamp BETWEEN '2021-01-01' and '2021-12-31'
"""

training_df = feature_store.get_historical_features(
                        features=feature_service, 
                        entity_df=entity_sql
                ).to_df()


#feature_vector = store.get_online_features(
#    features=[
#        "baseball_plays_fv:pitch_index",
#        "baseball_plays_fv:pitch_count",
#        "baseball_plays_fv:batting_hand",
#        "baseball_plays_fv:pitching_hand",
#        "baseball_plays_fv:runner_1b",
#        "baseball_plays_fv:runner_2b",
#        "baseball_plays_fv:runner_3b",
#        "baseball_plays_fv:outs",
#        "baseball_plays_fv:home_team_flag",
#        "baseball_plays_fv:score_home",
#        "baseball_plays_fv:score_visitor",
#        "baseball_plays_fv:primary_play_type_cd",
#    ],
#    entity_rows=[
#        # {join_key: entity_value}
##        {"driver_id": 1004},
##        {"driver_id": 1005},
#    ],
#).to_dict()

#training_df = store.get_historical_features(
#    entity_df=entity_df,
#    features=store.get_feature_service("model_v1"),
#).to_df()
#print(training_df.head())

#pprint(feature_vector)
