from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)

from feast import (
    FeatureView,
    Field,
)
from feast.types import Int32, Bool, String
from entity_game_play import entity_game_play

source_runners = PostgreSQLSource(
    name="source_runners",
    query="""

        select runner_1b,
            case when runner_1b is not null then TRUE
                    else FALSE
            end is_runner_1b,
            runner_2b,
            case when runner_2b is not null then TRUE
                    else FALSE
            end is_runner_2b,
            runner_3b,
            case when runner_3b is not null then TRUE
                    else FALSE
            end is_runner_3b,
            game_play.game_play_id game_play_id,
            to_timestamp(game_date || ' ' || COALESCE(game_time, '00:00:00'), 'YYYY-MM-DD HH24:MI:SS') as event_timestamp,
            now() as create_timestamp
        from game_play, game, game_play_atbat
        where game_play.game_id = game.game_id
        and game_play.game_play_id = game_play_atbat.game_play_id

    """,
    timestamp_field="event_timestamp",
    created_timestamp_column="create_timestamp",
)

fv_runners = FeatureView(
    name="fv_runners",
    entities=[entity_game_play],
#    ttl=timedelta(days=1),
    schema=[
        Field(name="runner_1b", dtype=String, description="Runner on 1st Base"),
        Field(name="is_runner_1b", dtype=Bool, description="Is there a runner on 1st Base?"),
        Field(name="runner_2b", dtype=String, description="Runner on 1st Base"),
        Field(name="is_runner_2b", dtype=Bool, description="Is there a runner on 1st Base?"),
        Field(name="runner_3b", dtype=String, description="Runner on 1st Base"),
        Field(name="is_runner_3b", dtype=Bool, description="Is there a runner on 1st Base?"),
        Field(name="game_play_id", dtype=Int32, description="Game Play ID"),
    ],
    online=True,
    source=source_runners
)
