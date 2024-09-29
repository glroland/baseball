""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from model.game_play import GamePlay
from model.play_record import PlayRecord

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class GameAtBat(GamePlay):
    """ At Bat Record for a Game """
    player_code : str = None
    count : int = None
    pitches : int = None
    play : PlayRecord = None
    hit_to_location : int = None
    fielded_by : str = None
