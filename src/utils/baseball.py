""" Baseball Utility Functions

Helper methods for baseball related data.
"""
import logging
import re
import functools
from utils.data import fail
from model.action_record import ActionRecord

logger = logging.getLogger(__name__)

# pylint: disable=inconsistent-return-statements
def get_base_as_int(base):
    """ Gets the specified base as a number.
    
        base - base str
    """
    if base in ["B", 0]:
        return 0
    if base in ["1", 1]:
        return 1
    if base in ["2", 2]:
        return 2
    if base in ["3", 3]:
        return 3
    if base in ["H", 4]:
        return 4

    fail(f"get_base_as_int failing due to illegal parameter!  {base}")

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
    for action in play.actions:
        if not is_action_str_defensive_play(action.action):
            logger.debug("Action is not a defensive play.  Skipping changes!  %s", action.action)
            return

    #sorted(play.actions, key=lambda x: x.attack)
    #sorted(timestamps, reverse=True)

    play.actions = sorted(play.actions,
                          key=functools.cmp_to_key(__comparator_defensive_play_actions),
                          reverse=True)
