""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class Starter:
    """ Starter Entry Fields """

    def __init__(self):
        self.player_code = None
        self.player_name = None
        self.home_team_flag = None
        self.batting_order = None
        self.fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "player_code": "{self.player_code}", "player_name": """ \
               f""""{self.player_name}", "home_team_flag": {str(self.home_team_flag).lower()}, """ \
               f""""batting_order": {self.batting_order}, "fielding_position": """ \
               f"""{self.fielding_position} }}"""
