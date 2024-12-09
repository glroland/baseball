""" API provider for baseball game/event predictions. """
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from predict_pitch_service import PredictPitchRequest, predict_pitch
from predict_play_service import PredictPlayRequest, PredictPlayResponse, predict_play
from utils import get_env_value
from health import health_api_handler
from config import init

logger = logging.getLogger(__name__)

# Setup Logging
logging.basicConfig(level=logging.DEBUG,
    handlers=[
        # no need from a docker container - logging.FileHandler("prediction_api.log"),
        logging.StreamHandler()
    ])

app = FastAPI()

ENV_MODEL_DIR = "MODEL_DIR"
DEFAULT_MODEL_DIR = "../output/predict_play/"
ENV_ENDPOINT_URL = "ENDPOINT_URL"
DEFAULT_ENDPOINT_URL = ""
ENV_MODEL_NAME = "MODEL_NAME"
DEFAULT_MODEL_NAME = ""
ENV_CONFIG_FILE = "CONFIG_FILE"
DEFAULT_CONFIG_FILE = "config.ini"

# Setup Config
init(get_env_value(ENV_CONFIG_FILE, DEFAULT_CONFIG_FILE))

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
    # perform operation
    result = predict_pitch(request)
    logger.info("predict_play response: %s", result)
    response = { "result": result }
    logger.info("predict_play_api response: %s", response)
    return response

@app.get("/predict_play")
async def predict_play_api(request : PredictPlayRequest) -> PredictPlayResponse:
    """ Fulfills a Predict Play API request
    
        request - request data structure
    """
    # perform operation
    result = predict_play(request)
    logger.info("predict_play response: %s", result)
    response = { "result": result }
    logger.info("predict_play_api response: %s", response)
    return response

@app.get("/health", response_model=str)
def health():
    """ Provide a basic response indicating the app is available for consumption. """
    return health_api_handler()
