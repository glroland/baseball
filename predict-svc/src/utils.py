""" General Utility Functions """
import os
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

def get_env_value(env_key : str, default : str = None):
    """ Gets the value of the specified environment variable.
    
        env_key - environment variable name
        default - default value if that is not set
    """
    # validate paratmers
    if env_key is None or len(env_key) == 0:
        fail("get_env() - called without valid env_key!")

    # get configured value
    value = default
    if env_key in os.environ:
        value = os.environ[env_key]
    else:
        logger.warning("Config Key not set!  Using default...  Key=%s", env_key)

    logger.debug("Configuration Value.  Key=%s  Value=%s", env_key, value)
    return value

def fail(s : str):
    """ Log and fail process.
    
        s - string to log
    """
    logger.fatal(s)
    raise ValueError(s)

def to_json_string(i : BaseModel):
    """ Create a JSON string for the provided pydantic model.
    
        i - model
    """
    return i.model_dump_json(indent=2)
