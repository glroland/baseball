""" Import Event Data Utilities 

Event files are a more complicated format that involves piecing together games
based on a serious of related rows in a particular order.  These utilities are
parsers for these files that are then able to insert into a relational database
that we can more easily use to build training data for the models.
"""
import logging
import os
import csv
from pipelines.event_file_pipeline import EventFilePipeline

logger = logging.getLogger(__name__)

ROSTER_FILE_EXTENSION_AMERICAN = ".EVA"
ROSTER_FILE_EXTENSION_NATIONAL = ".EVN"

def import_event_file(file_with_path):
    """ Imports the specified event file.
    
        file_with_path - file to import
    """
    logger.info("Importing Event File: %s", file_with_path)

    # Ensure file exists
    if not os.path.isfile(file_with_path):
        logger.error("Input file does not exist!  %s", file_with_path)
        raise ValueError("Cannot load file because it does not exist!")

    # Load CSV
    event_file_pipeline = EventFilePipeline()
    event_file_pipeline.filename = file_with_path
    with open(file_with_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            event_file_pipeline.stage_record(row)
    logger.info("%s Records Loaded from Events File %s",
                event_file_pipeline.count_staged_records(), file_with_path)

    # Execute data processing pipelines
    event_file_pipeline.execute_pipeline()

    # Save Games
    event_file_pipeline.save()

def import_all_event_data_files(directory):
    """ Imports all event data files stored in the specified directory.
    
        directory - directory to import roster files from
    """
    logger.info("Importing Roster Data Files from Directory: %s", directory)
    for file in os.listdir(directory):
        if file.endswith(ROSTER_FILE_EXTENSION_AMERICAN) or \
           file.endswith(ROSTER_FILE_EXTENSION_NATIONAL):
            file_with_path = directory + file
            import_event_file(file_with_path)

            logger.debug("Deleting file after successful processing: %s", file)
            os.remove(file)
    logger.debug("All files imported")
