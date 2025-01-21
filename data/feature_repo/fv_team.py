from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)

from feast import (
    FeatureView,
    Field,
)
from feast.types import Int32, String
from entity_team import entity_team

source_team = PostgreSQLSource(
    name="source_team",
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

fv_team = FeatureView(
    name="fv_team",
    entities=[entity_team],
#    ttl=timedelta(days=1),
    schema=[
        Field(name="season_year", dtype=Int32, description="MLB Season Year"),
        Field(name="team_code", dtype=String, description="Team Code"),
        Field(name="team_name", dtype=String, description="Team Name"),
        Field(name="team_location", dtype=String, description="City where team is located"),
        Field(name="league", dtype=String, description="Team's MLB League"),
        ],
    online=True,
    source=source_team
)
