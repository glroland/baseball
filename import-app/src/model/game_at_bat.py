""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from model.game_play import GamePlay
from model.play_record import PlayRecord
from utils.data import to_json_string

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class GameAtBat(GamePlay):
    """ At Bat Record for a Game """
    player_code : str = None
    count : str = None
    pitches : str = None
    play : PlayRecord = None
    hit_to_location : int = None
    fielded_by : str = None
    pitcher : str = None
    primary_play_type_cd : str = None

    def __str__(self) -> str:
        """ Create JSON string representation of the object. """
        return to_json_string(self)
