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

# pylint: disable=too-few-public-methods
class GameChunk:
    """ Data Structure for a game chunk that is incrementally assembled as 
    the file is parsed.
    """
    id = None
    info_attributes = {}
    starters = []
    play_list = []
    data_list = []

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
                    game = GameChunk()
                    game.id = row[1]
                    game_chunks.append(game)
                elif row[0] == "version":
                    pass
                elif row[0] == "info":
                    game.info_attributes[row[1]] = row[2]
                elif row[0] == "start":
                    game.starters.append(row)
                elif row[0] == "play" or row[0] == "sub":
                    game.play_list.append(row)
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
    print (game_chunks[0].info_attributes)



if __name__ == "__main__":
    import_event_file("2000ANA.EVA", "data/raw/")
