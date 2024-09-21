""" Core Game Event

Base logic for game events.
"""
import logging
from events.constants import Parameters

logger = logging.getLogger(__name__)

class BaseEvent(object):
    """ Base class for all game events.  """

    def handle(self, game_at_bat, play_list):
        """ Each Game Event Class should implement this method."""
        raise NotImplementedError()

    def batter_progressed_runners(self, game_at_bat):
        self.advance_runner(game_at_bat, "B", "1", "-")

    def debug_check_key_attributes_in(self, game_at_bat, op_details):
        logger.info ("BasicPlay=<%s>, Modifiers=<%s>, Advance=<%s>, op_details=<%s>", game_at_bat.basic_play, game_at_bat.modifiers, game_at_bat.advance, op_details)

    def debug_check_key_attributes_out(self, game_at_bat, op_details):
        logger.info("Score=%s-%s, Outs=%s, 1B=%s, 2B=%s, 3B=%s", game_at_bat.score_visitor,
                    game_at_bat.score_home, game_at_bat.outs, game_at_bat.runner_on_1b, 
                    game_at_bat.runner_on_2b, game_at_bat.runner_on_3b)
        if len(op_details) > 0:
            self.fail(f"UNHANDLED DETAILS!!!  {op_details}")


    def score(self, game_at_bat):
        """ Update the score based on the team at bat.
        
            game_at_bat - game at bat
        """
        if game_at_bat.home_team_flag is None:
            self.fail("Unknown Home Team Flag Type!  Its unexpectedly None!")
        if game_at_bat.home_team_flag:
            game_at_bat.score_home += 1
            logger.info("Home Team Scored!")
        else:
            game_at_bat.score_visitor += 1
            logger.info("Visiting Team Scored!")

    def advance_runner(self, game_at_bat, base_from, base_to, advancement_type = "-", parameter = ""):
        """ Advance runner from the specified from to the to base.
        
            game_at_bat - game at bat
            base_from - starting base
            base_to - ending base
            advancement_type - advancement type character
        """
        current_base = base_from
        while True:
            # stop the progression once the runner reaches the target base
            if current_base == base_to or current_base == "H":
                break
    
            # advance one base
            if current_base == "B":
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
                current_base = "1"

            elif current_base == "1":
                if not game_at_bat.runner_on_1b:
                    self.fail(f"Runner on 1st advancing to {base_to} but no runner is on base!")
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
                current_base = "2"

            elif current_base == "2":
                if not game_at_bat.runner_on_2b:
                    self.fail(f"Runner on 2nd advancing to {base_to} but no runner is on base!")
                if game_at_bat.runner_on_3b:
                    logger.info("3rd Base Runner Progressed")
                    self.score(game_at_bat)
                    game_at_bat.runner_on_3b = False
                game_at_bat.runner_on_3b = True
                game_at_bat.runner_on_2b = False
                current_base = "3"

            elif current_base == "3":
                if not game_at_bat.runner_on_3b:
                    self.fail(f"Runner on 3rd advancing to {base_to} but no runner is on base!")
                self.score(game_at_bat)
                game_at_bat.runner_on_3b = False
                current_base = "H"

            else:
                self.fail(f"Unknown value for current_base: {current_base}")

        if advancement_type == "X":
            extra_text = ""
            if parameter == None or len(parameter) == 0:
                pass
            if parameter == Parameters.UNEARNED_RUN:
                extra_text = "Unearned Run"
            elif parameter == Parameters.RBI_CREDITED:
                extra_text = "Credited with RBI"
            elif parameter == Parameters.RBI_NOT_CREDITED_1 or parameter == Parameters.RBI_NOT_CREDITED_2:
                extra_text = "RBI NOT Credited"
            else:
                self.fail(f"Unknown advancement parameter = {parameter}")
            logger.info("Base Runner OUT while progressing from %s to %s.  %s", base_from, base_to, extra_text)
            game_at_bat.outs += 1
        
        elif advancement_type == "-":
            logger.info("Base Runner advanced from %s to %s.", base_from, base_to)

        else:
            self.fail(f"Unexpected advance type = {advancement_type}")


    def handle_advances(self, game_at_bat):
        if game_at_bat.advance is not None and len(game_at_bat.advance) > 0:
            advances = game_at_bat.advance.split(";")
            game_at_bat.advance = ""
            for advance in advances:
                # gather first 3 characters - required for advance
                if len(advance) < 3:
                    self.fail(f"Advancement entry is invalid due to length! {advance}")            
                base_from = advance[0]
                safe_or_out = advance[1]
                base_to = advance[2]
                parameter = advance[3:]

                self.advance_runner(game_at_bat, base_from, base_to, safe_or_out, parameter)


    def fail(self, msg):
        """ Log and fail the application with the specified message.
        
            msg - message
        """
        logger.error(msg)
        raise ValueError(msg)
