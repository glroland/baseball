""" Advance Record Parser 

Parser for the play advance record string.
"""
import logging
import json
import re
from typing import List
from pydantic import BaseModel
from utils.data import extract_groups, to_json_string

logger = logging.getLogger(__name__)

class AdvanceRecord(BaseModel):

    original_advance_record : str = None
    advance : str = None
    base_from : str = None
    base_to : str = None
    was_out : bool = False
    groups : List[str] = []

    def __parse_advancement_str(self, a):
        if not re.match("^[B123][X-][123H](\\(.+\\))*$", a):
            msg = f"Invalid Advancement: {a}"
            logger.error(msg)
            raise ValueError(msg)

        # parse advancement
        self.advance = a[0:3]

        # extract advancement parameters
        advancement_parameters = extract_groups(a)
        if len(advancement_parameters) > 0:
            for group in advancement_parameters:
                self.groups.append(group)
   
                # all numbers test
                if re.match("^[0-9]+$", group):
                    logger.debug("Advancement Parameter - all numbers - %s", group)
                elif re.match("^[0-9]+X$", group):
                    logger.debug("Advancement Parameter - number X - %s", group)
                elif re.match("^[0-9]+H$", group):
                    logger.debug("Advancement Parameter - number H - %s", group)
                elif re.match("^[0-9]+/TH[123H]?$", group):
                    logger.debug("Advancement Parameter - numbers plus throw - %s", group)
                elif re.match("^[0-9]+/BINT$", group):
                    logger.debug("Advancement Parameter - numbers plus BINT - %s", group)
                elif re.match("^[0-9]+/RINT$", group):
                    logger.debug("Advancement Parameter - numbers plus RINT - %s", group)
                elif re.match("^[0-9]+/AP$", group):
                    logger.debug("Advancement Parameter - numbers plus AP - %s", group)
                elif re.match("^[0-9]*E[0-9]/TH[123H]?$", group):
                    logger.debug("Advancement Parameter - error due to throw - %s", group)
                elif re.match("^[0-9]*E[0-9]/OBS?$", group):
                    logger.debug("Advancement Parameter - error due to OBS - %s", group)
                elif re.match("^[0-9]*E[0-9]$", group):
                    logger.debug("Advancement Parameter - error - %s", group)
                elif group == "ER":
                    logger.debug("Advancement Parameter - Earned Run")
                elif group == "UR":
                    logger.debug("Advancement Parameter - Unearned Run")
                elif group == "TUR":
                    logger.debug("Advancement Parameter - Team Unearned Run")
                elif group == "NR":
                    logger.debug("Advancement Parameter - RBI Not Credited")
                elif group == "PB":
                    logger.debug("Advancement Parameter - Passed Ball")
                elif group == "RBI":
                    logger.debug("Advancement Parameter - RBI")
                elif group == "WP":
                    logger.debug("Advancement Parameter - WP")
                elif re.match("^TH[123H]?$", group):
                    logger.debug("Advancement Parameter - Throw")
                else:
                    msg = f"Illegal Advancement Parameter - {group}"
                    logger.error(msg)
                    raise ValueError(msg)


    def create(s):
        logger.debug("Parsing Advancement Record - <%s>", s)

        # parse advancements
        record = AdvanceRecord()
        record.original_advance_record = s
        record.__parse_advancement_str(s)

        # validate core advancement record
        if len(record.advance) != 3:
            msg = f"Advancement record is wrong length: {len(record.advance)}"
            logger.error(msg)
            raise ValueError(msg)
        if record.advance[0] not in ["B", "1", "2", "3"]:
            msg = f"Invalid base_from in advancement record: {record.advance[0]}"
            logger.error(msg)
            raise ValueError(msg)
        if record.advance[2] not in ["1", "2", "3", "H"]:
            msg = f"Invalid base_to in advancement record: {record.advance[2]}"
            logger.error(msg)
            raise ValueError(msg)
        if record.advance[1] not in ["-", "X"]:
            msg = f"Invalid advancement result in advancement record: {record.advance[1]}"
            logger.error(msg)
            raise ValueError(msg)

        # extrapolate key fields
        record.base_from = record.advance[0]
        record.base_to = record.advance[2]
        record.was_out = record.advance[1] == "X"

        return record

    def __str__(self) -> str:
        return to_json_string(self)
