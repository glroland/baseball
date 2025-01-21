from feast import (
    FeatureService,
)
from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination
from fv_pitch_count import fv_pitch_count

fs_game_play = FeatureService(
    name="fs_game_play",
    features=[fv_pitch_count],
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)
