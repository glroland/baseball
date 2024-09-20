""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from model.game_play import GamePlay

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class GameSubstitution(GamePlay):
    """ Player Substitution Event """
    player_from : str = None
    player_to : str = None
    batting_order : int = None
    fielding_position : int = None
    players_team_home_flag : bool = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "Substitution", "player_from": "{self.player_from}", """ \
               f""""player_to": "{self.player_to}", "players_team_home_flag": """ \
               f"""{str(self.players_team_home_flag).lower()}, "batting_order": {self.batting_order}, """ \
               f""""fielding_position": {self.fielding_position} }}"""
