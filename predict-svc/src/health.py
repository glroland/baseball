""" Health Check API Handler
"""
import logging
#from langchain_core.messages import HumanMessage
#from utils.openai_client import openai_invoke
#from utils.semantic_search import ping_database

logger = logging.getLogger(__name__)

def health_api_handler():
    """ Provide a basic response indicating the app is available for consumption. """
    # Test Database
#    ping_database()

#    # Test LLM
#    messages = [
#        HumanMessage(content="Why is the sky blue?")
#    ]
#    response = openai_invoke(messages, max_tokens=100, temperature=0.8, json_mode=False)
#    if response is None or len(response.content) == 0:
#        msg = "Health Check - LLM returned an invalid response!"
#        logger.fatal(msg)
#        raise ValueError(msg)

    return "OK"
