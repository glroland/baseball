""" Attempts to predict whether a baseball pitch will be a ball or a strike. """
import logging
import os
import numpy as np
from pydantic import BaseModel, Field
from utils import fail, to_json_string
from config import get_config_str, ConfigSections, ConfigKeys
from prediction_tools import load_scaler, get_tf_num_for_value, get_tf_num_for_bool
from prediction_tools import SCALER_SUFFIX, scale_single_value, get_item_float
from prediction_tools import start_local_model_session, local_infer
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

class PredictPitchResponse(BaseModel):
    """ Inference Response Values """
    probability_of_strike : float = Field(default=None)

    def __str__(self) -> str:
        return to_json_string(self)

def predict_pitch(request : PredictPitchRequest) -> PredictPitchResponse:
    """ Predicts whether a pitch will be a ball or a strike. """
    # validate parameters
    if request is None:
        fail ("predict_pitch() was passed an empty request object.")
    logger.info("Predict Pitch - Request=%s", request)

    # get configured model directory
    model_dir_str = get_config_str(ConfigSections.PREDICT_PITCH, ConfigKeys.DIR)
    model_dir = os.path.abspath(model_dir_str)
    logger.info("Configured Model Directory: %s", model_dir)

    # load scalers
    score_deficit_scaler = load_scaler(model_dir + "/" + "score_deficit" + SCALER_SUFFIX)
    pitch_count_scaler = load_scaler(model_dir + "/" + "pitch_count" + SCALER_SUFFIX)
    pitch_index_scaler = load_scaler(model_dir + "/" + "pitch_index" + SCALER_SUFFIX)

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
    if get_config_str(ConfigSections.DEFAULT, ConfigKeys.MODEL_SOURCE) == "local":
        logger.info("Using Local Models")

        predict_pitch_filename = model_dir + "/model.onnx"
        onnx_runtime_session = start_local_model_session(predict_pitch_filename)
        torch_input = np.array(data, dtype='float32')
        
        infer_result = local_infer(onnx_runtime_session, torch_input)[0]
    else:
        logger.info("Using Remote Inference Services")

        infer_endpoint = get_config_str(ConfigSections.PREDICT_PITCH, ConfigKeys.URL)
        deployed_model_name = get_config_str(ConfigSections.PREDICT_PITCH, ConfigKeys.NAME)
    
        infer_result = predict_via_rest(infer_endpoint, deployed_model_name, data)
    logger.info("Prediction Response: Value=%s   Type=%s", infer_result, type(infer_result))

    response = PredictPitchResponse()
    response.probability_of_strike = get_item_float(infer_result[0])

    return response
