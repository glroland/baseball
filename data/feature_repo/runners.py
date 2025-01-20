from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)

from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
)
from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination
from feast.types import Float32, Float64, Int64, Int32, Bool, String

runners_entity = Entity(name="runners", join_keys=["game_play_id"])

runners_source = PostgreSQLSource(
    name="runners",
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
            cast(game_date as timestamp) as event_timestamp,
            now() as create_timestamp
        from game_play, game, game_play_atbat
        where game_play.game_id = game.game_id
        and game_play.game_play_id = game_play_atbat.game_play_id

    """,
    timestamp_field="event_timestamp",
    created_timestamp_column="create_timestamp",
)

runners_fv = FeatureView(
    name="runners_fv",
    entities=[runners_entity],
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
    source=runners_source
)
