""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from model.game_play import GamePlay

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class GameSubstitution(GamePlay):
    """ Player Substitution Event """

    def __init__(self):
        self.player_code = None
        self.player_name = None
        self.home_team_flag = None
        self.batting_order = None
        self.fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "Substitution", "player_code": "{self.player_code}", """ \
               f""""player_name": "{self.player_name}", "home_team_flag": """ \
               f"""{str(self.home_team_flag).lower()}, "batting_order": {self.batting_order}, """ \
               f""""fielding_position": {self.fielding_position} }}"""
