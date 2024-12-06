""" Representation of an Offensive Player

Runner entity
"""
import logging
from pydantic import BaseModel
from utils.data import to_json_string
from utils.baseball import validate_base

logger = logging.getLogger(__name__)

class Runner(BaseModel):
    """ Base Runner or Batter """
    player_code : str = None
    original_base : str = None
    current_base : str = None
    is_out : bool = False

    def __init__(self, starting_base):
        """ Default constructor
        
            starting_base - base
        """
        super().__init__()
        logger.debug("New Runner: %s", starting_base)

        # validate and save base
        validate_base(starting_base)
        self.original_base = starting_base
        self.current_base = starting_base

    def clone(self):
        """ Clones the runner """
        runner = Runner(self.current_base)
        runner.is_out = False
        runner.player_code = self.player_code
        return runner

    def __str__(self) -> str:
        """ Create JSON string representation of the object. """
        return to_json_string(self)
