""" Utility methods for use by prediction services. """
import logging
import joblib
from pandas.api.typing import NAType
import numpy as np
import onnx
import onnxruntime
from utils import fail

logger = logging.getLogger(__name__)

SCALER_SUFFIX = "_scaler.gz"

LOCAL_INFERENCE_EXECUTION_PROVIDERS = ['CUDAExecutionProvider', 'CPUExecutionProvider']

# pylint: disable=too-few-public-methods
class PredictionConstants:
    """ Constants used by the prediction tools. """
    VALUE_TRUE = 1
    VALUE_FALSE = 0

    NUM_EPOCHS = 300
    BATCH_SIZE = 10
    LOSS_RATE = 0.0001

def start_local_model_session(filename):
    """ Load a persisted onnx model from disk.
    
        filename - model filename 
    """
    # validate parameters
    if filename is None or len(filename) == 0:
        fail("start_local_model_session() invoked without filename")

    # load the onnx file
    onnx_model = onnx.load(filename)
    onnx.checker.check_model(onnx_model)

    onnx_runtime_session = onnxruntime.InferenceSession(filename,
                                                        providers=LOCAL_INFERENCE_EXECUTION_PROVIDERS)


    return onnx_runtime_session

def one_for_true(row, label):
    """ Simple utility function that returns 1 or 0 for a given cell, depending on whether
        its populated or not.
    
        row - dataframe row
        label - column name
    """
    v = row[label]
    if v:
        return PredictionConstants.VALUE_TRUE
    return PredictionConstants.VALUE_FALSE

def get_tf_num_for_value(x):
    """ Gets the true/false numeric value for a given variable, based on whether it 
        has been populated with something.
        
        x - value to test
    """
    if not isinstance(x, NAType) and len(x) > 0:
        return PredictionConstants.VALUE_TRUE
    return PredictionConstants.VALUE_FALSE

def get_tf_num_for_bool(x):
    """ Gets the true/false numeric value for a given boolean.
        
        x - value to test
    """
    if x:
        return PredictionConstants.VALUE_TRUE
    return PredictionConstants.VALUE_FALSE

def scale_single_value(scaler, value):
    """ Scales a single value
    
        scaler - scaler
        value - value
    """
    npa = scaler.transform(np.array([value]).reshape(-1, 1))
    return npa.tolist()[0][0]

def load_scaler(filename):
    """ Loads a previously persisted scaler.

        filename - filename
    """
    # validate parameters
    if filename is None or len(filename) == 0:
        fail("load_scaler() No filename provided")

    # load the previously persisted scaler
    scaler = joblib.load(filename)
    if scaler is None:
        fail("load_scaler() Resulting scaler after load is null!")
    return scaler

def local_infer(onnx_runtime_session, torch_input):
    """ Execute an inference locally.
    
        onnx_runtime_session - ONNX runtime session
        torch_input - model inputs
    """
    if onnx_runtime_session is None:
        fail("local_infer() called without onnx_runtime_session")
    if torch_input is None:
        fail("local_infer() called without torch_inputs")

    # convert inputs
    onnx_runtime_session_inputs = {onnx_runtime_session.get_inputs()[0].name: torch_input}

    # execute prediction
    onnx_runtime_session_outputs = onnx_runtime_session.run(None, onnx_runtime_session_inputs)
    print (f"Outputs: {onnx_runtime_session_outputs}")
    logger.info("ONNX Runtime Outputs: %s", onnx_runtime_session_outputs)

    return onnx_runtime_session_outputs

def get_item_float(item):
    """ Gets the float from the item, whether directly or via the numpy api.
    
        item - item
    """
    if isinstance(item, np.float32) or isinstance(item, np.float64):
        if np.isnan(item):
            return None
        return item.item()
    if isinstance(item, float):
        return item
    if item is None:
        return None

    fail(f"Could not process item: {item}")
