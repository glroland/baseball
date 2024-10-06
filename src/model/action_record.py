""" Play Action Record Parser 

Parser for the play action record string.
"""
import logging
from typing import List
from pydantic import BaseModel
from utils.data import extract_groups, regex_split, to_json_string

logger = logging.getLogger(__name__)

class ActionRecord(BaseModel):
    """ Play Action Record """

    action : str = None
    groups : List[str] = []
    modifiers : List[str] = []
    chain_to : object = None
    handled_flag : bool = False

    # pylint: disable=no-self-argument,self-cls-assignment
    def create(s : str):
        """ Instantiate an action record object from an action string.
        
            s - action string
        """
        logger.info("Parsing Action Record - Action<%s>", s)

        record = ActionRecord()

        # split by modifiers
        components = s.split("/")
        action = components[0]
        record.groups = extract_groups(action)
        index = action.find("(")
        if index == -1:
            record.action = action
        else:
            record.action = action[0:index]
        modifiers = components[1:]

        # create list of modifiers
        for modifier in modifiers:
            modifier_index = modifier.find("(")
            if modifier_index == -1:
                record.modifiers.append(modifier)
            else:
                record.modifiers.append(modifier[0:modifier_index])

        return record

    def __str__(self) -> str:
        return to_json_string(self)
