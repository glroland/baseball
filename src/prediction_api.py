""" API provider for baseball game/event predictions. """
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from predict.predict_pitch_service import PredictPitchRequest, predict_pitch
from utils.data import get_env_value

logger = logging.getLogger(__name__)

app = FastAPI()

ENV_MODEL_DIR = "MODEL_DIR"
DEFAULT_MODEL_DIR = "../output/predict_pitch/"
ENV_ENDPOINT_URL = "ENDPOINT_URL"
DEFAULT_ENDPOINT_URL = ""
ENV_MODEL_NAME = "MODEL_NAME"
DEFAULT_MODEL_NAME = ""

# Setup Logging
logging.basicConfig(level=logging.DEBUG,
    handlers=[
        # no need from a docker container - logging.FileHandler("prediction_api.log"),
        logging.StreamHandler()
    ])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """ Additional logging for getting extra detail about certain http binding errors. """
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error("Request: %s - Exception: %s" , request, exc_str)
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/")
async def root():
    """ Default API Request """
    return { "message": "Welcome to the Baseball Prediction Service!" }

@app.get("/predict_pitch")
async def predict_pitch_api(request : PredictPitchRequest):
    """ Fulfills a Predict Pitch API request
    
        request - request data structure
    """
    # get configured directory for model and scalers
    model_dir = get_env_value(ENV_MODEL_DIR, DEFAULT_MODEL_DIR)
    infer_endpoint = get_env_value(ENV_ENDPOINT_URL, DEFAULT_ENDPOINT_URL)
    deployed_model_name = get_env_value(ENV_MODEL_NAME, DEFAULT_MODEL_NAME)

    # perform operation
    result = predict_pitch(infer_endpoint, deployed_model_name, model_dir, request)
    return { "result": result }
