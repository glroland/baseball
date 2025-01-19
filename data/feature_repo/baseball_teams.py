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
from feast.types import Int32, String

baseball_team_entity = Entity(name="baseball_team", join_keys=["team_code"])

baseball_plays_source = PostgreSQLSource(
    name="baseball_teams",
    query="""

            select season_year, 
                team_code, 
                team_name, 
                team_location, 
                league,
                to_timestamp(season_year || '-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') as event_timestamp,
                now() as created_timestamp
            from team

    """,
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

baseball_plays_fv = FeatureView(
    name="baseball_teams_fv",
    entities=[baseball_team_entity],
#    ttl=timedelta(days=1),
    schema=[
        Field(name="season_year", dtype=Int32, description="MLB Season Year"),
        Field(name="team_code", dtype=String, description="Team Code"),
        Field(name="team_name", dtype=String, description="Team Name"),
        Field(name="team_location", dtype=String, description="City where team is located"),
        Field(name="league", dtype=String, description="Team's MLB League"),
        ],
    online=True,
    source=baseball_plays_source
)

# This groups features into a model version
baseball_teams_v1 = FeatureService(
    name="baseball_teams_v1",
    features=[baseball_plays_fv],
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)
