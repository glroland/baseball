""" Attempts to predict whether a baseball pitch will be a ball or a strike. """
import logging
from pydantic import BaseModel
from utils import fail, to_json_string
from prediction_tools import load_scaler, get_tf_num_for_value, get_tf_num_for_bool
from prediction_tools import SCALER_SUFFIX, scale_single_value
from inference_gateway import predict_via_rest

logger = logging.getLogger(__name__)

class PredictPitchRequest(BaseModel):
    """ Inference Request Parameters """
    pitch_index : int = None
    pitch_count : int = None
    runner_1b : str = None
    runner_2b : str = None
    runner_3b : str = None
    is_home : bool = None
    is_night : bool = None
    score_deficit : int = None

    def __str__(self) -> str:
        return to_json_string(self)

def predict_pitch(infer_endpoint, deployed_model_name, model_dir,
                  request : PredictPitchRequest):
    """ Predicts whether a pitch will be a ball or a strike. """
    # validate parameters
    if request is None:
        fail ("predict_pitch() was passed an empty request object.")
    if model_dir is None or len(model_dir) == 0:
        fail("predict_pitch() - No Model Dir configured.")
    logger.info("Predict Pitch - ModelDir=%s Request=%s", model_dir, request)

    # load scalers
    score_deficit_scaler = load_scaler(model_dir + "score_deficit" + SCALER_SUFFIX)
    pitch_count_scaler = load_scaler(model_dir + "pitch_count" + SCALER_SUFFIX)
    pitch_index_scaler = load_scaler(model_dir + "pitch_index" + SCALER_SUFFIX)

    # create input data structure
    data = []
    data.append(scale_single_value(pitch_index_scaler, request.pitch_index))
    data.append(scale_single_value(pitch_count_scaler, request.pitch_count))
    data.append(get_tf_num_for_value(request.runner_1b))
    data.append(get_tf_num_for_value(request.runner_2b))
    data.append(get_tf_num_for_value(request.runner_3b))
    data.append(get_tf_num_for_bool(request.is_home))
    data.append(get_tf_num_for_bool(request.is_night))
    data.append(scale_single_value(score_deficit_scaler, request.score_deficit))

    # perform the prediction
    logger.info("Invoking Predict Pitch w/input array: %s", data)
    result = predict_via_rest(infer_endpoint, deployed_model_name, data)
    logger.info("Prediction Response: Value=%s   Type=%s", result, type(result))

    return result
