""" Advance Record Parser 

Parser for the play advance record string.
"""
import logging
import re
from typing import List
from pydantic import BaseModel
from utils.data import extract_groups, to_json_string, get_base_as_int

logger = logging.getLogger(__name__)

class AdvanceRecord(BaseModel):
    """ Advance Record for moving runners from one base to another. """

    original_advance_record : str = None
    advance : str = None
    base_from : str = None
    base_to : str = None
    was_out : bool = False
    groups : List[str] = []

    # pylint: disable=unused-private-member,too-many-branches
    def __parse_advancement_str(self, a):
        """ Parse Advancement String.
        
            a - advancement string
        """
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

    # pylint: disable=no-self-argument,protected-access
    def create(s):
        """ Create a new Advancement Record instance. """
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

    def is_completed(self, completed : List[object] ):
        """ Analyzes a list of advancement reocrds and determins if this advancement
            has already been handled.

            The advance runner logic is recursive and does breakup multi level advances
            into individual chains of function calls.  This completed advancements check
            assumes that the original requests are logged vs the incremental changes.

            completed - list of completed advancement requests
        """
        logger.debug("LENGTH OF ALREADY COMPLETED = %s", len(completed))
        for c in completed:
            logger.debug("ALREADY COMPLETED - From=%s To=%s", c.base_from, c.base_to)

        # create an array of to_be bases that must be reflected in the completed array
        self_from = get_base_as_int(self.base_from)
        self_to = get_base_as_int(self.base_to)
        coverage = []
        i = self_from+1
        while i <= self_to:
            coverage.append(i)
            i += 1
        logger.debug("BEFORE - is_completed() From=%s To=%s Coverage=%s", self_from, self_to, coverage)

        for a in completed:
            a_from = get_base_as_int(a.base_from)
            a_to = get_base_as_int(a.base_to)

            a_check = a_from + 1
            while a_check <= a_to:
                logger.debug("TESTING - is_completed() Value=%s Coverage=%s", a_check, coverage)
                if a_check in coverage:
                    coverage.remove(a_check)
                a_check += 1

        logger.debug("AFTER - is_completed() From=%s To=%s Coverage=%s", self_from, self_to, coverage)
        return len(coverage) == 0

    def __str__(self) -> str:
        """ Convert object to JSON string """
        return to_json_string(self)
