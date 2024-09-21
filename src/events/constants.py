""" Game Event Constants

Constants related to game events in the Retrosheet data feed.
"""
class EventCodes:

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
    STRIKEOUT = "K"
    HOMERUN = "HR"
    ERROR = "E"
    NO_PLAY_SUB_COMING = "NP"
    STOLEN_BASE = "SB"
    BATTER_HIT_BY_PITCH = "HP"
    FIELDERS_CHOICE = "FC"
    PICKED_OFF = "PO"
    FLY_BALL_ERROR = "FLE"
    DEFENSIVE_INDIFFERENCE = "DI"

class Modifiers:

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

class Parameters:

    UNEARNED_RUN = "UR"
    RBI_CREDITED = "RBI"
    RBI_NOT_CREDITED_1 = "NR"
    RBI_NOT_CREDITED_2 = "NORBI"
