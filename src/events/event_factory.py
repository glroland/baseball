""" Application of game events logic

Apply game events to game at bat event data.
"""
import logging
import re
import importlib
from utils.data import regex_split, split_num_paren_chunks
from events.constants import EventCodes

logger = logging.getLogger(__name__)

class EventFactory:

    EVENT_MODULE = "module"
    EVENT_CLASS = "class"
    MAPPING_DEFENSIVE = "defense"

    mappings = {
        MAPPING_DEFENSIVE: { EVENT_MODULE: "events.defensive_play", EVENT_CLASS: "DefensivePlayEvent" },
        EventCodes.WALK: { EVENT_MODULE: "events.walk", EVENT_CLASS: "WalkEvent" },
        EventCodes.INTENTIONAL_WALK_1: { EVENT_MODULE: "events.walk", EVENT_CLASS: "WalkEvent" },
        EventCodes.INTENTIONAL_WALK_2: { EVENT_MODULE: "events.walk", EVENT_CLASS: "WalkEvent" },
        EventCodes.SINGLE: { EVENT_MODULE: "events.single", EVENT_CLASS: "SingleEvent" },
        EventCodes.DOUBLE: { EVENT_MODULE: "events.double", EVENT_CLASS: "DoubleEvent" },
        EventCodes.TRIPLE: { EVENT_MODULE: "events.triple", EVENT_CLASS: "TripleEvent" },
        EventCodes.CAUGHT_STEALING: { EVENT_MODULE: "events.caught_stealing", EVENT_CLASS: "CaughtStealingEvent" },
        EventCodes.STRIKEOUT: { EVENT_MODULE: "events.strikeout", EVENT_CLASS: "StrikeoutEvent" },
        EventCodes.HOMERUN: { EVENT_MODULE: "events.homerun", EVENT_CLASS: "HomerunEvent" },
        EventCodes.ERROR: { EVENT_MODULE: "events.defensive_error", EVENT_CLASS: "DefensiveErrorEvent" }
    }

    def __instantiate_class(module_name, class_name):
        """ Instantiates the provided python class via reflection
        
        module_name - name of module containing class
        class_name - name of class to instantiate
        """
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_()

    def __create_event_by_name(mapping, game_at_bat):
        """ Instantiates the provided python class via reflection
        
        mapping - string used to find the event handler
        class_name - name of class to instantiate
        game_at_bat - game at bat event
        """
        if mapping not in EventFactory.mappings:
            msg = f"Unknown Event Type!  EventCode=<{mapping}>, FullBasicPlayDetails=<{game_at_bat.basic_play}>", 
            logger.error(msg)
            raise ValueError(msg)

        instance = EventFactory.__instantiate_class(
                    EventFactory.mappings[mapping][EventFactory.EVENT_MODULE],
                    EventFactory.mappings[mapping][EventFactory.EVENT_CLASS])
        return instance

    def create(game_at_bat):
        """ Interpret the game at bat event details to determine outs, runners on base, runs,
        etc.
        
        game_at_bat - game at bat record
        """
        logger.debug("Interpretting game at bat event.  BasicPlay = <%s>, Modifiers = <%s>, Advance = <%s>", game_at_bat.basic_play, game_at_bat.modifiers, game_at_bat.advance)

        # Analyze Defensive Play
        regex = "(^[0-9]+)"
        if re.search(regex, game_at_bat.basic_play):
            play_list = split_num_paren_chunks(game_at_bat.basic_play)
            event = EventFactory.__create_event_by_name(EventFactory.MAPPING_DEFENSIVE, game_at_bat)
            event.handle_advances(game_at_bat)
            event.handle(game_at_bat, play_list)

        # Analyze Offensive Play
        regex = "(^[A-Z]+)(.*)"
        if re.search(regex, game_at_bat.basic_play):
            play_list = regex_split(regex, game_at_bat.basic_play)
            op_event = play_list.pop(0)
            for result in play_list:
                logger.debug("Basic_Play Modifiers: - LEN=%s, RESULT = %s", len(play_list), result)

            event = EventFactory.__create_event_by_name(op_event, game_at_bat)
            event.handle_advances(game_at_bat)
            event.handle(game_at_bat, play_list)
            event.debug_check_key_attributes_out(game_at_bat, play_list)

        if game_at_bat.modifiers is not None and len(game_at_bat.modifiers) > 0:
            msg = f"UNHANDLED MODIFIERS!!!  {game_at_bat.modifiers}"
            logger.error(msg)
            raise ValueError(msg)
        if game_at_bat.advance is not None and len(game_at_bat.advance) > 0:
            msg = f"UNHANDLED ADVANCE!!!  {game_at_bat.advance}"
            logger.error(msg)
            raise ValueError(msg)

        #raise ValueError("incremental processing as i work through this")
