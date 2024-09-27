""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
import json
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

    def validate(self, prev):
        """ Validate self as a direct transition from the previous at bat. Exceptions
            are used to inform of issues, since invalid data generally is considered
            unrecoverable. 
        """
        # determine if there is a change in batting team
        change_in_batting_team = False
        if self.inning != prev.inning or self.home_team_flag != prev.home_team_flag:
            logger.debug("Change in batting team recognized in validation.")
            change_in_batting_team = True
        
        # validate outs
        if change_in_batting_team and self.outs not in [0, 1, 3]:
            msg = f"Incorrect number of outs after batting team change! #={self.outs}"
            logger.error(msg)
            raise ValueError(msg)
        if self.outs > 3:
            msg = f"Too many outs! #={self.outs}"
            logger.error(msg)
            raise ValueError(msg)

        # validate innings
        if self.inning < 1:
            msg = f"Inning value is less than 1! #={self.inning}"
            logger.error(msg)
            raise ValueError(msg)
