""" Play Action Record Parser 

Parser for the play action record string.
"""
import logging
import json
from typing import List
from pydantic import BaseModel
from utils.data import extract_groups, regex_split

logger = logging.getLogger(__name__)

class ActionRecord(BaseModel):

    action : str = None
    groups : List[str] = []
    modifiers : List[str] = []

    def create(s : str):
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
        return json.dumps(self)
