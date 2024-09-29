""" Event Code Mappings

Map event codes to event classes
"""
from pydantic import BaseModel
from events.constants import EventCodes

class EventCodeMappings:
    """ Event Code Mappings """

    EVENT_MODULE : str = "module"
    EVENT_CLASS : str = "class"
    MAPPING_DEFENSIVE : str = "defense"

    mappings = {

        MAPPING_DEFENSIVE:
        {
            EVENT_MODULE: "events.defensive_play",
            EVENT_CLASS: "DefensivePlayEvent"
        },

        EventCodes.WALK:
        {
            EVENT_MODULE: "events.walk",
            EVENT_CLASS: "WalkEvent"
        },

        EventCodes.BALK:
        {
            EVENT_MODULE: "events.walk",
            EVENT_CLASS: "WalkEvent"
        },

        EventCodes.WILD_PITCH:
        {
            EVENT_MODULE: "events.walk",
            EVENT_CLASS: "WalkEvent"
        },

        EventCodes.FIELDERS_CHOICE:
        {
            EVENT_MODULE: "events.fielders_choice",
            EVENT_CLASS: "FieldersChoiceEvent"
        },

        EventCodes.INTENTIONAL_WALK_1:
        {
            EVENT_MODULE: "events.walk",
            EVENT_CLASS: "WalkEvent"
        },

        EventCodes.INTENTIONAL_WALK_2:
        {
            EVENT_MODULE: "events.walk",
            EVENT_CLASS: "WalkEvent"
        },

        EventCodes.SINGLE:
        {
            EVENT_MODULE: "events.single",
            EVENT_CLASS: "SingleEvent"
        },

        EventCodes.DOUBLE:
        {
            EVENT_MODULE: "events.double",
            EVENT_CLASS: "DoubleEvent"
        },

        EventCodes.TRIPLE:
        {
            EVENT_MODULE: "events.triple",
            EVENT_CLASS: "TripleEvent"
        },

        EventCodes.CAUGHT_STEALING:
        {
            EVENT_MODULE: "events.caught_stealing",
            EVENT_CLASS: "CaughtStealingEvent"
        },

        EventCodes.PICKED_OFF_CAUGHT_STEALING:
        {
            EVENT_MODULE: "events.caught_stealing",
            EVENT_CLASS: "CaughtStealingEvent"
        },

        EventCodes.PICKED_OFF:
        {
            EVENT_MODULE: "events.picked_off",
            EVENT_CLASS: "PickedOffEvent"
        },

        EventCodes.STRIKEOUT:
        {
            EVENT_MODULE: "events.strikeout",
            EVENT_CLASS: "StrikeoutEvent"
        },

        EventCodes.HOMERUN:
        {
            EVENT_MODULE: "events.homerun",
            EVENT_CLASS: "HomerunEvent"
        },

        EventCodes.ERROR:
        {
            EVENT_MODULE: "events.defensive_error",
            EVENT_CLASS: "DefensiveErrorEvent"
        },

        EventCodes.STOLEN_BASE:
        {
            EVENT_MODULE: "events.stolen_base",
            EVENT_CLASS: "StolenBaseEvent"
        },

        EventCodes.DEFENSIVE_INDIFFERENCE:
        {
            EVENT_MODULE: "events.defensive_indifference",
            EVENT_CLASS: "DefensiveIndifferenceEvent"
        },

        EventCodes.BATTER_HIT_BY_PITCH:
        {
            EVENT_MODULE: "events.hit_by_pitch",
            EVENT_CLASS: "HitByPitchEvent"
        },

        EventCodes.FLY_BALL_ERROR:
        {
            EVENT_MODULE: "events.fly_ball_error",
            EVENT_CLASS: "FlyBallErrorEvent"
        },

        EventCodes.GROUND_RULE_DOUBLE:
        {
            EVENT_MODULE: "events.ground_rule_double",
            EVENT_CLASS: "GroundRuleDoubleEvent"
        },

        EventCodes.PASSED_BALL:
        {
            EVENT_MODULE: "events.passed_ball",
            EVENT_CLASS: "PassedBallEvent"
        },

        EventCodes.BASE_RUNNER_ADVANCE:
        {
            EVENT_MODULE: "events.base_runner_advance",
            EVENT_CLASS: "BaseRunnerAdvanceEvent"
        }
    }
