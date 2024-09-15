""" Application of game events logic

Apply game events to game at bat event data.
"""
import logging
import re
from data_utils import regex_split, split_leading_num

logger = logging.getLogger(__name__)

BASIC_EVENT_CODE_WALK = "W"
BASIC_EVENT_CODE_SINGLE = "S"
BASIC_EVENT_CODE_DOUBLE = "D"
BASIC_EVENT_CODE_TRIPLE = "T"
BASIC_EVENT_CODE_CAUGHT_STEALING = "CS"
BASIC_EVENT_CODE_STRIKEOUT = "K"
BASIC_EVENT_CODE_HOMERUN = "HR"
BASIC_EVENT_CODE_ERROR = "E"
BASIC_EVENT_CODE_NO_PLAY_SUB_COMING = "NP"

MODIFIER_CALLED_THIRD_STRIKE = "C"
MODIFIER_THROW = "TH"
MODIFIER_GROUNDER = "G"


def debug_check_key_attributes_in(game_at_bat, op_details):
    logger.info ("BasicPlay=<%s>, Modifiers=<%s>, Advance=<%s>, op_details=<%s>", game_at_bat.basic_play, game_at_bat.modifiers, game_at_bat.advance, op_details)

def debug_check_key_attributes_out(game_at_bat, op_details):
    logger.info("Score=%s-%s, Outs=%s, 1B=%s, 2B=%s, 3B=%s", game_at_bat.score_visitor,
                game_at_bat.score_home, game_at_bat.outs, game_at_bat.runner_on_1b, 
                game_at_bat.runner_on_2b, game_at_bat.runner_on_3b)
    if len(op_details) > 0:
        msg = f"UNHANDLED DETAILS!!!  {op_details}"
        logger.error(msg)
        raise ValueError(msg)


def score(game_at_bat):
    """ Update the score based on the team at bat.
    
        game_at_bat - game at bat
    """
    if game_at_bat.home_team_flag is None:
        msg = "Unknown Home Team Flag Type!  Its unexpectedly None!"
        logger.error(msg)
        raise ValueError(msg)
    if game_at_bat.home_team_flag:
        game_at_bat.score_home += 1
        logger.info("Home Team Scored!")
    else:
        game_at_bat.score_visitor += 1
        logger.info("Visiting Team Scored!")

def handle_advances(game_at_bat):
    if game_at_bat.advance is not None and len(game_at_bat.advance) > 0:
        advances = game_at_bat.advance.split(";")
        game_at_bat.advance = ""
        for advance in advances:
            if len(advance) != 3 or re.match("^\d[X-][H\d]$", advance) == None:
                msg = f"Advancement entry is invalid! {advance}"
                logger.error(msg)
                raise ValueError(msg)
        
            base_from = int(advance[0])
            base_to = advance[2]

            if base_from == 1:
                game_at_bat.runner_on_1b = False
            elif base_from == 2:
                game_at_bat.runner_on_2b = False
            elif base_from == 3:
                game_at_bat.runner_on_3b = False
            else:
                msg = f"Unexpected base_from value = {base_to}"
                logger.error(msg)
                raise ValueError(msg)
            
            if advance[1] == "X":
                logger.info("Base Runner OUT while progressing from %s to %s.", base_from, base_to)
                game_at_bat.outs += 1
            
            elif advance[1] == "-":
                logger.info("Base Runner advanced from %s to %s.", base_from, base_to)

                if base_to == "2":
                    pass
                elif base_to == "3":
                    pass
                elif base_to == "H":
                    pass
                else:
                    msg = f"Unexpected base_to value = {base_to}"
                    logger.error(msg)
                    raise ValueError(msg)

            else:
                msg = f"Unexpected advance type = {advance[1]}"
                logger.error(msg)
                raise ValueError(msg)


def batter_progressed_runners(game_at_bat):
    if game_at_bat.runner_on_1b:
        logger.info("1st Base Runner Progressed")
        if game_at_bat.runner_on_2b:
            logger.info("2nd Base Runner Progressed")
            if game_at_bat.runner_on_3b:
                logger.info("3rd Base Runner Progressed")
                score(game_at_bat)
                game_at_bat.runner_on_3b = False
            game_at_bat.runner_on_3b = True
            game_at_bat.runner_on_2b = False
        game_at_bat.runner_on_2b = True
        game_at_bat.runner_on_1b = False
    game_at_bat.runner_on_1b = True

