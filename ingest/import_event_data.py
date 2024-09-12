""" Import Event Data Utilities 

Event files are a more complicated format that involves piecing together games
based on a serious of related rows in a particular order.  These utilities are
parsers for these files that are then able to insert into a relational database
that we can more easily use to build training data for the models.
"""
import logging
import os
import csv
import psycopg
from db_utils import connect_to_db, truncate_table

logger = logging.getLogger(__name__)

ROSTER_FILE_EXTENSION_AMERICAN = ".EVA"
ROSTER_FILE_EXTENSION_NATIONAL = ".EVN"

# pylint: disable=too-few-public-methods
class Starter:
    """ Starter Entry Fields """

    def __init__(self):
        self.player_code = None
        self.player_name = None
        self.home_team_flag = None
        self.batting_order = None
        self.fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "player_code": "{self.player_code}", "player_name": """ \
               f""""{self.player_name}", "home_team_flag": {str(self.home_team_flag).lower()}, """ \
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

    def __init__(self):
        self.inning = None
        self.home_team_flag = None
        self.player_code = None
        self.count = None
        self.pitches = None
        self.game_event = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "AtBat", "inning": "{self.inning}", """ \
               f""""home_team_flag": {str(self.home_team_flag).lower()}, "player_code": """ \
               f""""{self.player_code}", "count": {self.count}, "pitches": """ \
               f""""{self.pitches}", "game_event": "{self.game_event}" }}"""


