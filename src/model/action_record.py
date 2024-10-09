""" Play Action Record Parser 

Parser for the play action record string.
"""
import logging
from typing import List
from pydantic import BaseModel
from utils.data import extract_groups, to_json_string, fail

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

        # get action first
        slash_index = s.find("/")
        paren_index = s.find("(")
        if slash_index != -1 and paren_index != -1:
            if slash_index < paren_index:
                record.action = s[0:slash_index]
                s = s[slash_index:]
            else:
                record.action = s[0:paren_index]
                s = s[paren_index:]
        elif slash_index != -1:
            record.action = s[0:slash_index]
            s = s[slash_index:]
        elif paren_index != -1:
            record.action = s[0:paren_index]
            s = s[paren_index:]
        else:
            record.action = s
            s = ""
        logger.debug("parsed action = %s and remaining action str = %s", record.action, s)

        # split the extended attributes
        group_start = -1
        i = 0
        group = None
        modifier = None
        while i < len(s):
            c = s[i]
            logger.debug("C = %s   Index=%s    Group_Start=%s", c, i, group_start)
            if c == "(":
                group_start = i + 1
                i += 1
            elif c == ")":
                if group_start == -1:
                    fail(f"Mailformed action string!  {s}")
                group = s[group_start:i]
                if len(group) > 0:
                    logger.debug("group = %s", group)
                    record.groups.append(group)
                group_start = -1
                s = s[i+1:]
                i = 0
            elif c == "/" and group_start == -1:
                logger.info("s = %s", s)
                if i == 0:
                    s = s[1:]
                else:
                    modifier = s[0:i]
                    s = s[i+1:]
                    i = 0
                    if len(modifier) > 0:
                        logger.debug("modifier = %s", modifier)
                        record.modifiers.append(modifier)
            else:
                i += 1
        if len(s) > 0:
            logger.debug("modifier = %s", s)
            record.modifiers.append(s)

        return record

    def __str__(self) -> str:
        return to_json_string(self)
