""" Attempts to predict what the next play will be. """
import logging
import os
from pydantic import BaseModel, Field
import numpy as np
from utils import fail, to_json_string
from config import get_config_bool, get_config_str, ConfigSections, ConfigKeys
from prediction_tools import load_scaler, get_tf_num_for_value, get_tf_num_for_bool
from prediction_tools import SCALER_SUFFIX, scale_single_value
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
    primary_play_type_cd_0 : float = Field(default=0)
    primary_play_type_cd_1 : float = Field(default=0)
    primary_play_type_cd_2 : float = Field(default=0)
    primary_play_type_cd_3 : float = Field(default=0)
    primary_play_type_cd_A : float = Field(default=0)
    primary_play_type_cd_B : float = Field(default=0)
    primary_play_type_cd_C : float = Field(default=0)
    primary_play_type_cd_D : float = Field(default=0)
    primary_play_type_cd_E : float = Field(default=0)
    primary_play_type_cd_F : float = Field(default=0)
    primary_play_type_cd_G : float = Field(default=0)
    primary_play_type_cd_H : float = Field(default=0)
    primary_play_type_cd_I : float = Field(default=0)
    primary_play_type_cd_K : float = Field(default=0)
    primary_play_type_cd_L : float = Field(default=0)
    primary_play_type_cd_N : float = Field(default=0)
    primary_play_type_cd_O : float = Field(default=0)
    primary_play_type_cd_P : float = Field(default=0)
    primary_play_type_cd_W : float = Field(default=0)
    primary_play_type_cd_X : float = Field(default=0)

    predicted_play : str = Field(default=None)
    probability : float = Field(default=None)

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
    response.primary_play_type_cd_0 = infer_result[0].item()
    response.primary_play_type_cd_1 = infer_result[1].item()
    response.primary_play_type_cd_2 = infer_result[2].item()
    response.primary_play_type_cd_3 = infer_result[3].item()
    response.primary_play_type_cd_A = infer_result[4].item()
    response.primary_play_type_cd_B = infer_result[5].item()
    response.primary_play_type_cd_C = infer_result[6].item()
    response.primary_play_type_cd_D = infer_result[7].item()
    response.primary_play_type_cd_E = infer_result[8].item()
    response.primary_play_type_cd_F = infer_result[9].item()
    response.primary_play_type_cd_G = infer_result[10].item()
    response.primary_play_type_cd_H = infer_result[11].item()
    response.primary_play_type_cd_I = infer_result[12].item()
    response.primary_play_type_cd_K = infer_result[13].item()
    response.primary_play_type_cd_L = infer_result[14].item()
    response.primary_play_type_cd_N = infer_result[15].item()
    response.primary_play_type_cd_O = infer_result[16].item()
    response.primary_play_type_cd_P = infer_result[17].item()
    response.primary_play_type_cd_W = infer_result[18].item()
    response.primary_play_type_cd_X = infer_result[19].item()

    max_num, index = [np.amax(infer_result), np.where(infer_result == np.amax(infer_result))[0]]
    response.probability = max_num.item()
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