# pylint: disable=too-few-public-methods
class GameSubstitution(GamePlay):
    """ Player Substitution Event """

    def __init__(self):
        self.player_code = None
        self.player_name = None
        self.home_team_flag = None
        self.batting_order = None
        self.fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "Substitution", "player_code": "{self.player_code}", """ \
               f""""player_name": "{self.player_name}", "home_team_flag": """ \
               f"""{str(self.home_team_flag).lower()}, "batting_order": {self.batting_order}, """ \
               f""""fielding_position": {self.fielding_position} }}"""


# pylint: disable=too-few-public-methods
class Data:
    """ Represents the end of game data records, such as earned runs. """

    def __init__(self):
        self.data_type = None
        self.pitcher_player_code = None
        self.quantity = None

    def __str__(self) -> str:
        return f"""{{ "data_type": "{self.data_type}", "pitcher_player_code": """ + \
               f""""{self.pitcher_player_code}", "quantity": {self.quantity} }}"""


# pylint: disable=too-few-public-methods
class Game:
    """ Data Structure for a game chunk that is incrementally assembled as 
    the file is parsed.
    """

    def __init__(self):
        self.game_id = None
        self.info_attributes = {}
        self.starters = []
        self.game_plays = []
        self.data = []

    def __str__(self) -> str:
        response = f"""{{ "id": "{self.game_id}", "info_attributes": {self.info_attributes}, """
        response += """"starters": [ """
        c = 0
        for starter in self.starters:
            if c > 0:
                response += ", "
            response += str(starter)
            c += 1
        response += " ], "
        response += """"game_plays": [ """
        c = 0
        for play in self.game_plays:
            if c > 0:
                response += ", "
            response += str(play)
            c += 1
        response += " ], "
        response += """"data": [ """
        c = 0
        for d in self.data:
            if c > 0:
                response += ", "
            response += str(d)
            c += 1
        response += " ] "
        response += "}"
        return response


def save_game_base_record(sql_connection, game):
    """ Save the provided game base record to the database.
    
        sql_connection - sql connection to use for the tx
        game - game record to save 
    """
    logger.debug("Saving Base Game Record!  ID=%s", game.game_id)

    # Save Game
    sql = """
        insert into game
        (
            id,
            game_date,
            game_time,
            game_number_that_day,
            team_visiting,
            team_home,
            game_site,
            night_flag,
            ump_home,
            ump_1b,
            ump_2b,
            ump_3b,
            official_scorer,
            temperature,
            wind_direction,
            wind_speed,
            field_condition,
            precipitation,
            sky,
            game_length,
            attendance,
            usedh,
            wp,
            lp,
            save_code
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game.game_id,
                game.info_attributes["date"],
                game.info_attributes["starttime"],
                game.info_attributes["number"],
                game.info_attributes["visteam"],
                game.info_attributes["hometeam"],
                game.info_attributes["site"],
                game.info_attributes["daynight"] == "night",
                game.info_attributes["umphome"],
                game.info_attributes["ump1b"],
                game.info_attributes["ump2b"],
                game.info_attributes["ump3b"],
                game.info_attributes["oscorer"],
                game.info_attributes["temp"],
                game.info_attributes["winddir"],
                game.info_attributes["windspeed"],
                game.info_attributes["fieldcond"],
                game.info_attributes["precip"],
                game.info_attributes["sky"],
                game.info_attributes["timeofgame"],
                game.info_attributes["attendance"],
                game.info_attributes["usedh"],
                game.info_attributes["wp"],
                game.info_attributes["lp"],
                game.info_attributes["save"]
            ]
        )


def save_game_starter(sql_connection, game_id, starter):
    """ Save the Game Starters.
    
        sql_connection - sql connection to use for transaction
        game_id - associated game id
        data - game data record
    """
    logger.debug("Saving Game Starter!  ID=%s, Starter=%s", game_id, starter)

    # Save Game Starter
    sql = """
        insert into game_starter
        (
            id, player_code, player_name, home_team_flag, batting_order, fielding_position
        )
        values 
        (
            %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                starter.player_code,
                starter.player_name,
                starter.home_team_flag,
                starter.batting_order,
                starter.fielding_position
            ]
        )


def save_game_data(sql_connection, game_id, data):
    """ Save the Game Data Entry.
    
        sql_connection - sql connection to use for transaction
        game_id - game id
        data - game data record
    """
    logger.debug("Saving Data Record!  ID=%s, Type=%s", game_id, data.data_type)

    # Save Data
    sql = """
        insert into game_data 
        (
            id, data_type, pitcher_player_code, quantity
        )
        values 
        (
            %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                data.data_type,
                data.pitcher_player_code,
                data.quantity
            ]
        )


def save_game_play(sql_connection, game_id, index):
    """ Save the Game Play record.
    
        sql_connection - sql connection to use for transaction
        game_id - associated game id
        index - game play index
    """
    logger.debug("Saving Game Play!  ID=%s, Index=%s", game_id, index)

    # Save Game Play
    sql = """
        insert into game_play
        (
            id, play_index
        )
        values 
        (
            %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                index
            ]
        )


def extract_and_save_pitches(sql_cursor, game_id, play_index, game_play):
    """ Extract the pitch strings and save as standalone events.  
    
        sql_cursor - sql cursor to use for tx
        game_id - associated game id
        play_index - game play index
        atbat - at bat record
    """
    pitches = game_play.pitches
    logger.debug("Saving At Bat Pitch!  ID=%s, PlayIndex=%s, Pitches=%s",
                     game_id, play_index, pitches)
    sql = """
            insert into game_play_atbat_pitch (id, play_index, pitch_index, pitch_type_cd)
            values(%s, %s, %s, %s)
          """
    pitch_index = 0
    for pitch_type_cd in pitches:
        pitch_index += 1
        logger.debug("Saving At Bat Pitch!  ID=%s, PlayIndex=%s, Pitches=%s, Pitch=%s",
                     game_id, play_index, pitches, pitch_type_cd)
        sql_cursor.execute(sql,
            [
                game_id,
                play_index,
                pitch_index,
                pitch_type_cd
            ]
        )


def save_game_play_atbat(sql_connection, game_id, index, atbat):
    """ Save the Game Play record.
    
        sql_connection - sql connection to use for transaction
        game_id - associated game id
        index - game play index
        atbat - at bat record
    """
    logger.debug("Saving At Bat!  ID=%s, Index=%s, AtBat=%s", game_id, index, atbat)

    # Save Game Play
    sql = """
        insert into game_play_atbat
        (
            id, play_index, inning, home_team_flag, player_code, count, pitches, game_event
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                index,
                atbat.inning,
                atbat.home_team_flag,
                atbat.player_code,
                atbat.count,
                atbat.pitches,
                atbat.game_event
            ]
        )
        extract_and_save_pitches(sql_cursor, game_id, index, atbat)


def save_game_play_sub(sql_connection, game_id, index, sub):
    """ Save the Game Play record.
    
        sql_connection - sql connection to use for transaction
        game_id - associated game id
        index - game play index
        sub - substitution record
    """
    logger.debug("Saving Substitution!  ID=%s, Index=%s, Sub=%s", game_id, index, sub)

    # Save Game Play
    sql = """
        insert into game_play_sub
        (
            id, play_index, player_code, player_name, home_team_flag, batting_order, fielding_position
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                index,
                sub.player_code,
                sub.player_name,
                sub.home_team_flag,
                sub.batting_order,
                sub.fielding_position
            ]
        )


def save_game(sql_connection, game):
    """ Save the provided game chunk to the database.
    
        sql_connection - sql connection to use for tx
        game - game to save 
    """
    logger.info("Saving Game Record!  ID=%s", game.game_id)
    try:
        save_game_base_record(sql_connection, game)
        for starter in game.starters:
            save_game_starter(sql_connection, game.game_id, starter)
        for data in game.data:
            save_game_data(sql_connection, game.game_id, data)
        game_play_index = 0
        for game_play in game.game_plays:
            game_play_index += 1
            save_game_play(sql_connection, game.game_id, game_play_index)
            if isinstance(game_play, GameAtBat):
                save_game_play_atbat(sql_connection, game.game_id, game_play_index, game_play)
            elif isinstance(game_play, GameSubstitution):
                save_game_play_sub(sql_connection, game.game_id, game_play_index, game_play)
            else:
                logger.error("Unknown game play type.  Type=%s", type(game_play))
                raise ValueError("Unknown game play record type.")
    except psycopg.Error as e:
        logger.error("Unable to save Record due to SQL error (%s):  Object=<%s>", e, str(game))
        raise e


# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
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
                    # Creating new Game
                    game = Game()
                    game.game_id = row[1]
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

    # Save Games List
    logger.info("Saving Games.  List is %s games long.", len(game_chunks))
    sql_connection = connect_to_db()
    try:
        for game in game_chunks:
            save_game(sql_connection, game)
    except psycopg.Error as e:
        sql_connection.rollback()
        logger.error("Unable to save games due to SQL error (%s)", e)
        raise e
    sql_connection.commit()


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
    logging.basicConfig(level=logging.DEBUG,
    handlers=[
        # no need - logging.FileHandler("baseball-ingest.log"),
        logging.StreamHandler()
    ])

    truncate_table(connect_to_db(), "game", True)
    import_event_file("2000ANA.EVA", "data/raw/")