def op_walk(game_at_bat, op_details):
    """ Walk the player
    
        game_at_bat - game at bat
        op_details - offensive play details
    """
    logger.info("Batter Walked")
        
    batter_progressed_runners(game_at_bat)

def op_strikeout(game_at_bat, op_details):
    called = ""
    if len(game_at_bat.modifiers) > 0:
        called = game_at_bat.modifiers.pop(0)
        if called == MODIFIER_CALLED_THIRD_STRIKE:
            called = "CALLED THIRD STRIKE"
        else:
            raise ValueError(f"Unknown modifier on strikeout! {called}")
    logger.info("Player Striked Out.  %s", called)
    game_at_bat.outs += 1

def op_homerun(game_at_bat, op_details):
    logger.info("Out of Park Home Run hit by batter")
    if len(game_at_bat.modifiers) > 0:
        game_at_bat.hit_to_location = game_at_bat.modifiers.pop(0)
    if game_at_bat.runner_on_3b:
        game_at_bat.runner_on_3b = False
        score(game_at_bat)
    if game_at_bat.runner_on_2b:
        game_at_bat.runner_on_2b = False
        score(game_at_bat)
    if game_at_bat.runner_on_1b:
        game_at_bat.runner_on_1b = False
        score(game_at_bat)
    score(game_at_bat)

def op_single(game_at_bat, op_details):
    if len(op_details) > 0:
        game_at_bat.fielded_by = op_details.pop(0)
    if len(game_at_bat.modifiers) > 0:
        game_at_bat.hit_to_location = game_at_bat.modifiers.pop(0)
    if len(game_at_bat.modifiers) > 1:
        raise f"Too many modifiers!  {game_at_bat.modifiers}"
    logger.info("Player Hit Single to %s.  Fielded By %s.",
                 game_at_bat.hit_to_location, game_at_bat.fielded_by)
    batter_progressed_runners(game_at_bat)

def op_double(game_at_bat, op_details):
    if len(op_details) > 0:
        game_at_bat.fielded_by = op_details.pop(0)
    if len(game_at_bat.modifiers) > 0:
        game_at_bat.hit_to_location = game_at_bat.modifiers.pop(0)
    if len(game_at_bat.modifiers) > 1:
        raise f"Too many modifiers!  {game_at_bat.modifiers}"
    logger.info("Player Hit Double to %s.  Fielded By %s.",
                 game_at_bat.hit_to_location, game_at_bat.fielded_by)
    batter_progressed_runners(game_at_bat)
    batter_progressed_runners(game_at_bat)
    game_at_bat.runner_on_1b = False

def op_triple(game_at_bat, op_details):
    if len(op_details) > 0:
        game_at_bat.fielded_by = op_details.pop(0)
    if len(game_at_bat.modifiers) > 0:
        game_at_bat.hit_to_location = game_at_bat.modifiers.pop(0)
    if len(game_at_bat.modifiers) > 1:
        raise f"Too many modifiers!  {game_at_bat.modifiers}"
    logger.info("Player Hit Triple to %s.  Fielded By %s.",
                 game_at_bat.hit_to_location, game_at_bat.fielded_by)
    batter_progressed_runners(game_at_bat)
    batter_progressed_runners(game_at_bat)
    game_at_bat.runner_on_1b = False
    batter_progressed_runners(game_at_bat)
    game_at_bat.runner_on_1b = False

def op_caught_stealing(game_at_bat, op_details):
    details = op_details.pop()
    details_list = split_leading_num(details)
    logger.debug("Stolen Base Details: %s", details_list)
    base = int(details_list.pop(0))
    logger.warning("Stolen Base Details Being Ignored!: %s", details_list)
    logger.info("Player Caught Stealing to Base #%s", base)
    game_at_bat.outs += 1
    if base == 2:
        game_at_bat.runner_on_1b = False
    elif base == 3:
        game_at_bat.runner_on_2b = False
    elif base == 4:
        game_at_bat.runner_on_3b = False

def op_error(game_at_bat, op_details):
    fb = ""
    if len(op_details) > 0:
        game_at_bat.fielded_by = op_details.pop(0)
        fb = f"by {game_at_bat.fielded_by}"
    cause = ""
    if len(game_at_bat.modifiers) > 0:
        cause = game_at_bat.modifiers.pop(0)
        if cause == MODIFIER_THROW:
            cause = "Due to Throw By "
    logger.info("Offensive Error Getting Batter on Base.  %s %s", cause, fb)
    batter_progressed_runners(game_at_bat)

