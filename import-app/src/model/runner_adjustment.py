""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from model.game_play import GamePlay

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class RunnerAdjustment(GamePlay):
    """ Player Substitution Event """
    runner_code : str = None
    adjusted_base : str = None
