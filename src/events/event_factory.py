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
        EventCodes.BALK: { EVENT_MODULE: "events.walk", EVENT_CLASS: "WalkEvent" },
        EventCodes.WILD_PITCH: { EVENT_MODULE: "events.walk", EVENT_CLASS: "WalkEvent" },
        EventCodes.FIELDERS_CHOICE: { EVENT_MODULE: "events.fielders_choice", EVENT_CLASS: "FieldersChoiceEvent" },
        EventCodes.INTENTIONAL_WALK_1: { EVENT_MODULE: "events.walk", EVENT_CLASS: "WalkEvent" },
        EventCodes.INTENTIONAL_WALK_2: { EVENT_MODULE: "events.walk", EVENT_CLASS: "WalkEvent" },
        EventCodes.SINGLE: { EVENT_MODULE: "events.single", EVENT_CLASS: "SingleEvent" },
        EventCodes.DOUBLE: { EVENT_MODULE: "events.double", EVENT_CLASS: "DoubleEvent" },
        EventCodes.TRIPLE: { EVENT_MODULE: "events.triple", EVENT_CLASS: "TripleEvent" },
        EventCodes.CAUGHT_STEALING: { EVENT_MODULE: "events.caught_stealing", EVENT_CLASS: "CaughtStealingEvent" },
        EventCodes.PICKED_OFF_CAUGHT_STEALING: { EVENT_MODULE: "events.caught_stealing", EVENT_CLASS: "CaughtStealingEvent" },
        EventCodes.PICKED_OFF: { EVENT_MODULE: "events.picked_off", EVENT_CLASS: "PickedOffEvent" },
        EventCodes.STRIKEOUT: { EVENT_MODULE: "events.strikeout", EVENT_CLASS: "StrikeoutEvent" },
        EventCodes.HOMERUN: { EVENT_MODULE: "events.homerun", EVENT_CLASS: "HomerunEvent" },
        EventCodes.ERROR: { EVENT_MODULE: "events.defensive_error", EVENT_CLASS: "DefensiveErrorEvent" },
        EventCodes.STOLEN_BASE: { EVENT_MODULE: "events.stolen_base", EVENT_CLASS: "StolenBaseEvent" },
        EventCodes.DEFENSIVE_INDIFFERENCE: { EVENT_MODULE: "events.defensive_indifference", EVENT_CLASS: "DefensiveIndifferenceEvent" },
        EventCodes.BATTER_HIT_BY_PITCH: { EVENT_MODULE: "events.hit_by_pitch", EVENT_CLASS: "HitByPitchEvent" },
        EventCodes.FLY_BALL_ERROR: { EVENT_MODULE: "events.fly_ball_error", EVENT_CLASS: "FlyBallErrorEvent" },
        EventCodes.GROUND_RULE_DOUBLE: { EVENT_MODULE: "events.ground_rule_double", EVENT_CLASS: "GroundRuleDoubleEvent" },
        EventCodes.PASSED_BALL: { EVENT_MODULE: "events.passed_ball", EVENT_CLASS: "PassedBallEvent" },
        EventCodes.BASE_RUNNER_ADVANCE: { EVENT_MODULE: "events.base_runner_advance", EVENT_CLASS: "BaseRunnerAdvanceEvent" }
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
        # Extract and Validate Code
        code_list = regex_split("^([A-Z]+)[0-9]*$", mapping)
        if len(code_list) == 0:
            msg = f"Basic Play Code Not Found in Mapping: {mapping}"
            logger.error(msg)
            raise ValueError(msg)
        if len(code_list) > 1:
            msg = f"Too many basic play codes found in mapping: {mapping} - # Found {len(code_list)}"
            logger.error(msg)
            raise ValueError(msg)
        code = code_list[0]

        # Process Code
        logger.debug(f"Basic Play Code '{code}' extracted from mapping: {mapping}")
        if code not in EventFactory.mappings:
            msg = f"Unknown Event Type!  EventCode=<{code}>, Mapping=<{mapping}>, FullBasicPlayDetails=<{game_at_bat.basic_play}>", 
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
        logger.debug("Interpretting game at bat event.  Play = <%s>", game_at_bat.play)

        # process each play action
        for action in game_at_bat.play.actions:
            a_str = action.action

            # Analyze Defensive Play
            regex = "(^[0-9]+)"
            if re.search(regex, a_str):
                event = EventFactory.__create_event_by_name(EventFactory.MAPPING_DEFENSIVE, game_at_bat)
                event.handle_advances(game_at_bat, game_at_bat.play.advances)
                event.handle(game_at_bat, action)
                #event.debug_check_key_attributes_out(game_at_bat, game_at_bat.basic_play)

            # Analyze Offensive Play
            regex = "(^[A-Z]+)(.*)"
            if re.search(regex, a_str):
                play_list = regex_split(regex, a_str)
                op_event = play_list.pop(0)
                for result in play_list:
                    logger.debug("Basic_Play Modifiers: - LEN=%s, RESULT = %s", len(play_list), result)

                event = EventFactory.__create_event_by_name(op_event, game_at_bat)
                event.handle_advances(game_at_bat, game_at_bat.play.advances)
                event.handle(game_at_bat, action)
                #event.debug_check_key_attributes_out(game_at_bat, play_list)
