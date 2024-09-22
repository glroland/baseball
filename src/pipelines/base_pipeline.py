""" Pipeline Base Class

Base class for all data pipelines.
"""
import logging
from typing import List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class BasePipeline(BaseModel):
    """ Base class for data pipelines. """

    staged_records : List[List[str]] = []
    processed_records : List[List[str]] = []

    def count_staged_records(self):
        """ Count the number of pending records. """
        return len(self.staged_records)

    def stage_record(self, record : List[str]):
        """ Add a new record to the list of records to be processed.
        
            record - new record to be processed
        """
        # silently skip empty recores
        if record is None or len(record) == 0:
            logger.debug("Skipping empty record")

        # check for redelegation
        if not self.optionally_redelegate_record(record):
            # save record to pending records list
            self.staged_records.append(record)

    # pylint: disable=unused-argument
    def optionally_redelegate_record(self, record : List[str]):
        """ If implemented by a subclass, this is its opportunity to re-delegate the record
            to another pipeline. 
            
            record - row to delegate, optionally
        """
        return False

    def execute_pipeline(self):
        """ Orchestrate the end to end ingestion process associated with this pipeline. """
        raise NotImplementedError()

    def fail(self, msg):
        """ Fail with the specified error message.
        
            msg - error message
        """
        logger.fatal(msg)
        raise ValueError(msg)
