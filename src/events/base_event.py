""" Core Game Event

Base logic for game events.
"""
import logging

logger = logging.getLogger(__name__)

class BaseEvent(object):
    """ Base class for all game events.  """

    def handle(self, game_at_bat, play_list):
        """ Each Game Event Class should implement this method."""
        raise NotImplementedError()

    def batter_progressed_runners(self, game_at_bat):
        if game_at_bat.runner_on_1b:
            logger.info("1st Base Runner Progressed")
            if game_at_bat.runner_on_2b:
                logger.info("2nd Base Runner Progressed")
                if game_at_bat.runner_on_3b:
                    logger.info("3rd Base Runner Progressed")
                    self.score(game_at_bat)
                    game_at_bat.runner_on_3b = False
                game_at_bat.runner_on_3b = True
                game_at_bat.runner_on_2b = False
            game_at_bat.runner_on_2b = True
            game_at_bat.runner_on_1b = False
        game_at_bat.runner_on_1b = True

    def debug_check_key_attributes_in(self, game_at_bat, op_details):
        logger.info ("BasicPlay=<%s>, Modifiers=<%s>, Advance=<%s>, op_details=<%s>", game_at_bat.basic_play, game_at_bat.modifiers, game_at_bat.advance, op_details)

    def debug_check_key_attributes_out(self, game_at_bat, op_details):
        logger.info("Score=%s-%s, Outs=%s, 1B=%s, 2B=%s, 3B=%s", game_at_bat.score_visitor,
                    game_at_bat.score_home, game_at_bat.outs, game_at_bat.runner_on_1b, 
                    game_at_bat.runner_on_2b, game_at_bat.runner_on_3b)
        if len(op_details) > 0:
            msg = f"UNHANDLED DETAILS!!!  {op_details}"
            logger.error(msg)
            raise ValueError(msg)


    def score(self, game_at_bat):
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

    def handle_advances(self, game_at_bat):
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
