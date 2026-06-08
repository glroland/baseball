""" CLI for trimming old games from retrosheet's play by play processed event files. """
import logging
import os
import sys
import csv
import click
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

GAME_DATE_FIELD_INDEX = 174

@click.command()
@click.argument('input_file')
@click.argument('output_file')
@click.option('--earliest_year', default=2000, help='Earlest year to allow.')
def cli(input_file: str, output_file: str, earliest_year: int):
    """ CLI for removing old games from retrosheet's play by play data file.
    
        input_file - csv containing historical play by play data
        output_file - new file to create with older games removed
        earliest_year - (optional) remove data related to games before the specified year
    """
    # Default to not set
    logging.getLogger().setLevel(logging.NOTSET)

    # Log info and higher to the console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(name)-13s: %(message)s'))
    logging.getLogger().addHandler(console)

    # ensure data file exists
    logger.info("Input Data File: %s", input_file)
    if not os.path.exists(input_file) or not os.path.isfile(input_file):
        logger.error("%s must exist and be a data file!  ", input_file)
        sys.exit(1)

    # log the earliest year
    logger.info("Filtering all game data for years prior to: %s", earliest_year)

    # metrics
    line_counter = 0
    filtered_lines_counter = 0

    # create output file
    output_file_path = Path(output_file)
    output_file_path.unlink(missing_ok=True)
    output_csv_file = open(output_file, 'w')

    # load file and process line by line
    try:
        with open(input_file, 'r') as csv_file:

            for line in csv_file:
                line_counter += 1
                save_line = False
                line = line.strip()
    
                if line_counter > 1 and line is not None and len(line) > 0:
                    # convert line to csv record
                    csv_reader = csv.reader([line])
                    csv_line = next(csv_reader)

                    if len(csv_line) <= GAME_DATE_FIELD_INDEX:
                        logger.warning("Saving a short line even though the date could not be verified")
                        save_line = True
                    else:
                        # get the game date field
                        game_date_str = csv_line[GAME_DATE_FIELD_INDEX]
                        try:
                            game_datetime_object = datetime.strptime(game_date_str,  "%Y%m%d")
                        except ValueError as e:
                            logger.error("Cannot extract date from record.  Game Date = %s.  Line Number = %s, Line = %s", game_date_str, line_counter, line)
                            raise e
                        game_date = game_datetime_object.date()

                        # filter data
                        if game_date.year < earliest_year:
                            filtered_lines_counter += 1
                            save_line = False
                        else:
                            save_line = True

                if save_line or line_counter == 1:
                    output_csv_file.write(line + "\n")

    except FileNotFoundError:
        logger.fatal(f"Error: The file '{input_file}' was not found.")
        sys.exit(2)

    # close the file
    output_csv_file.close()

    # Successfully loaded data file
    logger.info("%s Successfully Trimmed!  Out of %s lines, %s were filtered.", input_file, line_counter, filtered_lines_counter)
    sys.exit(0)


if __name__ == '__main__':
    cli()
