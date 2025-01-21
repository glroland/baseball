from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)

from feast import (
    FeatureView,
    Field,
)
from feast.types import Float32, Float64, Int64, Int32, Bool, String
from entity_game_play import entity_game_play

source_game_play = PostgreSQLSource(
    name="source_game_play",
    query="""

        select game_play.game_play_id as game_play_id, game_play_atbat.player_code as player_code, pitch_index, home_team_flag, game_play_atbat.score_home as score_home, game_play_atbat.score_visitor as score_visitor, sky, night_flag, temperature, wind_direction, wind_speed, precipitation, field_condition, roster_batter.batting_hand as batting_hand, roster_pitcher.throw_hand as pitching_hand, primary_play_type_cd, outs,
        to_timestamp(game_date || ' ' || COALESCE(game_time, '00:00:00'), 'YYYY-MM-DD HH24:MI:SS') as event_timestamp,
        now() as create_timestamp
        from game, game_play, game_play_atbat, game_play_atbat_pitch, roster as roster_batter, roster as roster_pitcher
        where game.game_id = game_play.game_id
        and game_play_atbat.game_play_id = game_play.game_play_id
        and game_play_atbat_pitch.game_play_id = game_play.game_play_id     
        and roster_batter.player_code = game_play_atbat.player_code
        and roster_batter.season_year = date_part('year', game.game_date)
        and roster_pitcher.player_code = game_play_atbat.pitcher
        and roster_pitcher.season_year = roster_batter.season_year

    """,
    timestamp_field="event_timestamp",
    created_timestamp_column="create_timestamp",
)

baseball_plays_fv = FeatureView(
    name="fv_game_play",
    entities=[entity_game_play],
#    ttl=timedelta(days=1),
    schema=[
        Field(name="game_play_id", dtype=Int32),
        Field(name="pitch_index", dtype=Int32),
        Field(name="batting_hand", dtype=String, description="Average daily trips"),
        Field(name="pitching_hand", dtype=String, description="Average daily trips"),
        Field(name="outs", dtype=Int32),
        Field(name="home_team_flag", dtype=Bool),
        Field(name="score_home", dtype=Int32, description="Average daily trips"),
        Field(name="score_visitor", dtype=Int32),
        Field(name="primary_play_type_cd", dtype=String),
    ],
    online=True,
    source=source_game_play
)
