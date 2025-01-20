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
from feast.types import Int32

pitch_count_entity = Entity(name="pitch_count", join_keys=["game_play_id"])

pitch_count_source = PostgreSQLSource(
    name="pitch_count",
    query="""

        select pitch_count,
            game_play_id,
            cast(game_date as timestamp) as event_timestamp,
            now() as create_timestamp
        from game_play, game
        where game_play.game_id = game.game_id
        and pitch_count is not null

    """,
    timestamp_field="event_timestamp",
    created_timestamp_column="create_timestamp",
)

pitch_count_fv = FeatureView(
    name="pitch_count_fv",
    entities=[pitch_count_entity],
#    ttl=timedelta(days=1),
    schema=[
        Field(name="pitch_count", dtype=Int32, description="Pitch Count at the time of play"),
        Field(name="game_play_id", dtype=Int32, description="Game Play ID"),
    ],
    online=True,
    source=pitch_count_source
)
