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

ROSTER_FILE_EXTENSION_AMERICAN = ".EVA"
ROSTER_FILE_EXTENSION_NATIONAL = ".EVN"

# pylint: disable=too-few-public-methods
class Starter:
    """ Starter Entry Fields """
    player_code = None
    player_name = None
    home_team_flag = None
    batting_order = None
    fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "player_code": "{self.player_code}", "player_name": """ \
               f""""{self.player_name}", "home_team_flag": {self.home_team_flag}, """ \
               f""""batting_order": {self.batting_order}, "fielding_position": """ \
               f"""{self.fielding_position} }}"""

# pylint: disable=too-few-public-methods
class GamePlay:
    """ Base Class of Game Play Types """
    # pylint: disable=unnecessary-pass
    pass

# pylint: disable=too-few-public-methods
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
               f""""home_team_flag": {self.home_team_flag}, "player_code": """ \
               f""""{self.player_code}", "count": {self.count}, "pitches": """ \
               f""""{self.pitches}", "game_event": "{self.game_event}" }}"""


# pylint: disable=too-few-public-methods
class GameSubstitution(GamePlay):
    """ Player Substitution Event """
    player_code = None
    player_name = None
    home_team_flag = None
    batting_order = None
    fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "Substitution", "player_code": "{self.player_code}", """ \
               f""""player_name": "{self.player_name}", "home_team_flag": """ \
               f"""{self.home_team_flag}, "batting_order": {self.batting_order}, """ \
               f""""fielding_position": {self.fielding_position} }}"""


# pylint: disable=too-few-public-methods
class Data:
    """ Represents the end of game data records, such as earned runs. """
    data_type = None
    pitcher_player_code = None
    quantity = None

    def __str__(self) -> str:
        return f"""{{ "data_type": "{self.data_type}", "pitcher_player_code": """ + \
               f""""{self.pitcher_player_code}", "quantity": {self.quantity} }}"""


# pylint: disable=too-few-public-methods
class Game:
    """ Data Structure for a game chunk that is incrementally assembled as 
    the file is parsed.
    """
    id = None
    info_attributes = {}
    starters = []
    game_plays = []
    data = []

    def __str__(self) -> str:
        response = f"""{{ "id": "{self.id}", "info_attributes": "{self.info_attributes}", """
        response += """"starters": {{ """
        c = 0
        for starter in self.starters:
            if c > 0:
                response += ", "
            response += str(starter)
            c += 1
        response += " } "
        response += """"game_plays": {{ """
        c = 0
        for play in self.game_plays:
            if c > 0:
                response += ", "
            response += str(play)
            c += 1
        response += " } "
        response += """"data": {{ """
        c = 0
        for d in self.data:
            if c > 0:
                response += ", "
            response += str(d)
            c += 1
        response += " } "
        response += "}"
        return response


def save_game(game):
    """ Save the provided game chunk to the database.
    
        game - game to save 
    """
    # pylint: disable=unnecessary-pass
    pass


# pylint: disable=too-many-statements
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
                    # pylint: disable=unnecessary-pass
                    pass
                elif row[0] == "info":
                    game.info_attributes[row[1]] = row[2]
                elif row[0] == "start":
                    starter = Starter()
                    starter.player_code = row[1]
                    starter.player_name = row[2]
                    starter.home_team_flag = row[3] == "1"
                    starter.batting_order = int(row[4])
                    starter.fielding_position = int(row[5])
                    game.starters.append(starter)
                elif row[0] == "play":
                    game_at_bat = GameAtBat()
                    game_at_bat.inning = row[1]
                    game_at_bat.home_team_flag = row[2] == "1"
                    game_at_bat.player_code = row[3]
                    game_at_bat.count = row[4]
                    game_at_bat.pitches = row[5]
                    game_at_bat.game_event = row[6]
                    game.game_plays.append(game_at_bat)
                elif row[0] == "sub":
                    game_subst = GameSubstitution()
                    game_subst.player_code = row[1]
                    game_subst.player_name = row[2]
                    game_subst.home_team_flag = row[3] == "1"
                    game_subst.batting_order = row[4]
                    game_subst.fielding_position = row[5]
                    game.game_plays.append(game_subst)
                elif row[0] == "data":
                    data = Data()
                    data.data_type = row[1]
                    data.pitcher_player_code = row[2]
                    data.quantity = int(row[3])
                    game.data.append(data)
                elif row[0] == "com":
                    logger.debug("Comment: %s", row[1])
                else:
                    logger.error("Unknown Row Type!  %s", row[0])

        # Save running game
        logger.info("Saving Game")
        save_game(game)

    print ("# of games: ", len(game_chunks))
    #print (game_chunks[0].info_attributes)
    print (game)


def import_all_event_data_files(directory):
    """ Imports all event data files stored in the specified directory.
    
        directory - directory to import roster files from
    """
    logger.info("Importing Roster Data Files from Directory: %s", directory)
    for file in os.listdir(directory):
        if file.endswith(ROSTER_FILE_EXTENSION_AMERICAN) or \
           file.endswith(ROSTER_FILE_EXTENSION_NATIONAL):
            import_event_file(file, directory)

            logger.debug("Deleting file after successful processing: %s", file)
            os.remove(file)
    logger.debug("All files imported")


if __name__ == "__main__":
    import_event_file("2000ANA.EVA", "data/raw/")
