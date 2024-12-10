""" Service Gateway for invoking a hosted predictive model. """
import logging
import os
import requests
import numpy as np
from utils import fail
from config import get_config_str, ConfigKeys, ConfigSections
from prediction_tools import start_local_model_session, local_infer
from registry_gateway import get_model_inference_endpoint

logger = logging.getLogger(__name__)

MODEL_SOURCE_LOCAL = "local"
MODEL_SOURCE_API = "api"
MODEL_SOURCE_REGISTRY = "registry"

DEFAULT_TIMEOUT = 30

def predict(config_section, data):
    """ Perofrm a prediction based on the provided input features.
    
        config_section - configuration section containing model details
        data - data / features array
    """
    # validate parameters
    if config_section is None or len(config_section) == 0:
        fail("predict() called with no config_section specified")

    # determine model source
    model_source = get_config_str(ConfigSections.DEFAULT, ConfigKeys.MODEL_SOURCE)
    if model_source is None or len(model_source) == 0:
        fail("predict() is unable to determine model source - required element")
    model_source = model_source.strip().lower()

    # invoke prediction
    logger.info("Invoking Prediction w/input array: %s", data)
    infer_result = None
    if model_source == MODEL_SOURCE_LOCAL:
        logger.info("Using Local Models")
        infer_result = predict_via_local(config_section, data)
    elif model_source == MODEL_SOURCE_API:
        logger.info("Using Remote Inference Services (API Config)")
        infer_result = predict_via_configured_api(config_section, data)
    elif model_source == MODEL_SOURCE_REGISTRY:
        logger.info("Using Remote Inference Services using Registry (Model Registry)")
        infer_result = predict_via_registry(config_section, data)
    else:
        fail(f"predict() Unexpected model source value: {model_source}")
    logger.info("Prediction Response: Value=%s   Type=%s", infer_result, type(infer_result))

    return infer_result

def predict_via_local(config_section, data):
    """ Execute inference using local model files.
    
        config_section - configuration section containing model details
        data - data / features array
    """
    # get configured model directory
    model_dir_str = get_config_str(config_section, ConfigKeys.DIR)
    model_dir = os.path.abspath(model_dir_str)
    logger.info("Configured Model Directory: %s", model_dir)

    # load model
    predict_play_filename = model_dir + "/model.onnx"
    onnx_runtime_session = start_local_model_session(predict_play_filename)
    torch_input = np.array(data, dtype='float32')

    # execute inference
    infer_result = local_infer(onnx_runtime_session, torch_input)[0]
    return infer_result

def predict_via_registry(config_section, data):
    """ Execute inference using local model files.
    
        config_section - configuration section containing model details
        data - data / features array
    """
    # get config values
    namespace = get_config_str(config_section, ConfigKeys.NAMESPACE)
    model_name = get_config_str(config_section, ConfigKeys.NAME)
    labels = get_config_str(config_section, ConfigKeys.LABELS)

    # setup the version labels
    version_labels = []
    if labels is not None and len(labels) > 0:
        version_labels = [x.strip() for x in labels.split(",")]

    # lookup the api url
    endpoint, name = get_model_inference_endpoint(namespace=namespace,
                                                  model_name=model_name,
                                                  version_dict=version_labels)


    # execute inference
    infer_result = predict_via_rest(endpoint, name, data)
    return infer_result

def predict_via_configured_api(config_section, data):
    """ Execute inference using remote inference api w/endpoints specified as configuration.
    
        config_section - configuration section containing model details
        data - data / features array
    """
    # get config
    infer_endpoint = get_config_str(config_section, ConfigKeys.URL)
    deployed_model_name = get_config_str(config_section, ConfigKeys.NAME)

    # execute inference
    infer_result = predict_via_rest(infer_endpoint, deployed_model_name, data)
    return infer_result

def predict_via_rest(infer_endpoint, deployed_model_name, data):
    """ Perform a predictive AI model inferance being served on a hosted model.
    
        Assumes a 1d data set/list for data.

        infer_endpoint - inference url (rest)
        deployed_model_name - name of the deployed model within the inference server
    """
    # validate arguments
    if infer_endpoint is None or len(infer_endpoint) == 0:
        fail("predict_via_rest() - No endpoint provided")
    if deployed_model_name is None or len(deployed_model_name) == 0:
        fail("predict_via_rest() - No deployed model name provided")
    if data is None or len(data) == 0:
        fail("predict_via_rest() - No or empty data set provided")

    # build inference url
    infer_url = f"{infer_endpoint}/v2/models/{deployed_model_name}/infer"
    logger.info("Inference URL: %s", infer_url)

    # how many features?
    num_features = len(data)
    logger.debug("Number of features: %s", num_features)

    # validate data type
    datatype_str = None
    if isinstance(data[0], float):
        datatype_str = "FP32"
    else:
        fail(f"predict_via_rest() was passed an unexpected data type.  {type(data[0])}")

    # build request structure
    json_data = {
        "inputs": [
            {
                "name": "input",
                "shape": [num_features],
                "datatype": datatype_str,
                "data": data
            }
        ]
    }

    # invoke service
    response = requests.post(infer_url, json=json_data, verify=False, timeout=DEFAULT_TIMEOUT)
    logger.debug("Prediction HTTP Response: %s", response.text)
    if response.status_code != 200:
        fail(f"Prediction service invocation failed!  HttpResponseCode={response.status_code}")

    # return response
    response_dict = response.json()
    ai_response = response_dict['outputs'][0]['data']
    logger.debug("Prediction HTTP Response: %s", ai_response)
    return ai_response
