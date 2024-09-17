""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class Data:
    """ Represents the end of game data records, such as earned runs. """

    def __init__(self):
        self.data_type = None
        self.pitcher_player_code = None
        self.quantity = None

    def __str__(self) -> str:
        return f"""{{ "data_type": "{self.data_type}", "pitcher_player_code": """ + \
               f""""{self.pitcher_player_code}", "quantity": {self.quantity} }}"""