def offensive_play(game_at_bat, play_list):
    """ Handle offensive play based on provided action list.
    
    game_at_bat - game at bat
    play_list - list of offensive play components
    """
    logger.debug("Offensive Play.  Play_List<%s>", play_list)

    op_event = play_list.pop(0)
    for result in play_list:
        logger.debug("Basic_Play Modifiers: - LEN=%s, RESULT = %s", len(play_list), result)

    debug_check_key_attributes_in(game_at_bat, play_list)

    if op_event == BASIC_EVENT_CODE_WALK:
        op_walk(game_at_bat, play_list)
    elif op_event == BASIC_EVENT_CODE_STRIKEOUT:
        op_strikeout(game_at_bat, play_list)
    elif op_event == BASIC_EVENT_CODE_SINGLE:
        op_single(game_at_bat, play_list)
    elif op_event == BASIC_EVENT_CODE_DOUBLE:
        op_double(game_at_bat, play_list)
    elif op_event == BASIC_EVENT_CODE_TRIPLE:
        op_triple(game_at_bat, play_list)
    elif op_event == BASIC_EVENT_CODE_CAUGHT_STEALING:
        op_caught_stealing(game_at_bat, play_list)
    elif op_event == BASIC_EVENT_CODE_ERROR:
        op_error(game_at_bat, play_list)
    elif op_event == BASIC_EVENT_CODE_HOMERUN:
        op_homerun(game_at_bat, play_list)
    elif op_event == BASIC_EVENT_CODE_NO_PLAY_SUB_COMING:
        logger.debug("Ignoring No Play Event.")
        pass
    else:
        msg = f"Unknown Offensive Play!  Play=<{op_event}>, FullBasicPlayDetails=<{game_at_bat.basic_play}>", 
        logger.error(msg)
        raise ValueError(msg)

    handle_advances(game_at_bat)
    debug_check_key_attributes_out(game_at_bat, play_list)


def defensive_play(game_at_bat, play_list):
    """ Handle defensive play based on provided action list.exc_info=
    
    game_at_bat - game at bat
    play_list - list of offensive play components
    """
    logger.debug("Defensive Play.  Play_List<%s>", play_list)

    # First fielding event after hit
    dp_event = play_list.pop(0)
    db_event_list = split_leading_num(dp_event)
    fielders = db_event_list.pop(0)
    game_at_bat.fielded_by = fielders[len(fielders) - 1]
    game_at_bat.outs += 1
    due_to = ""
    if len(game_at_bat.modifiers) > 0:
        modifier = game_at_bat.modifiers.pop(0)
        if modifier == MODIFIER_GROUNDER:
            due_to = "Due to Ground Ball"
    logger.info ("Batter out after hit.  Out credited to pos %s %s", game_at_bat.fielded_by, due_to)
    if len(db_event_list) > 0:
        logger.warning("Unhandled Fielded By Metadata.  %s", db_event_list)

    handle_advances(game_at_bat)


def interpret_game_at_bat_event(game_at_bat):
    """ Interpret the game at bat event details to determine outs, runners on base, runs,
    etc.
    
    game_at_bat - game at bat record
    """
    logger.debug("Interpretting game at bat event.  BasicPlay = <%s>, Modifiers = <%s>, Advance = <%s>", game_at_bat.basic_play, game_at_bat.modifiers, game_at_bat.advance)

    # Analyze Defensive Play
    regex = "(^[0-9]+)"
    if re.search(regex, game_at_bat.basic_play):
        play_list = regex_split(regex, game_at_bat.basic_play)
        defensive_play(game_at_bat, play_list)

    # Analyze Offensive Play
    regex = "(^[A-Z]+)(.*)"
    if re.search(regex, game_at_bat.basic_play):
        play_list = regex_split(regex, game_at_bat.basic_play)
        offensive_play(game_at_bat, play_list)

    if game_at_bat.modifiers is not None and len(game_at_bat.modifiers) > 0:
        msg = f"UNHANDLED MODIFIERS!!!  {game_at_bat.modifiers}"
        logger.error(msg)
        raise ValueError(msg)
    if game_at_bat.advance is not None and len(game_at_bat.advance) > 0:
        msg = f"UNHANDLED ADVANCE!!!  {game_at_bat.advance}"
        logger.error(msg)
        raise ValueError(msg)

    #raise ValueError("incremental processing as i work through this")
