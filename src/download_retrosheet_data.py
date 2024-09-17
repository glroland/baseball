""" Utility Functions for Downloading Game Data
"""
import logging
import os
import urllib.request
from datetime import datetime
from zipfile import ZipFile

logger = logging.getLogger(__name__)


RETROSHEET_URL = "https://www.retrosheet.org"
RETROSHEET_EVENTS_URL = RETROSHEET_URL + "/events/"

RETROSHEET_SEASON_FILE_SUFFIX = "seve.zip"
RETROSHEET_SEASON_START_YEAR = 2000     #oldest available - 1910


def download_retrosheet_decade_file(decade, location):
    """ Downloads the event file data from retrosheet for an entire decade.
    
        decade - decade for which to download
        location - where to store the zip file
    """
    logger.info("Downloading Retrosheet Season Data for Decade: %s", decade)

    file = str(decade) + RETROSHEET_SEASON_FILE_SUFFIX
    local_file = location + file
    if os.path.isfile(local_file):
        logger.info ("Skipping file (already exists): %s", local_file)
    else:
        url = RETROSHEET_EVENTS_URL + file
        logger.info ("Downloading zip file...  URL <%s> local_file<%s>", url, local_file)
        urllib.request.urlretrieve(url, local_file)
        logger.debug ("File downloaded: %s", local_file)


def download_all_retrosheet_seasons(location):
    """ Downloads all retrosheet season data.

        location - where to store the data files
    """
    logger.info("Downloading all retrosheet season data to location: %s", location)

    current_year = datetime.now().year
    year = RETROSHEET_SEASON_START_YEAR
    while year < current_year:
        download_retrosheet_decade_file(year, location)
        year += 10


def extract_zip_file(zip_file, target_dir):
    """ Extract a zip file to the specified target directory.
    
        zip_file - file to unzip
        target_dir - destination directory
    """
    logger.info("Extracting zip file to the target directory.  Zip=%s OutputDir=%s",
                zip_file, target_dir)
    with ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(target_dir)
        logger.debug("Unzipped file: %s", zip_file)


def extract_retrosheet_zip_files(source_dir, target_dir):
    """ Extract all available retrosheet zip files to the specified working directory.
    
        source_dir - where the zip files reside
        target_dir - destination folder for the contents
    """
    logger.info("Extracting all the downloaded retrosheet zip files.  Source=<%s> Target=<%s>",
                source_dir, target_dir)
    for file in os.listdir(source_dir):
        file_with_path = source_dir + file
        extract_zip_file(file_with_path, target_dir)
