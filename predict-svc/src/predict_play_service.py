""" Attempts to predict what the next play will be. """
import logging
import os
from pydantic import BaseModel, Field
import numpy as np
from utils import fail, to_json_string
from config import get_config_bool, get_config_str, ConfigSections, ConfigKeys
from prediction_tools import load_scaler, get_tf_num_for_value, get_tf_num_for_bool
from prediction_tools import SCALER_SUFFIX, scale_single_value, get_item_float
from prediction_tools import start_local_model_session, local_infer
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

class PredictPlayResponse(BaseModel):
    """ Inference Response Values """
    primary_play_type_cd_0 : float = 0
    primary_play_type_cd_1 : float = 0
    primary_play_type_cd_2 : float = 0
    primary_play_type_cd_3 : float = 0
    primary_play_type_cd_A : float = 0
    primary_play_type_cd_B : float = 0
    primary_play_type_cd_C : float = 0
    primary_play_type_cd_D : float = 0
    primary_play_type_cd_E : float = 0
    primary_play_type_cd_F : float = 0
    primary_play_type_cd_G : float = 0
    primary_play_type_cd_H : float = 0
    primary_play_type_cd_I : float = 0
    primary_play_type_cd_K : float = 0
    primary_play_type_cd_L : float = 0
    primary_play_type_cd_N : float = 0
    primary_play_type_cd_O : float = 0
    primary_play_type_cd_P : float = 0
    primary_play_type_cd_W : float = 0
    primary_play_type_cd_X : float = 0

    predicted_play : str = None
    probability : float = None

    def __str__(self) -> str:
        return to_json_string(self)

def predict_play(request : PredictPlayRequest) -> PredictPlayResponse:
    """ Predicts what the next play will be. 
    
        request - play state to evaluate
    """
    # validate parameters
    if request is None:
        fail ("predict_play() was passed an empty request object.")
    logger.info("Predict Play - Request=%s", request)

    # get configured model directory
    model_dir_str = get_config_str(ConfigSections.PREDICT_PLAY, ConfigKeys.MODEL_DIR)
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
    if get_config_bool(ConfigSections.DEFAULT, ConfigKeys.USE_LOCAL_MODELS):
        logger.info("Using Local Models")

        predict_play_filename = model_dir + "/model.onnx"
        onnx_runtime_session = start_local_model_session(predict_play_filename)
        torch_input = np.array(data, dtype='float32')
        
        infer_result = local_infer(onnx_runtime_session, torch_input)[0]
    else:
        logger.info("Using Remote Inference Services")

        infer_endpoint = get_config_str(ConfigSections.PREDICT_PLAY, ConfigKeys.ENDPOINT_URL)
        deployed_model_name = get_config_str(ConfigSections.PREDICT_PLAY, ConfigKeys.MODEL_NAME)
    
        infer_result = predict_via_rest(infer_endpoint, deployed_model_name, data)
    logger.info("Prediction Response: Value=%s   Type=%s", infer_result, type(infer_result))

    response = PredictPlayResponse()
    response.primary_play_type_cd_0 = get_item_float(infer_result[0])
    response.primary_play_type_cd_1 = get_item_float(infer_result[1])
    response.primary_play_type_cd_2 = get_item_float(infer_result[2])
    response.primary_play_type_cd_3 = get_item_float(infer_result[3])
    response.primary_play_type_cd_A = get_item_float(infer_result[4])
    response.primary_play_type_cd_B = get_item_float(infer_result[5])
    response.primary_play_type_cd_C = get_item_float(infer_result[6])
    response.primary_play_type_cd_D = get_item_float(infer_result[7])
    response.primary_play_type_cd_E = get_item_float(infer_result[8])
    response.primary_play_type_cd_F = get_item_float(infer_result[9])
    response.primary_play_type_cd_G = get_item_float(infer_result[10])
    response.primary_play_type_cd_H = get_item_float(infer_result[11])
    response.primary_play_type_cd_I = get_item_float(infer_result[12])
    response.primary_play_type_cd_K = get_item_float(infer_result[13])
    response.primary_play_type_cd_L = get_item_float(infer_result[14])
    response.primary_play_type_cd_N = get_item_float(infer_result[15])
    response.primary_play_type_cd_O = get_item_float(infer_result[16])
    response.primary_play_type_cd_P = get_item_float(infer_result[17])
    response.primary_play_type_cd_W = get_item_float(infer_result[18])
    response.primary_play_type_cd_X = get_item_float(infer_result[19])

    max_num, index = [np.amax(infer_result), np.where(infer_result == np.amax(infer_result))[0]]
    response.probability = get_item_float(max_num)
    if index == 0:
        response.predicted_play = "0"
    elif index == 1:
        response.predicted_play = "1"
    elif index == 2:
        response.predicted_play = "2"
    elif index == 3:
        response.predicted_play = "3"
    elif index == 4:
        response.predicted_play = "A"
    elif index == 5:
        response.predicted_play = "B"
    elif index == 6:
        response.predicted_play = "C"
    elif index == 7:
        response.predicted_play = "D"
    elif index == 8:
        response.predicted_play = "E"
    elif index == 9:
        response.predicted_play = "F"
    elif index == 10:
        response.predicted_play = "G"
    elif index == 11:
        response.predicted_play = "H"
    elif index == 12:
        response.predicted_play = "I"
    elif index == 13:
        response.predicted_play = "K"
    elif index == 14:
        response.predicted_play = "L"
    elif index == 15:
        response.predicted_play = "N"
    elif index == 16:
        response.predicted_play = "O"
    elif index == 17:
        response.predicted_play = "P"
    elif index == 18:
        response.predicted_play = "W"
    elif index == 19:
        response.predicted_play = "X"
    else:
        logger.warning("Index with maximum index is out of the bounds of the array!  %s", index)

    logger.info("API Response: Value=%s", response)
    logger.info("Root Prediction.  Play=%s   Probability=%s", response.predicted_play, response.probability)

    return response
