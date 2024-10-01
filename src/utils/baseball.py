""" Baseball Utility Functions

Helper methods for baseball related data.
"""
import logging
import re
import functools
from utils.data import fail, get_base_as_int
from model.action_record import ActionRecord
from model.advance_record import AdvanceRecord

logger = logging.getLogger(__name__)

def validate_base(base_str, first_allowed=True, home_allowed=True):
    """ Validates the provided string representation of the base
        to ensure it is valid for the circumstance.  Otherwise an exception
        is thrown.
        
        base_str - string representation of the base
        first_allowed - whether first base is a permissiable value
        home_allowed - whether home is a permissiable value
    """
    if base_str is None or len(base_str) != 1:
        fail("Invalid Base String!  Empty string or None.")
    if base_str in ["B", 0]:
        return True
    if base_str in ["1", 1]:
        if not first_allowed:
            fail("First base is not a permissible value for this play!")
        return True
    if base_str in ["2", 2]:
        return True
    if base_str in ["3", 3]:
        return True
    if base_str in ["H", 4]:
        if not home_allowed:
            fail("Home base is not a permissible value for this play!")
        return True
    fail(f"Unexpected value for Base!  <{base_str}>")

def is_action_str_defensive_play(s):
    """ Analyzes an action string to determine if its defensive play.  
    
        s - action string
    """
    if re.search("(^[0-9]+)", s):
        return True
    return False

def __comparator_defensive_play_actions(action1, action2):
    """ Utility function used to compare play actions for sorting purposes.
    
        action1 - first action to compare
        action2 - second action to compare
    """
    # validate argumnents
    if action1 is None or action2 is None:
        fail("Input action(s) are null!")
    if not isinstance(action1, ActionRecord):
        fail(f"Input action1 is wrong type. {type(action1)}")
    if not isinstance(action2, ActionRecord):
        fail(f"Input action1 is wrong type. {type(action2)}")

    # extract action1 value
    action1_int = 0
    if len(action1.groups) > 0:
        base = action1.groups[0]
        validate_base(base)
        if base == "H":
            action1_int = 4
        elif base != "B":
            action1_int = int(base)

    # extract action2 value
    action2_int = 0
    if len(action2.groups) > 0:
        base = action2.groups[0]
        validate_base(base)
        if base == "H":
            action2_int = 4
        elif base != "B":
            action2_int = int(base)

    return action1_int - action2_int

def sort_defensive_play_actions_desc(play):
    """ Sorts the play actions in reverse/descending order.  The behavior is to ignore
        non-defensive actions.  The sort action uses the group as the key.  In the 
        unexpected event that a base be listed twice (not accurate anyway?), further
        sorting does not occur.
        
        play - play record for which to sort actions
    """
    logger.debug("sort_defensive_play_actions_desc()")

    # before touching the record, ensure that all actions are defensive
    if not is_defensive_play(play):
        logger.debug("Action is not a defensive play.  Skipping changes!")
        return

    # sort descending
    play.actions = sorted(play.actions,
                          key=functools.cmp_to_key(__comparator_defensive_play_actions),
                          reverse=True)

def is_defensive_play_missing_batter_event(play):
    """ Analyzes the defensive play to determine if it contains any batter
        related events.
        
        play - play record to analyze
    """
    logger.debug("does_defensive_play_contain_batter_event()")

    # before touching the record, ensure that all actions are defensive
    for action in play.actions:
        # abort on non-defensive plays
        if not is_action_str_defensive_play(action.action):
            logger.debug("Action is not a defensive play. Providing positive response!  %s", action.action)
            return False

        # check for batter play
        if len(action.groups) == 0 or action.groups[0] in ["B", 0]:
            logger.debug("Found batter position in groups list")
            return False

    return True

def is_defensive_play(play):
    """ Analyzes the play to determine if its a defensive play.
    
        play - play to analyze
    """
    logger.debug("is_defensive_play()")

    # validate paramters
    if play is None:
        fail("Input play is null!")

    for action in play.actions:
        if not is_action_str_defensive_play(action.action):
            return False

    return True

def __comparator_play_advances(advance1, advance2):
    """ Utility function used to compare advances for sorting purposes.
    
        advance1 - first advance to compare
        advance2 - second advance to compare
    """
    # validate argumnents
    if advance1 is None or advance2 is None:
        fail("Input action(s) are null!")
    if not isinstance(advance1, AdvanceRecord):
        fail(f"Input action1 is wrong type. {type(advance1)}")
    if not isinstance(advance2, AdvanceRecord):
        fail(f"Input action1 is wrong type. {type(advance2)}")

    # extract base from values
    advance1_int = get_base_as_int(advance1.base_from[0])
    advance2_int = get_base_as_int(advance2.base_from[0])
    if advance1_int == advance2_int:
        advance1_int = get_base_as_int(advance1.base_from[2])
        advance2_int = get_base_as_int(advance2.base_from[2])

    return advance1_int - advance2_int

def sort_play_advances_desc(advances):
    """ Sorts the advances in reverse/descending order. 
        
        advances - list of advances to sort
    """
    logger.debug("sort_play_advances_desc()")

    # sort descending
    return sorted(advances,
                  key=functools.cmp_to_key(__comparator_play_advances),
                  reverse=True)

def base_after(base):
    """ Returns the base after the one provided.
    
        base - starting base
    """
    after_int = get_base_as_int(base) + 1
    if after_int >= 4:
        return "H"
    return str(after_int)
