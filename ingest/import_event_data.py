""" Import Event Data Utilities 

Event files are a more complicated format that involves piecing together games
based on a serious of related rows in a particular order.  These utilities are
parsers for these files that are then able to insert into a relational database
that we can more easily use to build training data for the models.
"""
import logging
import os
import csv

logger = logging.getLogger(__name__)

class Starter:
    """ Starter Entry Fields """
    player_code = None
    player_name = None
    home_team_flag = None
    batting_order = None
    fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "player_code": "{self.player_code}", "player_name": "{self.player_name}", """ \
               f""""home_team_flag": {self.home_team_flag}, "batting_order": {self.batting_order}, """ \
               f""""fielding_position": {self.fielding_position} }}"""

class GamePlay:
    pass

class GameAtBat(GamePlay):
    """ At Bat Record for a Game """
    inning = None
    home_team_flag = None
    player_code = None
    count = None
    pitches = None
    game_event = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "AtBat", "inning": "{self.inning}", """ \
               f""""home_team_flag": {self.home_team_flag}, "player_code": "{self.player_code}", """ \
               f""""count": {self.count}, "pitches": "{self.pitches}", "game_event": "{self.game_event}" }}"""


class GameSubstitution(GamePlay):
    """ Player Substitution Event """
    player_code = None
    player_name = None
    home_team_flag = None
    batting_order = None
    fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "Substitution", "player_code": "{self.player_code}", """ \
               f""""player_name": "{self.player_name}", "home_team_flag": {self.home_team_flag}, """ \
               f""""batting_order": {self.batting_order}, "fielding_position": {self.fielding_position} }}"""


# pylint: disable=too-few-public-methods
class Game:
    """ Data Structure for a game chunk that is incrementally assembled as 
    the file is parsed.
    """
    id = None
    info_attributes = {}
    starters = []
    game_plays = []
    data_list = []

    def __str__(self) -> str:
        response = f"""{{ "id": "{self.id}", "info_attributes": "{self.info_attributes}", """ \
                   f""""starters": "{self.starters}", "data_list": {self.data_list}, """
        response += """"game_plays": {{ """
        c = 0
        for play in self.game_plays:
            if c > 0:
                response += ", "
            response += str(play)
            c += 1
        response += "} }"
        return response


def save_game(game):
    """ Save the provided game chunk to the database.
    
        game - game to save 
    """
    pass


def import_event_file(file, directory):
    """ Imports the specified event file.
    
        file - file to import
        directory - location of file
    """
    file_with_path = directory + file
    logger.info("Importing Event File: %s", file_with_path)

    # Ensure file exists
    if not os.path.isfile(file_with_path):
        logger.error("Input file does not exist!  %s", file_with_path)
        raise ValueError("Cannot load file because it does not exist!")

    # Load CSV
    game_chunks = []
    with open(file_with_path, newline='', encoding="utf-8") as csvfile:
        game = None

        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if len(row) > 0:
                if row[0] == "id":
                    # Save running game
                    logger.info("Saving Game")
                    save_game(game)

                    # Creating new Game
                    game = Game()
                    game.id = row[1]
                    game_chunks.append(game)
                elif row[0] == "version":
                    pass
                elif row[0] == "info":
                    game.info_attributes[row[1]] = row[2]
                elif row[0] == "start":
                    starter = Starter()
                    starter.player_code = row[1]
                    starter.player_name = row[2]
                    starter.home_team_flag = (row[3] == "1")
                    starter.batting_order = int(row[4])
                    starter.fielding_position = int(row[5])
                    game.starters.append(starter)
                elif row[0] == "play":
                    game_at_bat = GameAtBat()
                    game_at_bat.inning = row[1]
                    game_at_bat.home_team_flag = (row[2] == "1")
                    game_at_bat.player_code = row[3]
                    game_at_bat.count = row[4]
                    game_at_bat.pitches = row[5]
                    game_at_bat.game_event = row[6]
                    game.game_plays.append(game_at_bat)
                elif row[0] == "sub":
                    game_subst = GameSubstitution()
                    game_subst.player_code = row[1]
                    game_subst.player_name = row[2]
                    game_subst.home_team_flag = (row[3] == "1")
                    game_subst.batting_order = row[4]
                    game_subst.fielding_position = row[5]
                    game.game_plays.append(game_subst)
                elif row[0] == "data":
                    game.data_list.append(row)
                elif row[0] == "com":
                    logger.debug("Comment: %s", row[1])
                else:
                    logger.error("Unknown Row Type!  %s", row[0])

        # Save running game
        logger.info("Saving Game")
        save_game(game)

    print ("# of games: ", len(game_chunks))
    #print (game_chunks[0].info_attributes)
    #print (game)


if __name__ == "__main__":
    import_event_file("2000ANA.EVA", "data/raw/")
