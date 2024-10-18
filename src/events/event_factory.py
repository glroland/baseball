""" Application of game events logic

Apply game events to game at bat event data.
"""
import logging
import re
import importlib
from utils.data import regex_split, fail
from utils.baseball import is_action_str_defensive_play, is_action_str_defensive_error
from utils.baseball import sort_defensive_play_actions_desc
from utils.baseball import is_defensive_play_missing_batter_event
from utils.baseball import is_defensive_play
from events.event_code_mappings import EventCodeMappings
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class EventFactory:
    """ Event Factory """

    # pylint: disable=no-self-argument
    def __instantiate_class(module_name, class_name):
        """ Instantiates the provided python class via reflection
        
        module_name - name of module containing class
        class_name - name of class to instantiate
        """
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_()

    # pylint: disable=no-self-argument
    def __create_event_by_name(mapping, game_at_bat):
        """ Instantiates the provided python class via reflection
        
        mapping - string used to find the event handler
        class_name - name of class to instantiate
        game_at_bat - game at bat event
        """
        # Extract and Validate Code
        code_list = regex_split("^([A-Z]+)[0-9]*$", mapping)
        if len(code_list) == 0:
            msg = f"Basic Play Code Not Found in Mapping: {mapping}"
            logger.error(msg)
            raise ValueError(msg)
        if len(code_list) > 1:
            msg = f"Too many basic play codes found in mapping: {mapping} " + \
                  f"- # Found {len(code_list)}"
            logger.error(msg)
            raise ValueError(msg)
        code = code_list[0]

        # Process Code
        logger.debug("Basic Play Code '%s' extracted from mapping: %s", code, mapping)
        if code not in EventCodeMappings.mappings:
            msg = f"Unknown Event Type!  EventCode=<{code}>, Mapping=<{mapping}>, " + \
                  f"FullBasicPlayDetails=<{game_at_bat.play}>"
            logger.error(msg)
            raise ValueError(msg)

        instance = EventFactory.__instantiate_class(
                    EventCodeMappings.mappings[mapping][EventCodeMappings.EVENT_MODULE],
                    EventCodeMappings.mappings[mapping][EventCodeMappings.EVENT_CLASS])
        return instance

    # pylint: disable=no-self-argument,no-member
    def create(game_at_bat : GameAtBat):
        """ Interpret the game at bat event details to determine outs, runners on base, runs,
        etc.
        
        game_at_bat - game at bat record
        """
        play = game_at_bat.play
        game_state = game_at_bat.game_state

        logger.debug("Interpretting game at bat event.  Play = <%s>", play)

        # sort the actions descending - handle in reverse order
        if is_defensive_play(play):
            sort_defensive_play_actions_desc(play)

        # process each play action
        for action in play.actions:
            a_str = action.action
            if action.handled_flag:
                logger.info("Skipping Handled Action: %s", action.action)
            else:
                action_handler_assigned = False

                # Analyze Defensive Error
                if is_action_str_defensive_error(a_str):
                    action_handler_assigned = True
                    event = EventFactory.__create_event_by_name(
                        EventCodeMappings.MAPPING_DEFENSIVE_ERROR, game_at_bat)
                    event.pre_handle(game_state, action)
                    event.handle(game_state, action)
                    event.post_handle(game_state, action)

                # Analyze Defensive Play
                if is_action_str_defensive_play(a_str):
                    action_handler_assigned = True
                    event = EventFactory.__create_event_by_name(
                        EventCodeMappings.MAPPING_DEFENSIVE, game_at_bat)
                    event.pre_handle(game_state, action)
                    event.handle(game_state, action)
                    event.post_handle(game_state, action)

                # Analyze Offensive Play
                regex = "(^[A-Z]+)(.*)"
                if re.search(regex, a_str):
                    action_handler_assigned = True
                    play_list = regex_split(regex, a_str)
                    op_event = play_list.pop(0)
                    for result in play_list:
                        logger.debug("Basic_Play Modifiers: - LEN=%s, RESULT = %s",
                                    len(play_list), result)

                    event = EventFactory.__create_event_by_name(op_event, game_at_bat)
                    event.pre_handle(game_state, action)
                    event.handle(game_state, action)
                    event.post_handle(game_state, action)

                if not action_handler_assigned:
                    fail(f"Action not handled!  {a_str}")

        # handle advances before other play actions
        game_state.handle_advances(play.advances)

        # ensure that at least one batter event exists
        if is_defensive_play(play):
            if is_defensive_play_missing_batter_event(play):
                game_state.action_advance_runner("B", "1", is_out=False)
