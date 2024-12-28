from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)
from datetime import timedelta

import pandas as pd

from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    Project,
    PushSource,
    RequestSource,
)
from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64, Int64, Int32, Bool, String

project = Project(name="baseball", description="A project for driver statistics")
baseball_play_entity = Entity(name="baseball_play", join_keys=["game_play_id"])

baseball_plays_source = PostgreSQLSource(
    name="baseball_plays",
    query="""
        select random() as r_id, game_play.game_play_id as game_play_id, game_play_atbat.player_code as player_code, pitch_index, home_team_flag, game_play_atbat.score_home as score_home, game_play_atbat.score_visitor as score_visitor, sky, night_flag, temperature, wind_direction, wind_speed, precipitation, field_condition, roster_batter.batting_hand as batting_hand, roster_pitcher.throw_hand as pitching_hand, runner_1b, runner_2b, runner_3b, primary_play_type_cd, outs,
        (select count(*)
         from game_play_atbat pc_atbat, game_play_atbat_pitch pc_pitch, pitch_type pc_pitch_type
         where pc_pitch.game_play_id = pc_atbat.game_play_id
         and pc_atbat.game_play_id = game_play.game_play_id
         and pc_atbat.pitcher = game_play_atbat.pitcher  
         and pc_pitch_type.pitch_type_cd = pc_pitch.pitch_type_cd
         and pc_pitch_type.ball_or_strike is not null
         and pc_pitch.pitch_index < game_play_atbat_pitch.pitch_index
        ) as pitch_count, now() as event_timestamp, now() as create_timestamp
        from game, game_play, game_play_atbat, game_play_atbat_pitch, roster as roster_batter, roster as roster_pitcher
        where game.game_id = game_play.game_id
        and game_play_atbat.game_play_id = game_play.game_play_id
        and game_play_atbat_pitch.game_play_id = game_play.game_play_id     
        and roster_batter.player_code = game_play_atbat.player_code
        and roster_batter.season_year = date_part('year', game.game_date)
        and roster_pitcher.player_code = game_play_atbat.pitcher
        and roster_pitcher.season_year = roster_batter.season_year
        order by r_id 

limit 100
    """,
    timestamp_field="event_timestamp",
    created_timestamp_column="create_timestamp",
)

baseball_plays_fv = FeatureView(
    name="baseball_plays_fv",
    entities=[baseball_play_entity],
#    ttl=timedelta(days=1),
    schema=[
        Field(name="pitch_index", dtype=Int32),
        Field(name="pitch_count", dtype=Int32, description="Average daily trips"),
        Field(name="batting_hand", dtype=String, description="Average daily trips"),
        Field(name="pitching_hand", dtype=String, description="Average daily trips"),
        Field(name="runner_1b", dtype=String),
        Field(name="runner_2b", dtype=String, description="Average daily trips"),
        Field(name="runner_3b", dtype=String),
        Field(name="outs", dtype=Int32),
        Field(name="home_team_flag", dtype=Bool),
        Field(name="score_home", dtype=Int32, description="Average daily trips"),
        Field(name="score_visitor", dtype=Int32),
        Field(name="primary_play_type_cd", dtype=String),
    ],
    online=True,
    source=baseball_plays_source
)

# This groups features into a model version
baseball_plays_v1 = FeatureService(
    name="baseball_plays_v1",
    features=[
        baseball_plays_fv[["pitch_index"]],
        baseball_plays_fv[["pitch_count"]],
        baseball_plays_fv[["batting_hand"]],
        baseball_plays_fv[["pitching_hand"]],
        baseball_plays_fv[["runner_1b"]],
        baseball_plays_fv[["runner_2b"]],
        baseball_plays_fv[["runner_3b"]],
        baseball_plays_fv[["outs"]],
        baseball_plays_fv[["home_team_flag"]],
        baseball_plays_fv[["score_home"]],
        baseball_plays_fv[["score_visitor"]],
        baseball_plays_fv[["primary_play_type_cd"]],
    ],
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)



"""

# Define a request data source which encodes features / information only
# available at request time (e.g. part of the user initiated HTTP request)
input_request = RequestSource(
    name="vals_to_add",
    schema=[
        Field(name="val_to_add", dtype=Int64),
        Field(name="val_to_add_2", dtype=Int64),
    ],
)


# Define an on demand feature view which can generate new features based on
# existing feature views and RequestSource features
@on_demand_feature_view(
    sources=[driver_stats_fv, input_request],
    schema=[
        Field(name="conv_rate_plus_val1", dtype=Float64),
        Field(name="conv_rate_plus_val2", dtype=Float64),
    ],
)
def transformed_conv_rate(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["conv_rate_plus_val1"] = inputs["conv_rate"] + inputs["val_to_add"]
    df["conv_rate_plus_val2"] = inputs["conv_rate"] + inputs["val_to_add_2"]
    return df


# This groups features into a model version
driver_activity_v1 = FeatureService(
    name="driver_activity_v1",
    features=[
        driver_stats_fv[["conv_rate"]],  # Sub-selects a feature from a feature view
        transformed_conv_rate,  # Selects all features from the feature view
    ],
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)
driver_activity_v2 = FeatureService(
    name="driver_activity_v2", features=[driver_stats_fv, transformed_conv_rate]
)

# Defines a way to push data (to be available offline, online or both) into Feast.
driver_stats_push_source = PushSource(
    name="driver_stats_push_source",
    batch_source=baseball_plays_source,
)

# Defines a slightly modified version of the feature view from above, where the source
# has been changed to the push source. This allows fresh features to be directly pushed
# to the online store for this feature view.
driver_stats_fresh_fv = FeatureView(
    name="driver_hourly_stats_fresh",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    online=True,
    source=baseball_plays_source,  # Changed from above
    tags={"team": "driver_performance"},
)


# Define an on demand feature view which can generate new features based on
# existing feature views and RequestSource features
@on_demand_feature_view(
    sources=[driver_stats_fresh_fv, input_request],  # relies on fresh version of FV
    schema=[
        Field(name="conv_rate_plus_val1", dtype=Float64),
        Field(name="conv_rate_plus_val2", dtype=Float64),
    ],
)
def transformed_conv_rate_fresh(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["conv_rate_plus_val1"] = inputs["conv_rate"] + inputs["val_to_add"]
    df["conv_rate_plus_val2"] = inputs["conv_rate"] + inputs["val_to_add_2"]
    return df


driver_activity_v3 = FeatureService(
    name="driver_activity_v3",
    features=[driver_stats_fresh_fv, transformed_conv_rate_fresh],
)
 """
