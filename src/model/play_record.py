""" Play Record Parser 

Parser for the play record string.
"""
import logging
from typing import List
from pydantic import BaseModel
from model.action_record import ActionRecord
from model.advance_record import AdvanceRecord
from utils.data import to_json_string, fail

logger = logging.getLogger(__name__)

class PlayRecord(BaseModel):
    """ Data structure for analyzing and leveraging action strings in the game data. """

    original_play_record : str = None
    actions : List[ActionRecord] = []
    advances : List[AdvanceRecord] = []
    uncertainty_flag : bool = False
    exceptional_play_flag : bool = False
    softly_hit_ball_flag : bool = False
    hard_hit_ball_flag : bool = False

    # pylint: disable=unused-private-member
    def __split_advancements(self, action_str):
        # validate input parameter
        if action_str.count(".") > 1:
            fail("Unexpected - too Many dots encountered with advancement!  " + \
                f"{action_str.count('.')} Action={action_str}")

        # split advancements
        advancements = action_str.split(".")
        if action_str.count(".") != (len(advancements) - 1):
            fail("Split Operation for advancements failed due to count mispatch.")
        beginning = advancements[0]
        advancements = advancements[1:]
        if len(advancements) > 0:
            adv_list = advancements[0].split(";")

            # create advancements
            for a in adv_list:
                advance_record = AdvanceRecord.create(a)
                self.advances.append(advance_record)

        return beginning

    def __create_actions_chained_or_standalone(self, play):
        """ Takes a parsed play string with chained components and breaks
            them apart into discrete actions that are still chained together.
            
            play - play string
        """
        split_plays = play.split("+")

        # determine if there is a need to chain
        chained_flag = False
        if len(split_plays) > 1:
            chained_flag = True

        # create all the action records
        for split_play in split_plays:
            record = ActionRecord.create(split_play)
            self.actions.append(record)

        # chain the actions together when +'ed
        if chained_flag:
            prev_action = None
            for action in self.actions:
                if prev_action is not None:
                    prev_action.chain_to = action
                prev_action = action

        return split_plays

    # pylint: disable=unused-private-member
    def __break_up_play(self, s):
        # get trailing modifiers
        in_group = False
        mod_index = -1
        index = 0
        while index < len(s):
            c = s[index]
            if c == "(":
                in_group = True
            elif c == ")":
                in_group = False
            elif not in_group and c == "/":
                mod_index = index
                break
            index += 1
        modifiers = ""
        if mod_index != -1:
            modifiers = s[mod_index:]
            s = s[0:mod_index]
        logger.debug("Identified Play and Modifiers - s=%s m=%s", s, modifiers)

        # break out plays (usually just 1 but that's a big usually)
        play = s
        is_first = True
        while True:
            # stop condition - empty string
            if len(play) == 0:
                break

            # stop condition - no more groups
            end_parens = play.find(")")
            if end_parens == -1:
                if is_first:
                    play += modifiers
                logger.debug ("No groups in action.  Play w/modifiers = %s", play)
                self.__create_actions_chained_or_standalone(play)
                break

            # parse action w/group
            part_one = play[0:end_parens+1]
            if is_first:
                part_one += modifiers
            logger.debug ("Groups exist in action.  Play w/o groups plus modifiers = %s",
                            part_one)
            self.__create_actions_chained_or_standalone(part_one)

            # progress to next chunk
            play = play[end_parens+1:]

            modifiers = None
            is_first = False

    # pylint: disable=no-self-argument,protected-access
    def create(s) -> object:
        """ Create a Play Record from string.
        
            s - action string
        """
        logger.debug("Parsing Play Record - <%s>", s)

        # create basic play record structure
        record = PlayRecord()
        record.original_play_record = s

        # trim uncertainty flag
        action_str = s
        if action_str[len(action_str)-1] == "#":
            record.uncertainty_flag = True
            action_str = action_str[0:len(action_str)-1]
            logger.warning("Uncertainty Flag set for play! %s", record.original_play_record)

        # manage exceptional plays
        if action_str.find("!") != -1:
            record.exceptional_play_flag = True
            action_str = action_str.replace("!", "")

        # parse advancements
        play_str = record.__split_advancements(action_str)
        logger.debug("Resulting Play Str - <%s>", play_str)

        # trim softly hit ball flag
        if play_str[len(play_str)-1] == "-":
            record.softly_hit_ball_flag = True
            play_str = action_str[0:len(play_str)-1]
            logger.info("Softly Hit Ball Flag set for play! %s", record.original_play_record)

        # trim hard hit ball flag
        if play_str[len(play_str)-1] == "+":
            record.hard_hit_ball_flag = True
            play_str = action_str[0:len(play_str)-1]
            logger.info("Hard Hit Ball Flag set for play! %s", record.original_play_record)

        # Break up play components
        record.__break_up_play(play_str)

        return record

    def __str__(self) -> str:
        return to_json_string(self)
