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
from baseball_data import Game, Starter, GameAtBat, GameSubstitution, Data
from save_event_data import save_game
from game_events import interpret_game_at_bat_event

logger = logging.getLogger(__name__)

ROSTER_FILE_EXTENSION_AMERICAN = ".EVA"
ROSTER_FILE_EXTENSION_NATIONAL = ".EVN"

def extract_batter_events(game_id, batter_events, game_at_bat):
    """ Extract the batter event strings and apply onto the game at bat.
    
        game_id - game id
        batter_events - batter events
        atbat - at bat record
    """
    logger.debug("Extracting Batter Events!  ID=%s, Events=%s",
                     game_id, batter_events)

    # split batter events into chunks
    dot_index = batter_events.find(".")
    basic_play_w_mods = batter_events
    advance = None
    if dot_index != -1 and dot_index < len(batter_events):
        advance = batter_events[(dot_index+1):]
        basic_play_w_mods = batter_events[0:dot_index]
    l = basic_play_w_mods.split("/")
    basic_play = l.pop(0)
    modifiers = l

    # apply onto game at bat object
    game_at_bat.basic_play = basic_play
    game_at_bat.modifiers = modifiers
    game_at_bat.advance = advance


def on_game_end(game):
    """ Validate that the results of the game matches  the play by play data.
    
        game - game record
    """
    logger.info("Game Ended!  ID=%s Score=%-%", game.game_id,
                game.info_attributes[""],
                game.info_attributes[""])
    pass


def process_event_file_rows(file_with_path, game_limit):
    game_chunks = []

    with open(file_with_path, newline='', encoding="utf-8") as csvfile:
        game = None
        game_counter = 0

        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if len(row) > 0:
                if row[0] == "id":
                    # Reached game counter?
                    if game_limit > 0 and game_counter >= game_limit:
                        logger.warning("Game Limit Reached!  Aborting...  %s", game_counter)
                        return game_chunks

                    # Validate prior game
                    if game is not None:
                        on_game_end(game)

                    # Creating new Game
                    logger.info("New Game Record in Data File.  Index # %s", game_counter)
                    game = Game()
                    game.game_id = row[1]
                    game_chunks.append(game)
                    game_counter += 1
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
                    game_at_bat = game.new_at_bat(
                                inning = row[1],
                                home_team_flag = row[2] == "1",
                                player_code = row[3],
                                count = row[4],
                                pitches = row[5],
                                game_event = row[6])

                    # Process batter event
                    extract_batter_events(game.game_id, game_at_bat.game_event, game_at_bat)
                    interpret_game_at_bat_event(game_at_bat)
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

        # Validate prior game
        if game is not None:
            on_game_end(game)

    return game_chunks


def import_event_file(file, directory, game_limit = -1):
    """ Imports the specified event file.
    
        file - file to import
        directory - location of file
        game_limit - optionally limit the number of games loaded
    """
    file_with_path = directory + file
    logger.info("Importing Event File: %s", file_with_path)

    # Ensure file exists
    if not os.path.isfile(file_with_path):
        logger.error("Input file does not exist!  %s", file_with_path)
        raise ValueError("Cannot load file because it does not exist!")

    # Load CSV
    game_chunks = process_event_file_rows(file_with_path, game_limit)

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
    import_event_file("2000ANA.EVA", "data/raw/", 1)
