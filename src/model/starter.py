""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from pydantic import BaseModel
from utils.data import to_json_string

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class Starter(BaseModel):
    """ Starter Entry Fields """

    player_code : str = None
    player_name : str = None
    home_team_flag : bool = None
    batting_order : int = None
    fielding_position : int = None

    def __str__(self) -> str:
        return to_json_string(self)
