""" Service Gateway for invoking a hosted predictive model. """
import logging
import requests
from utils.data import fail

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30

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
    logger.debug("Inference URL: %s", infer_url)

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
                "name": "dense_input",
                "shape": [1, num_features],
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
