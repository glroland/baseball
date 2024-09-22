""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from pydantic import BaseModel

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
        return f"""{{ "player_code": "{self.player_code}", "player_name": """ \
               f""""{self.player_name}", "home_team_flag": {str(self.home_team_flag).lower()}, """ \
               f""""batting_order": {self.batting_order}, "fielding_position": """ \
               f"""{self.fielding_position} }}"""
