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
    DEFAULT = "DEFAULT"
    PREDICT_PITCH = "PredictPitch"
    PREDICT_PLAY = "PredictPlay"
    REGISTRY = "ModelRegistry"

# pylint: disable=too-few-public-methods
class ConfigKeys:
    """ Constants for valid config keys """
    MODEL_SOURCE = "model_source"
    DIR = "dir"
    NAME = "name"
    URL = "url"
    TOKEN = "token"
    NAMESPACE = "namespace"
    LABELS = "labels"
    KUBECONFIG = "kubeconfig"

def init(filename):
    """ Initializes configuration from INI file.
    
        filename - filename
    """
    # validate arguments
    if filename is None or len(filename) == 0:
        fail("Config Management provided an empty filename.")

    # get absolute path to config
    filename_abs = os.path.abspath(filename)

    # verify config file exists
    logger.info("Loading Configuration: %s", filename_abs)
    if not os.path.isfile(filename_abs):
        fail (f"Config file does not exist!  {filename_abs}")

    # initialize config
    results = config.read(filename_abs)
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
        if key not in config:
            return None
        return config[key]
    if key not in config[section]:
        return None
    return config[section][key]

def get_config_bool(section, key):
    """ Gets config value as a boolean.
    
        section - optional section name
        key - key name
    """
    # get config value
    val_str = get_config_str(section, key)
    logger.warning("VALUE == %s", val_str)
    if val_str is None or len(val_str) == 0:
        return None

    # convert to bool
    if val_str.lower().strip() in ['true', 1]:
        return True
    return False
