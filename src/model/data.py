""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class Data(BaseModel):
    """ Represents the end of game data records, such as earned runs. """

    data_type : str = None
    pitcher_player_code : str = None
    quantity : int = None

    def __str__(self) -> str:
        return f"""{{ "data_type": "{self.data_type}", "pitcher_player_code": """ + \
               f""""{self.pitcher_player_code}", "quantity": {self.quantity} }}"""
