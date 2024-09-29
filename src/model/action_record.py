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
        logger.debug("Parsing Action Record - Action<%s>", s)

        record = ActionRecord()
        record.groups = extract_groups(s)

        # Pull "action" from the input stream, whether before a group, mod, or standalone
        paren_index = s.find("(")
        if paren_index == -1:                       # no group
            slash_index = s.find("/")
            if slash_index == -1:                   # no mods
                record.action = s                   # standalone
            else:
                record.action = s[0:slash_index]    # w/mod
        else:
            record.action = s[0:paren_index]        # w/group

        # Create list of modifiers
        paren_index = s.find(")")
        if paren_index != -1:
            s = s[paren_index+1:]               # assumed after group ends
        slash_index = s.find("/")
        if slash_index != -1:
            m_str = s[slash_index+1:]
            record.modifiers = regex_split("/", m_str)

        return record

    def __str__(self) -> str:
        return to_json_string(self)