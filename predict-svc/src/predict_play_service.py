""" Attempts to predict what the next play will be. """
import logging
from pydantic import BaseModel
from utils import fail, to_json_string
from prediction_tools import load_scaler, get_tf_num_for_value, get_tf_num_for_bool
from prediction_tools import SCALER_SUFFIX, scale_single_value
from inference_gateway import predict_via_rest

logger = logging.getLogger(__name__)

class PredictPlayRequest(BaseModel):
    """ Inference Request Parameters """
    pitch_index : int = None
    pitch_count : int = None
    score_deficit : int = None
    runner_1b : str = None
    runner_2b : str = None
    runner_3b : str = None
    batting_hand : str = None
    pitching_hand : str = None
    outs : int = None

    def __str__(self) -> str:
        return to_json_string(self)

def predict_play(infer_endpoint, deployed_model_name, model_dir,
                  request : PredictPlayRequest):
    """ Predicts what the next play will be. """
    # validate parameters
    if request is None:
        fail ("predict_play() was passed an empty request object.")
    if model_dir is None or len(model_dir) == 0:
        fail("predict_play() - No Model Dir configured.")
    logger.info("Predict Play - ModelDir=%s Request=%s", model_dir, request)

    # load scalers
    score_deficit_scaler = load_scaler(model_dir + "score_deficit" + SCALER_SUFFIX)
    pitch_count_scaler = load_scaler(model_dir + "pitch_count" + SCALER_SUFFIX)
    pitch_index_scaler = load_scaler(model_dir + "pitch_index" + SCALER_SUFFIX)

    # create input data structure
    data = []
    data.append(scale_single_value(pitch_index_scaler, request.pitch_index))
    data.append(scale_single_value(pitch_count_scaler, request.pitch_count))
    data.append(scale_single_value(score_deficit_scaler, request.score_deficit))
    data.append(get_tf_num_for_value(request.runner_1b))
    data.append(get_tf_num_for_value(request.runner_2b))
    data.append(get_tf_num_for_value(request.runner_3b))
    data.append(get_tf_num_for_bool(request.batting_hand == "L"))
    data.append(get_tf_num_for_bool(request.batting_hand == "R"))
    data.append(get_tf_num_for_bool(request.batting_hand == "B"))
    data.append(get_tf_num_for_bool(request.batting_hand == "L"))
    data.append(get_tf_num_for_bool(request.batting_hand == "R"))
    data.append(get_tf_num_for_bool(request.outs == 0))
    data.append(get_tf_num_for_bool(request.outs == 1))
    data.append(get_tf_num_for_bool(request.outs == 2))
    data.append(get_tf_num_for_bool(request.outs == 3))

    # perform the prediction
    logger.info("Invoking Predict Play w/input array: %s", data)
    result = predict_via_rest(infer_endpoint, deployed_model_name, data)
    logger.info("Prediction Response: Value=%s   Type=%s", result, type(result))

    return result
