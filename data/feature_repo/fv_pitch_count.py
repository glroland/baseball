from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)

from feast import (
    FeatureView,
    Field,
)
from feast.types import Int32
from entity_game_play import entity_game_play

source_pitch_count = PostgreSQLSource(
    name="source_pitch_count",
    query="""

        select pitch_count,
            game_play_id,
            to_timestamp(game_date || ' ' || COALESCE(game_time, '00:00:00'), 'YYYY-MM-DD HH24:MI:SS') as event_timestamp,
            now() as create_timestamp
        from game_play, game
        where game_play.game_id = game.game_id
        and pitch_count is not null

    """,
    timestamp_field="event_timestamp",
    created_timestamp_column="create_timestamp",
)

fv_pitch_count = FeatureView(
    name="fv_pitch_count",
    entities=[entity_game_play],
#    ttl=timedelta(days=1),
    schema=[
        Field(name="pitch_count", dtype=Int32, description="Pitch Count at the time of play"),
        Field(name="game_play_id", dtype=Int32, description="Game Play ID"),
    ],
    online=True,
    source=source_pitch_count
)
