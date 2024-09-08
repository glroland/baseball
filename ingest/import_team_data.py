""" Import Team Data File """
import os
import logging
from db_utils import bulk_import_csv_file

logger = logging.getLogger(__name__)

TEAM_FILE_PREFIX = "TEAM"

def import_team_data_file(file, directory):
    """ Import the specified team data file.
    
        data_file - team file to import
    """
    data_file = directory + file
    logger.info("Importing Team Data File: %s", data_file)
    year = int(file.replace(TEAM_FILE_PREFIX, ""))
    logger.debug("Data File <%s> is mapping to Year <%s>", file, year)

    sql_table = "teams"
    sql_columns_mapping = ["team_code",
                           "league",
                           "team_location",
                           "team_name"]

    bulk_import_csv_file(data_file, sql_table, sql_columns_mapping, "season_year", year)

    logger.debug("Deleting file after successful processing: %s", data_file)
    os.remove(data_file)


def import_all_team_data_files(directory):
    """ Imports all team data files stored in the specified directory.
    
        directory - directory to import team files from
    """
    logger.info("Importing Team Data Files from Directory: %s", directory)
    for file in os.listdir(directory):
        if file.startswith(TEAM_FILE_PREFIX):
            import_team_data_file(file, directory)
    logger.debug("All files imported")
