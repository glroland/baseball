""" Baseball App CLI """
import logging
import sys
import os
import click
from utils.db import truncate_table, connect_to_db_with_conn_str
from ingest.import_event_data import import_event_file, import_all_event_data_files

logger = logging.getLogger(__name__)

class ColorOutputFormatter(logging.Formatter):
    """ Add colors to stdout logging output to simplify text.  Thank you to:
        https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = '%(name)-13s: %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

@click.command()
@click.argument('event_file_or_dir')
@click.option('--save', 'db_conn_str', default=None, nargs=1,
              help='whether or not to truncate game tables before import')
@click.option('--truncate', default=False, is_flag=True,
              help='whether or not to truncate game tables before import')
@click.option('--debug', 'log_file', nargs=1, default=None,
              help='enable debug level logging or keep as info')
@click.option('--move', 'move_to_dir', nargs=1, default=None,
              help='move files to another directory after processing')
@click.option('--skip-errors', default=False, is_flag=True,
              help='whether or not to skip files with errors or abort')
@click.option('--delete', default=False, is_flag=True,
              help='whether or not to delete files after processing')
# pylint: disable=too-many-arguments
def cli(db_conn_str, event_file_or_dir, truncate, log_file, move_to_dir,
        skip_errors=False, delete=False):
    """ CLI utility for importing Retrosheet event files into the game
        history database.  This tool assumes that team and roster data
        has already been imported.
    """
    # Default to not set
    logging.getLogger().setLevel(logging.NOTSET)

    # Log info and higher to the console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(ColorOutputFormatter())
    logging.getLogger().addHandler(console)

    # Log debug and higher to a file
    if log_file is not None:
        file_handler = logging.FileHandler(log_file, 'w+')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    # Validate arguments
    if truncate and db_conn_str is None:
        logger.error("Cannot truncate tables if no connection string was provided!")
        sys.exit(1)
    if delete and move_to_dir is not None:
        logger.error("Cannot both delete file and move to another directory after processing!")
        sys.exit(2)
    if os.path.isfile(event_file_or_dir) and skip_errors:
        logger.error("Skipping errors is only allowed when the input is a directory, not a file!")
        sys.exit(3)

    # (Optional) Truncate all game event data in the database
    if truncate:
        logger.warning("Truncating game table!")
        truncate_table(connect_to_db_with_conn_str(db_conn_str), "game", True)

    if os.path.isfile(event_file_or_dir):
        # Import event file
        import_event_file(event_file_or_dir, db_conn_str, move_to_dir, delete)
    elif os.path.isdir(event_file_or_dir):
        # Import all files in directory
        import_all_event_data_files(event_file_or_dir,
                                    skip_errors,
                                    db_conn_str,
                                    move_to_dir,
                                    delete)
    else:
        logger.error("Input events location is neither a file nor a directory! %s",
                     event_file_or_dir)
        sys.exit(2)

if __name__ == '__main__':
    cli(None, None, None, None, None)
