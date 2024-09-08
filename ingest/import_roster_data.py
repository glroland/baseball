""" Import Team Roster Data """
import logging
import os
from db_utils import bulk_import_csv_file

logger = logging.getLogger(__name__)

ROSTER_FILE_EXTENSION = ".ROS"

def import_roster_data_file(file, directory):
    """ Import the specified roster data file.
    
        data_file - roster file to import
    """
    data_file = directory + file
    logger.info("Importing Roster Data File: %s", data_file)

    year = int(file[3:7])
    logger.debug("Data File <%s> is mapping to Year <%s>", file, year)

    sql_table = "rosters"
    sql_columns_mapping = ["player_code",
                           "last_name",
                           "first_name",
                           "throw_hand",
                           "batting_hand",
                           "team_code",
                           "position"]

    bulk_import_csv_file(data_file, sql_table, sql_columns_mapping, "season_year", year)

    logger.debug("Deleting file after successful processing: %s", data_file)
    os.remove(data_file)


def import_all_roster_data_files(directory):
    """ Imports all roster data files stored in the specified directory.
    
        directory - directory to import roster files from
    """
    logger.info("Importing Roster Data Files from Directory: %s", directory)
    for file in os.listdir(directory):
        if file.endswith(ROSTER_FILE_EXTENSION):
            import_roster_data_file(file, directory)
    logger.debug("All files imported")
