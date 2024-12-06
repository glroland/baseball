""" Config Management Utilities """
import os.path
import logging
import configparser
from utils import fail

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()

# pylint: disable=too-few-public-methods
class ConfigSections:
    """ Constants for valid config sections """
    SERVING = "SERVING"

# pylint: disable=too-few-public-methods
class ConfigKeys:
    """ Constants for valid config keys """

def init(filename):
    """ Initializes configuration from INI file.
    
        filename - filename
    """
    # validate arguments
    if filename is None or len(filename) == 0:
        fail("Config Management provided an empty filename.")

    # verify config file exists
    logger.info("Loading Configuration: %s", filename)
    if not os.path.isfile(filename):
        fail (f"Config file does not exist!  {filename}")

    # initialize config
    results = config.read(filename)
    logger.info("Configuration Loaded. %s", results)

def get_config_str(section, key):
    """ Gets config value as a string.
    
        section - optional section name
        key - key name
    """
    # validate state
    if config is None:
        fail("Config Management - Getting config value before initialization")

    # get config value
    if section is None:
        return config[key]
    return config[section][key]
