""" Game Event Constants

Constants related to game events in the Retrosheet data feed.
"""
class EventCodes:

    WALK = "W"
    SINGLE = "S"
    DOUBLE = "D"
    TRIPLE = "T"
    CAUGHT_STEALING = "CS"
    STRIKEOUT = "K"
    HOMERUN = "HR"
    ERROR = "E"
    NO_PLAY_SUB_COMING = "NP"
    STOLEN_BASE = "SB"

class Modifiers:

    CALLED_THIRD_STRIKE = "C"
    THROW = "TH"
    GROUNDER = "G"
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
