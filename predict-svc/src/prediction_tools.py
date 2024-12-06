""" Utility methods for use by prediction services. """
import logging
import joblib
from pandas.api.typing import NAType
import numpy as np
import onnx
#import onnxruntime
from utils import fail

logger = logging.getLogger(__name__)

SCALER_SUFFIX = "_scaler.gz"

# pylint: disable=too-few-public-methods
class PredictionConstants:
    """ Constants used by the prediction tools. """
    VALUE_TRUE = 1
    VALUE_FALSE = 0

    NUM_EPOCHS = 300
    BATCH_SIZE = 10
    LOSS_RATE = 0.0001

def load_model(filename):
    """ Load a persisted onnx model from disk.
    
        filename - model filename 
    """
    # load the onnx file
    onnx_model = onnx.load(filename)
    onnx.checker.check_model(onnx_model)
    return onnx_model

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

#def onnx_infer(filename, torch_input):
#    onnx_input = onnx_program.adapt_torch_inputs_to_onnx(torch_input)
#    print(f"Input length: {len(onnx_input)}")
#    print(f"Sample input: {onnx_input}")
#
#    ort_session = onnxruntime.InferenceSession(filename, providers=['CPUExecutionProvider'])
#
#    def to_numpy(tensor):
#        return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()
#
#    onnxruntime_input = {k.name: to_numpy(v) for k, v in zip(ort_session.get_inputs(), onnx_input)}
#
#    onnxruntime_outputs = ort_session.run(None, onnxruntime_input)
#    return onnxruntime_outputs

#def onnx_infer2():
#    torch_outputs = model(torch_input)
#    torch_outputs = onnx_program.adapt_torch_outputs_to_onnx(torch_outputs)
#
#    assert len(torch_outputs) == len(onnxruntime_outputs)
#    for torch_output, onnxruntime_output in zip(torch_outputs, onnxruntime_outputs):
#        torch.testing.assert_close(torch_output, torch.tensor(onnxruntime_output))
#
#    print("PyTorch and ONNX Runtime output matched!")
#    print(f"Output length: {len(onnxruntime_outputs)}")
#    print(f"Sample output: {onnxruntime_outputs}")

## define 5-fold cross validation test harness
#kfold = StratifiedKFold(n_splits=5, shuffle=True)
#cv_scores = []
#for train, test in kfold.split(X_train, y_train):
#    model = PitchPredictionModel()
#    acc = model_train(model, X_train[train], y_train[train], X_train[test], y_train[test])
#    print("Accuracy (wide): %.2f" % acc)
#    cv_scores.append(acc)

# evaluate the model
#acc = np.mean(cv_scores)
#std = np.std(cv_scores)
#print("Cross Validation Scores: %.2f%% (+/- %.2f%%)" % (acc*100, std*100))
