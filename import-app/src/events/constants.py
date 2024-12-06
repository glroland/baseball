""" Game Event Constants

Constants related to game events in the Retrosheet data feed.
"""
#pylint: disable=too-few-public-methods
class EventCodes:
    """ Retrosheet Event Codes """

    WALK = "W"
    BALK = "BK"
    WILD_PITCH = "WP"
    INTENTIONAL_WALK_1 = "IW"
    INTENTIONAL_WALK_2 = "I"
    SINGLE = "S"
    DOUBLE = "D"
    TRIPLE = "T"
    CAUGHT_STEALING = "CS"
    CAUGHT_STEALING_HOME = "CSH"
    PICKED_OFF_CAUGHT_STEALING = "POCS"
    PICKED_OFF_CAUGHT_STEALING_HOME = "POCSH"
    STRIKEOUT = "K"
    HOMERUN = "HR"
    ERROR = "E"
    NO_PLAY_SUB_COMING = "NP"
    STOLEN_BASE = "SB"
    STOLEN_BASE_HOME = "SBH"
    BATTER_HIT_BY_PITCH = "HP"
    FIELDERS_CHOICE = "FC"
    PICKED_OFF = "PO"
    FLY_BALL_ERROR = "FLE"
    DEFENSIVE_INDIFFERENCE = "DI"
    GROUND_RULE_DOUBLE = "DGR"
    PASSED_BALL = "PB"
    BASE_RUNNER_ADVANCE = "OA"
    WILD_PITCH = "WP"
    CATCHER_INTERFERENCE = "C"

#pylint: disable=too-few-public-methods
class Modifiers:
    """ Retrosheet Action Modifier Codes """

    CALLED_THIRD_STRIKE = "C"
    THROW = "TH"
    GROUNDER = "G"
    GROUNDER_UNKNOWN = "G#"
    DOUBLE_PLAY = "DP"
    TRIPLE_PLAY = "TP"
    GROUNDER_DOUBLE_PLAY = "GDP"
    GROUNDER_TRIPLE_PLAY = "GTP"
    LINED_INTO_DOUBLE_PLAY = "LDP"
    LINED_INTO_TRIPLE_PLAY = "LTP"
    LINE_DRIVE = "L"
    FORCE_OUT = "FO"
    FOUL = "FL"
    FLY = "F"
    FLY_BALL_DOUBLE_PLAY = "FDP"
    FAN_INTERFERENCE = "FINT"
    POP_FLY = "P"
    RUNNER_PASSED_ANOTHER_RUNNER = "PASS"
    SACRIFICE_FLY = "SF"
    SACRIFICE_HIT_BUNT = "SH"
    BUNT_POPUP = "BP"
    PICKED_OFF = "PO"
    GROUND_BALL_BUNT = "BG"
    LINE_DRIVE_BUNT = "BL"
    BATTER_INTERFERENCE = "BINT"

#pylint: disable=too-few-public-methods
class Parameters:
    """ Actionsheet Parameter Codes """

    UNEARNED_RUN = "UR"
    RBI_CREDITED = "RBI"
    RBI_NOT_CREDITED_1 = "NR"
    RBI_NOT_CREDITED_2 = "NORBI"
    ERROR = "E"