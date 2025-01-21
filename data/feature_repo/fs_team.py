from feast import (
    FeatureService,
)
from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination
from fv_team import fv_team

fs_team = FeatureService(
    name="fs_team",
    features=[fv_team],
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)
